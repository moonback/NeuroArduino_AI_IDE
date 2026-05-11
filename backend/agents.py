import os
import re
import json
from groq import Groq
import google.generativeai as genai
import sys
from dotenv import load_dotenv
from tools_registry import ToolRegistry
from system_prompts import get_prompt_manager

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
    def __init__(self, workspace_root: str = None):
        # Groq Setup
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
            # Use llama-3.3-70b-versatile (latest available model)
            # Note: Function calling support varies by model
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
        
        # Tool Registry
        self.tool_registry = ToolRegistry(workspace_root)
        
        # System Prompt Manager
        self.prompt_manager = get_prompt_manager()

    def generate(self, prompt: str, board: str, provider: str = "groq", history: list = None, enable_tools: bool = True) -> dict:
        # Get appropriate system prompt with tool calling capabilities
        tool_definitions = ""
        if enable_tools:
            tool_definitions = self.tool_registry.get_tool_definitions_text()
        
        system_instruction = self.prompt_manager.get_combined_prompt(
            contexts=["base", "code_generation"],
            board=board,
            enable_tools=enable_tools,
            tool_definitions=tool_definitions
        )

        history = history or []

        # 1. Groq Provider (with function calling support)
        if provider == "groq" and self.groq_client:
            try:
                messages = [{"role": "system", "content": system_instruction}]
                
                # Add history
                for msg in history:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
                
                # Add current prompt
                messages.append({"role": "user", "content": prompt})

                # Check if Groq supports function calling (it does for some models)
                if enable_tools:
                    # Try with function calling
                    try:
                        print(f"[DEBUG] Calling Groq with tools enabled")
                        print(f"[DEBUG] Number of tools available: {len(self.tool_registry.get_tool_definitions())}")
                        
                        completion = self.groq_client.chat.completions.create(
                            messages=messages,
                            model=self.groq_model,
                            tools=self.tool_registry.get_tool_definitions(),
                            tool_choice="auto"
                        )
                        
                        response_message = completion.choices[0].message
                        
                        print(f"[DEBUG] Response has tool_calls: {hasattr(response_message, 'tool_calls') and response_message.tool_calls is not None}")
                        
                        # Check if AI wants to use tools
                        if response_message.tool_calls:
                            print(f"[DEBUG] AI wants to use {len(response_message.tool_calls)} tool(s)")
                            tool_calls = []
                            tool_results = []
                            
                            for tool_call in response_message.tool_calls:
                                tool_name = tool_call.function.name
                                tool_params = json.loads(tool_call.function.arguments)
                                
                                print(f"[DEBUG] Executing tool: {tool_name}")
                                print(f"[DEBUG] Parameters: {tool_params}")
                                
                                # Execute tool
                                result = self.tool_registry.execute_tool(tool_name, tool_params)
                                
                                print(f"[DEBUG] Tool result: {result.get('status', 'unknown')}")
                                
                                tool_calls.append({
                                    "id": tool_call.id,
                                    "tool": tool_name,
                                    "parameters": tool_params
                                })
                                
                                tool_results.append({
                                    "id": tool_call.id,
                                    "tool": tool_name,
                                    "result": result
                                })
                            
                            return {
                                "message": response_message.content or "I've executed the requested operations.",
                                "tool_calls": tool_calls,
                                "tool_results": tool_results,
                                "code": None
                            }
                        else:
                            print(f"[DEBUG] No tool calls, returning regular response")
                            # No tool calls, just return the message
                            content = response_message.content
                            code = self._extract_code(content)
                            return {
                                "message": content if not code else self._remove_code_from_message(content),
                                "code": code,
                                "tool_calls": [],
                                "tool_results": []
                            }
                    
                    except Exception as e:
                        # Fallback to regular completion if function calling fails
                        print(f"[DEBUG] Function calling failed: {e}")
                        print(f"[DEBUG] Attempting manual tool parsing fallback")
                        completion = self.groq_client.chat.completions.create(
                            messages=messages,
                            model=self.groq_model,
                        )
                        content = completion.choices[0].message.content
                        
                        # Try to parse manual tool calls from response
                        result = self._parse_response_with_tools(content)
                        
                        # If no tools were found but we have a current file context, force tool usage
                        if not result.get('tool_calls') and enable_tools:
                            # Check if this looks like a modification request
                            if any(keyword in prompt.lower() for keyword in ['change', 'modify', 'update', 'improve', 'fix', 'add', 'refactor']):
                                if '[CURRENT FILE:' in prompt:
                                    print(f"[DEBUG] Detected modification request without tool call - forcing smart_modify_file")
                                    # Extract file path from context
                                    import re
                                    file_match = re.search(r"\[CURRENT FILE: '([^']+)' at '([^']+)'\]", prompt)
                                    if file_match:
                                        file_name = file_match.group(1)
                                        file_path = file_match.group(2)
                                        
                                        # Try to extract what needs to be changed from the AI's response
                                        print(f"[WARNING] AI did not use tools. Response: {content[:200]}")
                                        result['message'] = "⚠️ I generated a response but didn't use the file modification tools. Please try rephrasing your request, or I can show you the code to manually apply."
                        
                        return result
                else:
                    # Tools disabled, regular generation
                    completion = self.groq_client.chat.completions.create(
                        messages=messages,
                        model=self.groq_model,
                    )
                    content = completion.choices[0].message.content
                    code = self._extract_code(content)
                    return {
                        "message": content if not code else self._remove_code_from_message(content),
                        "code": code,
                        "tool_calls": [],
                        "tool_results": []
                    }
                    
            except Exception as e:
                print(f"Groq API Error: {e}")
                return {
                    "message": f"Error: Groq Generation Failed.\nDetails: {str(e)}",
                    "code": None,
                    "tool_calls": [],
                    "tool_results": []
                }

        # 2. Gemini Provider (with native function calling support)
        elif provider == "gemini" and self.gemini_model:
            try:
                # Gemini supports native function calling
                if enable_tools:
                    # Convert tool definitions to Gemini format
                    # Gemini expects a list of function declarations
                    from google.generativeai.types import FunctionDeclaration, Tool
                    
                    gemini_functions = []
                    for tool_def in self.tool_registry.get_tool_definitions():
                        func = tool_def["function"]
                        
                        # Clean parameters - remove "default" fields that Gemini doesn't support
                        clean_params = self._clean_params_for_gemini(func["parameters"])
                        
                        gemini_functions.append(
                            FunctionDeclaration(
                                name=func["name"],
                                description=func["description"],
                                parameters=clean_params
                            )
                        )
                    
                    gemini_tool = Tool(function_declarations=gemini_functions)
                    
                    print(f"[DEBUG] Calling Gemini with {len(gemini_functions)} tools")
                    
                    # Create model with tools
                    model_with_tools = genai.GenerativeModel(
                        "gemini-2.0-flash-exp",
                        tools=[gemini_tool]
                    )
                    
                    # Build chat history
                    chat_history = []
                    for msg in history:
                        role = "user" if msg.get("role") == "user" else "model"
                        chat_history.append({"role": role, "parts": [msg.get("content", "")]})
                    
                    chat = model_with_tools.start_chat(history=chat_history)
                    response = chat.send_message(f"{system_instruction}\n\nUser Request: {prompt}")
                    
                    # Check if Gemini wants to use tools
                    if response.candidates[0].content.parts:
                        tool_calls = []
                        tool_results = []
                        
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                fc = part.function_call
                                tool_name = fc.name
                                tool_params = dict(fc.args)
                                
                                print(f"[DEBUG] Gemini calling tool: {tool_name}")
                                print(f"[DEBUG] Parameters: {tool_params}")
                                
                                # Execute tool
                                result = self.tool_registry.execute_tool(tool_name, tool_params)
                                
                                print(f"[DEBUG] Tool result: {result.get('status', 'unknown')}")
                                
                                tool_calls.append({
                                    "id": f"gemini_{len(tool_calls)}",
                                    "tool": tool_name,
                                    "parameters": tool_params
                                })
                                
                                tool_results.append({
                                    "id": f"gemini_{len(tool_results)}",
                                    "tool": tool_name,
                                    "result": result
                                })
                        
                        if tool_calls:
                            # Get text response if any
                            text_response = ""
                            for part in response.candidates[0].content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_response += part.text
                            
                            return {
                                "message": text_response or "I've executed the requested operations.",
                                "tool_calls": tool_calls,
                                "tool_results": tool_results,
                                "code": None
                            }
                    
                    # No tool calls, regular response
                    content = response.text
                    code = self._extract_code(content)
                    return {
                        "message": content if not code else self._remove_code_from_message(content),
                        "code": code,
                        "tool_calls": [],
                        "tool_results": []
                    }
                else:
                    # Tools disabled
                    chat_history = []
                    for msg in history:
                        role = "user" if msg.get("role") == "user" else "model"
                        chat_history.append({"role": role, "parts": [msg.get("content", "")]})
                    
                    chat = self.gemini_model.start_chat(history=chat_history)
                    response = chat.send_message(f"{system_instruction}\n\nUser Request: {prompt}")
                    content = response.text
                    code = self._extract_code(content)
                    return {
                        "message": content if not code else self._remove_code_from_message(content),
                        "code": code,
                        "tool_calls": [],
                        "tool_results": []
                    }
                
            except Exception as e:
                import traceback
                print(f"Gemini API Error: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                return {
                    "message": f"Error: Gemini Generation Failed.\nDetails: {str(e)}",
                    "code": None,
                    "tool_calls": [],
                    "tool_results": []
                }

        # 3. Offline/Fallback Logic
        return {
            "message": self._generate_offline(prompt, board),
            "code": self._generate_offline(prompt, board),
            "tool_calls": [],
            "tool_results": []
        }
    
    def _parse_response_with_tools(self, content: str) -> dict:
        """Parse AI response that might contain tool calls in JSON format"""
        # Try to extract JSON tool calls
        try:
            # Look for JSON block
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                tool_data = json.loads(json_match.group(1))
                
                if "tool_calls" in tool_data:
                    # Execute tools
                    tool_results = []
                    for tool_call in tool_data["tool_calls"]:
                        result = self.tool_registry.execute_tool(
                            tool_call["tool"],
                            tool_call["parameters"]
                        )
                        tool_results.append({
                            "id": tool_call.get("id", "unknown"),
                            "tool": tool_call["tool"],
                            "result": result
                        })
                    
                    return {
                        "message": tool_data.get("message", "Operations executed."),
                        "code": tool_data.get("code"),
                        "tool_calls": tool_data["tool_calls"],
                        "tool_results": tool_results
                    }
        except Exception as e:
            print(f"Failed to parse tool calls: {e}")
        
        # No tool calls found, treat as regular response
        code = self._extract_code(content)
        return {
            "message": content if not code else self._remove_code_from_message(content),
            "code": code,
            "tool_calls": [],
            "tool_results": []
        }
    
    def _extract_code(self, content: str) -> str:
        """Extract code from markdown code blocks"""
        code_match = re.search(r'```(?:cpp|c\+\+|arduino|c)?\s*\n?(.*?)```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        return None
    
    def _clean_params_for_gemini(self, params: dict) -> dict:
        """Remove fields that Gemini doesn't support (like 'default')"""
        if not isinstance(params, dict):
            return params
        
        cleaned = {}
        for key, value in params.items():
            if key == "default":
                continue  # Skip default fields
            elif isinstance(value, dict):
                cleaned[key] = self._clean_params_for_gemini(value)
            elif isinstance(value, list):
                cleaned[key] = [self._clean_params_for_gemini(item) if isinstance(item, dict) else item for item in value]
            else:
                cleaned[key] = value
        
        return cleaned
    
    def _remove_code_from_message(self, content: str) -> str:
        """Remove code blocks from message"""
        return re.sub(r'```(?:cpp|c\+\+|arduino|c)?\s*\n?.*?```', '', content, flags=re.DOTALL).strip()

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
        
        # System Prompt Manager
        self.prompt_manager = get_prompt_manager()

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

            # Get vision-specific system prompt
            system_prompt = self.prompt_manager.get_prompt(
                context="vision",
                board=board,
                enable_tools=False
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

def process_ai_request(prompt: str, board: str, provider: str = "groq", history: list = None, enable_tools: bool = True):
    # 1. Generate Code or Execute Tools
    result = code_agent.generate(prompt, board, provider, history, enable_tools)
    
    # 2. Safety Check on generated code
    if result.get("code"):
        warnings = safety_agent.check_safety(prompt, result["code"])
        if warnings:
            result["message"] = result.get("message", "") + "\n\n" + "\n".join(warnings)
    
    # 3. Add explanation if not present
    if not result.get("message"):
        if result.get("tool_calls"):
            result["message"] = f"I've executed {len(result['tool_calls'])} operation(s) for you."
        elif result.get("code"):
            result["message"] = f"I've generated the code for you using {provider.capitalize()}."
    
    return result

def process_vision_request(image_data: str, prompt: str = "", board: str = "arduino:avr:uno"):
    # 1. Vision Analysis
    result = vision_agent.analyze(image_data, prompt, board)
    
    # 2. Safety Check on generated code
    combined_prompt = prompt + " " + " ".join(result.get("components", []))
    warnings = safety_agent.check_safety(combined_prompt, result.get("code", ""))
    
    if warnings:
        result["explanation"] += "\n\n" + "\n".join(warnings)
    
    return result
