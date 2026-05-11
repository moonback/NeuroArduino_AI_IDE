"""
Unit tests for analyze_code tool in Tool Registry
Tests tool registration, parameter validation, and execution
"""

import pytest
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from tools_registry import ToolRegistry


class TestAnalyzeCodeTool:
    """Test suite for analyze_code tool"""
    
    @pytest.fixture
    def registry(self, tmp_path):
        """Create a ToolRegistry instance with temporary workspace"""
        return ToolRegistry(workspace_root=str(tmp_path))
    
    @pytest.fixture
    def sample_arduino_code(self):
        """Sample Arduino code for testing"""
        return """
void setup() {
    pinMode(13, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    digitalWrite(13, HIGH);
    delay(1000);
    digitalWrite(13, LOW);
    delay(1000);
}
"""
    
    def test_tool_registered(self, registry):
        """Test that analyze_code tool is registered"""
        assert "analyze_code" in registry.tools
        tool = registry.tools["analyze_code"]
        assert tool["name"] == "analyze_code"
        assert "description" in tool
        assert "parameters" in tool
    
    def test_tool_parameters_schema(self, registry):
        """Test that analyze_code tool has correct parameter schema"""
        tool = registry.tools["analyze_code"]
        params = tool["parameters"]
        
        assert params["type"] == "object"
        assert "properties" in params
        
        properties = params["properties"]
        
        # Check path parameter
        assert "path" in properties
        assert properties["path"]["type"] == "string"
        assert properties["path"]["default"] == ""
        
        # Check analysis_type parameter
        assert "analysis_type" in properties
        assert properties["analysis_type"]["type"] == "string"
        assert properties["analysis_type"]["enum"] == ["full", "quick", "security", "performance"]
        assert properties["analysis_type"]["default"] == "full"
        
        # Check board parameter
        assert "board" in properties
        assert properties["board"]["type"] == "string"
        assert properties["board"]["default"] == "arduino:avr:uno"
        
        # Check language parameter
        assert "language" in properties
        assert properties["language"]["type"] == "string"
        assert properties["language"]["enum"] == ["en", "fr"]
        assert properties["language"]["default"] == "en"
    
    def test_tool_in_definitions(self, registry):
        """Test that analyze_code appears in tool definitions"""
        definitions = registry.get_tool_definitions()
        
        analyze_code_def = None
        for tool_def in definitions:
            if tool_def["function"]["name"] == "analyze_code":
                analyze_code_def = tool_def
                break
        
        assert analyze_code_def is not None
        assert analyze_code_def["type"] == "function"
        assert "description" in analyze_code_def["function"]
        assert "parameters" in analyze_code_def["function"]
    
    def test_execute_analyze_code_no_path(self, registry):
        """Test executing analyze_code without path parameter"""
        result = registry.execute_tool("analyze_code", {})
        
        assert result["status"] == "error"
        assert "No file path provided" in result["error"]
    
    def test_execute_analyze_code_file_not_found(self, registry):
        """Test executing analyze_code with non-existent file"""
        result = registry.execute_tool("analyze_code", {
            "path": "nonexistent.ino"
        })
        
        assert result["status"] == "error"
        assert "File not found" in result["error"]
    
    def test_execute_analyze_code_success(self, registry, tmp_path, sample_arduino_code):
        """Test successful execution of analyze_code"""
        # Create a test file
        test_file = tmp_path / "test.ino"
        test_file.write_text(sample_arduino_code)
        
        result = registry.execute_tool("analyze_code", {
            "path": "test.ino",
            "analysis_type": "full"
        })
        
        assert result["status"] == "success"
        assert result["path"] == "test.ino"
        assert result["analysis_type"] == "full"
        assert "results" in result
        assert "summary" in result
        
        # Check results structure
        results = result["results"]
        assert "errors" in results
        assert "warnings" in results
        assert "suggestions" in results
        assert "optimizations" in results
        
        # Check summary
        summary = result["summary"]
        assert "errors" in summary
        assert "warnings" in summary
        assert "suggestions" in summary
        assert "optimizations" in summary
    
    def test_execute_analyze_code_quick_type(self, registry, tmp_path, sample_arduino_code):
        """Test analyze_code with quick analysis type"""
        test_file = tmp_path / "test.ino"
        test_file.write_text(sample_arduino_code)
        
        result = registry.execute_tool("analyze_code", {
            "path": "test.ino",
            "analysis_type": "quick"
        })
        
        assert result["status"] == "success"
        assert result["analysis_type"] == "quick"
    
    def test_execute_analyze_code_security_type(self, registry, tmp_path, sample_arduino_code):
        """Test analyze_code with security analysis type"""
        test_file = tmp_path / "test.ino"
        test_file.write_text(sample_arduino_code)
        
        result = registry.execute_tool("analyze_code", {
            "path": "test.ino",
            "analysis_type": "security"
        })
        
        assert result["status"] == "success"
        assert result["analysis_type"] == "security"
    
    def test_execute_analyze_code_performance_type(self, registry, tmp_path, sample_arduino_code):
        """Test analyze_code with performance analysis type"""
        test_file = tmp_path / "test.ino"
        test_file.write_text(sample_arduino_code)
        
        result = registry.execute_tool("analyze_code", {
            "path": "test.ino",
            "analysis_type": "performance"
        })
        
        assert result["status"] == "success"
        assert result["analysis_type"] == "performance"
    
    def test_execute_analyze_code_with_board(self, registry, tmp_path, sample_arduino_code):
        """Test analyze_code with board parameter"""
        test_file = tmp_path / "test.ino"
        test_file.write_text(sample_arduino_code)
        
        result = registry.execute_tool("analyze_code", {
            "path": "test.ino",
            "board": "esp32:esp32:esp32"
        })
        
        assert result["status"] == "success"
        assert result["board"] == "esp32:esp32:esp32"
    
    def test_execute_analyze_code_with_language(self, registry, tmp_path, sample_arduino_code):
        """Test analyze_code with language parameter"""
        test_file = tmp_path / "test.ino"
        test_file.write_text(sample_arduino_code)
        
        result = registry.execute_tool("analyze_code", {
            "path": "test.ino",
            "language": "fr"
        })
        
        assert result["status"] == "success"
        assert result["language"] == "fr"
    
    def test_execute_analyze_code_detects_issues(self, registry, tmp_path):
        """Test that analyze_code detects actual code issues"""
        # Code with blocking delay
        code_with_issues = """
void setup() {
    pinMode(13, OUTPUT);
}

void loop() {
    digitalWrite(13, HIGH);
    delay(5000);  // Blocking delay
    digitalWrite(13, LOW);
    delay(5000);
}
"""
        test_file = tmp_path / "test.ino"
        test_file.write_text(code_with_issues)
        
        result = registry.execute_tool("analyze_code", {
            "path": "test.ino",
            "analysis_type": "full"
        })
        
        assert result["status"] == "success"
        
        # Should detect blocking delay warning
        warnings = result["results"]["warnings"]
        assert len(warnings) > 0
        
        # Check that at least one warning is about blocking delay
        has_delay_warning = any("delay" in w["message"].lower() for w in warnings)
        assert has_delay_warning
    
    def test_execute_analyze_code_path_validation(self, registry):
        """Test that analyze_code validates file paths"""
        # Try to access file outside workspace
        result = registry.execute_tool("analyze_code", {
            "path": "../../../etc/passwd"
        })
        
        assert result["status"] == "error"
        assert "outside workspace" in result["error"].lower() or "not allowed" in result["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
