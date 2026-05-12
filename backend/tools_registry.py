"""
Tool Registry for AI Tool Calling System
Defines all available tools that the AI can use to interact with the filesystem and IDE
"""

import os
import json
import time
import shutil
import subprocess
import difflib
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
from code_analyzer import CodeAnalyzer

class ToolRegistry:
    """Registry of all available tools for AI"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.tools = self._register_tools()
        # Create backup directory if it doesn't exist
        self.backup_dir = os.path.join(self.workspace_root, '.backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _generate_diff(self, original: str, modified: str, filename: str = "file") -> str:
        """Generate a unified diff between original and modified content"""
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"{filename} (original)",
            tofile=f"{filename} (modified)",
            lineterm=''
        )
        
        return ''.join(diff)
    
    def _create_backup(self, full_path: str) -> Optional[str]:
        """Create a timestamped backup of a file"""
        try:
            timestamp = int(time.time())
            filename = os.path.basename(full_path)
            backup_filename = f"{filename}.backup.{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(full_path, backup_path)
            print(f"[BACKUP] Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"[WARNING] Failed to create backup: {e}")
            return None
    
    def _validate_arduino_syntax(self, full_path: str, board: str = "arduino:avr:uno") -> Dict[str, Any]:
        """
        Validate Arduino/C++ syntax using arduino-cli compile
        Returns: {"valid": bool, "errors": str, "warnings": str}
        """
        try:
            # Check if arduino-cli is available
            result = subprocess.run(
                ['arduino-cli', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print("[WARNING] arduino-cli not found, skipping syntax validation")
                return {"valid": True, "errors": "", "warnings": "", "skipped": True}
            
            # Get the sketch directory (parent of .ino file)
            sketch_dir = os.path.dirname(full_path)
            
            # Compile the sketch
            print(f"[VALIDATION] Compiling with arduino-cli for board {board}...")
            result = subprocess.run(
                ['arduino-cli', 'compile', '--fqbn', board, sketch_dir],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("[VALIDATION] ✓ Compilation successful")
                return {
                    "valid": True,
                    "errors": "",
                    "warnings": result.stderr,
                    "skipped": False
                }
            else:
                print(f"[VALIDATION] ✗ Compilation failed")
                return {
                    "valid": False,
                    "errors": result.stderr,
                    "warnings": "",
                    "skipped": False
                }
        
        except subprocess.TimeoutExpired:
            print("[WARNING] Compilation timeout, skipping validation")
            return {"valid": True, "errors": "", "warnings": "", "skipped": True, "timeout": True}
        except FileNotFoundError:
            print("[WARNING] arduino-cli not found, skipping syntax validation")
            return {"valid": True, "errors": "", "warnings": "", "skipped": True}
        except Exception as e:
            print(f"[WARNING] Validation error: {e}")
            return {"valid": True, "errors": "", "warnings": "", "skipped": True, "error": str(e)}
        
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
            
            "smart_modify_file": {
                "name": "smart_modify_file",
                "description": "Intelligently modify specific parts of a file with multiple operations in one call. Safer than modify_file for complex changes. Supports dry-run preview, automatic backup, and optional compilation validation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to modify"
                        },
                        "modifications": {
                            "type": "array",
                            "description": "List of modifications to apply in order",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["replace", "insert_after", "insert_before", "delete_lines", "replace_lines"],
                                        "description": "Type of modification"
                                    },
                                    "search": {
                                        "type": "string",
                                        "description": "Text to search for (for replace, insert_after, insert_before)"
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "Content to insert or replace with"
                                    },
                                    "start_line": {
                                        "type": "integer",
                                        "description": "Starting line number (for delete_lines, replace_lines)"
                                    },
                                    "end_line": {
                                        "type": "integer",
                                        "description": "Ending line number (for delete_lines, replace_lines)"
                                    },
                                    "count": {
                                        "type": "integer",
                                        "description": "Number of occurrences to replace (default: all)",
                                        "default": -1
                                    }
                                },
                                "required": ["type"]
                            }
                        },
                        "description": {
                            "type": "string",
                            "description": "Brief description of what changes are being made"
                        },
                        "dry_run": {
                            "type": "boolean",
                            "description": "If true, preview changes without applying them (returns diff)",
                            "default": False
                        },
                        "validate_syntax": {
                            "type": "boolean",
                            "description": "If true, validate Arduino/C++ syntax after modification (auto-rollback on error)",
                            "default": False
                        },
                        "board": {
                            "type": "string",
                            "description": "Arduino board FQBN for syntax validation (e.g., 'arduino:avr:uno')",
                            "default": "arduino:avr:uno"
                        },
                        "create_backup": {
                            "type": "boolean",
                            "description": "If true, create a timestamped backup before modification",
                            "default": True
                        }
                    },
                    "required": ["path", "modifications"]
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
            },
            
            "analyze_code": {
                "name": "analyze_code",
                "description": "Analyze Arduino code for errors, warnings, suggestions, and optimizations. Provides intelligent code analysis with pattern detection for common issues, hardware safety concerns, and performance improvements.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to analyze (defaults to current file if not specified)",
                            "default": ""
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["full", "quick", "security", "performance"],
                            "description": "Type of analysis: 'full' (all checks), 'quick' (errors and warnings only), 'security' (hardware safety), 'performance' (memory and optimization)",
                            "default": "full"
                        },
                        "board": {
                            "type": "string",
                            "description": "Target Arduino board type (e.g., 'arduino:avr:uno', 'esp32:esp32:esp32')",
                            "default": "arduino:avr:uno"
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "fr"],
                            "description": "Language for analysis messages ('en' for English, 'fr' for French)",
                            "default": "en"
                        }
                    }
                }
            },
            
            "restore_backup": {
                "name": "restore_backup",
                "description": "Restore a file from a timestamped backup. Use this to undo modifications if something went wrong.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to restore"
                        },
                        "backup_path": {
                            "type": "string",
                            "description": "Optional: specific backup file path. If not provided, restores from most recent backup."
                        },
                        "list_backups": {
                            "type": "boolean",
                            "description": "If true, list available backups instead of restoring",
                            "default": False
                        }
                    },
                    "required": ["path"]
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
            elif tool_name == "smart_modify_file":
                return self._smart_modify_file(**parameters)
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
            elif tool_name == "analyze_code":
                return self._analyze_code(**parameters)
            elif tool_name == "restore_backup":
                return self._restore_backup(**parameters)
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
    
    def _smart_modify_file(self, path: str, modifications: List[Dict], description: str = "", 
                           dry_run: bool = False, validate_syntax: bool = False, 
                           board: str = "arduino:avr:uno", create_backup: bool = True) -> Dict:
        """
        Intelligently modify a file with multiple operations
        
        Features:
        - Dry-run mode: Preview changes without applying
        - Automatic backup: Create timestamped backup before modification
        - Syntax validation: Validate Arduino/C++ syntax after modification with auto-rollback
        - Detailed logging: Track every operation
        
        Args:
            path: Relative path to the file to modify
            modifications: List of modification operations
            description: Brief description of changes
            dry_run: If True, preview changes without applying (returns diff)
            validate_syntax: If True, validate syntax after modification (auto-rollback on error)
            board: Arduino board FQBN for syntax validation
            create_backup: If True, create timestamped backup before modification
        
        Returns:
            Dictionary with status, changes, and optional diff/validation results
        """
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        if not os.path.exists(full_path):
            return {"status": "error", "error": f"File not found: {path}"}
        
        # Read current content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"status": "error", "error": f"Failed to read file: {str(e)}"}
        
        original_content = content
        lines = content.split('\n')
        changes_made = []
        
        # Apply modifications in order
        for idx, mod in enumerate(modifications):
            mod_type = mod.get('type')
            
            try:
                if mod_type == 'replace':
                    search = mod.get('search')
                    replace_with = mod.get('content', '')
                    count = mod.get('count', -1)
                    
                    if not search:
                        return {"status": "error", "error": f"Modification {idx}: 'search' required for replace"}
                    
                    print(f"[DEBUG] Searching for: {search[:100]}...")
                    print(f"[DEBUG] Search found in content: {search in content}")
                    
                    if search not in content:
                        print(f"[WARNING] Search pattern not found in file")
                        print(f"[DEBUG] File content preview: {content[:200]}...")
                        return {
                            "status": "error", 
                            "error": f"Modification {idx}: Search text not found in file. The file may have been modified already or the search pattern is incorrect.",
                            "search_pattern": search[:100],
                            "file_preview": content[:200]
                        }
                    
                    if count == -1:
                        content = content.replace(search, replace_with)
                        occurrences = original_content.count(search)
                    else:
                        parts = content.split(search, count)
                        content = replace_with.join(parts)
                        occurrences = count
                    
                    print(f"[DEBUG] Replaced {occurrences} occurrence(s)")
                    changes_made.append(f"Replaced {occurrences} occurrence(s) of text")
                    lines = content.split('\n')
                
                elif mod_type == 'insert_after':
                    search = mod.get('search')
                    insert_content = mod.get('content', '')
                    
                    if not search:
                        return {"status": "error", "error": f"Modification {idx}: 'search' required for insert_after"}
                    
                    print(f"[DEBUG] insert_after - Searching for: {search[:100]}...")
                    print(f"[DEBUG] Search found: {search in content}")
                    
                    if search not in content:
                        print(f"[WARNING] insert_after: Search pattern not found")
                        return {
                            "status": "error", 
                            "error": f"Modification {idx}: Search text not found for insert_after operation.",
                            "search_pattern": search[:100]
                        }
                    
                    found = False
                    for i, line in enumerate(lines):
                        if search in line:
                            lines.insert(i + 1, insert_content)
                            changes_made.append(f"Inserted content after line {i + 1}")
                            found = True
                            print(f"[DEBUG] Inserted after line {i + 1}")
                            break
                    
                    if not found:
                        return {"status": "error", "error": f"Modification {idx}: Could not find line with search text"}
                    
                    content = '\n'.join(lines)
                
                elif mod_type == 'insert_before':
                    search = mod.get('search')
                    insert_content = mod.get('content', '')
                    
                    if not search:
                        return {"status": "error", "error": f"Modification {idx}: 'search' required for insert_before"}
                    
                    print(f"[DEBUG] insert_before - Searching for: {search[:100]}...")
                    print(f"[DEBUG] Search found: {search in content}")
                    
                    if search not in content:
                        print(f"[WARNING] insert_before: Search pattern not found")
                        return {
                            "status": "error", 
                            "error": f"Modification {idx}: Search text not found for insert_before operation.",
                            "search_pattern": search[:100]
                        }
                    
                    found = False
                    for i, line in enumerate(lines):
                        if search in line:
                            lines.insert(i, insert_content)
                            changes_made.append(f"Inserted content before line {i + 1}")
                            found = True
                            print(f"[DEBUG] Inserted before line {i + 1}")
                            break
                    
                    if not found:
                        return {"status": "error", "error": f"Modification {idx}: Could not find line with search text"}
                    
                    content = '\n'.join(lines)
                
                elif mod_type == 'delete_lines':
                    start_line = mod.get('start_line')
                    end_line = mod.get('end_line')
                    
                    if start_line is None:
                        return {"status": "error", "error": f"Modification {idx}: 'start_line' required for delete_lines"}
                    
                    if end_line is None:
                        end_line = start_line
                    
                    if start_line < 1 or start_line > len(lines):
                        return {"status": "error", "error": f"Modification {idx}: Invalid start_line: {start_line}"}
                    
                    if end_line < start_line or end_line > len(lines):
                        return {"status": "error", "error": f"Modification {idx}: Invalid end_line: {end_line}"}
                    
                    del lines[start_line - 1:end_line]
                    changes_made.append(f"Deleted lines {start_line}-{end_line}")
                    content = '\n'.join(lines)
                
                elif mod_type == 'replace_lines':
                    start_line = mod.get('start_line')
                    end_line = mod.get('end_line')
                    replace_content = mod.get('content', '')
                    
                    if start_line is None:
                        return {"status": "error", "error": f"Modification {idx}: 'start_line' required for replace_lines"}
                    
                    if end_line is None:
                        end_line = start_line
                    
                    if start_line < 1 or start_line > len(lines):
                        return {"status": "error", "error": f"Modification {idx}: Invalid start_line: {start_line}"}
                    
                    if end_line < start_line or end_line > len(lines):
                        return {"status": "error", "error": f"Modification {idx}: Invalid end_line: {end_line}"}
                    
                    lines[start_line - 1:end_line] = [replace_content]
                    changes_made.append(f"Replaced lines {start_line}-{end_line}")
                    content = '\n'.join(lines)
                
                else:
                    return {"status": "error", "error": f"Modification {idx}: Unknown type: {mod_type}"}
            
            except Exception as e:
                return {"status": "error", "error": f"Modification {idx} failed: {str(e)}"}
        
        # DRY-RUN MODE: Return preview without applying changes
        if dry_run:
            print("[DRY-RUN] Generating preview (no changes applied)")
            diff = self._generate_diff(original_content, content, os.path.basename(path))
            
            return {
                "status": "preview",
                "message": f"Preview of changes to {path} (not applied)",
                "path": path,
                "modifications_count": len(modifications),
                "changes": changes_made,
                "description": description,
                "diff": diff,
                "original_size": len(original_content),
                "modified_size": len(content),
                "dry_run": True
            }
        
        # CREATE BACKUP before writing
        backup_path = None
        if create_backup:
            backup_path = self._create_backup(full_path)
        
        # Write modified content
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[SUCCESS] File written: {path}")
        except Exception as e:
            # Try to restore original content
            print(f"[ERROR] Failed to write file: {e}")
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                print("[ROLLBACK] Restored original content")
            except:
                print("[CRITICAL] Failed to restore original content!")
            return {"status": "error", "error": f"Failed to write file: {str(e)}"}
        
        # SYNTAX VALIDATION (if requested and file is Arduino/C++)
        validation_result = None
        if validate_syntax and (path.endswith('.ino') or path.endswith('.cpp') or path.endswith('.h')):
            print(f"[VALIDATION] Validating syntax for {path}...")
            validation_result = self._validate_arduino_syntax(full_path, board)
            
            if not validation_result.get("valid", True):
                # ROLLBACK: Restore original content
                print("[ROLLBACK] Syntax validation failed, restoring original content")
                try:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    print("[ROLLBACK] ✓ Original content restored")
                    
                    return {
                        "status": "error",
                        "error": "Modifications would break compilation. Changes have been rolled back.",
                        "path": path,
                        "modifications_attempted": len(modifications),
                        "changes": changes_made,
                        "validation_errors": validation_result.get("errors", ""),
                        "rollback": True,
                        "backup_path": backup_path
                    }
                except Exception as e:
                    print(f"[CRITICAL] Rollback failed: {e}")
                    return {
                        "status": "error",
                        "error": f"Compilation failed AND rollback failed: {str(e)}",
                        "validation_errors": validation_result.get("errors", ""),
                        "backup_path": backup_path
                    }
        
        # SUCCESS: Return result with all details
        result = {
            "status": "success",
            "message": f"File modified: {path}",
            "path": path,
            "modifications_applied": len(modifications),
            "changes": changes_made,
            "description": description,
            "backup_path": backup_path
        }
        
        # Add validation info if performed
        if validation_result:
            result["validation"] = {
                "performed": True,
                "valid": validation_result.get("valid", True),
                "skipped": validation_result.get("skipped", False),
                "warnings": validation_result.get("warnings", "")
            }
        
        return result

    def _analyze_code(self, path: str = "", analysis_type: str = "full", 
                      board: str = "arduino:avr:uno", language: str = "en") -> Dict:
        """
        Analyze Arduino code for errors, warnings, suggestions, and optimizations.
        
        Args:
            path: Relative path to the file to analyze (defaults to current file)
            analysis_type: Type of analysis - "full", "quick", "security", or "performance"
            board: Target Arduino board type
            language: Language for analysis messages ("en" or "fr")
        
        Returns:
            Dictionary with status and analysis results
        """
        # If no path provided, return error (frontend should provide current file)
        if not path:
            return {
                "status": "error",
                "error": "No file path provided. Please specify a file to analyze."
            }
        
        # Validate path
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        # Check if file exists
        if not os.path.exists(full_path):
            return {
                "status": "error",
                "error": f"File not found: {path}"
            }
        
        # Read file content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to read file: {str(e)}"
            }
        
        # Create analyzer instance
        try:
            analyzer = CodeAnalyzer(board=board, language=language)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to initialize analyzer: {str(e)}"
            }
        
        # Perform analysis
        try:
            results = analyzer.analyze(code, analysis_type=analysis_type, board=board, language=language)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Analysis failed: {str(e)}"
            }
        
        # Return structured result
        return {
            "status": "success",
            "path": path,
            "analysis_type": analysis_type,
            "board": board,
            "language": language,
            "results": results,
            "summary": {
                "errors": len(results.get("errors", [])),
                "warnings": len(results.get("warnings", [])),
                "suggestions": len(results.get("suggestions", [])),
                "optimizations": len(results.get("optimizations", []))
            }
        }

    def _restore_backup(self, path: str, backup_path: Optional[str] = None, list_backups: bool = False) -> Dict:
        """
        Restore a file from backup or list available backups
        
        Args:
            path: Relative path to the file to restore
            backup_path: Optional specific backup file path
            list_backups: If True, list available backups instead of restoring
        
        Returns:
            Dictionary with status and backup information
        """
        is_valid, full_path = self.validate_path(path)
        if not is_valid:
            return {"status": "error", "error": full_path}
        
        filename = os.path.basename(full_path)
        
        # Find all backups for this file
        backup_pattern = f"{filename}.backup.*"
        available_backups = []
        
        try:
            if os.path.exists(self.backup_dir):
                for backup_file in os.listdir(self.backup_dir):
                    if backup_file.startswith(f"{filename}.backup."):
                        backup_full_path = os.path.join(self.backup_dir, backup_file)
                        timestamp_str = backup_file.split('.')[-1]
                        try:
                            timestamp = int(timestamp_str)
                            backup_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                            backup_size = os.path.getsize(backup_full_path)
                            
                            available_backups.append({
                                "filename": backup_file,
                                "path": backup_full_path,
                                "timestamp": timestamp,
                                "time": backup_time,
                                "size": backup_size
                            })
                        except (ValueError, OSError):
                            continue
            
            # Sort by timestamp (most recent first)
            available_backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to list backups: {str(e)}"
            }
        
        # LIST MODE: Return available backups
        if list_backups:
            return {
                "status": "success",
                "path": path,
                "backups": available_backups,
                "count": len(available_backups),
                "message": f"Found {len(available_backups)} backup(s) for {filename}"
            }
        
        # RESTORE MODE
        if not available_backups:
            return {
                "status": "error",
                "error": f"No backups found for {filename}",
                "path": path
            }
        
        # Determine which backup to restore
        if backup_path:
            # Use specified backup
            if not os.path.exists(backup_path):
                return {
                    "status": "error",
                    "error": f"Specified backup not found: {backup_path}"
                }
            restore_from = backup_path
            backup_info = next((b for b in available_backups if b['path'] == backup_path), None)
        else:
            # Use most recent backup
            backup_info = available_backups[0]
            restore_from = backup_info['path']
        
        # Create a backup of current file before restoring
        current_backup = None
        if os.path.exists(full_path):
            try:
                current_backup = self._create_backup(full_path)
                print(f"[BACKUP] Created backup of current file before restore: {current_backup}")
            except Exception as e:
                print(f"[WARNING] Could not backup current file: {e}")
        
        # Restore from backup
        try:
            shutil.copy2(restore_from, full_path)
            print(f"[RESTORE] ✓ Restored {filename} from backup")
            
            return {
                "status": "success",
                "message": f"File restored from backup: {filename}",
                "path": path,
                "restored_from": {
                    "path": restore_from,
                    "time": backup_info['time'] if backup_info else "unknown",
                    "size": backup_info['size'] if backup_info else 0
                },
                "current_backup": current_backup,
                "available_backups": len(available_backups)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to restore from backup: {str(e)}",
                "restore_from": restore_from
            }
