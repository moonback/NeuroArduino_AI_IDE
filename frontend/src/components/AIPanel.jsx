import api from '../api';
import { Camera, ChevronLeft, ChevronRight, Cpu, Send, Sparkles, Wrench } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import ToolCallDisplay from './ToolCallDisplay';

const AIPanel = ({ onApplyCode, onOpenVision, onOpenFile, onFileModified, currentFile, currentCode, fileTree }) => {
    const { t } = useTranslation();
    const [input, setInput] = useState('');
    const [provider, setProvider] = useState('openrouter'); // 'openrouter' or 'gemini'
    const [enableTools, setEnableTools] = useState(true); // Enable tool calling
    const [includeProjectContext, setIncludeProjectContext] = useState(false); // Include all project files
    const [messages, setMessages] = useState([
        { role: 'assistant', content: t('aiGreeting') }
    ]);
    const [loading, setLoading] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    
    // Automatic analysis state
    const [autoAnalysisEnabled, setAutoAnalysisEnabled] = useState(() => {
        const stored = localStorage.getItem('autoAnalysisEnabled');
        return stored !== null ? JSON.parse(stored) : true; // Default to enabled
    });
    const [isAutoAnalyzing, setIsAutoAnalyzing] = useState(false);
    const debounceTimerRef = useRef(null);
    const previousFileRef = useRef(null);
    const previousCodeRef = useRef(null);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            // Get workspace path from Electron API
            let workspacePath = null;
            if (window.api && window.api.getWorkspacePath) {
                workspacePath = await window.api.getWorkspacePath();
            }
            
            // Prepare context with current file info
            const context = {
                current_file: currentFile ? {
                    name: currentFile.name,
                    path: currentFile.relativePath || currentFile.path,
                    content: currentCode
                } : null
            };
            
            // Add project files if requested
            if (includeProjectContext && fileTree) {
                context.project_files = fileTree.files.map(file => ({
                    name: file.name,
                    path: file.path,
                    isDirectory: file.isDirectory
                }));
                context.workspace_path = fileTree.path;
            }
            
            // Call Backend API with provider, history, and tool calling
            const res = await api.post('/ai/generate', { 
                prompt: input,
                provider: provider,
                enable_tools: enableTools,
                workspace_path: workspacePath || (fileTree ? fileTree.path : null),
                context: context,
                include_project_context: includeProjectContext,
                history: messages.filter(m => !m.error).map(m => ({ 
                    role: m.role === 'assistant' ? 'assistant' : 'user', 
                    content: m.content 
                }))
            });
            
            const aiMsg = {
                role: 'assistant',
                content: res.data.message || res.data.explanation,
                code: res.data.code,
                tool_calls: res.data.tool_calls || [],
                tool_results: res.data.tool_results || []
            };
            
            // Auto-apply tool results to editor
            if (aiMsg.tool_results && aiMsg.tool_results.length > 0) {
                for (const result of aiMsg.tool_results) {
                    if (result.result.status === 'success') {
                        const toolCall = aiMsg.tool_calls.find(tc => tc.id === result.id);
                        if (toolCall) {
                            await handleToolResult(toolCall, result.result);
                        }
                    }
                }
            }
            
            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: t('errorAIBrain'), error: true }]);
        }
        setLoading(false);
    };
    
    // Automatic analysis function
    const triggerAutoAnalysis = async () => {
        if (!autoAnalysisEnabled || !currentFile || !currentCode) {
            return;
        }
        
        setIsAutoAnalyzing(true);
        
        try {
            // Get workspace path from Electron API
            let workspacePath = null;
            if (window.api && window.api.getWorkspacePath) {
                workspacePath = await window.api.getWorkspacePath();
            }
            
            // Prepare context with current file info
            const context = {
                current_file: {
                    name: currentFile.name,
                    path: currentFile.relativePath || currentFile.path,
                    content: currentCode
                }
            };
            
            // Call Backend API with analyze_code tool request
            const res = await api.post('/ai/generate', { 
                prompt: 'Analyze this code for issues',
                provider: provider,
                enable_tools: true,
                workspace_path: workspacePath || (fileTree ? fileTree.path : null),
                context: context,
                include_project_context: false,
                history: []
            });
            
            const aiMsg = {
                role: 'assistant',
                content: res.data.message || res.data.explanation,
                code: res.data.code,
                tool_calls: res.data.tool_calls || [],
                tool_results: res.data.tool_results || [],
                isAutoAnalysis: true
            };
            
            // Only add to messages if there are findings
            if (aiMsg.tool_results && aiMsg.tool_results.length > 0) {
                setMessages(prev => [...prev, aiMsg]);
            }
        } catch (err) {
            console.error('Auto-analysis error:', err);
            // Don't show error to user for automatic analysis
        }
        
        setIsAutoAnalyzing(false);
    };
    
    const handleToolResult = async (toolCall, result) => {
        // Auto-apply file operations to the editor
        switch (toolCall.tool) {
            case 'create_file':
                // Open the newly created file in editor
                if (result.path && toolCall.parameters.content) {
                    await onOpenFile(result.path);
                    // The file is already created by backend, just open it
                }
                break;
                
            case 'modify_file':
                // Reload the modified file if it's currently open
                if (result.path) {
                    await onFileModified(result.path);
                }
                break;
                
            case 'rename_file':
                // Handle file rename
                if (result.new_path) {
                    await onFileModified(result.new_path);
                }
                break;
                
            default:
                // Other tools don't need editor updates
                break;
        }
    };
    
    // Store auto-analysis preference in localStorage
    useEffect(() => {
        localStorage.setItem('autoAnalysisEnabled', JSON.stringify(autoAnalysisEnabled));
    }, [autoAnalysisEnabled]);
    
    // Detect file open events
    useEffect(() => {
        if (!currentFile || !autoAnalysisEnabled) {
            return;
        }
        
        // Check if file has changed (file open event)
        if (previousFileRef.current?.path !== currentFile.path) {
            previousFileRef.current = currentFile;
            previousCodeRef.current = currentCode;
            
            // Clear any existing debounce timer
            if (debounceTimerRef.current) {
                clearTimeout(debounceTimerRef.current);
            }
            
            // Trigger analysis after 2 second debounce
            debounceTimerRef.current = setTimeout(() => {
                triggerAutoAnalysis();
            }, 2000);
        }
    }, [currentFile, autoAnalysisEnabled]);
    
    // Detect file save events (code changes)
    useEffect(() => {
        if (!currentFile || !autoAnalysisEnabled) {
            return;
        }
        
        // Check if code has changed significantly (not just typing)
        // We detect "save" by checking if code changed but file path stayed the same
        if (previousFileRef.current?.path === currentFile.path && 
            previousCodeRef.current !== currentCode) {
            
            previousCodeRef.current = currentCode;
            
            // Clear any existing debounce timer
            if (debounceTimerRef.current) {
                clearTimeout(debounceTimerRef.current);
            }
            
            // Trigger analysis after 2 second debounce
            debounceTimerRef.current = setTimeout(() => {
                triggerAutoAnalysis();
            }, 2000);
        }
    }, [currentCode, currentFile, autoAnalysisEnabled]);
    
    // Cleanup debounce timer on unmount
    useEffect(() => {
        return () => {
            if (debounceTimerRef.current) {
                clearTimeout(debounceTimerRef.current);
            }
        };
    }, []);

    return (
        <div className={`ai-panel ${isMinimized ? 'ai-panel-minimized' : ''}`}>
            {/* Minimize Toggle Button */}
            <button 
                className="ai-panel-toggle"
                onClick={() => setIsMinimized(!isMinimized)}
                title={isMinimized ? 'Expand AI Assistant' : 'Minimize AI Assistant'}
            >
                {isMinimized ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
            </button>

            {!isMinimized && (
                <>
                    {/* Header */}
                    <div className="ai-panel-header">
                        <div className="ai-panel-title">
                            <Sparkles size={18} className="ai-icon-glow" />
                            <span>{t('aiAssistant')}</span>
                            {isAutoAnalyzing && (
                                <span className="auto-analysis-indicator" title="Analyzing code...">
                                    ⚡
                                </span>
                            )}
                        </div>
                        
                        {/* Provider Selector & Tools Toggle */}
                        <div className="ai-provider-selector">
                            <span className="provider-label">Model:</span>
                            <select 
                                value={provider} 
                                onChange={(e) => setProvider(e.target.value)}
                                className="provider-select"
                            >
                                <option value="openrouter">OpenRouter Llama 3.1</option>
                                <option value="gemini">Gemini 2.0 Flash</option>
                            </select>
                            <button 
                                onClick={() => setEnableTools(!enableTools)}
                                className={`tools-toggle ${enableTools ? 'tools-active' : ''}`}
                                title={enableTools ? 'Tools Enabled' : 'Tools Disabled'}
                            >
                                <Wrench size={14} />
                            </button>
                        </div>
                    </div>
                    
                    {/* Auto-Analysis Toggle */}
                    <div className="ai-auto-analysis-toggle">
                        <label className="auto-analysis-label">
                            <input 
                                type="checkbox" 
                                checked={autoAnalysisEnabled}
                                onChange={(e) => setAutoAnalysisEnabled(e.target.checked)}
                                className="auto-analysis-checkbox"
                            />
                            <span className="auto-analysis-text">
                                ⚡ Auto-analyze on save/open
                            </span>
                        </label>
                    </div>
                    
                    {/* Project Context Toggle */}
                    {fileTree && (
                        <div className="ai-context-toggle">
                            <label className="context-toggle-label">
                                <input 
                                    type="checkbox" 
                                    checked={includeProjectContext}
                                    onChange={(e) => setIncludeProjectContext(e.target.checked)}
                                    className="context-toggle-checkbox"
                                />
                                <span className="context-toggle-text">
                                    📁 Include all project files ({fileTree.files.length} files)
                                </span>
                            </label>
                        </div>
                    )}
                    
                    {/* Header continuation */}
                    <div style={{ display: 'none' }}>
                    </div>
                    
                    {/* Current File Indicator */}
                    {currentFile && (
                        <div className="ai-current-file">
                            <div className="current-file-icon">📄</div>
                            <div className="current-file-info">
                                <div className="current-file-label">Current File:</div>
                                <div className="current-file-name">{currentFile.name}</div>
                            </div>
                        </div>
                    )}

                    {/* Messages */}
                    <div className="ai-messages-container">
                        {messages.map((msg, i) => (
                            <div key={i} className={`ai-message ${msg.role === 'user' ? 'ai-message-user' : 'ai-message-assistant'}`}>
                                {/* Avatar */}
                                <div className="ai-message-avatar">
                                    {msg.role === 'user' ? (
                                        <div className="avatar-user">U</div>
                                    ) : (
                                        <Cpu size={14} className="avatar-ai" />
                                    )}
                                </div>

                                {/* Content */}
                                <div className="ai-message-content">
                                    <div className="ai-message-bubble">
                                        {msg.content}
                                    </div>

                                    {/* Tool Calls Display */}
                                    {msg.tool_calls && msg.tool_calls.length > 0 && (
                                        <div className="ai-tool-calls">
                                            {msg.tool_calls.map((toolCall, idx) => (
                                                <ToolCallDisplay
                                                    key={idx}
                                                    toolCall={toolCall}
                                                    toolResult={msg.tool_results?.[idx]}
                                                    onOpenFile={onOpenFile}
                                                />
                                            ))}
                                        </div>
                                    )}

                                    {/* Code Block - Only show if no tool calls were made (for new file generation) */}
                                    {msg.code && (!msg.tool_calls || msg.tool_calls.length === 0) && (
                                        <div className="ai-code-block">
                                            <div className="ai-code-header">
                                                <div className="ai-code-label">
                                                    <Sparkles size={12} className="code-icon" />
                                                    <span>Arduino C++</span>
                                                </div>
                                                <button 
                                                    onClick={() => onApplyCode(msg.code)} 
                                                    className="ai-code-apply-btn"
                                                >
                                                    Apply to Editor
                                                </button>
                                            </div>
                                            <pre className="ai-code-content">
                                                <code>{msg.code}</code>
                                            </pre>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        
                        {loading && (
                            <div className="ai-loading">
                                <div className="ai-loading-dots">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                                <span className="ai-loading-text">
                                    {provider === 'openrouter' ? 'OpenRouter' : 'Gemini'} is thinking...
                                </span>
                            </div>
                        )}
                    </div>

                    {/* Input */}
                    <div className="ai-input-container">
                        <div className="ai-input-wrapper">
                            <input
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                                placeholder={`Ask ${provider === 'openrouter' ? 'OpenRouter' : 'Gemini'} anything...`}
                                className="ai-input"
                            />
                            <div className="ai-input-actions">
                                <button 
                                    onClick={onOpenVision} 
                                    className="ai-input-btn ai-vision-btn" 
                                    title="Vision-to-Wire"
                                >
                                    <Camera size={16} />
                                </button>
                                <button 
                                    onClick={sendMessage} 
                                    className="ai-input-btn ai-send-btn" 
                                    title="Send"
                                    disabled={!input.trim()}
                                >
                                    <Send size={16} />
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default AIPanel;
