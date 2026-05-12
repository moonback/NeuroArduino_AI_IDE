import axios from 'axios';
import { Camera, ChevronLeft, ChevronRight, Cpu, Send, Sparkles, Wrench, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import ToolCallDisplay from './ToolCallDisplay';

const AIPanel = ({ onApplyCode, onOpenVision, onOpenFile, onFileModified, currentFile, currentCode, fileTree }) => {
    const { t } = useTranslation();
    const [input, setInput] = useState('');
    const [provider, setProvider] = useState('openrouter');
    const [enableTools, setEnableTools] = useState(true);
    const [includeProjectContext, setIncludeProjectContext] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'assistant', content: t('aiGreeting') }
    ]);
    const [loading, setLoading] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    
    // File mention (@) autocomplete state
    const [showFileSuggestions, setShowFileSuggestions] = useState(false);
    const [fileSuggestions, setFileSuggestions] = useState([]);
    const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(0);
    const [mentionedFiles, setMentionedFiles] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const inputRef = useRef(null);
    const suggestionsRef = useRef(null);
    
    // Automatic analysis state
    const [autoAnalysisEnabled, setAutoAnalysisEnabled] = useState(() => {
        const stored = localStorage.getItem('autoAnalysisEnabled');
        return stored !== null ? JSON.parse(stored) : true;
    });
    const [isAutoAnalyzing, setIsAutoAnalyzing] = useState(false);
    const debounceTimerRef = useRef(null);
    const previousFileRef = useRef(null);
    const previousCodeRef = useRef(null);

    // Filter files based on search query
    const filterFiles = (query) => {
        if (!fileTree || !fileTree.files) {
            console.log('[FILE MENTION] No fileTree available');
            setFileSuggestions([]);
            return;
        }
        
        const allFiles = fileTree.files.filter(f => !f.isDirectory);
        console.log('[FILE MENTION] Total files:', allFiles.length);
        
        if (!query) {
            const suggestions = allFiles.slice(0, 10);
            console.log('[FILE MENTION] Showing', suggestions.length, 'files');
            setFileSuggestions(suggestions);
            setSelectedSuggestionIndex(0);
            return;
        }
        
        const lowerQuery = query.toLowerCase();
        const filtered = allFiles.filter(file => {
            const fileName = file.name.toLowerCase();
            const filePath = file.path.toLowerCase();
            return fileName.includes(lowerQuery) || filePath.includes(lowerQuery);
        });
        
        console.log('[FILE MENTION] Filtered to', filtered.length, 'files for query:', query);
        setFileSuggestions(filtered.slice(0, 10));
        setSelectedSuggestionIndex(0);
    };

    // Handle input change with @ detection
    const handleInputChange = (e) => {
        const value = e.target.value;
        setInput(value);
        
        const cursorPos = e.target.selectionStart;
        const textBeforeCursor = value.substring(0, cursorPos);
        const lastAtIndex = textBeforeCursor.lastIndexOf('@');
        
        console.log('[FILE MENTION] Input changed:', { value, cursorPos, lastAtIndex });
        
        if (lastAtIndex !== -1) {
            const textAfterAt = textBeforeCursor.substring(lastAtIndex + 1);
            
            if (!textAfterAt.includes(' ')) {
                console.log('[FILE MENTION] @ detected, query:', textAfterAt);
                setSearchQuery(textAfterAt);
                setShowFileSuggestions(true);
                filterFiles(textAfterAt);
            } else {
                console.log('[FILE MENTION] Space after @, hiding suggestions');
                setShowFileSuggestions(false);
            }
        } else {
            setShowFileSuggestions(false);
        }
    };

    // Select a file from suggestions
    const selectFile = (file) => {
        if (!mentionedFiles.find(f => f.path === file.path)) {
            setMentionedFiles(prev => [...prev, file]);
        }
        
        const cursorPos = inputRef.current.selectionStart;
        const textBeforeCursor = input.substring(0, cursorPos);
        const lastAtIndex = textBeforeCursor.lastIndexOf('@');
        
        const newInput = input.substring(0, lastAtIndex) + input.substring(cursorPos);
        setInput(newInput.trim());
        
        setShowFileSuggestions(false);
        setSearchQuery('');
        
        setTimeout(() => inputRef.current?.focus(), 0);
    };

    // Handle keyboard navigation
    const handleKeyDown = (e) => {
        if (!showFileSuggestions) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
            return;
        }
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedSuggestionIndex(prev => 
                Math.min(prev + 1, fileSuggestions.length - 1)
            );
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedSuggestionIndex(prev => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (fileSuggestions[selectedSuggestionIndex]) {
                selectFile(fileSuggestions[selectedSuggestionIndex]);
            }
        } else if (e.key === 'Escape') {
            setShowFileSuggestions(false);
        }
    };

    // Remove a mentioned file
    const removeMentionedFile = (index) => {
        setMentionedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const sendMessage = async () => {
        if (!input.trim() && mentionedFiles.length === 0) return;
        
        const mentionedFilesCopy = [...mentionedFiles];
        const userMsg = { 
            role: 'user', 
            content: input,
            mentionedFiles: mentionedFilesCopy
        };
        
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setMentionedFiles([]);
        setLoading(true);

        try {
            let workspacePath = null;
            if (window.api && window.api.getWorkspacePath) {
                workspacePath = await window.api.getWorkspacePath();
            }
            
            const context = {
                current_file: currentFile ? {
                    name: currentFile.name,
                    path: currentFile.path,
                    content: currentCode
                } : null
            };
            
            // Add mentioned files to context
            if (mentionedFilesCopy.length > 0) {
                context.mentioned_files = [];
                for (const file of mentionedFilesCopy) {
                    try {
                        if (window.api && window.api.readFile) {
                            const fullPath = fileTree.path + '/' + file.path;
                            const content = await window.api.readFile(fullPath);
                            context.mentioned_files.push({
                                name: file.name,
                                path: file.path,
                                content: content
                            });
                        }
                    } catch (err) {
                        console.error(`Failed to read mentioned file ${file.name}:`, err);
                    }
                }
            }
            
            if (includeProjectContext && fileTree) {
                context.project_files = fileTree.files.map(file => ({
                    name: file.name,
                    path: file.path,
                    isDirectory: file.isDirectory
                }));
                context.workspace_path = fileTree.path;
            }
            
            const res = await axios.post('http://localhost:8001/ai/generate', { 
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
    
    const triggerAutoAnalysis = async () => {
        if (!autoAnalysisEnabled || !currentFile || !currentCode) {
            return;
        }
        
        setIsAutoAnalyzing(true);
        
        try {
            let workspacePath = null;
            if (window.api && window.api.getWorkspacePath) {
                workspacePath = await window.api.getWorkspacePath();
            }
            
            const context = {
                current_file: {
                    name: currentFile.name,
                    path: currentFile.path,
                    content: currentCode
                }
            };
            
            const res = await axios.post('http://localhost:8001/ai/generate', { 
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
            
            if (aiMsg.tool_results && aiMsg.tool_results.length > 0) {
                setMessages(prev => [...prev, aiMsg]);
            }
        } catch (err) {
            console.error('Auto-analysis error:', err);
        }
        
        setIsAutoAnalyzing(false);
    };
    
    const handleToolResult = async (toolCall, result) => {
        switch (toolCall.tool) {
            case 'create_file':
                if (result.path && toolCall.parameters.content) {
                    await onOpenFile(result.path);
                }
                break;
                
            case 'modify_file':
            case 'smart_modify_file':
                if (result.path) {
                    await onFileModified(result.path);
                }
                break;
                
            case 'rename_file':
                if (result.new_path) {
                    await onFileModified(result.new_path);
                }
                break;
                
            default:
                break;
        }
    };
    
    useEffect(() => {
        localStorage.setItem('autoAnalysisEnabled', JSON.stringify(autoAnalysisEnabled));
    }, [autoAnalysisEnabled]);
    
    useEffect(() => {
        if (!currentFile || !autoAnalysisEnabled) {
            return;
        }
        
        if (previousFileRef.current?.path !== currentFile.path) {
            previousFileRef.current = currentFile;
            previousCodeRef.current = currentCode;
            
            if (debounceTimerRef.current) {
                clearTimeout(debounceTimerRef.current);
            }
            
            debounceTimerRef.current = setTimeout(() => {
                triggerAutoAnalysis();
            }, 2000);
        }
    }, [currentFile, autoAnalysisEnabled]);
    
    useEffect(() => {
        if (!currentFile || !autoAnalysisEnabled) {
            return;
        }
        
        if (previousFileRef.current?.path === currentFile.path && 
            previousCodeRef.current !== currentCode) {
            
            previousCodeRef.current = currentCode;
            
            if (debounceTimerRef.current) {
                clearTimeout(debounceTimerRef.current);
            }
            
            debounceTimerRef.current = setTimeout(() => {
                triggerAutoAnalysis();
            }, 2000);
        }
    }, [currentCode, currentFile, autoAnalysisEnabled]);
    
    useEffect(() => {
        return () => {
            if (debounceTimerRef.current) {
                clearTimeout(debounceTimerRef.current);
            }
        };
    }, []);

    // Get file icon based on extension
    const getFileIcon = (fileName) => {
        if (fileName.endsWith('.ino')) return '🔧';
        if (fileName.endsWith('.h')) return '📋';
        if (fileName.endsWith('.cpp')) return '⚙️';
        if (fileName.endsWith('.c')) return '⚙️';
        return '📄';
    };

    // Get just the filename from a path
    const getFileName = (filePath) => {
        if (!filePath) return '';
        // Handle both forward and backward slashes
        const parts = filePath.split(/[/\\]/);
        return parts[parts.length - 1];
    };

    // Get directory path from full path
    const getDirectoryPath = (filePath) => {
        if (!filePath) return '';
        const parts = filePath.split(/[/\\]/);
        if (parts.length <= 1) return filePath;
        return parts.slice(0, -1).join('/');
    };

    return (
        <div className={`ai-panel ${isMinimized ? 'ai-panel-minimized' : ''}`}>
            <button 
                className="ai-panel-toggle"
                onClick={() => setIsMinimized(!isMinimized)}
                title={isMinimized ? 'Expand AI Assistant' : 'Minimize AI Assistant'}
            >
                {isMinimized ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
            </button>

            {!isMinimized && (
                <>
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
                        
                        <div className="ai-provider-selector">
                            <span className="provider-label">Model:</span>
                            <select 
                                value={provider} 
                                onChange={(e) => setProvider(e.target.value)}
                                className="provider-select"
                            >
                                <option value="openrouter">OpenRouter GPT-OSS</option>
                                <option value="gemini">Gemini 2.5 Flash</option>
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
                                    📁 Inclure tous les fichiers du projet ({fileTree.files.length} files)
                                </span>
                            </label>
                        </div>
                    )}
                    
                    {currentFile && (
                        <div className="ai-current-file">
                            <div className="current-file-icon">📄</div>
                            <div className="current-file-info">
                                <div className="current-file-label">Fichier Actuel:</div>
                                <div className="current-file-name">{currentFile.name}</div>
                            </div>
                        </div>
                    )}

                    <div className="ai-messages-container">
                        {messages.map((msg, i) => (
                            <div key={i} className={`ai-message ${msg.role === 'user' ? 'ai-message-user' : 'ai-message-assistant'}`}>
                                <div className="ai-message-avatar">
                                    {msg.role === 'user' ? (
                                        <div className="avatar-user">U</div>
                                    ) : (
                                        <Cpu size={14} className="avatar-ai" />
                                    )}
                                </div>

                                <div className="ai-message-content">
                                    {msg.mentionedFiles && msg.mentionedFiles.length > 0 && (
                                        <div className="message-mentioned-files">
                                            <div className="message-mentioned-files-label">
                                                📎 Fichiers joints:
                                            </div>
                                            {msg.mentionedFiles.map((file, idx) => (
                                                <div key={idx} className="message-mentioned-file">
                                                    <span className="message-file-icon">{getFileIcon(file.name)}</span>
                                                    <span className="message-file-name">{getFileName(file.name)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                    
                                    <div className="ai-message-bubble">
                                        {msg.content}
                                    </div>

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
                                                    Appliquer à l'éditeur
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

                    <div className="ai-input-container">
                        {mentionedFiles.length > 0 && (
                            <div className="mentioned-files-container">
                                {mentionedFiles.map((file, idx) => (
                                    <div key={idx} className="mentioned-file-pill">
                                        <span className="mentioned-file-icon">{getFileIcon(file.name)}</span>
                                        <span className="mentioned-file-name">{getFileName(file.name)}</span>
                                        <button 
                                            className="mentioned-file-remove"
                                            onClick={() => removeMentionedFile(idx)}
                                            title="Remove file"
                                        >
                                            <X size={14} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                        
                        <div className="ai-input-wrapper">
                            {showFileSuggestions && (
                                <div className="file-suggestions-dropdown" ref={suggestionsRef}>
                                    <div className="file-suggestions-header">
                                        <span>📁 Fichiers ({fileSuggestions.length})</span>
                                    </div>
                                    {!fileTree ? (
                                        <div className="file-suggestions-empty">
                                            Ouvrez un dossier pour voir les fichiers
                                        </div>
                                    ) : fileSuggestions.length === 0 ? (
                                        <div className="file-suggestions-empty">
                                            Aucun fichier trouvé
                                        </div>
                                    ) : (
                                        fileSuggestions.map((file, idx) => (
                                            <div
                                                key={idx}
                                                className={`file-suggestion-item ${
                                                    idx === selectedSuggestionIndex ? 'selected' : ''
                                                }`}
                                                onClick={() => selectFile(file)}
                                                onMouseEnter={() => setSelectedSuggestionIndex(idx)}
                                            >
                                                <span className="file-suggestion-icon">
                                                    {getFileIcon(file.name)}
                                                </span>
                                                <div className="file-suggestion-info">
                                                    <div className="file-suggestion-name">{getFileName(file.name)}</div>
                                                    <div className="file-suggestion-path">{getDirectoryPath(file.path)}</div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                    <div className="file-suggestions-hint">
                                        ↑↓ pour naviguer • Enter pour sélectionner • Esc pour fermer
                                    </div>
                                </div>
                            )}
                            
                            <input
                                ref={inputRef}
                                value={input}
                                onChange={handleInputChange}
                                onKeyDown={handleKeyDown}
                                placeholder={`Tapez @ pour mentionner un fichier...`}
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
                                    disabled={!input.trim() && mentionedFiles.length === 0}
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
