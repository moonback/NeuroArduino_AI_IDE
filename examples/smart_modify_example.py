"""
Exemple d'utilisation de smart_modify_file
Démontre comment l'outil peut être utilisé pour modifier du code Arduino
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from tools_registry import ToolRegistry
import tempfile
import shutil

def print_section(title):
    """Print a formatted section title"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_file_content(path, title="File Content"):
    """Print file content with formatting"""
    print(f"\n--- {title} ---")
    with open(path, 'r') as f:
        content = f.read()
        for i, line in enumerate(content.split('\n'), 1):
            print(f"{i:2d} | {line}")
    print()

def example_1_simple_replace():
    """Example 1: Simple text replacement"""
    print_section("Example 1: Simple Replace - Change delay to 500ms")
    
    # Create temp workspace
    temp_dir = tempfile.mkdtemp()
    registry = ToolRegistry(workspace_root=temp_dir)
    
    # Create test file
    test_file = "blink.ino"
    test_path = os.path.join(temp_dir, test_file)
    
    original_code = """// Blink LED
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
    
    with open(test_path, 'w') as f:
        f.write(original_code)
    
    print("BEFORE:")
    print_file_content(test_path)
    
    # Apply modification
    result = registry.execute_tool("smart_modify_file", {
        "path": test_file,
        "modifications": [
            {
                "type": "replace",
                "search": "delay(1000);",
                "content": "delay(500);"
            }
        ],
        "description": "Changed delay to 500ms"
    })
    
    print(f"Result: {result['status']}")
    print(f"Changes: {result['changes']}")
    
    print("\nAFTER:")
    print_file_content(test_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_2_add_serial_debugging():
    """Example 2: Add Serial debugging"""
    print_section("Example 2: Add Serial Debugging")
    
    # Create temp workspace
    temp_dir = tempfile.mkdtemp()
    registry = ToolRegistry(workspace_root=temp_dir)
    
    # Create test file
    test_file = "blink.ino"
    test_path = os.path.join(temp_dir, test_file)
    
    original_code = """// Blink LED
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
    
    with open(test_path, 'w') as f:
        f.write(original_code)
    
    print("BEFORE:")
    print_file_content(test_path)
    
    # Apply modifications
    result = registry.execute_tool("smart_modify_file", {
        "path": test_file,
        "modifications": [
            {
                "type": "insert_after",
                "search": "void setup() {",
                "content": "  Serial.begin(9600);\n  Serial.println(\"Sketch started\");"
            },
            {
                "type": "insert_before",
                "search": "digitalWrite(13, HIGH);",
                "content": "  Serial.println(\"LED ON\");"
            },
            {
                "type": "insert_before",
                "search": "digitalWrite(13, LOW);",
                "content": "  Serial.println(\"LED OFF\");"
            }
        ],
        "description": "Added Serial debugging"
    })
    
    print(f"Result: {result['status']}")
    print(f"Modifications applied: {result['modifications_applied']}")
    print(f"Changes: {result['changes']}")
    
    print("\nAFTER:")
    print_file_content(test_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_3_refactor_with_constants():
    """Example 3: Refactor code to use constants"""
    print_section("Example 3: Refactor with Constants")
    
    # Create temp workspace
    temp_dir = tempfile.mkdtemp()
    registry = ToolRegistry(workspace_root=temp_dir)
    
    # Create test file
    test_file = "blink.ino"
    test_path = os.path.join(temp_dir, test_file)
    
    original_code = """// Blink LED
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
    
    with open(test_path, 'w') as f:
        f.write(original_code)
    
    print("BEFORE:")
    print_file_content(test_path)
    
    # Apply modifications
    result = registry.execute_tool("smart_modify_file", {
        "path": test_file,
        "modifications": [
            {
                "type": "insert_after",
                "search": "// Blink LED",
                "content": "const int LED_PIN = 13;\nconst int DELAY_MS = 500;"
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
                "content": "delay(DELAY_MS);"
            }
        ],
        "description": "Refactored to use named constants"
    })
    
    print(f"Result: {result['status']}")
    print(f"Modifications applied: {result['modifications_applied']}")
    print(f"Changes: {result['changes']}")
    
    print("\nAFTER:")
    print_file_content(test_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)

def example_4_complete_refactoring():
    """Example 4: Complete refactoring with all improvements"""
    print_section("Example 4: Complete Refactoring")
    
    # Create temp workspace
    temp_dir = tempfile.mkdtemp()
    registry = ToolRegistry(workspace_root=temp_dir)
    
    # Create test file
    test_file = "blink.ino"
    test_path = os.path.join(temp_dir, test_file)
    
    original_code = """// Blink LED
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
    
    with open(test_path, 'w') as f:
        f.write(original_code)
    
    print("BEFORE:")
    print_file_content(test_path)
    
    # Apply ALL modifications at once
    result = registry.execute_tool("smart_modify_file", {
        "path": test_file,
        "modifications": [
            # 1. Add constants
            {
                "type": "insert_after",
                "search": "// Blink LED",
                "content": "const int LED_PIN = 13;\nconst int DELAY_MS = 500;"
            },
            # 2. Add Serial initialization
            {
                "type": "insert_after",
                "search": "void setup() {",
                "content": "  Serial.begin(9600);\n  Serial.println(\"Blink sketch started\");"
            },
            # 3. Replace pin numbers with constants
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
            # 4. Replace delays with constant
            {
                "type": "replace",
                "search": "delay(1000);",
                "content": "delay(DELAY_MS);"
            },
            # 5. Add debug messages
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
        "description": "Complete refactoring: constants, Serial debugging, optimizations"
    })
    
    print(f"Result: {result['status']}")
    print(f"Modifications applied: {result['modifications_applied']}")
    print(f"Changes made:")
    for i, change in enumerate(result['changes'], 1):
        print(f"  {i}. {change}")
    
    print("\nAFTER:")
    print_file_content(test_path)
    
    print("\n✨ Summary of improvements:")
    print("  ✅ Added named constants (LED_PIN, DELAY_MS)")
    print("  ✅ Added Serial debugging")
    print("  ✅ Replaced magic numbers with constants")
    print("  ✅ Changed delay from 1000ms to 500ms")
    print("  ✅ Added debug messages for LED states")
    
    # Cleanup
    shutil.rmtree(temp_dir)

def main():
    """Run all examples"""
    print("\n" + "🚀 "*20)
    print("  SMART MODIFY FILE - EXAMPLES")
    print("🚀 "*20)
    
    try:
        example_1_simple_replace()
        input("\nPress Enter to continue to Example 2...")
        
        example_2_add_serial_debugging()
        input("\nPress Enter to continue to Example 3...")
        
        example_3_refactor_with_constants()
        input("\nPress Enter to continue to Example 4...")
        
        example_4_complete_refactoring()
        
        print("\n" + "✅ "*20)
        print("  ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("✅ "*20 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
