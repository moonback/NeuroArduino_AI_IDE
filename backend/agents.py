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
            self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
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


class VisionAgent:
    """Analyzes wiring photos using Gemini multimodal and generates Arduino code."""

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            # Use a model that supports multimodal input
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

    def analyze(self, image_data: str, prompt: str = "", board: str = "arduino:avr:uno") -> dict:
        """
        Analyze a base64-encoded image of an Arduino wiring setup.
        Returns dict with keys: code, explanation, components
        """
        if not self.model:
            return {
                "code": "// Error: GEMINI_API_KEY is required for Vision-to-Wire.\n// Please set it in your .env file.",
                "explanation": "Gemini API key is not configured. Vision-to-Wire requires a valid GEMINI_API_KEY.",
                "components": []
            }

        try:
            import base64

            # Extract mime type and raw base64 from data URL
            # Format: data:image/jpeg;base64,/9j/4AAQ...
            if "," in image_data:
                header, b64_data = image_data.split(",", 1)
                mime_type = header.split(":")[1].split(";")[0] if ":" in header else "image/jpeg"
            else:
                b64_data = image_data
                mime_type = "image/jpeg"

            image_bytes = base64.b64decode(b64_data)

            system_prompt = (
                "You are Audino Vision, an expert Arduino wiring analyzer.\n"
                "You are given a photo of an Arduino/electronics breadboard wiring setup.\n\n"
                "Your task is to:\n"
                "1. IDENTIFY all visible electronic components (LEDs, resistors, sensors, motors, buttons, etc.)\n"
                "2. TRACE the wiring connections between components and the Arduino board\n"
                "3. DETERMINE which Arduino pins are connected to which components\n"
                "4. GENERATE clean, correct, compilable Arduino code that matches the wiring\n\n"
                f"Target board: {board}\n\n"
                "You MUST respond in EXACTLY this format (use these exact headers):\n"
                "COMPONENTS: comma-separated list of detected components\n"
                "EXPLANATION: 2-3 sentence description of the circuit and what the code does\n"
                "CODE:\n```\n<your Arduino code here>\n```\n"
            )

            user_msg = "Analyze this Arduino wiring photo and generate the corresponding code."
            if prompt:
                user_msg += f"\n\nAdditional context from the user: {prompt}"

            # Build multimodal content
            image_part = {
                "mime_type": mime_type,
                "data": image_bytes
            }

            response = self.model.generate_content([
                system_prompt,
                image_part,
                user_msg
            ])

            return self._parse_response(response.text)

        except Exception as e:
            print(f"Vision Analysis Error: {e}")
            return {
                "code": f"// Error during vision analysis.\n// Details: {str(e)}",
                "explanation": f"An error occurred during image analysis: {str(e)}",
                "components": []
            }

    def _parse_response(self, text: str) -> dict:
        """Parse the structured response from Gemini into components, explanation, and code."""
        components = []
        explanation = ""
        code = ""

        # Extract components
        comp_match = re.search(r'COMPONENTS:\s*(.+?)(?:\n|EXPLANATION)', text, re.DOTALL | re.IGNORECASE)
        if comp_match:
            comp_str = comp_match.group(1).strip()
            components = [c.strip() for c in comp_str.split(",") if c.strip()]

        # Extract explanation
        exp_match = re.search(r'EXPLANATION:\s*(.+?)(?:\nCODE|```)', text, re.DOTALL | re.IGNORECASE)
        if exp_match:
            explanation = exp_match.group(1).strip()

        # Extract code
        code_match = re.search(r'```(?:cpp|c\+\+|arduino|c)?\s*\n?(.*?)```', text, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
        else:
            # Try to find code block after CODE: header
            code_match2 = re.search(r'CODE:\s*\n(.*)', text, re.DOTALL | re.IGNORECASE)
            if code_match2:
                code = code_match2.group(1).strip()
                code = code.replace("```cpp", "").replace("```c++", "").replace("```arduino", "").replace("```", "").strip()

        # Fallback: if parsing failed, use the full text
        if not code:
            code = "// Could not parse code from vision response.\n// Raw response was logged to console."
            print(f"Vision parse fallback. Raw text:\n{text}")

        if not explanation:
            explanation = "Circuit analyzed successfully."

        return {
            "code": code,
            "explanation": explanation,
            "components": components
        }


# Main Orchestrator
code_agent = CodeGeneratorAgent()
safety_agent = HardwareRulesAgent()
vision_agent = VisionAgent()

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

def process_vision_request(image_data: str, prompt: str = "", board: str = "arduino:avr:uno"):
    # 1. Vision Analysis
    result = vision_agent.analyze(image_data, prompt, board)
    
    # 2. Safety Check on generated code
    combined_prompt = prompt + " " + " ".join(result.get("components", []))
    warnings = safety_agent.check_safety(combined_prompt, result.get("code", ""))
    
    if warnings:
        result["explanation"] += "\n\n" + "\n".join(warnings)
    
    return result
