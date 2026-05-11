"""
Tool Registry for AI Tool Calling System
Defines all available tools that the AI can use to interact with the filesystem and IDE
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

class ToolRegistry:
    """Registry of all available tools for AI"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.tools = self._register_tools()
        
    def _register_tools(self) -> Dict[str, Dict]:
        """Register all available tools with their schemas"""
        return {
            "create_file": {
                "name": "create_file",
                "description": "Create a new file with specified content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to create (e.g., 'src/blink.ino')"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        },
                        "overwrite": {
                            "type": "boolean",
                            "description": "Whether to overwrite if file exists",
                            "default": False
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            
            "modify_file": {
                "name": "modify_file",
                "description": "Modify an existing file (replace, insert, or append content)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to modify"
                        },
                        "operation": {
                            "type": "string",
                            "enum": ["replace", "insert", "append"],
                            "description": "Type of modification: replace (find and replace), insert (at line), append (at end)"
                        },
                        "search": {
                            "type": "string",
                            "description": "Text to search for (required for 'replace' operation)"
                        },
                        "content": {
                            "type": "string",
                            "description": "New content to insert/append/replace with"
                        },
                        "line": {
                            "type": "integer",
                            "description": "Line number for 'insert' operation (1-indexed)"
                        }
                    },
                    "required": ["path", "operation", "content"]
                }
            },
            
            "read_file": {
                "name": "read_file",
                "description": "Read the content of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to read"
                        }
                    },
                    "required": ["path"]
                }
            },
            
            "delete_file": {
                "name": "delete_file",
                "description": "Delete a file (requires user confirmation)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to delete"
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Must be true to confirm deletion"
                        }
                    },
                    "required": ["path", "confirm"]
                }
            },
            
            "list_files": {
                "name": "list_files",
                "description": "List files in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to directory (default: current directory)",
                            "default": "."
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to list files recursively",
                            "default": False
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern to filter files (e.g., '*.ino')"
                        }
                    }
                }
            },
            
            "create_directory": {
                "name": "create_directory",
                "description": "Create a new directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the directory to create"
                        }
                    },
                    "required": ["path"]
                }
            },
            
            "rename_file": {
                "name": "rename_file",
                "description": "Rename or move a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "old_path": {
                            "type": "string",
                            "description": "Current path of the file"
                        },
                        "new_path": {
                            "type": "string",
                            "description": "New path for the file"
                        }
                    },
                    "required": ["old_path", "new_path"]
                }
            }
        }
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions in format suitable for AI models"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            for tool in self.tools.values()
        ]
    
    def get_tool_definitions_text(self) -> str:
        """Get tool definitions as formatted text for models that don't support function calling"""
        text = "You have access to the following tools:\n\n"
        for tool in self.tools.values():
            text += f"## {tool['name']}\n"
            text += f"{tool['description']}\n\n"
            text += "Parameters:\n"
            text += json.dumps(tool['parameters'], indent=2)
            text += "\n\n"
        
        text += """
To use a tool, respond with a JSON object in this format:
{
  "message": "Your explanation to the user",
  "tool_calls": [
    {
      "id": "call_1",
      "tool": "tool_name",
      "parameters": {
        "param1": "value1"
      }
    }
  ]
}
"""
        return text
    
    def validate_path(self, path: str) -> tuple[bool, str]:
        """Validate that a path is safe and within workspace"""
        # Normalize path
        full_path = os.path.normpath(os.path.join(self.workspace_root, path))
        
        # Check if path is within workspace
        if not full_path.startswith(os.path.normpath(self.workspace_root)):
            return False, "Path is outside workspace"
        
        # Check for forbidden paths
        forbidden = [
            "/etc", "/sys", "/proc", "/dev",
            "C:\\Windows", "C:\\Program Files",
            "/System", "/Library"
        ]
        
        for forbidden_path in forbidden:
            if full_path.startswith(forbidden_path):
                return False, f"Access to {forbidden_path} is forbidden"
        
        # Check for path traversal
        if ".." in path:
            return False, "Path traversal is not allowed"
        
        return True, full_path
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        if tool_name not in self.tools:
            return {
                "status": "error",
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            # Route to appropriate handler
            if tool_name == "create_file":
                return self._create_file(**parameters)
            elif tool_name == "modify_file":
                return self._modify_file(**parameters)
            elif tool_name == "read_file":
                return self._read_file(**parameters)
            elif tool_name == "delete_file":
                return self._delete_file(**parameters)
            elif tool_name == "list_files":
                return self._list_files(**parameters)
            elif tool_name == "create_directory":
                return self._create_directory(**parameters)
            elif tool_name == "rename_file":
                return self._rename_file(**parameters)
            else:
                return {
                    "status": "error",
                    "error": f"Tool {tool_name} not implemented"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _create_file(self, path: str, content: str, overwrite: bool = False) -> Dict:
        """Create a new file"""
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        # Check if file exists
        if os.path.exists(full_path) and not overwrite:
            return {
                "status": "error",
                "error": f"File already exists: {path}. Use overwrite=true to replace."
            }
        
        # Create parent directories if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"File created: {path}",
            "path": path,
            "size": len(content)
        }
    
    def _modify_file(self, path: str, operation: str, content: str, 
                     search: Optional[str] = None, line: Optional[int] = None) -> Dict:
        """Modify an existing file"""
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        if not os.path.exists(full_path):
            return {"status": "error", "error": f"File not found: {path}"}
        
        # Read current content
        with open(full_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Perform operation
        if operation == "replace":
            if not search:
                return {"status": "error", "error": "search parameter required for replace operation"}
            
            if search not in current_content:
                return {"status": "error", "error": f"Search text not found: {search}"}
            
            new_content = current_content.replace(search, content)
            
        elif operation == "insert":
            if line is None:
                return {"status": "error", "error": "line parameter required for insert operation"}
            
            lines = current_content.split('\n')
            if line < 1 or line > len(lines) + 1:
                return {"status": "error", "error": f"Invalid line number: {line}"}
            
            lines.insert(line - 1, content)
            new_content = '\n'.join(lines)
            
        elif operation == "append":
            new_content = current_content + content
            
        else:
            return {"status": "error", "error": f"Unknown operation: {operation}"}
        
        # Write modified content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return {
            "status": "success",
            "message": f"File modified: {path}",
            "operation": operation,
            "path": path
        }
    
    def _read_file(self, path: str) -> Dict:
        """Read file content"""
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        if not os.path.exists(full_path):
            return {"status": "error", "error": f"File not found: {path}"}
        
        # Check file size (limit to 1MB)
        file_size = os.path.getsize(full_path)
        if file_size > 1024 * 1024:
            return {"status": "error", "error": "File too large (max 1MB)"}
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "status": "success",
            "path": path,
            "content": content,
            "size": file_size
        }
    
    def _delete_file(self, path: str, confirm: bool = False) -> Dict:
        """Delete a file"""
        if not confirm:
            return {"status": "error", "error": "Deletion requires confirm=true"}
        
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        if not os.path.exists(full_path):
            return {"status": "error", "error": f"File not found: {path}"}
        
        os.remove(full_path)
        
        return {
            "status": "success",
            "message": f"File deleted: {path}",
            "path": path
        }
    
    def _list_files(self, path: str = ".", recursive: bool = False, 
                    pattern: Optional[str] = None) -> Dict:
        """List files in directory"""
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        if not os.path.exists(full_path):
            return {"status": "error", "error": f"Directory not found: {path}"}
        
        if not os.path.isdir(full_path):
            return {"status": "error", "error": f"Not a directory: {path}"}
        
        files = []
        
        if recursive:
            for root, dirs, filenames in os.walk(full_path):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(root, filename), self.workspace_root)
                    if pattern is None or Path(filename).match(pattern):
                        files.append(rel_path)
        else:
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if os.path.isfile(item_path):
                    if pattern is None or Path(item).match(pattern):
                        rel_path = os.path.relpath(item_path, self.workspace_root)
                        files.append(rel_path)
        
        return {
            "status": "success",
            "path": path,
            "files": files,
            "count": len(files)
        }
    
    def _create_directory(self, path: str) -> Dict:
        """Create a directory"""
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        if os.path.exists(full_path):
            return {"status": "error", "error": f"Directory already exists: {path}"}
        
        os.makedirs(full_path, exist_ok=True)
        
        return {
            "status": "success",
            "message": f"Directory created: {path}",
            "path": path
        }
    
    def _rename_file(self, old_path: str, new_path: str) -> Dict:
        """Rename or move a file"""
        is_valid_old, full_old_path = self.validate_path(old_path)
        if not is_valid_old:
            return {"status": "error", "error": full_old_path}
        
        is_valid_new, full_new_path = self.validate_path(new_path)
        if not is_valid_new:
            return {"status": "error", "error": full_new_path}
        
        if not os.path.exists(full_old_path):
            return {"status": "error", "error": f"File not found: {old_path}"}
        
        if os.path.exists(full_new_path):
            return {"status": "error", "error": f"Destination already exists: {new_path}"}
        
        # Create parent directories if needed
        os.makedirs(os.path.dirname(full_new_path), exist_ok=True)
        
        os.rename(full_old_path, full_new_path)
        
        return {
            "status": "success",
            "message": f"File renamed: {old_path} → {new_path}",
            "old_path": old_path,
            "new_path": new_path
        }
