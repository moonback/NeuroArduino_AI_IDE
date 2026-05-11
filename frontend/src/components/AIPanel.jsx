import React, { useState } from 'react';
import { Send, Cpu, Sparkles, Camera, ChevronRight, ChevronLeft } from 'lucide-react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const AIPanel = ({ onApplyCode, onOpenVision }) => {
    const { t } = useTranslation();
    const [input, setInput] = useState('');
    const [provider, setProvider] = useState('groq'); // 'groq' or 'gemini'
    const [messages, setMessages] = useState([
        { role: 'assistant', content: t('aiGreeting') }
    ]);
    const [loading, setLoading] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            // Call Backend API with provider and history
            const res = await axios.post('http://localhost:8001/ai/generate', { 
                prompt: input,
                provider: provider,
                history: messages.filter(m => !m.error).map(m => ({ 
                    role: m.role === 'assistant' ? 'assistant' : 'user', 
                    content: m.content 
                }))
            });
            const aiMsg = {
                role: 'assistant',
                content: res.data.explanation,
                code: res.data.code
            };
            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: t('errorAIBrain'), error: true }]);
        }
        setLoading(false);
    };

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
                        </div>
                        
                        {/* Provider Selector */}
                        <div className="ai-provider-selector">
                            <span className="provider-label">Model:</span>
                            <select 
                                value={provider} 
                                onChange={(e) => setProvider(e.target.value)}
                                className="provider-select"
                            >
                                <option value="groq">Groq Llama 3</option>
                                <option value="gemini">Gemini 2.5</option>
                            </select>
                        </div>
                    </div>

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

                                    {/* Code Block */}
                                    {msg.code && (
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
                                    {provider === 'groq' ? 'Groq' : 'Gemini'} is thinking...
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
                                placeholder={`Ask ${provider === 'groq' ? 'Groq' : 'Gemini'} anything...`}
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
