# Design Document: Code Analysis and Proactive Suggestions

## Overview

The Code Analysis and Proactive Suggestions feature adds intelligent, automated code analysis capabilities to the Arduino IDE. This feature integrates seamlessly with the existing AI-powered tool system, providing developers with real-time feedback on code quality, safety issues, performance optimizations, and best practices.

### Key Capabilities

- **Automated Analysis**: Automatic code analysis triggered on file save/open events
- **Manual Analysis**: On-demand analysis through natural language requests
- **Multi-Type Analysis**: Support for full, quick, security, and performance analysis modes
- **Context-Aware**: Board-specific analysis considering Arduino Uno, ESP32, and other platforms
- **AI Integration**: Works with both Groq (Llama 3.3) and Gemini (2.0 Flash) providers
- **Safety Integration**: Complements existing HardwareRulesAgent for comprehensive safety checks
- **Internationalization**: Supports English and French output

### Design Goals

1. **Non-Intrusive**: Analysis should enhance workflow without interrupting development
2. **Actionable**: Findings should be specific, clear, and actionable
3. **Fast**: Analysis should complete within seconds for typical Arduino sketches
4. **Extensible**: Easy to add new analysis patterns and checks
5. **Integrated**: Seamless integration with existing IDE components

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend (React)"
        Editor[Editor Component]
        AIPanel[AI Panel Component]
        ToolDisplay[Tool Call Display]
        Settings[Settings Component]
    end
    
    subgraph "Backend (Python)"
        API[FastAPI Endpoints]
        Agent[Code Generator Agent]
        Registry[Tool Registry]
        Analyzer[Code Analyzer]
        Safety[Hardware Rules Agent]
    end
    
    subgraph "AI Providers"
        Groq[Groq API<br/>Llama 3.3]
        Gemini[Gemini API<br/>2.0 Flash]
    end
    
    Editor -->|File Save/Open| AIPanel
    AIPanel -->|Trigger Analysis| API
    API -->|Route Request| Agent
    Agent -->|Call Tool| Registry
    Registry -->|Execute| Analyzer
    Analyzer -->|Safety Check| Safety
    Analyzer -->|Return Results| Registry
    Registry -->|Format Response| Agent
    Agent -->|Function Calling| Groq
    Agent -->|Function Calling| Gemini
    Agent -->|Display Results| AIPanel
    AIPanel -->|Render| ToolDisplay
    Settings -->|Configure| Analyzer
    
    style Analyzer fill:#4CAF50
    style AIPanel fill:#2196F3
    style Agent fill:#FF9800
