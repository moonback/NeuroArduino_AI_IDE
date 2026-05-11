import os
import re
from groq import Groq
import google.generativeai as genai
import sys
from dotenv import load_dotenv

# Env Loading Logic
search_paths = [
    os.path.join(os.getcwd(), ".env"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
]

if getattr(sys, 'frozen', False):
    search_paths.append(os.path.join(os.path.dirname(sys.executable), ".env"))

env_path = None
for p in search_paths:
    if os.path.exists(p):
        env_path = p
        break

if env_path:
    print(f"Loading .env from: {env_path}")
    load_dotenv(env_path, override=True)
else:
    print("Warning: No .env file found!")

class CodeGeneratorAgent:
    def __init__(self):
        # Groq Setup
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
            self.groq_model = "llama-3.3-70b-versatile"
        else:
            self.groq_client = None

        # Gemini Setup
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.gemini_model = None

    def generate(self, prompt: str, board: str, provider: str = "groq", history: list = None) -> str:
        system_instruction = (
            "You are Audino, an AI-powered Arduino IDE and code generator.\n"
            "Your only task is to generate clean, correct, and compilable Arduino code from simple natural language instructions.\n"
            "Always output valid Arduino C/C++ code.\n"
            f"Assume Arduino Uno unless specified otherwise. Current Target: {board}.\n"
            "Always include setup() and loop().\n"
            "Prefer simplicity over complexity.\n"
            "Infer sensible defaults when details are missing.\n"
            "Output only code. No explanations. No markdown."
        )

        history = history or []

        # 1. Groq Provider
        if provider == "groq" and self.groq_client:
            try:
                messages = [{"role": "system", "content": system_instruction}]
                # Add history
                for msg in history:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
                
                # Add current prompt
                messages.append({"role": "user", "content": prompt})

                completion = self.groq_client.chat.completions.create(
                    messages=messages,
                    model=self.groq_model,
                )
                code = completion.choices[0].message.content
                return self._clean_code(code)
            except Exception as e:
                print(f"Groq API Error: {e}")
                return f"// Error: Groq Generation Failed.\n// Details: {str(e)}"

        # 2. Gemini Provider
        elif provider == "gemini" and self.gemini_model:
            try:
                # Gemini chat history format: [{'role': 'user', 'parts': ['...']}, {'role': 'model', 'parts': ['...']}]
                chat_history = []
                for msg in history:
                    role = "user" if msg.get("role") == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg.get("content", "")]})
                
                chat = self.gemini_model.start_chat(history=chat_history)
                response = chat.send_message(f"{system_instruction}\n\nUser Request: {prompt}")
                code = response.text
                return self._clean_code(code)
            except Exception as e:
                print(f"Gemini API Error: {e}")
                return f"// Error: Gemini Generation Failed.\n// Details: {str(e)}"

        # 3. Offline/Fallback Logic (if keys missing or invalid provider)
        return self._generate_offline(prompt, board)

    def _clean_code(self, code: str) -> str:
        code = code.replace("```cpp", "").replace("```c++", "").replace("```arduino", "").replace("```", "").strip()
        return code

    def _generate_offline(self, prompt: str, board: str) -> str:
        prompt = prompt.lower()
        setup_lines = []
        loop_lines = []
        globals_lines = []

        if "blink" in prompt or "led" in prompt:
            pin = 13
            pin_match = re.search(r'pin (\d+)', prompt)
            if pin_match:
                pin = int(pin_match.group(1))
            
            setup_lines.append(f"pinMode({pin}, OUTPUT);")
            loop_lines.append(f"digitalWrite({pin}, HIGH);")
            loop_lines.append("delay(1000);")
            loop_lines.append(f"digitalWrite({pin}, LOW);")
            loop_lines.append("delay(1000);")

        if "button" in prompt:
            btn_pin = 2
            setup_lines.append(f"pinMode({btn_pin}, INPUT_PULLUP);")
            loop_lines.append(f"if (digitalRead({btn_pin}) == LOW) {{")
            loop_lines.append("  // Button pressed action")
            loop_lines.append("}}")

        if "motor" in prompt:
            motor_pin = 9
            setup_lines.append(f"pinMode({motor_pin}, OUTPUT);")
            loop_lines.append(f"analogWrite({motor_pin}, 128); // 50% speed")

        if not setup_lines:
            if not self.groq_api_key and not self.gemini_api_key:
                return "// Error: No AI API keys found (GROQ_API_KEY or GEMINI_API_KEY).\n// Please check your .env file."
            return "// I'm not sure what you want to build. Try 'Blink LED' or 'Read Button'."

        code = "// Generated by Audino AI (Offline Mode)\n"
        code += "\n".join(globals_lines) + "\n\n"
        code += "void setup() {\n  " + "\n  ".join(setup_lines) + "\n}\n\n"
        code += "void loop() {\n  " + "\n  ".join(loop_lines) + "\n}\n"
        return code

class HardwareRulesAgent:
    def check_safety(self, prompt: str, code: str) -> list:
        warnings = []
        prompt = prompt.lower()
        if "motor" in prompt:
            warnings.append("⚠️ SAFETY: Do not power motors directly from Arduino 5V pin! Use an external power supply and share Ground.")
        if "pin 0" in code or "pin 1" in code:
            warnings.append("ℹ️ NOTE: Pins 0 and 1 are used for Serial communication. Avoid using them for IO if using Serial.")
        return warnings

# Main Orchestrator
code_agent = CodeGeneratorAgent()
safety_agent = HardwareRulesAgent()

def process_ai_request(prompt: str, board: str, provider: str = "groq", history: list = None):
    # 1. Generate Code
    code = code_agent.generate(prompt, board, provider, history)
    
    # 2. Safety Check
    warnings = safety_agent.check_safety(prompt, code)
    
    explanation = f"I've generated the code for you using {provider.capitalize()}."
    if "Offline Mode" in code:
        explanation = "I've generated a basic template (Offline Mode)."
    
    if warnings:
        explanation += "\n\n" + "\n".join(warnings)
    
    return {"code": code, "explanation": explanation}
