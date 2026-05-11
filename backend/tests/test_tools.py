"""
Tests for Tool Calling System
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools_registry import ToolRegistry


class TestToolRegistry:
    """Test suite for ToolRegistry"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def registry(self, temp_workspace):
        """Create a ToolRegistry instance with temp workspace"""
        return ToolRegistry(workspace_root=temp_workspace)
    
    # ==================== Path Validation Tests ====================
    
    def test_validate_path_success(self, registry):
        """Test valid path validation"""
        is_valid, full_path = registry.validate_path("test.ino")
        assert is_valid is True
        assert "test.ino" in full_path
    
    def test_validate_path_traversal(self, registry):
        """Test path traversal prevention"""
        is_valid, error = registry.validate_path("../../../etc/passwd")
        assert is_valid is False
        assert "not allowed" in error.lower()
    
    def test_validate_path_outside_workspace(self, registry):
        """Test prevention of access outside workspace"""
        is_valid, error = registry.validate_path("/etc/passwd")
        assert is_valid is False
        assert "outside workspace" in error.lower()
    
    # ==================== Create File Tests ====================
    
    def test_create_file_success(self, registry):
        """Test successful file creation"""
        result = registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "void setup() {}\nvoid loop() {}"
        })
        
        assert result["status"] == "success"
        assert "test.ino" in result["path"]
        assert result["size"] > 0
        
        # Verify file exists
        full_path = os.path.join(registry.workspace_root, "test.ino")
        assert os.path.exists(full_path)
    
    def test_create_file_with_subdirectory(self, registry):
        """Test file creation in subdirectory"""
        result = registry.execute_tool("create_file", {
            "path": "src/main.ino",
            "content": "// Main file"
        })
        
        assert result["status"] == "success"
        full_path = os.path.join(registry.workspace_root, "src", "main.ino")
        assert os.path.exists(full_path)
    
    def test_create_file_already_exists(self, registry):
        """Test error when file already exists"""
        # Create file first
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "test"
        })
        
        # Try to create again without overwrite
        result = registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "test2"
        })
        
        assert result["status"] == "error"
        assert "already exists" in result["error"].lower()
    
    def test_create_file_with_overwrite(self, registry):
        """Test file overwrite"""
        # Create file first
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "original"
        })
        
        # Overwrite
        result = registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "new content",
            "overwrite": True
        })
        
        assert result["status"] == "success"
        
        # Verify content
        full_path = os.path.join(registry.workspace_root, "test.ino")
        with open(full_path, 'r') as f:
            assert f.read() == "new content"
    
    # ==================== Modify File Tests ====================
    
    def test_modify_file_replace(self, registry):
        """Test replace operation"""
        # Create file
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "delay(1000);"
        })
        
        # Modify
        result = registry.execute_tool("modify_file", {
            "path": "test.ino",
            "operation": "replace",
            "search": "1000",
            "content": "500"
        })
        
        assert result["status"] == "success"
        
        # Verify
        full_path = os.path.join(registry.workspace_root, "test.ino")
        with open(full_path, 'r') as f:
            assert "delay(500);" in f.read()
    
    def test_modify_file_insert(self, registry):
        """Test insert operation"""
        # Create file
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "void setup() {\n}\nvoid loop() {\n}"
        })
        
        # Insert at line 2
        result = registry.execute_tool("modify_file", {
            "path": "test.ino",
            "operation": "insert",
            "line": 2,
            "content": "  Serial.begin(9600);"
        })
        
        assert result["status"] == "success"
        
        # Verify
        full_path = os.path.join(registry.workspace_root, "test.ino")
        with open(full_path, 'r') as f:
            content = f.read()
            assert "Serial.begin(9600);" in content
    
    def test_modify_file_append(self, registry):
        """Test append operation"""
        # Create file
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "void setup() {}"
        })
        
        # Append
        result = registry.execute_tool("modify_file", {
            "path": "test.ino",
            "operation": "append",
            "content": "\nvoid loop() {}"
        })
        
        assert result["status"] == "success"
        
        # Verify
        full_path = os.path.join(registry.workspace_root, "test.ino")
        with open(full_path, 'r') as f:
            content = f.read()
            assert "void setup() {}" in content
            assert "void loop() {}" in content
    
    def test_modify_file_not_found(self, registry):
        """Test error when file doesn't exist"""
        result = registry.execute_tool("modify_file", {
            "path": "nonexistent.ino",
            "operation": "replace",
            "search": "test",
            "content": "new"
        })
        
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()
    
    # ==================== Read File Tests ====================
    
    def test_read_file_success(self, registry):
        """Test successful file reading"""
        content = "void setup() {}\nvoid loop() {}"
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": content
        })
        
        result = registry.execute_tool("read_file", {
            "path": "test.ino"
        })
        
        assert result["status"] == "success"
        assert result["content"] == content
        assert result["size"] > 0
    
    def test_read_file_not_found(self, registry):
        """Test error when file doesn't exist"""
        result = registry.execute_tool("read_file", {
            "path": "nonexistent.ino"
        })
        
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()
    
    # ==================== Delete File Tests ====================
    
    def test_delete_file_success(self, registry):
        """Test successful file deletion"""
        # Create file
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "test"
        })
        
        # Delete
        result = registry.execute_tool("delete_file", {
            "path": "test.ino",
            "confirm": True
        })
        
        assert result["status"] == "success"
        
        # Verify deleted
        full_path = os.path.join(registry.workspace_root, "test.ino")
        assert not os.path.exists(full_path)
    
    def test_delete_file_without_confirmation(self, registry):
        """Test error when confirmation is missing"""
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "test"
        })
        
        result = registry.execute_tool("delete_file", {
            "path": "test.ino",
            "confirm": False
        })
        
        assert result["status"] == "error"
        assert "confirm" in result["error"].lower()
    
    # ==================== List Files Tests ====================
    
    def test_list_files_success(self, registry):
        """Test listing files in directory"""
        # Create some files
        registry.execute_tool("create_file", {"path": "file1.ino", "content": "test"})
        registry.execute_tool("create_file", {"path": "file2.ino", "content": "test"})
        registry.execute_tool("create_file", {"path": "readme.md", "content": "test"})
        
        result = registry.execute_tool("list_files", {
            "path": "."
        })
        
        assert result["status"] == "success"
        assert result["count"] == 3
        assert any("file1.ino" in f for f in result["files"])
        assert any("file2.ino" in f for f in result["files"])
    
    def test_list_files_with_pattern(self, registry):
        """Test listing files with glob pattern"""
        # Create files
        registry.execute_tool("create_file", {"path": "file1.ino", "content": "test"})
        registry.execute_tool("create_file", {"path": "file2.cpp", "content": "test"})
        registry.execute_tool("create_file", {"path": "readme.md", "content": "test"})
        
        result = registry.execute_tool("list_files", {
            "path": ".",
            "pattern": "*.ino"
        })
        
        assert result["status"] == "success"
        assert result["count"] == 1
        assert any("file1.ino" in f for f in result["files"])
    
    def test_list_files_recursive(self, registry):
        """Test recursive file listing"""
        # Create nested structure
        registry.execute_tool("create_file", {"path": "root.ino", "content": "test"})
        registry.execute_tool("create_file", {"path": "src/main.ino", "content": "test"})
        registry.execute_tool("create_file", {"path": "src/lib/helper.ino", "content": "test"})
        
        result = registry.execute_tool("list_files", {
            "path": ".",
            "recursive": True
        })
        
        assert result["status"] == "success"
        assert result["count"] == 3
    
    # ==================== Create Directory Tests ====================
    
    def test_create_directory_success(self, registry):
        """Test directory creation"""
        result = registry.execute_tool("create_directory", {
            "path": "src"
        })
        
        assert result["status"] == "success"
        
        # Verify
        full_path = os.path.join(registry.workspace_root, "src")
        assert os.path.isdir(full_path)
    
    def test_create_nested_directory(self, registry):
        """Test nested directory creation"""
        result = registry.execute_tool("create_directory", {
            "path": "src/lib/utils"
        })
        
        assert result["status"] == "success"
        
        # Verify
        full_path = os.path.join(registry.workspace_root, "src", "lib", "utils")
        assert os.path.isdir(full_path)
    
    # ==================== Rename File Tests ====================
    
    def test_rename_file_success(self, registry):
        """Test file renaming"""
        # Create file
        registry.execute_tool("create_file", {
            "path": "old.ino",
            "content": "test"
        })
        
        # Rename
        result = registry.execute_tool("rename_file", {
            "old_path": "old.ino",
            "new_path": "new.ino"
        })
        
        assert result["status"] == "success"
        
        # Verify
        old_path = os.path.join(registry.workspace_root, "old.ino")
        new_path = os.path.join(registry.workspace_root, "new.ino")
        assert not os.path.exists(old_path)
        assert os.path.exists(new_path)
    
    def test_rename_file_to_subdirectory(self, registry):
        """Test moving file to subdirectory"""
        # Create file
        registry.execute_tool("create_file", {
            "path": "test.ino",
            "content": "test"
        })
        
        # Move
        result = registry.execute_tool("rename_file", {
            "old_path": "test.ino",
            "new_path": "src/test.ino"
        })
        
        assert result["status"] == "success"
        
        # Verify
        new_path = os.path.join(registry.workspace_root, "src", "test.ino")
        assert os.path.exists(new_path)
    
    # ==================== Tool Definitions Tests ====================
    
    def test_get_tool_definitions(self, registry):
        """Test getting tool definitions"""
        definitions = registry.get_tool_definitions()
        
        assert len(definitions) > 0
        assert all("type" in d for d in definitions)
        assert all("function" in d for d in definitions)
    
    def test_get_tool_definitions_text(self, registry):
        """Test getting tool definitions as text"""
        text = registry.get_tool_definitions_text()
        
        assert "create_file" in text
        assert "modify_file" in text
        assert "Parameters:" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
