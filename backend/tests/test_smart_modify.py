"""
Tests for smart_modify_file tool
"""

import os
import tempfile
import pytest
from tools_registry import ToolRegistry


class TestSmartModifyFile:
    """Test suite for smart_modify_file tool"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = ToolRegistry(workspace_root=self.temp_dir)
        
        # Create a test Arduino file
        self.test_file = "test_sketch.ino"
        self.test_content = """// Blink LED sketch
void setup() {
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
"""
        self.test_path = os.path.join(self.temp_dir, self.test_file)
        with open(self.test_path, 'w') as f:
            f.write(self.test_content)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_replace_single_occurrence(self):
        """Test replacing a single occurrence"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "replace",
                    "search": "delay(1000);",
                    "content": "delay(500);",
                    "count": 1
                }
            ],
            "description": "Change first delay to 500ms"
        })
        
        assert result["status"] == "success"
        assert result["modifications_applied"] == 1
        
        # Verify file content
        with open(self.test_path, 'r') as f:
            content = f.read()
        
        assert "delay(500);" in content
        assert content.count("delay(500);") == 1
        assert content.count("delay(1000);") == 1
    
    def test_replace_all_occurrences(self):
        """Test replacing all occurrences"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "replace",
                    "search": "delay(1000);",
                    "content": "delay(500);"
                }
            ]
        })
        
        assert result["status"] == "success"
        
        # Verify file content
        with open(self.test_path, 'r') as f:
            content = f.read()
        
        assert content.count("delay(500);") == 2
        assert "delay(1000);" not in content
    
    def test_insert_after(self):
        """Test inserting content after a line"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "insert_after",
                    "search": "void setup() {",
                    "content": "  Serial.begin(9600);"
                }
            ]
        })
        
        assert result["status"] == "success"
        
        # Verify file content
        with open(self.test_path, 'r') as f:
            content = f.read()
        
        assert "Serial.begin(9600);" in content
        lines = content.split('\n')
        setup_idx = next(i for i, line in enumerate(lines) if "void setup()" in line)
        assert "Serial.begin(9600);" in lines[setup_idx + 1]
    
    def test_insert_before(self):
        """Test inserting content before a line"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "insert_before",
                    "search": "digitalWrite(13, HIGH);",
                    "content": "  Serial.println(\"LED ON\");"
                }
            ]
        })
        
        assert result["status"] == "success"
        
        # Verify file content
        with open(self.test_path, 'r') as f:
            content = f.read()
        
        assert "Serial.println(\"LED ON\");" in content
        assert content.index("Serial.println") < content.index("digitalWrite(13, HIGH)")
    
    def test_delete_lines(self):
        """Test deleting lines"""
        # Count original lines
        original_line_count = len(self.test_content.split('\n'))
        
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "delete_lines",
                    "start_line": 7,
                    "end_line": 8
                }
            ]
        })
        
        assert result["status"] == "success"
        
        # Verify file content
        with open(self.test_path, 'r') as f:
            content = f.read()
        
        new_line_count = len(content.split('\n'))
        
        # Should have 2 fewer lines
        assert new_line_count == original_line_count - 2
    
    def test_replace_lines(self):
        """Test replacing lines"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "replace_lines",
                    "start_line": 7,
                    "end_line": 10,
                    "content": "  // Optimized blink\n  digitalWrite(13, !digitalRead(13));\n  delay(500);"
                }
            ]
        })
        
        assert result["status"] == "success"
        
        # Verify file content
        with open(self.test_path, 'r') as f:
            content = f.read()
        
        assert "Optimized blink" in content
        assert "!digitalRead(13)" in content
    
    def test_multiple_modifications(self):
        """Test applying multiple modifications at once"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "insert_after",
                    "search": "// Blink LED sketch",
                    "content": "const int LED_PIN = 13;"
                },
                {
                    "type": "replace",
                    "search": "pinMode(13, OUTPUT);",
                    "content": "pinMode(LED_PIN, OUTPUT);"
                },
                {
                    "type": "replace",
                    "search": "digitalWrite(13,",
                    "content": "digitalWrite(LED_PIN,"
                },
                {
                    "type": "replace",
                    "search": "delay(1000);",
                    "content": "delay(500);"
                }
            ],
            "description": "Refactor to use constants and change delay"
        })
        
        assert result["status"] == "success"
        assert result["modifications_applied"] == 4
        
        # Verify file content
        with open(self.test_path, 'r') as f:
            content = f.read()
        
        assert "const int LED_PIN = 13;" in content
        assert "pinMode(LED_PIN, OUTPUT);" in content
        assert "digitalWrite(LED_PIN," in content
        assert content.count("delay(500);") == 2
    
    def test_search_not_found(self):
        """Test error when search text is not found"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "replace",
                    "search": "nonexistent text",
                    "content": "new text"
                }
            ]
        })
        
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()
    
    def test_invalid_line_number(self):
        """Test error with invalid line numbers"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "delete_lines",
                    "start_line": 100,
                    "end_line": 105
                }
            ]
        })
        
        assert result["status"] == "error"
        assert "invalid" in result["error"].lower()
    
    def test_file_not_found(self):
        """Test error when file doesn't exist"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": "nonexistent.ino",
            "modifications": [
                {
                    "type": "replace",
                    "search": "test",
                    "content": "new"
                }
            ]
        })
        
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()
    
    def test_missing_required_parameters(self):
        """Test error when required parameters are missing"""
        # Missing 'search' for replace
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "replace",
                    "content": "new text"
                }
            ]
        })
        
        assert result["status"] == "error"
        
        # Missing 'start_line' for delete_lines
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                {
                    "type": "delete_lines",
                    "end_line": 5
                }
            ]
        })
        
        assert result["status"] == "error"
    
    def test_complex_refactoring(self):
        """Test complex refactoring scenario"""
        result = self.registry.execute_tool("smart_modify_file", {
            "path": self.test_file,
            "modifications": [
                # Add constants
                {
                    "type": "insert_after",
                    "search": "// Blink LED sketch",
                    "content": "const int LED_PIN = 13;\nconst int DELAY_MS = 500;"
                },
                # Add Serial debugging
                {
                    "type": "insert_after",
                    "search": "void setup() {",
                    "content": "  Serial.begin(9600);\n  Serial.println(\"Sketch started\");"
                },
                # Replace pin numbers with constants
                {
                    "type": "replace",
                    "search": "pinMode(13, OUTPUT);",
                    "content": "pinMode(LED_PIN, OUTPUT);"
                },
                {
                    "type": "replace",
                    "search": "digitalWrite(13,",
                    "content": "digitalWrite(LED_PIN,"
                },
                # Replace delays with constant
                {
                    "type": "replace",
                    "search": "delay(1000);",
                    "content": "delay(DELAY_MS);"
                },
                # Add debug messages
                {
                    "type": "insert_before",
                    "search": "digitalWrite(LED_PIN, HIGH);",
                    "content": "  Serial.println(\"LED ON\");"
                },
                {
                    "type": "insert_before",
                    "search": "digitalWrite(LED_PIN, LOW);",
                    "content": "  Serial.println(\"LED OFF\");"
                }
            ],
            "description": "Complete refactoring with constants, Serial debugging, and optimizations"
        })
        
        assert result["status"] == "success"
        assert result["modifications_applied"] == 7
        
        # Verify all changes
        with open(self.test_path, 'r') as f:
            content = f.read()
        
        assert "const int LED_PIN = 13;" in content
        assert "const int DELAY_MS = 500;" in content
        assert "Serial.begin(9600);" in content
        assert "Serial.println(\"Sketch started\");" in content
        assert "pinMode(LED_PIN, OUTPUT);" in content
        assert "digitalWrite(LED_PIN," in content
        assert "delay(DELAY_MS);" in content
        assert "Serial.println(\"LED ON\");" in content
        assert "Serial.println(\"LED OFF\");" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
