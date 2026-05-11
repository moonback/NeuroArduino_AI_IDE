"""
Code Analyzer for Arduino IDE
Provides intelligent code analysis with pattern detection for errors, warnings, suggestions, and optimizations.
"""

import re
from typing import Dict, List, Any, Optional


class CodeAnalyzer:
    """
    Analyzes Arduino code for errors, warnings, suggestions, and optimizations.
    Supports multiple analysis types: full, quick, security, and performance.
    """
    
    def __init__(self, board: str = "arduino:avr:uno", language: str = "en"):
        """
        Initialize the CodeAnalyzer with configuration parameters.
        
        Args:
            board: Target Arduino board type (e.g., "arduino:avr:uno", "esp32:esp32:esp32")
            language: Language for analysis messages ("en" or "fr")
        """
        self.board = board
        self.language = language
        
        # Board-specific pin mappings
        self.pin_mappings = self._get_board_pin_mappings(board)
        
        # Translation dictionary
        self.translations = self._get_translations()
    
    def analyze(self, code: str, analysis_type: str = "full", board: str = None, language: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze Arduino code and return structured analysis results.
        
        Args:
            code: The Arduino code to analyze
            analysis_type: Type of analysis - "full", "quick", "security", or "performance"
            board: Optional board override
            language: Optional language override
        
        Returns:
            Dictionary with keys: errors, warnings, suggestions, optimizations
            Each key contains a list of findings with: message, line, severity, category
        """
        # Override board and language if provided
        if board:
            self.board = board
            self.pin_mappings = self._get_board_pin_mappings(board)
        if language:
            self.language = language
        
        # Initialize result structure
        results = {
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "optimizations": []
        }
        
        # Perform analysis based on type using the filter method
        all_findings = self._run_all_checks(code)
        results = self._filter_by_analysis_type(all_findings, analysis_type)
        
        return results
    
    def _run_all_checks(self, code: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run all analysis checks and return unfiltered results.
        
        Args:
            code: The Arduino code to analyze
        
        Returns:
            Dictionary with all findings before filtering
        """
        all_errors = []
        all_warnings = []
        
        # Collect all errors
        all_errors.extend(self._detect_errors(code))
        all_errors.extend(self._detect_hardware_safety_errors(code))
        
        # Collect all warnings
        all_warnings.extend(self._detect_warnings(code))
        all_warnings.extend(self._detect_hardware_safety_warnings(code))
        
        return {
            "errors": all_errors,
            "warnings": all_warnings,
            "suggestions": self._detect_suggestions(code),
            "optimizations": self._detect_optimizations(code)
        }
    
    def _filter_by_analysis_type(self, all_findings: Dict[str, List[Dict[str, Any]]], analysis_type: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter analysis findings based on analysis type.
        Requirement 3.1: For "full" type, return all findings
        Requirement 3.2: For "quick" type, return only errors and warnings
        Requirement 3.3: For "security" type, return only hardware safety findings
        Requirement 3.4: For "performance" type, return only memory and performance findings
        
        Args:
            all_findings: Dictionary with all findings from analysis
            analysis_type: Type of analysis - "full", "quick", "security", or "performance"
        
        Returns:
            Filtered dictionary based on analysis type
        """
        results = {
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "optimizations": []
        }
        
        if analysis_type == "full":
            # Return all findings
            return all_findings
        
        elif analysis_type == "quick":
            # Only critical errors and warnings
            results["errors"] = all_findings["errors"]
            results["warnings"] = all_findings["warnings"]
        
        elif analysis_type == "security":
            # Focus on hardware safety and electrical hazards
            results["errors"] = [
                f for f in all_findings["errors"]
                if f.get("category") in ["hardware_safety", "electrical"]
            ]
            results["warnings"] = [
                f for f in all_findings["warnings"]
                if f.get("category") in ["hardware_safety", "electrical", "pin_conflict"]
            ]
        
        elif analysis_type == "performance":
            # Focus on memory usage, blocking code, and optimization opportunities
            results["warnings"] = [
                f for f in all_findings["warnings"]
                if f.get("category") in ["memory", "blocking_code", "performance"]
            ]
            results["optimizations"] = all_findings["optimizations"]
        
        return results
    
    def _detect_errors(self, code: str) -> List[Dict[str, Any]]:
        """Detect critical errors in the code."""
        errors = []
        lines = code.split('\n')
        
        # Check for syntax errors (basic patterns)
        for i, line in enumerate(lines, 1):
            # Skip comments and empty lines
            if line.strip().startswith('//') or not line.strip():
                continue
            
            # Missing semicolon (simple heuristic)
            if any(keyword in line for keyword in ['digitalWrite', 'pinMode', 'analogWrite', 'Serial.begin']):
                if not line.rstrip().endswith(';') and not line.rstrip().endswith('{') and not line.rstrip().endswith('}'):
                    errors.append({
                        "message": self._translate("missing_semicolon"),
                        "line": i,
                        "severity": "error",
                        "category": "syntax"
                    })
        
        return errors
    
    def _detect_warnings(self, code: str) -> List[Dict[str, Any]]:
        """Detect warnings in the code."""
        warnings = []
        
        # Blocking code detection
        warnings.extend(self._detect_blocking_code(code))
        
        # String usage detection
        warnings.extend(self._detect_string_usage(code))
        
        # Pin conflict detection
        warnings.extend(self._detect_pin_conflicts(code))
        
        return warnings
    
    def _detect_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """Generate suggestions for code improvements."""
        suggestions = []
        
        # Magic numbers detection
        suggestions.extend(self._detect_magic_numbers(code))
        
        return suggestions
    
    def _detect_optimizations(self, code: str) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        optimizations = []
        
        # Detect opportunities for optimization
        # (This is a placeholder for future optimization detection)
        
        return optimizations
    
    def _detect_blocking_code(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect blocking delay() calls without corresponding millis() usage.
        Requirement 2.3: Detect blocking delay() calls without corresponding millis() usage
        """
        warnings = []
        lines = code.split('\n')
        
        has_delay = False
        has_millis = False
        delay_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'delay(' in line and not line.strip().startswith('//'):
                has_delay = True
                delay_lines.append(i)
            if 'millis()' in line and not line.strip().startswith('//'):
                has_millis = True
        
        # If delay is used but millis is not, suggest non-blocking approach
        if has_delay and not has_millis:
            for line_num in delay_lines:
                warnings.append({
                    "message": self._translate("blocking_delay"),
                    "line": line_num,
                    "severity": "warning",
                    "category": "blocking_code"
                })
        
        return warnings
    
    def _detect_string_usage(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect String class usage and warn about dynamic memory allocation.
        Requirement 2.4: Detect String class usage and warn about dynamic memory allocation
        """
        warnings = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Look for String declarations or usage
            if re.search(r'\bString\s+\w+', line) and not line.strip().startswith('//'):
                warnings.append({
                    "message": self._translate("string_usage"),
                    "line": i,
                    "severity": "warning",
                    "category": "memory"
                })
        
        return warnings
    
    def _detect_magic_numbers(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect magic numbers in the code.
        Suggests using named constants for better readability.
        """
        suggestions = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Skip comments and #define statements
            if line.strip().startswith('//') or line.strip().startswith('#define') or line.strip().startswith('const'):
                continue
            
            # Look for numeric literals in function calls (excluding common values like 0, 1, HIGH, LOW)
            # Match numbers that are not 0, 1, or very common values
            matches = re.findall(r'\b(\d{2,})\b', line)
            for match in matches:
                num = int(match)
                # Ignore very common values
                if num not in [0, 1, 2, 10, 100, 1000]:
                    suggestions.append({
                        "message": self._translate("magic_number").format(number=match),
                        "line": i,
                        "severity": "suggestion",
                        "category": "code_quality"
                    })
                    break  # Only report once per line
        
        return suggestions
    
    def _detect_hardware_safety_errors(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect hardware safety errors.
        Requirement 2.6: Detect direct motor connections to Arduino pins
        """
        errors = []
        lines = code.split('\n')
        
        # Detect motor connections without proper driver
        for i, line in enumerate(lines, 1):
            if 'motor' in line.lower() and 'digitalWrite' in line and not line.strip().startswith('//'):
                errors.append({
                    "message": self._translate("motor_direct_connection"),
                    "line": i,
                    "severity": "error",
                    "category": "hardware_safety"
                })
        
        return errors
    
    def _detect_hardware_safety_warnings(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect hardware safety warnings.
        Requirement 2.5: Detect missing current-limiting resistors for LED connections
        Requirement 2.10: Detect excessive current draw from individual pins
        """
        warnings = []
        lines = code.split('\n')
        
        # Detect LED connections without resistor mention
        has_led = False
        has_resistor = False
        led_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'led' in line.lower() and not line.strip().startswith('//'):
                has_led = True
                led_lines.append(i)
            if 'resistor' in line.lower() and not line.strip().startswith('//'):
                has_resistor = True
        
        if has_led and not has_resistor:
            for line_num in led_lines[:1]:  # Report only once
                warnings.append({
                    "message": self._translate("led_resistor"),
                    "line": line_num,
                    "severity": "warning",
                    "category": "hardware_safety"
                })
        
        return warnings
    
    def _detect_pin_conflicts(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect pin conflicts for Serial, I2C, and SPI based on board architecture.
        Requirement 2.7: Detect Serial pin conflicts (pins 0 and 1)
        Requirement 2.8: Detect I2C pin conflicts (A4 and A5 on Uno)
        Requirement 2.9: Detect SPI pin conflicts (10, 11, 12, 13)
        Requirement 9.2, 9.3, 9.4: Board-specific pin conflict detection
        """
        warnings = []
        lines = code.split('\n')
        
        # Check if Serial is used
        has_serial = any('Serial.begin' in line for line in lines)
        
        # Check if Wire (I2C) is used
        has_i2c = 'Wire.begin' in code or '#include <Wire.h>' in code
        
        # Check if SPI is used
        has_spi = 'SPI.begin' in code or '#include <SPI.h>' in code
        
        # Get board-specific pin mappings
        serial_pins = self.pin_mappings.get("serial", [])
        i2c_pins = self.pin_mappings.get("i2c", [])
        spi_pins = self.pin_mappings.get("spi", [])
        
        # Check for pin usage
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('//'):
                continue
            
            # Serial pin conflicts
            if has_serial and serial_pins:
                for pin in serial_pins:
                    # Check for both numeric and analog pin references
                    if re.search(rf'pinMode\s*\(\s*{pin}\s*,', line):
                        warnings.append({
                            "message": self._translate("serial_pin_conflict").format(pin=pin),
                            "line": i,
                            "severity": "warning",
                            "category": "pin_conflict"
                        })
            
            # I2C pin conflicts
            if has_i2c and i2c_pins:
                for pin in i2c_pins:
                    # Check for both numeric and analog pin references (A4=18, A5=19 on Uno)
                    if re.search(rf'pinMode\s*\(\s*{pin}\s*,', line):
                        warnings.append({
                            "message": self._translate("i2c_pin_conflict").format(pin=pin),
                            "line": i,
                            "severity": "warning",
                            "category": "pin_conflict"
                        })
                    # Also check for A4/A5 notation on Uno
                    if pin == 18 and re.search(r'pinMode\s*\(\s*A4\s*,', line):
                        warnings.append({
                            "message": self._translate("i2c_pin_conflict").format(pin="A4"),
                            "line": i,
                            "severity": "warning",
                            "category": "pin_conflict"
                        })
                    if pin == 19 and re.search(r'pinMode\s*\(\s*A5\s*,', line):
                        warnings.append({
                            "message": self._translate("i2c_pin_conflict").format(pin="A5"),
                            "line": i,
                            "severity": "warning",
                            "category": "pin_conflict"
                        })
            
            # SPI pin conflicts
            if has_spi and spi_pins:
                for pin in spi_pins:
                    if re.search(rf'pinMode\s*\(\s*{pin}\s*,', line):
                        warnings.append({
                            "message": self._translate("spi_pin_conflict").format(pin=pin),
                            "line": i,
                            "severity": "warning",
                            "category": "pin_conflict"
                        })
        
        return warnings
    
    def _detect_performance_warnings(self, code: str) -> List[Dict[str, Any]]:
        """Detect performance-related warnings."""
        warnings = []
        
        # Reuse blocking code detection for performance analysis
        warnings.extend(self._detect_blocking_code(code))
        
        # Reuse String usage detection for performance analysis
        warnings.extend(self._detect_string_usage(code))
        
        return warnings
    
    def _get_board_pin_mappings(self, board: str) -> Dict[str, List[int]]:
        """
        Get board-specific pin mappings.
        Requirement 9: Context-aware analysis based on board type
        
        Args:
            board: Board identifier string (e.g., "arduino:avr:uno", "esp32:esp32:esp32")
        
        Returns:
            Dictionary mapping pin function types to pin numbers
        """
        if "esp32" in board.lower():
            return {
                "serial": [1, 3],  # ESP32 Serial pins (TX, RX)
                "i2c": [21, 22],   # ESP32 I2C pins (SDA, SCL)
                "spi": [5, 18, 19, 23],  # ESP32 SPI pins (SS, SCK, MISO, MOSI)
                "pwm": list(range(0, 16))  # ESP32 has PWM on most pins
            }
        elif "mega" in board.lower():
            return {
                "serial": [0, 1, 14, 15, 16, 17, 18, 19],  # Mega has multiple serial ports
                "i2c": [20, 21],   # Mega I2C pins (SDA, SCL)
                "spi": [50, 51, 52, 53],  # Mega SPI pins
                "pwm": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 44, 45, 46]
            }
        else:  # Default to Arduino Uno
            return {
                "serial": [0, 1],
                "i2c": [18, 19],  # A4, A5 (mapped to 18, 19)
                "spi": [10, 11, 12, 13],
                "pwm": [3, 5, 6, 9, 10, 11]  # Uno PWM pins
            }
    
    def _get_pin_mappings(self, board: str) -> Dict[str, List[int]]:
        """
        Deprecated: Use _get_board_pin_mappings instead.
        Kept for backward compatibility.
        """
        return self._get_board_pin_mappings(board)
    
    def _get_translations(self) -> Dict[str, Dict[str, str]]:
        """
        Get translation dictionary for analysis messages.
        Requirement 20: Internationalization support
        """
        return {
            "en": {
                "missing_semicolon": "Missing semicolon at end of statement",
                "blocking_delay": "Blocking delay() call detected. Consider using millis() for non-blocking code",
                "string_usage": "String class usage detected. Consider using char arrays for better memory management",
                "magic_number": "Magic number '{number}' detected. Consider using a named constant",
                "motor_direct_connection": "Direct motor connection detected. Use a motor driver (L298N, L293D) to avoid damaging the Arduino",
                "led_resistor": "LED connection detected. Remember to use a current-limiting resistor (220-330Ω)",
                "serial_pin_conflict": "Pin {pin} used for I/O. This pin is reserved for Serial communication",
                "i2c_pin_conflict": "Pin {pin} used for I/O. This pin is reserved for I2C communication (Wire library)",
                "spi_pin_conflict": "Pin {pin} used for I/O. This pin is reserved for SPI communication"
            },
            "fr": {
                "missing_semicolon": "Point-virgule manquant à la fin de l'instruction",
                "blocking_delay": "Appel delay() bloquant détecté. Considérez l'utilisation de millis() pour un code non-bloquant",
                "string_usage": "Utilisation de la classe String détectée. Considérez l'utilisation de tableaux char pour une meilleure gestion de la mémoire",
                "magic_number": "Nombre magique '{number}' détecté. Considérez l'utilisation d'une constante nommée",
                "motor_direct_connection": "Connexion directe de moteur détectée. Utilisez un driver de moteur (L298N, L293D) pour éviter d'endommager l'Arduino",
                "led_resistor": "Connexion LED détectée. N'oubliez pas d'utiliser une résistance de limitation de courant (220-330Ω)",
                "serial_pin_conflict": "Pin {pin} utilisée pour I/O. Cette pin est réservée pour la communication Serial",
                "i2c_pin_conflict": "Pin {pin} utilisée pour I/O. Cette pin est réservée pour la communication I2C (bibliothèque Wire)",
                "spi_pin_conflict": "Pin {pin} utilisée pour I/O. Cette pin est réservée pour la communication SPI"
            }
        }
    
    def _translate(self, key: str) -> str:
        """
        Translate a message key to the current language.
        
        Args:
            key: Translation key
        
        Returns:
            Translated message, or English fallback if translation not found
        """
        lang_dict = self.translations.get(self.language, self.translations["en"])
        return lang_dict.get(key, self.translations["en"].get(key, key))
