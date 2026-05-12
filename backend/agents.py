import os
import re
import json
from openai import OpenAI  # For OpenRouter (OpenAI-compatible)
from google import genai
from google.genai import types as genai_types
import sys
from dotenv import load_dotenv
from tools_registry import ToolRegistry
from system_prompts import get_prompt_manager

# Import Logger
from logger_config import app_logger, log_error, log_tool_call, log_ai_request

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
    app_logger.info(f"Loading .env from: {env_path}")
    load_dotenv(env_path, override=True)
else:
    app_logger.warning("No .env file found!")

class CodeGeneratorAgent:
    def __init__(self, workspace_root: str = None):
        # OpenRouter Setup (replaces Groq)
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if self.openrouter_api_key:
            # OpenRouter uses OpenAI-compatible API
            from openai import OpenAI
            self.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key,
            )
            # Use a free model from OpenRouter
            self.openrouter_model = "openai/gpt-oss-120b:free"
        else:
            self.openrouter_client = None

        # Gemini Setup (new google.genai SDK)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            self.gemini_model_name = "gemini-2.5-flash"
        else:
            self.gemini_client = None
            self.gemini_model_name = None
        
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

        app_logger.info(f"Generating code with provider: {provider}, board: {board}, tools: {enable_tools}")

        # 1. OpenRouter Provider (replaces Groq, uses OpenAI-compatible API)
        if provider == "openrouter" and self.openrouter_client:
            try:
                messages = [{"role": "system", "content": system_instruction}]
                
                # Add history
                for msg in history:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
                
                # Add current prompt
                messages.append({"role": "user", "content": prompt})

                log_ai_request(provider, len(prompt))

                # OpenRouter supports function calling (OpenAI-compatible)
                if enable_tools:
                    try:
                        app_logger.debug(f"Calling OpenRouter with tools enabled")
                        app_logger.debug(f"Number of tools available: {len(self.tool_registry.get_tool_definitions())}")
                        
                        completion = self.openrouter_client.chat.completions.create(
                            messages=messages,
                            model=self.openrouter_model,
                            tools=self.tool_registry.get_tool_definitions(),
                            tool_choice="auto"
                        )
                        
                        response_message = completion.choices[0].message
                        
                        # CRITICAL FIX: Handle None content from OpenRouter
                        content = response_message.content or ""
                        tool_calls_present = hasattr(response_message, 'tool_calls') and response_message.tool_calls is not None
                        
                        app_logger.debug(f"Content length: {len(content) if content else 0}")
                        app_logger.debug(f"Response has tool_calls: {tool_calls_present}")
                        
                        # Check if AI wants to use tools
                        if tool_calls_present and response_message.tool_calls:
                            app_logger.info(f"AI wants to use {len(response_message.tool_calls)} tool(s)")
                            tool_calls = []
                            tool_results = []
                            
                            for tool_call in response_message.tool_calls:
                                tool_name = tool_call.function.name
                                tool_params = json.loads(tool_call.function.arguments)
                                
                                app_logger.info(f"Executing tool: {tool_name}")
                                app_logger.debug(f"Parameters: {tool_params}")
                                
                                # Execute tool
                                result = self.tool_registry.execute_tool(tool_name, tool_params)
                                
                                app_logger.info(f"Tool result: {result.get('status', 'unknown')}")
                                log_tool_call(tool_name, tool_params, str(result))
                                
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
                            
                            # CRITICAL FIX: Use the content variable we already extracted
                            return {
                                "message": content or "I've executed the requested operations.",
                                "tool_calls": tool_calls,
                                "tool_results": tool_results,
                                "code": None
                            }
                        else:
                            print(f"[DEBUG] No tool calls, returning regular response")
                            # No tool calls, just return the message
                            # CRITICAL FIX: content already extracted above, handle None case
                            if not content:
                                print(f"[WARNING] OpenRouter returned no content and no tool calls")
                                return {
                                    "message": "I received your request but couldn't generate a response. Please try rephrasing.",
                                    "code": None,
                                    "tool_calls": [],
                                    "tool_results": []
                                }
                            
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
                        completion = self.openrouter_client.chat.completions.create(
                            messages=messages,
                            model=self.openrouter_model,
                        )
                        # CRITICAL FIX: Handle None content
                        content = completion.choices[0].message.content or ""
                        
                        if not content:
                            print(f"[WARNING] OpenRouter returned empty content in fallback")
                            return {
                                "message": "I encountered an error processing your request. Please try again.",
                                "code": None,
                                "tool_calls": [],
                                "tool_results": []
                            }
                        
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
                    completion = self.openrouter_client.chat.completions.create(
                        messages=messages,
                        model=self.openrouter_model,
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
                print(f"OpenRouter API Error: {e}")
                return {
                    "message": f"Error: OpenRouter Generation Failed.\nDetails: {str(e)}",
                    "code": None,
                    "tool_calls": [],
                    "tool_results": []
                }

        # 2. Gemini Provider (using new google.genai SDK)
        elif provider == "gemini" and self.gemini_client:
            try:
                if enable_tools:
                    # Convert tool definitions to Gemini FunctionDeclaration format
                    gemini_functions = []
                    for tool_def in self.tool_registry.get_tool_definitions():
                        func = tool_def["function"]
                        clean_params = self._clean_params_for_gemini(func["parameters"])
                        gemini_functions.append(
                            genai_types.FunctionDeclaration(
                                name=func["name"],
                                description=func["description"],
                                parameters=clean_params
                            )
                        )
                    
                    gemini_tool = genai_types.Tool(function_declarations=gemini_functions)
                    config = genai_types.GenerateContentConfig(
                        tools=[gemini_tool],
                        system_instruction=system_instruction
                    )
                    
                    print(f"[DEBUG] Calling Gemini with {len(gemini_functions)} tools")
                    
                    # Build content list from history + current prompt
                    contents = []
                    for msg in history:
                        role = "user" if msg.get("role") == "user" else "model"
                        contents.append(genai_types.Content(
                            role=role,
                            parts=[genai_types.Part.from_text(text=msg.get("content", ""))]
                        ))
                    contents.append(genai_types.Content(
                        role="user",
                        parts=[genai_types.Part.from_text(text=prompt)]
                    ))
                    
                    response = self.gemini_client.models.generate_content(
                        model=self.gemini_model_name,
                        contents=contents,
                        config=config
                    )
                    
                    # Check for tool calls in response
                    tool_calls = []
                    tool_results = []
                    
                    if response.candidates and response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                fc = part.function_call
                                tool_name = fc.name
                                tool_params = dict(fc.args)
                                
                                print(f"[DEBUG] Gemini calling tool: {tool_name}")
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
                        text_response = ""
                        if response.candidates and response.candidates[0].content.parts:
                            for part in response.candidates[0].content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_response += part.text
                        return {
                            "message": text_response or "I've executed the requested operations.",
                            "tool_calls": tool_calls,
                            "tool_results": tool_results,
                            "code": None
                        }
                    
                    # No tool calls — regular text response
                    content = response.text
                    code = self._extract_code(content)
                    return {
                        "message": content if not code else self._remove_code_from_message(content),
                        "code": code,
                        "tool_calls": [],
                        "tool_results": []
                    }
                
                else:
                    # Tools disabled — simple generation
                    contents = []
                    for msg in history:
                        role = "user" if msg.get("role") == "user" else "model"
                        contents.append(genai_types.Content(
                            role=role,
                            parts=[genai_types.Part.from_text(text=msg.get("content", ""))]
                        ))
                    contents.append(genai_types.Content(
                        role="user",
                        parts=[genai_types.Part.from_text(text=prompt)]
                    ))
                    config = genai_types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                    response = self.gemini_client.models.generate_content(
                        model=self.gemini_model_name,
                        contents=contents,
                        config=config
                    )
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
            if not self.openrouter_api_key and not self.gemini_api_key:
                return "// Error: No AI API keys found (OPENROUTER_API_KEY or GEMINI_API_KEY).\n// Please check your .env file."
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
            # Use new google.genai SDK
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            self.gemini_model_name = "gemini-1.5-flash"
        else:
            self.gemini_client = None
            self.gemini_model_name = None
        
        # System Prompt Manager
        self.prompt_manager = get_prompt_manager()

    def analyze(self, image_data: str, prompt: str = "", board: str = "arduino:avr:uno") -> dict:
        """
        Analyze a base64-encoded image of an Arduino wiring setup.
        Returns dict with keys: code, explanation, components
        """
        if not self.gemini_client:
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

            # Build multimodal content using new SDK types
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model_name,
                contents=[
                    genai_types.Content(parts=[
                        genai_types.Part.from_text(text=system_prompt),
                        genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        genai_types.Part.from_text(text=user_msg)
                    ])
                ]
            )

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


# Main Orchestrator - wrapped in try/except to prevent import-time crashes
try:
    code_agent = CodeGeneratorAgent()
except Exception as e:
    print(f"[WARNING] Failed to initialize CodeGeneratorAgent at import: {e}")
    code_agent = None

try:
    safety_agent = HardwareRulesAgent()
except Exception as e:
    print(f"[WARNING] Failed to initialize HardwareRulesAgent at import: {e}")
    safety_agent = None

try:
    vision_agent = VisionAgent()
except Exception as e:
    print(f"[WARNING] Failed to initialize VisionAgent at import: {e}")
    vision_agent = None

def process_ai_request(prompt: str, board: str, provider: str = "groq", history: list = None, enable_tools: bool = True):
    if code_agent is None:
        return {
            "message": "AI agent failed to initialize. Check your API keys in .env",
            "code": None, "tool_calls": [], "tool_results": []
        }
    # 1. Generate Code or Execute Tools
    result = code_agent.generate(prompt, board, provider, history, enable_tools)
    
    # 2. Safety Check on generated code
    if result.get("code") and safety_agent:
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
