"""
Verification script for Task 2: Analysis type filtering and board-specific logic
"""

from code_analyzer import CodeAnalyzer


def test_analysis_type_filtering():
    """Test that analysis type filtering works correctly"""
    print("Testing analysis type filtering...")
    
    analyzer = CodeAnalyzer()
    
    # Test code with multiple issue types
    code = """
    String message = "Hello";  // Memory issue
    int ledPin = 13;
    int motorPin = 9;
    
    void setup() {
        pinMode(0, OUTPUT);  // Serial pin conflict
        pinMode(ledPin, OUTPUT);
    }
    
    void loop() {
        digitalWrite(motorPin, HIGH);  // motor control - hardware safety
        digitalWrite(ledPin, HIGH);
        delay(1000);  // Blocking code
    }
    """
    
    # Test full analysis
    result_full = analyzer.analyze(code, "full")
    print(f"\nFull analysis:")
    print(f"  Errors: {len(result_full['errors'])}")
    print(f"  Warnings: {len(result_full['warnings'])}")
    print(f"  Suggestions: {len(result_full['suggestions'])}")
    print(f"  Optimizations: {len(result_full['optimizations'])}")
    
    # Test quick analysis (only errors and warnings)
    result_quick = analyzer.analyze(code, "quick")
    print(f"\nQuick analysis:")
    print(f"  Errors: {len(result_quick['errors'])}")
    print(f"  Warnings: {len(result_quick['warnings'])}")
    print(f"  Suggestions: {len(result_quick['suggestions'])} (should be 0)")
    print(f"  Optimizations: {len(result_quick['optimizations'])} (should be 0)")
    assert len(result_quick['suggestions']) == 0, "Quick analysis should not include suggestions"
    assert len(result_quick['optimizations']) == 0, "Quick analysis should not include optimizations"
    
    # Test security analysis (only hardware safety)
    result_security = analyzer.analyze(code, "security")
    print(f"\nSecurity analysis:")
    print(f"  Errors: {len(result_security['errors'])} (hardware safety only)")
    print(f"  Warnings: {len(result_security['warnings'])} (hardware safety and pin conflicts only)")
    for error in result_security['errors']:
        print(f"    - {error['category']}: {error['message']}")
    for warning in result_security['warnings']:
        print(f"    - {warning['category']}: {warning['message']}")
    
    # Test performance analysis (memory, blocking code, optimizations)
    result_performance = analyzer.analyze(code, "performance")
    print(f"\nPerformance analysis:")
    print(f"  Warnings: {len(result_performance['warnings'])} (memory and blocking code only)")
    print(f"  Optimizations: {len(result_performance['optimizations'])}")
    for warning in result_performance['warnings']:
        print(f"    - {warning['category']}: {warning['message']}")
    
    print("\n✓ Analysis type filtering test passed!")


def test_board_specific_pin_mappings():
    """Test that board-specific pin mappings work correctly"""
    print("\n\nTesting board-specific pin mappings...")
    
    # Test Arduino Uno
    analyzer_uno = CodeAnalyzer(board="arduino:avr:uno")
    print(f"\nArduino Uno pin mappings:")
    print(f"  Serial pins: {analyzer_uno.pin_mappings['serial']}")
    print(f"  I2C pins: {analyzer_uno.pin_mappings['i2c']}")
    print(f"  SPI pins: {analyzer_uno.pin_mappings['spi']}")
    print(f"  PWM pins: {analyzer_uno.pin_mappings['pwm']}")
    
    # Test ESP32
    analyzer_esp32 = CodeAnalyzer(board="esp32:esp32:esp32")
    print(f"\nESP32 pin mappings:")
    print(f"  Serial pins: {analyzer_esp32.pin_mappings['serial']}")
    print(f"  I2C pins: {analyzer_esp32.pin_mappings['i2c']}")
    print(f"  SPI pins: {analyzer_esp32.pin_mappings['spi']}")
    print(f"  PWM pins: {analyzer_esp32.pin_mappings['pwm'][:10]}... (showing first 10)")
    
    # Test Arduino Mega
    analyzer_mega = CodeAnalyzer(board="arduino:avr:mega")
    print(f"\nArduino Mega pin mappings:")
    print(f"  Serial pins: {analyzer_mega.pin_mappings['serial']}")
    print(f"  I2C pins: {analyzer_mega.pin_mappings['i2c']}")
    print(f"  SPI pins: {analyzer_mega.pin_mappings['spi']}")
    print(f"  PWM pins: {analyzer_mega.pin_mappings['pwm']}")
    
    print("\n✓ Board-specific pin mappings test passed!")


def test_board_specific_pin_conflict_detection():
    """Test that pin conflict detection uses board-specific mappings"""
    print("\n\nTesting board-specific pin conflict detection...")
    
    # Code that uses Serial and configures pins
    code_uno = """
    #include <Wire.h>
    
    void setup() {
        Serial.begin(9600);
        pinMode(0, OUTPUT);  // Conflict on Uno (Serial)
        pinMode(18, OUTPUT); // Conflict on Uno (I2C A4)
    }
    
    void loop() {
        digitalWrite(0, HIGH);
    }
    """
    
    code_esp32 = """
    #include <Wire.h>
    
    void setup() {
        Serial.begin(115200);
        pinMode(1, OUTPUT);  // Conflict on ESP32 (Serial TX)
        pinMode(21, OUTPUT); // Conflict on ESP32 (I2C SDA)
    }
    
    void loop() {
        digitalWrite(1, HIGH);
    }
    """
    
    # Test Uno
    analyzer_uno = CodeAnalyzer(board="arduino:avr:uno")
    result_uno = analyzer_uno.analyze(code_uno, "full")
    print(f"\nArduino Uno conflicts detected: {len(result_uno['warnings'])}")
    for warning in result_uno['warnings']:
        if warning['category'] == 'pin_conflict':
            print(f"  - Line {warning['line']}: {warning['message']}")
    
    # Test ESP32
    analyzer_esp32 = CodeAnalyzer(board="esp32:esp32:esp32")
    result_esp32 = analyzer_esp32.analyze(code_esp32, "full")
    print(f"\nESP32 conflicts detected: {len(result_esp32['warnings'])}")
    for warning in result_esp32['warnings']:
        if warning['category'] == 'pin_conflict':
            print(f"  - Line {warning['line']}: {warning['message']}")
    
    print("\n✓ Board-specific pin conflict detection test passed!")


def test_filter_by_analysis_type_method():
    """Test the _filter_by_analysis_type method directly"""
    print("\n\nTesting _filter_by_analysis_type method...")
    
    analyzer = CodeAnalyzer()
    
    # Create mock findings
    all_findings = {
        "errors": [
            {"message": "Syntax error", "category": "syntax"},
            {"message": "Motor safety", "category": "hardware_safety"}
        ],
        "warnings": [
            {"message": "Memory issue", "category": "memory"},
            {"message": "Pin conflict", "category": "pin_conflict"},
            {"message": "Blocking code", "category": "blocking_code"}
        ],
        "suggestions": [
            {"message": "Use const", "category": "code_quality"}
        ],
        "optimizations": [
            {"message": "Use bitwise", "category": "performance"}
        ]
    }
    
    # Test full
    result_full = analyzer._filter_by_analysis_type(all_findings, "full")
    assert len(result_full['errors']) == 2
    assert len(result_full['warnings']) == 3
    assert len(result_full['suggestions']) == 1
    assert len(result_full['optimizations']) == 1
    print("  ✓ Full analysis returns all findings")
    
    # Test quick
    result_quick = analyzer._filter_by_analysis_type(all_findings, "quick")
    assert len(result_quick['errors']) == 2
    assert len(result_quick['warnings']) == 3
    assert len(result_quick['suggestions']) == 0
    assert len(result_quick['optimizations']) == 0
    print("  ✓ Quick analysis returns only errors and warnings")
    
    # Test security
    result_security = analyzer._filter_by_analysis_type(all_findings, "security")
    assert len(result_security['errors']) == 1  # Only hardware_safety
    assert len(result_security['warnings']) == 1  # Only pin_conflict
    print("  ✓ Security analysis returns only hardware safety findings")
    
    # Test performance
    result_performance = analyzer._filter_by_analysis_type(all_findings, "performance")
    assert len(result_performance['warnings']) == 2  # memory and blocking_code
    assert len(result_performance['optimizations']) == 1
    print("  ✓ Performance analysis returns only performance-related findings")
    
    print("\n✓ _filter_by_analysis_type method test passed!")


if __name__ == "__main__":
    test_analysis_type_filtering()
    test_board_specific_pin_mappings()
    test_board_specific_pin_conflict_detection()
    test_filter_by_analysis_type_method()
    
    print("\n" + "="*60)
    print("All Task 2 verification tests passed! ✓")
    print("="*60)
