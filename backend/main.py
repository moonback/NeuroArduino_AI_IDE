from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import sys
import os
import subprocess
import tempfile
from typing import Optional, List, Dict

# Import Agents
# Ensure current dir is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents import process_ai_request, process_vision_request

# Import Logger
from logger_config import app_logger, log_request, log_error, log_tool_call, log_ai_request

def get_cli_path():
    # Detect if we are running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # We are running as backend.exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running from source
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    local_cli = os.path.join(base_dir, "tools", "arduino-cli.exe")
    if os.path.exists(local_cli):
        return local_cli
    return "arduino-cli" # Fallback to PATH

def _parse_cors_origins() -> list[str]:
    """Build a safe origin list for local dev + Electron + optional env overrides."""
    default_origins = {
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "app://.",
        "file://",
        "null",  # Electron file:// origin appears as null in some contexts
    }
    raw = os.getenv("CORS_ORIGINS", "")
    if raw.strip():
        for origin in raw.split(","):
            cleaned = origin.strip()
            if cleaned:
                default_origins.add(cleaned)
    return sorted(default_origins)


app = FastAPI(title="Arduino AI IDE Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Sketch(BaseModel):
    code: str
    board: str
    port: Optional[str] = None

class AIQuery(BaseModel):
    prompt: str
    context_code: Optional[str] = None
    board: str = "arduino:avr:uno"
    provider: str = "groq" # Default to groq
    history: Optional[List[dict]] = None
    enable_tools: bool = True  # Enable tool calling by default
    workspace_path: Optional[str] = None  # Workspace path for file operations
    context: Optional[Dict] = None  # Current file context
    include_project_context: bool = False  # Include all project files in context

class VisionQuery(BaseModel):
    image_data: str  # base64 data URL
    prompt: Optional[str] = ""
    board: str = "arduino:avr:uno"

@app.get("/")
def read_root():
    app_logger.info("Health check endpoint called")
    return {"status": "Aireduino Backend Online"}

@app.post("/api/keys")
async def update_api_keys(payload: Dict[str, str]):
    """
    Update API keys in the .env file.
    Accepts: { openrouter_api_key: str, gemini_api_key: str }
    """
    log_request("/api/keys", "POST", {"keys": list(payload.keys())})
    
    allowed_keys = {
        "openrouter_api_key": "OPENROUTER_API_KEY",
        "gemini_api_key": "GEMINI_API_KEY",
    }

    # Determine .env file path (same dir as this script)
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    # Read existing .env content
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            env_lines = f.readlines()

    # Build a dict of current env vars
    env_dict = {}
    for line in env_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _, v = stripped.partition("=")
            env_dict[k.strip()] = v.strip()

    # Apply updates
    updated = []
    for payload_key, env_var in allowed_keys.items():
        if payload_key in payload and payload[payload_key].strip():
            new_value = payload[payload_key].strip()
            env_dict[env_var] = new_value
            updated.append(env_var)

    if not updated:
        app_logger.warning("No valid keys provided in update request")
        raise HTTPException(status_code=400, detail="No valid keys provided.")

    # Write back .env
    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in env_dict.items():
            f.write(f"{k}={v}\n")

    # Reload environment variables immediately (for current process)
    from dotenv import load_dotenv
    load_dotenv(env_path, override=True)

    # Signal agents to reinitialize on next request
    try:
        import importlib
        import agents as agents_module
        importlib.reload(agents_module)
        app_logger.info(f"agents.py reloaded after key update: {updated}")
    except Exception as e:
        app_logger.warning(f"Could not reload agents: {e}")

    app_logger.info(f"API keys updated successfully: {', '.join(updated)}")
    return {
        "status": "success",
        "message": f"Updated and applied: {', '.join(updated)}",
        "updated_keys": updated
    }

@app.get("/ports")
def get_ports():
    log_request("/ports", "GET")
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        data = [{"device": p.device, "description": p.description} for p in ports]
        # Always return a mock port if empty for demo
        if not data:
            data = [{"device": "MOCK_COM3", "description": "Arduino Uno (Simulated)"}]
        app_logger.info(f"Found {len(data)} serial ports")
        return data
    except ImportError as e:
        log_error(e, "get_ports - ImportError")
        return [{"device": "MOCK_COM3", "description": "Arduino Uno (Mock)"}]

@app.post("/compile")
async def compile_sketch(sketch: Sketch):
    log_request("/compile", "POST", {"board": sketch.board, "code_length": len(sketch.code)})
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Arduino CLI requires folder name = sketch name
        sketch_name = "AireduinoSketch"
        sketch_dir = os.path.join(temp_dir, sketch_name)
        os.makedirs(sketch_dir)
        
        sketch_path = os.path.join(sketch_dir, f"{sketch_name}.ino")
        with open(sketch_path, "w") as f:
            f.write(sketch.code)
        
        # Run arduino-cli compile
        # Assumes arduino-cli is in PATH
        # Command: arduino-cli compile --fqbn {board} {sketch_path}
        # Determine CLI path
        cli_path = get_cli_path()
        app_logger.info(f"Using CLI: {cli_path}")

        try:
            cmd = [cli_path, "compile", "--fqbn", sketch.board, sketch_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                app_logger.error(f"Compile Error: {result.stderr}")
                raise HTTPException(status_code=400, detail=f"Compilation Failed:\n{result.stderr}")
            
            app_logger.info("Sketch compiled successfully")
            return {"status": "success", "message": "Sketch compiled successfully!"}
            
        except FileNotFoundError as e:
             # Fallback for dev/demo if CLI not installed
             log_error(e, "compile_sketch - CLI not found")
             return {"status": "warning", "message": "Arduino CLI not found. Mode: Simulation."}


@app.post("/upload")
async def upload_sketch(sketch: Sketch):
    log_request("/upload", "POST", {"board": sketch.board, "port": sketch.port})
    
    if not sketch.port:
        app_logger.warning("Upload attempted without port")
        raise HTTPException(status_code=400, detail="Port required for upload")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Arduino CLI requires folder name = sketch name
        sketch_name = "AireduinoSketch"
        sketch_dir = os.path.join(temp_dir, sketch_name)
        os.makedirs(sketch_dir)
        
        sketch_path = os.path.join(sketch_dir, f"{sketch_name}.ino")
        with open(sketch_path, "w") as f:
            f.write(sketch.code)
            
        try:
            # Determine CLI path
            cli_path = get_cli_path()
            app_logger.info(f"Using CLI: {cli_path}")

            # Command: arduino-cli compile --upload -p {port} --fqbn {board} {sketch_path}
            # We use compile --upload because the temp dir is fresh and has no previous build artifacts
            cmd = [cli_path, "compile", "--upload", "-p", sketch.port, "--fqbn", sketch.board, sketch_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                app_logger.error(f"Upload Error: {result.stderr}")
                raise HTTPException(status_code=400, detail=f"Upload Failed:\n{result.stderr}")
                
            app_logger.info(f"Sketch uploaded successfully to {sketch.port}")
            return {"status": "success", "message": "Sketch uploaded successfully!"}
            
        except FileNotFoundError as e:
             log_error(e, "upload_sketch - CLI not found")
             return {"status": "warning", "message": "Arduino CLI not found. Mode: Simulation."}


@app.get("/libraries/search")
async def search_libraries(query: str):
    cli_path = get_cli_path()
    try:
        cmd = [cli_path, "lib", "search", query, "--format", "json"]
        import json
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout) if (result.stdout and result.stdout.strip()) else {"libraries": []}
        return {"libraries": []}
    except Exception as e:
        print(f"Library Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/libraries/installed")
async def list_installed_libraries():
    cli_path = get_cli_path()
    try:
        cmd = [cli_path, "lib", "list", "--format", "json"]
        import json
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout) if (result.stdout and result.stdout.strip()) else {"libraries": []}
        return {"libraries": []}
    except Exception as e:
        print(f"Library List Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/libraries/install")
async def install_library(payload: Dict[str, str]):
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Library name required")
    
    cli_path = get_cli_path()
    try:
        cmd = [cli_path, "lib", "install", name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Install failed: {result.stderr}")
        return {"status": "success", "message": f"Library {name} installed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/boards/search")
async def search_cores(query: str):
    cli_path = get_cli_path()
    try:
        cmd = [cli_path, "core", "search", query, "--format", "json"]
        import json
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout) if (result.stdout and result.stdout.strip()) else []
        return []
    except Exception as e:
        print(f"Board Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/boards/installed")
async def list_installed_cores():
    cli_path = get_cli_path()
    try:
        cmd = [cli_path, "core", "list", "--format", "json"]
        import json
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout) if (result.stdout and result.stdout.strip()) else []
        return []
    except Exception as e:
        print(f"Board List Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/boards/install")
async def install_core(payload: Dict[str, str]):
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Core name required")
    
    cli_path = get_cli_path()
    try:
        # For ESP32/ESP8266, we might need to add URLs first, but let's try direct install
        cmd = [cli_path, "core", "install", name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
             # Try to update index first if failed
             subprocess.run([cli_path, "core", "update-index"])
             result = subprocess.run(cmd, capture_output=True, text=True)
             
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Install failed: {result.stderr}")
        return {"status": "success", "message": f"Core {name} installed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/boards/listall")
async def list_all_supported_boards():
    cli_path = get_cli_path()
    try:
        cmd = [cli_path, "board", "listall", "--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else "[]"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate")
async def generate_code(query: AIQuery):
    log_request("/ai/generate", "POST", {
        "provider": query.provider,
        "board": query.board,
        "enable_tools": query.enable_tools,
        "prompt_length": len(query.prompt)
    })
    
    # Use workspace path if provided, otherwise use current directory
    workspace = query.workspace_path or os.getcwd()
    
    app_logger.debug(f"Workspace path: {workspace}")
    app_logger.debug(f"Enable tools: {query.enable_tools}")
    
    try:
        # Create agent with workspace (inside try/except to catch init errors)
        from agents import CodeGeneratorAgent
        agent = CodeGeneratorAgent(workspace_root=workspace)
        
        # Build enhanced prompt with context
        enhanced_prompt = query.prompt
        context_parts = []
        
        # Add current file context
        if query.context and query.context.get('current_file'):
            current_file = query.context['current_file']
            # Use full path for file operations
            file_full_path = os.path.join(workspace, current_file['path']) if workspace else current_file['path']
            
            app_logger.debug(f"Current file: {current_file['name']}")
            app_logger.debug(f"File path: {current_file['path']}")
            
            context_parts.append(f"[CURRENT FILE: '{current_file['name']}' at '{current_file['path']}']")
            if current_file.get('content'):
                context_parts.append(f"Current file content:\n```cpp\n{current_file['content']}\n```")
        
        # Add mentioned files context (@mentions)
        if query.context and query.context.get('mentioned_files'):
            mentioned_files = query.context['mentioned_files']
            app_logger.debug(f"Mentioned files: {len(mentioned_files)}")
            
            mentioned_context = []
            for file_info in mentioned_files:
                app_logger.debug(f"Processing mentioned file: {file_info['name']}")
                mentioned_context.append(f"\n--- @Mentioned File: {file_info['name']} ({file_info['path']}) ---")
                if file_info.get('content'):
                    mentioned_context.append(f"```cpp\n{file_info['content']}\n```")
            
            if mentioned_context:
                context_parts.append(f"\n[MENTIONED FILES: {len(mentioned_files)} file(s) mentioned with @]\n" + "\n".join(mentioned_context))
        
        # Add project context if requested
        if query.include_project_context and query.context and query.context.get('project_files'):
            project_files = query.context['project_files']
            workspace_path = query.context.get('workspace_path', workspace)
            
            project_context = []
            for file_info in project_files:
                if file_info['isDirectory']:
                    continue
                
                file_ext = os.path.splitext(file_info['name'])[1].lower()
                if file_ext in ['.ino', '.cpp', '.h', '.c', '.hpp']:
                    try:
                        file_path = os.path.join(workspace_path, file_info['path'].replace('/', os.sep))
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if len(content) < 5000:
                                project_context.append(f"\n--- File: {file_info['path']} ---\n{content}")
                            else:
                                project_context.append(f"\n--- File: {file_info['path']} (truncated) ---\n{content[:2000]}...\n[File truncated]")
                    except Exception as e:
                        app_logger.error(f"Error reading file {file_info['path']}: {e}")
            
            if project_context:
                context_parts.append(f"\n[PROJECT CONTEXT: {len(project_context)} files from workspace]\n" + "\n".join(project_context))
        
        # Combine context with prompt
        if context_parts:
            enhanced_prompt = "\n\n".join(context_parts) + "\n\n[USER REQUEST]\n" + query.prompt
        
        app_logger.debug(f"Enhanced prompt length: {len(enhanced_prompt)}")
        
        result = agent.generate(
            enhanced_prompt, 
            query.board, 
            query.provider, 
            query.history, 
            query.enable_tools
        )
        
        app_logger.info(f"AI generation completed - Response length: {len(result.get('message', ''))}")
        app_logger.debug(f"Tool calls: {len(result.get('tool_calls', []))}")
        
        log_ai_request(query.provider, len(enhanced_prompt), len(result.get('message', '')))
        
        return result
    except Exception as e:
        import traceback
        log_error(e, "generate_code")
        app_logger.error(traceback.format_exc())
        return {
            "message": f"Sorry, I encountered an error during generation: {str(e)}",
            "error": str(e),
            "status": "error",
            "tool_calls": [],
            "tool_results": []
        }

@app.post("/ai/vision")
async def vision_analyze(query: VisionQuery):
    """Analyze an image of Arduino wiring and generate corresponding code."""
    if not query.image_data:
        raise HTTPException(status_code=400, detail="No image data provided")
    result = process_vision_request(query.image_data, query.prompt or "", query.board)
    return result

import serial
import serial.tools.list_ports

class SerialManager:
    def __init__(self):
        self.port: Optional[serial.Serial] = None
        self.read_task = None
        self.clients = set()
        self.path = None

    async def connect(self, path: str, baudrate: int):
        if self.port and self.port.is_open:
            self.disconnect()
        
        try:
            # timeout=0.1 ensures read() doesn't block forever
            self.port = serial.Serial(path, baudrate, timeout=0.1)
            self.path = path
            return True
        except Exception as e:
            print(f"Serial Connection Error: {e}")
            return False

    def disconnect(self):
        if self.port and self.port.is_open:
            self.port.close()
        self.port = None
        self.path = None

    def write(self, data: str):
        if self.port and self.port.is_open:
            self.port.write((data + "\n").encode())
            return True
        return False

    async def stream_to_ws(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.add(websocket)
        try:
            while True:
                if self.port and self.port.is_open:
                    if self.port.in_waiting > 0:
                        # Read line or chunk
                        line = self.port.readline().decode('utf-8', errors='replace')
                        if line:
                            await websocket.send_text(line)
                    else:
                        await asyncio.sleep(0.01)
                else:
                    # If port not open, just wait and check occasionally
                    await asyncio.sleep(0.5)
        except Exception as e:
            print(f"WS Stream Error: {e}")
        finally:
            self.clients.discard(websocket)

serial_manager = SerialManager()

class SerialConfig(BaseModel):
    path: str
    baudrate: int = 9600

@app.post("/serial/connect")
async def serial_connect(config: SerialConfig):
    log_request("/serial/connect", "POST", {"path": config.path, "baudrate": config.baudrate})
    success = await serial_manager.connect(config.path, config.baudrate)
    if not success:
        app_logger.error(f"Could not connect to {config.path}")
        raise HTTPException(status_code=400, detail=f"Could not connect to {config.path}")
    app_logger.info(f"Connected to serial port {config.path} at {config.baudrate} baud")
    return {"status": "success", "message": f"Connected to {config.path}"}

@app.post("/serial/disconnect")
async def serial_disconnect():
    serial_manager.disconnect()
    return {"status": "success", "message": "Disconnected"}

@app.post("/serial/write")
async def serial_write(payload: Dict[str, str]):
    data = payload.get("data", "")
    success = serial_manager.write(data)
    if not success:
        raise HTTPException(status_code=400, detail="Port not open")
    return {"status": "success"}

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await serial_manager.stream_to_ws(websocket)

if __name__ == "__main__":
    import uvicorn
    app_logger.info("Starting Uvicorn server on 127.0.0.1:8001")
    # Use frozen port 8001, loop='asyncio' to avoid compatibility issues in frozen apps
    uvicorn.run(app, host="127.0.0.1", port=8001)
