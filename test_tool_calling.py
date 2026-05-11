#!/usr/bin/env python3
"""
Quick Test Script for AI Tool Calling System
Run this to test the tool calling functionality without starting the full server
"""

import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from tools_registry import ToolRegistry
from agents import CodeGeneratorAgent

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_result(result):
    """Print a formatted result"""
    print(json.dumps(result, indent=2, ensure_ascii=False))

def test_tool_registry():
    """Test the ToolRegistry directly"""
    print_header("Testing Tool Registry")
    
    # Create a test workspace
    import tempfile
    workspace = tempfile.mkdtemp()
    print(f"📁 Test Workspace: {workspace}\n")
    
    registry = ToolRegistry(workspace_root=workspace)
    
    # Test 1: Create File
    print("Test 1: Create File")
    result = registry.execute_tool("create_file", {
        "path": "blink.ino",
        "content": "void setup() {\n  pinMode(13, OUTPUT);\n}\n\nvoid loop() {\n  digitalWrite(13, HIGH);\n  delay(1000);\n  digitalWrite(13, LOW);\n  delay(1000);\n}"
    })
    print_result(result)
    
    # Test 2: Read File
    print("\nTest 2: Read File")
    result = registry.execute_tool("read_file", {
        "path": "blink.ino"
    })
    print(f"Status: {result['status']}")
    print(f"Content Length: {len(result.get('content', ''))}")
    
    # Test 3: Modify File
    print("\nTest 3: Modify File (Replace)")
    result = registry.execute_tool("modify_file", {
        "path": "blink.ino",
        "operation": "replace",
        "search": "delay(1000);",
        "content": "delay(500);"
    })
    print_result(result)
    
    # Test 4: List Files
    print("\nTest 4: List Files")
    result = registry.execute_tool("list_files", {
        "path": "."
    })
    print_result(result)
    
    # Test 5: Create Directory
    print("\nTest 5: Create Directory")
    result = registry.execute_tool("create_directory", {
        "path": "src"
    })
    print_result(result)
    
    # Test 6: Create File in Subdirectory
    print("\nTest 6: Create File in Subdirectory")
    result = registry.execute_tool("create_file", {
        "path": "src/main.ino",
        "content": "// Main file"
    })
    print_result(result)
    
    # Test 7: Rename File
    print("\nTest 7: Rename File")
    result = registry.execute_tool("rename_file", {
        "old_path": "blink.ino",
        "new_path": "blink_modified.ino"
    })
    print_result(result)
    
    # Test 8: Delete File
    print("\nTest 8: Delete File")
    result = registry.execute_tool("delete_file", {
        "path": "blink_modified.ino",
        "confirm": True
    })
    print_result(result)
    
    print(f"\n✅ All tests completed!")
    print(f"📁 Test files are in: {workspace}")
    
    # Cleanup option
    import shutil
    cleanup = input("\n🗑️  Delete test workspace? (y/n): ")
    if cleanup.lower() == 'y':
        shutil.rmtree(workspace)
        print("✅ Workspace deleted")
    else:
        print(f"📁 Workspace preserved at: {workspace}")

def test_ai_agent():
    """Test the AI Agent with tool calling"""
    print_header("Testing AI Agent with Tool Calling")
    
    # Check for API keys
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not groq_key and not gemini_key:
        print("⚠️  No API keys found!")
        print("Please set GROQ_API_KEY or GEMINI_API_KEY in backend/.env")
        return
    
    # Create agent
    import tempfile
    workspace = tempfile.mkdtemp()
    agent = CodeGeneratorAgent(workspace_root=workspace)
    
    # Test prompt
    prompt = "Crée un fichier test.ino avec un simple blink LED sur la pin 13"
    provider = "groq" if groq_key else "gemini"
    
    print(f"🤖 Provider: {provider}")
    print(f"💬 Prompt: {prompt}\n")
    
    try:
        result = agent.generate(
            prompt=prompt,
            board="arduino:avr:uno",
            provider=provider,
            enable_tools=True
        )
        
        print("📤 AI Response:")
        print_result(result)
        
        # Check if file was created
        test_file = os.path.join(workspace, "test.ino")
        if os.path.exists(test_file):
            print(f"\n✅ File created successfully!")
            print(f"📄 Location: {test_file}")
            with open(test_file, 'r') as f:
                print(f"\n📝 Content:\n{f.read()}")
        else:
            print("\n⚠️  File was not created")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Cleanup
    import shutil
    shutil.rmtree(workspace)
    print(f"\n🗑️  Workspace cleaned up")

def interactive_test():
    """Interactive testing mode"""
    print_header("Interactive Tool Calling Test")
    
    import tempfile
    workspace = tempfile.mkdtemp()
    registry = ToolRegistry(workspace_root=workspace)
    
    print(f"📁 Workspace: {workspace}")
    print("\nAvailable tools:")
    for tool_name in registry.tools.keys():
        print(f"  - {tool_name}")
    
    print("\nType 'help <tool>' for tool details")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            command = input("🔧 > ").strip()
            
            if not command:
                continue
            
            if command == "exit":
                break
            
            if command.startswith("help"):
                parts = command.split()
                if len(parts) > 1:
                    tool_name = parts[1]
                    if tool_name in registry.tools:
                        tool = registry.tools[tool_name]
                        print(f"\n{tool['name']}")
                        print(f"Description: {tool['description']}")
                        print(f"Parameters: {json.dumps(tool['parameters'], indent=2)}\n")
                    else:
                        print(f"❌ Unknown tool: {tool_name}")
                else:
                    print("Usage: help <tool_name>")
                continue
            
            # Try to parse as JSON
            try:
                data = json.loads(command)
                tool_name = data.get("tool")
                parameters = data.get("parameters", {})
                
                if tool_name:
                    result = registry.execute_tool(tool_name, parameters)
                    print_result(result)
                else:
                    print("❌ Missing 'tool' field")
            except json.JSONDecodeError:
                print("❌ Invalid JSON. Format: {\"tool\": \"tool_name\", \"parameters\": {...}}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Bye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Cleanup
    import shutil
    cleanup = input("\n🗑️  Delete test workspace? (y/n): ")
    if cleanup.lower() == 'y':
        shutil.rmtree(workspace)
        print("✅ Workspace deleted")
    else:
        print(f"📁 Workspace preserved at: {workspace}")

def main():
    """Main menu"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🛠️  AI Tool Calling System - Test Suite             ║
║                                                          ║
║     NeuroArduino AI IDE                                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("Select a test mode:\n")
    print("1. Test Tool Registry (Direct)")
    print("2. Test AI Agent (with API)")
    print("3. Interactive Mode")
    print("4. Exit\n")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        test_tool_registry()
    elif choice == "2":
        test_ai_agent()
    elif choice == "3":
        interactive_test()
    elif choice == "4":
        print("\n👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
