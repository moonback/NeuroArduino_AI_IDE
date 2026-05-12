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

app = FastAPI(title="Arduino AI IDE Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "app://-", "file://"],
    allow_credentials=False,
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
    return {"status": "Aireduino Backend Online"}

@app.get("/ports")
def get_ports():
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        data = [{"device": p.device, "description": p.description} for p in ports]
        # Always return a mock port if empty for demo
        if not data:
            data = [{"device": "MOCK_COM3", "description": "Arduino Uno (Simulated)"}]
        return data
    except ImportError:
        return [{"device": "MOCK_COM3", "description": "Arduino Uno (Mock)"}]

@app.post("/compile")
async def compile_sketch(sketch: Sketch):
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
        print(f"Using CLI: {cli_path}")

        try:
            cmd = [cli_path, "compile", "--fqbn", sketch.board, sketch_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Compile Error: {result.stderr}")
                raise HTTPException(status_code=400, detail=f"Compilation Failed:\n{result.stderr}")
            
            return {"status": "success", "message": "Sketch compiled successfully!"}
            
        except FileNotFoundError:
             # Fallback for dev/demo if CLI not installed
             return {"status": "warning", "message": "Arduino CLI not found. Mode: Simulation."}


@app.post("/upload")
async def upload_sketch(sketch: Sketch):
    if not sketch.port:
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
            print(f"Using CLI: {cli_path}")

            # Command: arduino-cli compile --upload -p {port} --fqbn {board} {sketch_path}
            # We use compile --upload because the temp dir is fresh and has no previous build artifacts
            cmd = [cli_path, "compile", "--upload", "-p", sketch.port, "--fqbn", sketch.board, sketch_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Upload Error: {result.stderr}")
                raise HTTPException(status_code=400, detail=f"Upload Failed:\n{result.stderr}")
                
            return {"status": "success", "message": "Sketch uploaded successfully!"}
            
        except FileNotFoundError:
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
    # Use workspace path if provided, otherwise use current directory
    workspace = query.workspace_path or os.getcwd()
    
    print(f"[DEBUG] Workspace path: {workspace}")
    print(f"[DEBUG] Context: {query.context}")
    print(f"[DEBUG] Enable tools: {query.enable_tools}")
    
    # Create agent with workspace
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
        
        print(f"[DEBUG] Current file: {current_file['name']}")
        print(f"[DEBUG] File path: {current_file['path']}")
        print(f"[DEBUG] Full path: {file_full_path}")
        
        context_parts.append(f"[CURRENT FILE: '{current_file['name']}' at '{current_file['path']}']")
        if current_file.get('content'):
            context_parts.append(f"Current file content:\n```cpp\n{current_file['content']}\n```")
    
    # Add project context if requested
    if query.include_project_context and query.context and query.context.get('project_files'):
        project_files = query.context['project_files']
        workspace_path = query.context.get('workspace_path', workspace)
        
        # Read content of relevant files (Arduino files, headers, etc.)
        project_context = []
        for file_info in project_files:
            if file_info['isDirectory']:
                continue
            
            # Only include relevant file types
            file_ext = os.path.splitext(file_info['name'])[1].lower()
            if file_ext in ['.ino', '.cpp', '.h', '.c', '.hpp']:
                try:
                    file_path = os.path.join(workspace_path, file_info['path'].replace('/', os.sep))
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Limit file size to avoid token overflow
                        if len(content) < 5000:
                            project_context.append(f"\n--- File: {file_info['path']} ---\n{content}")
                        else:
                            # Include only first 2000 chars for large files
                            project_context.append(f"\n--- File: {file_info['path']} (truncated) ---\n{content[:2000]}...\n[File truncated]")
                except Exception as e:
                    print(f"Error reading file {file_info['path']}: {e}")
        
        if project_context:
            context_parts.append(f"\n[PROJECT CONTEXT: {len(project_context)} files from workspace]\n" + "\n".join(project_context))
    
    # Combine context with prompt
    if context_parts:
        enhanced_prompt = "\n\n".join(context_parts) + "\n\n[USER REQUEST]\n" + query.prompt
    
    print(f"[DEBUG] Enhanced prompt length: {len(enhanced_prompt)}")
    
    result = agent.generate(
        enhanced_prompt, 
        query.board, 
        query.provider, 
        query.history, 
        query.enable_tools
    )
    
    print(f"[DEBUG] Result: {result.get('message', '')[:100]}...")
    print(f"[DEBUG] Tool calls: {len(result.get('tool_calls', []))}")
    
    return result

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
            self.clients.remove(websocket)

serial_manager = SerialManager()

class SerialConfig(BaseModel):
    path: str
    baudrate: int = 9600

@app.post("/serial/connect")
async def serial_connect(config: SerialConfig):
    success = await serial_manager.connect(config.path, config.baudrate)
    if not success:
        raise HTTPException(status_code=400, detail=f"Could not connect to {config.path}")
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
    # Use frozen port 8001, loop='asyncio' to avoid compatibility issues in frozen apps
    uvicorn.run(app, host="127.0.0.1", port=8001)
