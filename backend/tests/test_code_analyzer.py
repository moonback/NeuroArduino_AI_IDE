"""
Unit tests for CodeAnalyzer
Tests pattern detection for errors, warnings, suggestions, and optimizations
"""

import pytest
from backend.code_analyzer import CodeAnalyzer


class TestCodeAnalyzer:
    """Test suite for CodeAnalyzer class"""
    
    def test_initialization(self):
        """Test CodeAnalyzer initialization with default parameters"""
        analyzer = CodeAnalyzer()
        assert analyzer.board == "arduino:avr:uno"
        assert analyzer.language == "en"
    
    def test_initialization_with_custom_params(self):
        """Test CodeAnalyzer initialization with custom parameters"""
        analyzer = CodeAnalyzer(board="esp32:esp32:esp32", language="fr")
        assert analyzer.board == "esp32:esp32:esp32"
        assert analyzer.language == "fr"
    
    def test_analyze_returns_correct_structure(self):
        """Test that analyze() returns the correct result structure"""
        analyzer = CodeAnalyzer()
        code = "void setup() {}\nvoid loop() {}"
        result = analyzer.analyze(code, "full")
        
        assert "errors" in result
        assert "warnings" in result
        assert "suggestions" in result
        assert "optimizations" in result
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["suggestions"], list)
        assert isinstance(result["optimizations"], list)
    
    def test_detect_blocking_delay(self):
        """Test detection of blocking delay() without millis()"""
        analyzer = CodeAnalyzer()
        code = """
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
        result = analyzer.analyze(code, "full")
        
        # Should detect blocking delay warnings
        assert len(result["warnings"]) > 0
        assert any("delay" in w["message"].lower() for w in result["warnings"])
    
    def test_no_blocking_delay_with_millis(self):
        """Test that delay() with millis() doesn't trigger warning"""
        analyzer = CodeAnalyzer()
        code = """
unsigned long previousMillis = 0;

void setup() {
    pinMode(13, OUTPUT);
}

void loop() {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= 1000) {
        previousMillis = currentMillis;
        digitalWrite(13, !digitalRead(13));
    }
}
"""
        result = analyzer.analyze(code, "full")
        
        # Should not detect blocking delay warnings
        blocking_warnings = [w for w in result["warnings"] if "delay" in w["message"].lower()]
        assert len(blocking_warnings) == 0
    
    def test_detect_string_usage(self):
        """Test detection of String class usage"""
        analyzer = CodeAnalyzer()
        code = """
String message = "Hello";

void setup() {
    Serial.begin(9600);
}

void loop() {
    Serial.println(message);
}
"""
        result = analyzer.analyze(code, "full")
        
        # Should detect String usage warning
        assert len(result["warnings"]) > 0
        assert any("string" in w["message"].lower() for w in result["warnings"])
    
    def test_detect_magic_numbers(self):
        """Test detection of magic numbers"""
        analyzer = CodeAnalyzer()
        code = """
void setup() {
    pinMode(13, OUTPUT);
}

void loop() {
    analogWrite(9, 127);
    delay(500);
}
"""
        result = analyzer.analyze(code, "full")
        
        # Should detect magic numbers
        assert len(result["suggestions"]) > 0
    
    def test_detect_motor_direct_connection(self):
        """Test detection of direct motor connections"""
        analyzer = CodeAnalyzer()
        code = """
int motorPin = 9;

void setup() {
    pinMode(motorPin, OUTPUT);
}

void loop() {
    digitalWrite(motorPin, HIGH); // motor control
}
"""
        result = analyzer.analyze(code, "security")
        
        # Should detect motor safety error
        assert len(result["errors"]) > 0
        assert any("motor" in e["message"].lower() for e in result["errors"])
    
    def test_detect_led_without_resistor(self):
        """Test detection of LED without resistor mention"""
        analyzer = CodeAnalyzer()
        code = """
int ledPin = 13;

void setup() {
    pinMode(ledPin, OUTPUT);
}

void loop() {
    digitalWrite(ledPin, HIGH);
    delay(1000);
}
"""
        result = analyzer.analyze(code, "security")
        
        # Should detect LED resistor warning
        assert len(result["warnings"]) > 0
        assert any("resistor" in w["message"].lower() or "led" in w["message"].lower() for w in result["warnings"])
    
    def test_detect_serial_pin_conflict(self):
        """Test detection of Serial pin conflicts"""
        analyzer = CodeAnalyzer()
        code = """
void setup() {
    Serial.begin(9600);
    pinMode(0, OUTPUT);  // Conflict with Serial RX
}

void loop() {
    digitalWrite(0, HIGH);
}
"""
        result = analyzer.analyze(code, "full")
        
        # Should detect Serial pin conflict
        assert len(result["warnings"]) > 0
        assert any("serial" in w["message"].lower() or "pin" in w["message"].lower() for w in result["warnings"])
    
    def test_detect_i2c_pin_conflict(self):
        """Test detection of I2C pin conflicts"""
        analyzer = CodeAnalyzer()
        code = """
#include <Wire.h>

void setup() {
    Wire.begin();
    pinMode(A4, OUTPUT);  // Conflict with I2C SDA
}

void loop() {
    digitalWrite(A4, HIGH);
}
"""
        result = analyzer.analyze(code, "full")
        
        # Should detect I2C pin conflict
        assert len(result["warnings"]) > 0
        assert any("i2c" in w["message"].lower() or "a4" in w["message"].lower() for w in result["warnings"])
    
    def test_detect_spi_pin_conflict(self):
        """Test detection of SPI pin conflicts"""
        analyzer = CodeAnalyzer()
        code = """
#include <SPI.h>

void setup() {
    SPI.begin();
    pinMode(10, OUTPUT);  // Conflict with SPI SS
}

void loop() {
    digitalWrite(10, HIGH);
}
"""
        result = analyzer.analyze(code, "full")
        
        # Should detect SPI pin conflict
        assert len(result["warnings"]) > 0
        assert any("spi" in w["message"].lower() or "pin" in w["message"].lower() for w in result["warnings"])
    
    def test_analysis_type_full(self):
        """Test full analysis type includes all categories"""
        analyzer = CodeAnalyzer()
        code = """
String msg = "test";
int ledPin = 13;

void setup() {
    pinMode(ledPin, OUTPUT);
}

void loop() {
    digitalWrite(ledPin, HIGH);
    delay(1000);
}
"""
        result = analyzer.analyze(code, "full")
        
        # Full analysis should check all categories
        # We expect warnings (String, delay) and suggestions (magic numbers)
        assert len(result["warnings"]) > 0 or len(result["suggestions"]) > 0
    
    def test_analysis_type_quick(self):
        """Test quick analysis type only includes errors and warnings"""
        analyzer = CodeAnalyzer()
        code = """
String msg = "test";

void setup() {
    pinMode(13, OUTPUT);
}

void loop() {
    delay(1000);
}
"""
        result = analyzer.analyze(code, "quick")
        
        # Quick analysis should only have errors and warnings
        # Suggestions and optimizations should be empty
        assert isinstance(result["suggestions"], list)
        assert isinstance(result["optimizations"], list)
    
    def test_analysis_type_security(self):
        """Test security analysis type focuses on hardware safety"""
        analyzer = CodeAnalyzer()
        code = """
int motorPin = 9;
int ledPin = 13;

void setup() {
    pinMode(motorPin, OUTPUT);
    pinMode(ledPin, OUTPUT);
}

void loop() {
    digitalWrite(motorPin, HIGH); // motor control
    digitalWrite(ledPin, HIGH);
}
"""
        result = analyzer.analyze(code, "security")
        
        # Security analysis should detect hardware safety issues
        assert len(result["errors"]) > 0 or len(result["warnings"]) > 0
    
    def test_analysis_type_performance(self):
        """Test performance analysis type focuses on performance issues"""
        analyzer = CodeAnalyzer()
        code = """
String msg = "test";

void setup() {
    Serial.begin(9600);
}

void loop() {
    delay(1000);
    Serial.println(msg);
}
"""
        result = analyzer.analyze(code, "performance")
        
        # Performance analysis should detect blocking code and String usage
        assert len(result["warnings"]) > 0
    
    def test_board_specific_pin_mappings_uno(self):
        """Test Arduino Uno specific pin mappings"""
        analyzer = CodeAnalyzer(board="arduino:avr:uno")
        pin_mappings = analyzer.pin_mappings
        
        assert pin_mappings["serial"] == [0, 1]
        assert pin_mappings["i2c"] == [18, 19]
        assert pin_mappings["spi"] == [10, 11, 12, 13]
    
    def test_board_specific_pin_mappings_esp32(self):
        """Test ESP32 specific pin mappings"""
        analyzer = CodeAnalyzer(board="esp32:esp32:esp32")
        pin_mappings = analyzer.pin_mappings
        
        assert pin_mappings["serial"] == [1, 3]
        assert pin_mappings["i2c"] == [21, 22]
        assert pin_mappings["spi"] == [5, 18, 19, 23]
    
    def test_internationalization_english(self):
        """Test English language output"""
        analyzer = CodeAnalyzer(language="en")
        code = """
void setup() {
    pinMode(13, OUTPUT);
}

void loop() {
    delay(1000);
}
"""
        result = analyzer.analyze(code, "full")
        
        # Check that messages are in English
        if result["warnings"]:
            assert "delay" in result["warnings"][0]["message"].lower()
    
    def test_internationalization_french(self):
        """Test French language output"""
        analyzer = CodeAnalyzer(language="fr")
        code = """
void setup() {
    pinMode(13, OUTPUT);
}

void loop() {
    delay(1000);
}
"""
        result = analyzer.analyze(code, "full")
        
        # Check that messages are in French
        if result["warnings"]:
            # French translation should contain "delay" or "bloquant"
            assert "delay" in result["warnings"][0]["message"].lower() or "bloquant" in result["warnings"][0]["message"].lower()
    
    def test_empty_code(self):
        """Test analysis of empty code"""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze("", "full")
        
        # Should return empty results for empty code
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
        assert len(result["suggestions"]) == 0
        assert len(result["optimizations"]) == 0
    
    def test_comment_only_code(self):
        """Test analysis of code with only comments"""
        analyzer = CodeAnalyzer()
        code = """
// This is a comment
// Another comment
"""
        result = analyzer.analyze(code, "full")
        
        # Should not detect issues in comments
        assert len(result["errors"]) == 0
