# Implementation Plan: Code Analysis and Proactive Suggestions

## Overview

This implementation plan breaks down the Code Analysis and Proactive Suggestions feature into discrete, actionable coding tasks. The feature will integrate with the existing Arduino IDE infrastructure, adding automated code analysis capabilities through the AI tool calling system.

**Implementation Language**: Python (backend), JavaScript/React (frontend)

**Key Integration Points**:
- Backend: `backend/tools_registry.py`, `backend/agents.py`
- Frontend: `frontend/src/components/AIPanel.jsx`, `frontend/src/components/ToolCallDisplay.jsx`, `frontend/src/components/Settings.jsx`
- I18n: `frontend/src/i18n/en.json`, `frontend/src/i18n/fr.json`

## Tasks

- [x] 1. Create CodeAnalyzer class with pattern detection engine
  - Create `backend/code_analyzer.py` file
  - Implement `CodeAnalyzer` class with `__init__` method accepting configuration parameters
  - Implement `analyze(code: str, analysis_type: str, board: str, language: str)` method returning structured analysis results
  - Implement pattern detection methods for blocking code (delay without millis), String usage, and magic numbers
  - Implement hardware safety pattern detection (motor connections, current limits, resistor checks)
  - Implement pin conflict detection for Serial (pins 0, 1), I2C (A4, A5), and SPI (10, 11, 12, 13)
  - Implement categorization logic to classify findings as errors, warnings, suggestions, or optimizations
  - Return results in structured format: `{"errors": [], "warnings": [], "suggestions": [], "optimizations": []}`
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11_

- [ ]* 1.1 Write unit tests for CodeAnalyzer pattern detection
  - Create `backend/tests/test_code_analyzer.py` file
  - Test blocking delay() detection with and without millis()
  - Test String class usage detection
  - Test pin conflict detection for Serial, I2C, and SPI
  - Test hardware safety checks (motor connections, current limits)
  - Test categorization logic (errors vs warnings vs suggestions)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11_

- [x] 2. Implement analysis type filtering and board-specific logic
  - In `backend/code_analyzer.py`, implement `_filter_by_analysis_type` method
  - For "full" type: return all findings (errors, warnings, suggestions, optimizations)
  - For "quick" type: return only errors and warnings
  - For "security" type: return only hardware safety and electrical hazard findings
  - For "performance" type: return only memory usage, blocking code, and optimization findings
  - Implement `_get_board_pin_mappings` method for Arduino Uno, ESP32, and other boards
  - Adjust pin conflict detection based on board architecture
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 9.1, 9.2, 9.3, 9.4_

- [ ]* 2.1 Write unit tests for analysis type filtering
  - Test that "full" analysis returns all finding types
  - Test that "quick" analysis returns only errors and warnings
  - Test that "security" analysis returns only safety-related findings
  - Test that "performance" analysis returns only performance-related findings
  - Test board-specific pin mapping for Uno vs ESP32
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 9.1, 9.2, 9.3, 9.4_

- [x] 3. Register analyze_code tool in Tool Registry
  - In `backend/tools_registry.py`, add `analyze_code` tool definition to `_register_tools` method
  - Define tool schema with parameters: `path` (string, default to current file), `analysis_type` (enum: full, quick, security, performance), `board` (string), `language` (string, default "en")
  - Add tool description explaining its purpose for AI model understanding
  - Implement `_analyze_code` method in `ToolRegistry` class
  - Extract path parameter, read file content, handle file not found errors
  - Call `CodeAnalyzer.analyze()` with file content and parameters
  - Return structured result with status "success" or "error"
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

- [ ]* 3.1 Write integration tests for analyze_code tool
  - Test tool registration in Tool Registry
  - Test tool execution with valid Arduino code
  - Test tool execution with file not found error
  - Test tool execution with different analysis types
  - Test that results are properly formatted with status field
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

- [x] 4. Checkpoint - Ensure backend analysis works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Integrate analyze_code tool with AI agents
  - In `backend/agents.py`, ensure `analyze_code` tool is included in `CodeGeneratorAgent` tool definitions
  - Verify tool is available for both Groq and Gemini providers
  - For Groq: ensure tool is in `tools` parameter with `tool_choice="auto"`
  - For Gemini: ensure tool is converted to `FunctionDeclaration` format
  - Handle analyze_code tool responses consistently from both providers
  - Format analysis results for display in conversation
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ]* 5.1 Write integration tests for AI agent tool calling
  - Test that Groq can call analyze_code tool
  - Test that Gemini can call analyze_code tool
  - Test that tool results are properly formatted for display
  - Test error handling when analysis fails
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 6. Enhance ToolCallDisplay for analysis results
  - In `frontend/src/components/ToolCallDisplay.jsx`, add analysis-specific rendering logic
  - Add icon for analyze_code tool (use a magnifying glass or code icon)
  - Display analysis_type parameter with appropriate badge styling
  - Display file path being analyzed
  - Group findings by category (errors, warnings, suggestions, optimizations)
  - Use red color with error icon for errors
  - Use yellow color with warning icon for warnings
  - Use blue color with lightbulb icon for suggestions
  - Use green color with performance icon for optimizations
  - Display finding count for each category
  - Make findings expandable/collapsible for better readability
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12_

- [ ]* 6.1 Test ToolCallDisplay rendering for analysis results
  - Manually test display of errors, warnings, suggestions, and optimizations
  - Verify color coding and icons are correct
  - Verify finding counts are accurate
  - Verify expand/collapse functionality works
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12_

- [x] 7. Implement automatic analysis triggers in AIPanel
  - In `frontend/src/components/AIPanel.jsx`, add state for automatic analysis settings
  - Implement `useEffect` hook to detect file save events from Editor component
  - Implement `useEffect` hook to detect file open events
  - Add debounce logic (2 seconds) to prevent excessive analysis calls
  - Trigger analyze_code tool call with analysis_type "quick" on file save/open
  - Display subtle loading indicator during automatic analysis
  - Store automatic analysis preference in browser localStorage
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.8_

- [ ]* 7.1 Test automatic analysis triggers
  - Manually test that analysis triggers on file save
  - Manually test that analysis triggers on file open
  - Verify debounce logic prevents excessive calls
  - Verify loading indicator appears during analysis
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.8_

- [x] 8. Add analysis configuration to Settings component
  - In `frontend/src/components/Settings.jsx`, add "Code Analysis" section
  - Add toggle for enabling/disabling automatic analysis
  - Add checkboxes for enabling/disabling individual check categories (errors, warnings, suggestions, optimizations)
  - Add slider for configuring memory usage warning threshold
  - Add dropdown for selecting target board type
  - Add "Reset to Defaults" button
  - Save all settings to browser localStorage
  - Pass settings to analyze_code tool calls
  - _Requirements: 7.6, 7.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_

- [ ]* 8.1 Test Settings component for analysis configuration
  - Manually test that settings are saved to localStorage
  - Verify that settings are applied to subsequent analyses
  - Test "Reset to Defaults" button functionality
  - _Requirements: 7.6, 7.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_

- [~] 9. Checkpoint - Ensure frontend integration works
  - Ensure all tests pass, ask the user if questions arise.

- [~] 10. Implement error detection patterns
  - In `backend/code_analyzer.py`, add `_detect_errors` method
  - Detect missing semicolons using regex pattern matching
  - Detect mismatched braces and parentheses using stack-based parsing
  - Detect undefined variables by tracking declarations and references
  - Detect pinMode() calls with invalid pin numbers (negative or > 53)
  - Detect digitalWrite() on pins not configured as OUTPUT
  - Detect analogRead() on digital-only pins
  - Detect Serial.begin() with invalid baud rates
  - Detect array index out of bounds access
  - Detect division by zero operations
  - Detect infinite loops without exit conditions
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 11.10_

- [ ]* 10.1 Write unit tests for error detection patterns
  - Test missing semicolon detection
  - Test mismatched braces detection
  - Test undefined variable detection
  - Test invalid pin number detection
  - Test digitalWrite on non-OUTPUT pin detection
  - Test analogRead on digital-only pin detection
  - Test invalid baud rate detection
  - Test array out of bounds detection
  - Test division by zero detection
  - Test infinite loop detection
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 11.10_

- [~] 11. Implement warning detection patterns
  - In `backend/code_analyzer.py`, add `_detect_warnings` method
  - Warn when delay() is used without corresponding millis() usage
  - Warn when String concatenation is used in loop()
  - Warn when floating-point arithmetic is used extensively
  - Warn when global variables consume > 50% of available RAM (estimate based on board)
  - Warn when sketch size exceeds 75% of Flash (requires compilation, may be optional)
  - Warn when analogWrite() is used on non-PWM pins
  - Warn when Serial communication is used without Serial.available() check
  - Warn when interrupts are disabled for extended periods (noInterrupts without interrupts)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_

- [ ]* 11.1 Write unit tests for warning detection patterns
  - Test delay() without millis() warning
  - Test String concatenation in loop() warning
  - Test floating-point arithmetic warning
  - Test global variable RAM usage warning
  - Test analogWrite on non-PWM pin warning
  - Test Serial without available() check warning
  - Test noInterrupts without interrupts warning
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_

- [~] 12. Implement suggestion generation
  - In `backend/code_analyzer.py`, add `_generate_suggestions` method
  - Suggest using millis() when delay() is detected
  - Suggest using char arrays when String is detected
  - Suggest using named constants when magic numbers are detected
  - Suggest creating functions when repeated code blocks are detected
  - Suggest refactoring when setup() or loop() exceeds 50 lines
  - Suggest adding Serial availability checks when Serial.print() is used
  - Suggest averaging multiple readings when analogRead() is called repeatedly
  - Suggest using #define or const when pin numbers are hardcoded
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

- [ ]* 12.1 Write unit tests for suggestion generation
  - Test millis() suggestion for delay()
  - Test char array suggestion for String
  - Test named constant suggestion for magic numbers
  - Test function creation suggestion for repeated code
  - Test refactoring suggestion for long functions
  - Test Serial.available() suggestion
  - Test analogRead averaging suggestion
  - Test #define suggestion for hardcoded pins
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

- [~] 13. Implement optimization recommendations
  - In `backend/code_analyzer.py`, add `_generate_optimizations` method
  - Recommend bitwise operations for integer division by powers of 2
  - Recommend integer math with scaling instead of floating-point
  - Recommend sprintf() or char array manipulation instead of String concatenation
  - Recommend PROGMEM for large constant arrays
  - Recommend caching repeated calculations in loop()
  - Recommend appropriate data types to avoid unnecessary conversions
  - Recommend buffering Serial.print() output
  - Estimate memory savings and performance improvements for each recommendation
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9_

- [ ]* 13.1 Write unit tests for optimization recommendations
  - Test bitwise operation recommendation
  - Test integer math recommendation
  - Test sprintf() recommendation
  - Test PROGMEM recommendation
  - Test calculation caching recommendation
  - Test data type recommendation
  - Test Serial buffering recommendation
  - Verify memory and performance estimates are included
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9_

- [~] 14. Checkpoint - Ensure all analysis patterns work
  - Ensure all tests pass, ask the user if questions arise.

- [~] 15. Integrate with HardwareRulesAgent for safety checks
  - In `backend/code_analyzer.py`, import `HardwareRulesAgent` from `agents.py`
  - In `analyze` method, call `HardwareRulesAgent.check_safety()` with code and prompt
  - Merge HardwareRulesAgent warnings into analysis results
  - Implement deduplication logic to avoid duplicate warnings
  - Consolidate warnings when both analyzers detect the same issue
  - Preserve severity level from HardwareRulesAgent
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

- [ ]* 15.1 Write integration tests for HardwareRulesAgent integration
  - Test that HardwareRulesAgent warnings are included in results
  - Test deduplication of warnings
  - Test that severity levels are preserved
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

- [~] 16. Implement internationalization support
  - In `backend/code_analyzer.py`, create `_get_translations` method
  - Create translation dictionary for all analysis messages in English and French
  - Accept `language` parameter in `analyze` method (default "en")
  - Return analysis messages in the specified language
  - Implement fallback to English when translation is missing
  - Add analysis-related strings to `frontend/src/i18n/en.json`
  - Add analysis-related strings to `frontend/src/i18n/fr.json`
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7_

- [ ]* 16.1 Test internationalization support
  - Test that English messages are returned when language="en"
  - Test that French messages are returned when language="fr"
  - Test fallback to English for missing translations
  - Verify frontend displays translated strings correctly
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7_

- [~] 17. Implement analysis result persistence
  - In `frontend/src/components/AIPanel.jsx`, store analysis results in conversation history
  - Use browser sessionStorage to persist results across page refreshes
  - Implement "Clear Analysis History" button in AIPanel
  - Limit stored results to most recent 10 analyses per file
  - Display both old and new results when file is re-analyzed
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [ ]* 17.1 Test analysis result persistence
  - Manually test that results persist across page refreshes
  - Test "Clear Analysis History" button functionality
  - Verify that only 10 most recent analyses are stored per file
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [~] 18. Implement manual analysis invocation through natural language
  - In `backend/agents.py`, update system prompts to recognize analysis requests
  - Add examples of analysis requests to prompt: "analyze my code", "check for errors", "check security", "optimize my code"
  - Ensure AI agent interprets variations: "review code", "find issues", "check for problems"
  - When no file is open, respond with message requesting user to open a file
  - Provide natural language summary of analysis results in addition to structured display
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [ ]* 18.1 Test manual analysis invocation
  - Test "analyze my code" triggers full analysis
  - Test "check for errors" triggers quick analysis
  - Test "check security" triggers security analysis
  - Test "optimize my code" triggers performance analysis
  - Test variations of analysis requests
  - Test error message when no file is open
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [~] 19. Implement performance optimizations and caching
  - In `backend/code_analyzer.py`, add caching mechanism for analysis results
  - Cache results using file path and content hash as key
  - Invalidate cache when file content changes
  - Implement parallel processing for independent analysis checks
  - Add performance timing to measure analysis duration
  - Display warning when file exceeds 2000 lines
  - Optimize regex patterns for better performance
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8_

- [ ]* 19.1 Test performance optimizations
  - Test that analysis completes within 1 second for 500-line files
  - Test that analysis completes within 2 seconds for 1000-line files
  - Test that cache is used for unchanged files
  - Test that cache is invalidated when file changes
  - Test warning display for files > 2000 lines
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8_

- [~] 20. Implement error reporting and logging
  - In `backend/code_analyzer.py`, add comprehensive error handling
  - Return detailed error messages with file path, line number, and description
  - Log analysis errors to backend console for debugging
  - In `frontend/src/components/AIPanel.jsx`, display user-friendly error messages
  - Handle file read errors with descriptive messages
  - Handle analysis timeout errors with timeout duration
  - Provide stack traces for unexpected errors in development mode
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_

- [ ]* 20.1 Test error reporting and logging
  - Test error message for file not found
  - Test error message for analysis timeout
  - Test error message for unexpected errors
  - Verify errors are logged to backend console
  - Verify user-friendly messages are displayed in frontend
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_

- [~] 21. Final checkpoint - End-to-end testing
  - Test complete workflow: open file → automatic analysis → view results
  - Test manual analysis through natural language: "analyze my code"
  - Test different analysis types: full, quick, security, performance
  - Test board-specific analysis for Arduino Uno and ESP32
  - Test internationalization with English and French
  - Test settings configuration and persistence
  - Test integration with HardwareRulesAgent
  - Test error handling and edge cases
  - Ensure all tests pass, ask the user if questions arise.

## Notes

### Implementation Order

The tasks are ordered to build incrementally:
1. **Backend Core** (Tasks 1-3): Create analyzer and register tool
2. **Backend Integration** (Tasks 4-5): Integrate with AI agents
3. **Frontend Display** (Tasks 6-9): Display results and add triggers
4. **Analysis Patterns** (Tasks 10-14): Implement all detection patterns
5. **Integration & Polish** (Tasks 15-20): Safety integration, i18n, performance, error handling
6. **Final Testing** (Task 21): End-to-end validation

### Testing Strategy

- Tasks marked with `*` are optional test tasks that can be skipped for faster MVP
- Unit tests validate individual components in isolation
- Integration tests validate component interactions
- Manual testing validates user-facing functionality
- All tests should pass before moving to the next checkpoint

### Key Dependencies

- **Task 3** depends on **Task 1** (analyzer must exist before tool registration)
- **Task 5** depends on **Task 3** (tool must be registered before AI integration)
- **Task 6** depends on **Task 5** (tool must work before display enhancement)
- **Task 15** depends on **Tasks 1-3** (analyzer must exist before safety integration)
- **Task 16** depends on **Tasks 1-3** (analyzer must exist before i18n)

### Performance Targets

- Quick analysis: < 1 second for files up to 500 lines
- Full analysis: < 2 seconds for files up to 1000 lines
- Automatic analysis debounce: 2 seconds after last file change
- Cache hit: < 100ms for unchanged files

### Internationalization

All user-facing messages must be added to both:
- `frontend/src/i18n/en.json` (English)
- `frontend/src/i18n/fr.json` (French)

### Safety Integration

The CodeAnalyzer complements the existing HardwareRulesAgent:
- HardwareRulesAgent: Prompt-based safety checks
- CodeAnalyzer: Pattern-based code analysis
- Both results are merged and deduplicated

### Future Enhancements

Not included in this implementation plan:
- Real-time analysis as user types (incremental analysis)
- AI-powered fix suggestions with automatic code modification
- Integration with Arduino compiler for compilation error analysis
- Machine learning-based pattern detection
- Multi-file cross-reference analysis
- Analysis result export to PDF/HTML
