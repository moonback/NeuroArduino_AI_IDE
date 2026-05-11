import React, { useState } from 'react';
import { Send, Cpu, Sparkles, Camera } from 'lucide-react';
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
        <div className="panel-ai" style={{ width: '350px', borderLeft: '1px solid var(--border)', display: 'flex', flexDirection: 'column', background: 'var(--bg-panel)' }}>
            {/* Header */}
            <div style={{ 
                padding: '12px', 
                borderBottom: '1px solid var(--border)', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between' 
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
                    <Cpu size={16} color="var(--accent)" />
                    <span>{t('aiAssistant')}</span>
                </div>
                
                {/* Provider Selector */}
                <select 
                    value={provider} 
                    onChange={(e) => setProvider(e.target.value)}
                    style={{ 
                        background: '#21262d', 
                        color: 'var(--text-primary)', 
                        border: '1px solid var(--border)', 
                        borderRadius: '4px', 
                        fontSize: '11px',
                        padding: '2px 4px',
                        outline: 'none',
                        cursor: 'pointer'
                    }}
                >
                    <option value="groq">Groq (Llama 3)</option>
                    <option value="gemini">Gemini 1.5 Flash</option>
                </select>
            </div>

            {/* Messages */}
            <div style={{ flexGrow: 1, padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {messages.map((msg, i) => (
                    <div key={i} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '90%' }}>

                        <div style={{
                            background: msg.role === 'user' ? 'var(--accent)' : '#21262d',
                            color: msg.role === 'user' ? '#000' : 'var(--text-primary)',
                            padding: '10px', borderRadius: '8px', fontSize: '14px', lineHeight: '1.4',
                            boxShadow: msg.role === 'user' ? '0 2px 10px rgba(0, 212, 255, 0.2)' : 'none'
                        }}>
                            {msg.content}
                        </div>

                        {/* Code Block Option */}
                        {msg.code && (
                            <div style={{ marginTop: '8px', background: '#0d1117', border: '1px solid var(--border)', borderRadius: '6px', overflow: 'hidden' }}>
                                <div style={{ background: '#30363d', padding: '4px 8px', fontSize: '11px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <Sparkles size={10} color="var(--accent)" />
                                        <span>Arduino C++</span>
                                    </div>
                                    <button onClick={() => onApplyCode(msg.code)} style={{ 
                                        color: 'var(--accent)', 
                                        cursor: 'pointer', 
                                        background: 'none', 
                                        border: 'none',
                                        fontSize: '11px',
                                        fontWeight: 600
                                    }}>Apply</button>
                                </div>
                                <pre style={{ padding: '8px', fontSize: '12px', overflowX: 'auto', margin: 0 }}>
                                    <code>{msg.code}</code>
                                </pre>
                            </div>
                        )}
                    </div>
                ))}
                {loading && <div style={{ opacity: 0.5, fontSize: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div className="pulse" style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent)' }}></div>
                    Thinking with {provider === 'groq' ? 'Groq' : 'Gemini'}...
                </div>}
            </div>

            {/* Input */}
            <div style={{ padding: '10px', borderTop: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', gap: '8px', background: 'var(--bg-input)', padding: '8px', borderRadius: '6px', border: '1px solid var(--border)' }}>
                    <input
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && sendMessage()}
                        placeholder={`Ask ${provider === 'groq' ? 'Groq' : 'Gemini'} to blink an LED...`}
                        style={{ background: 'transparent', border: 'none', color: '#fff', outline: 'none', flexGrow: 1, fontSize: '14px' }}
                    />
                    <button onClick={onOpenVision} title="Vision-to-Wire" style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '2px' }}>
                        <Camera size={16} color="#a78bfa" />
                    </button>
                    <button onClick={sendMessage} title="Send" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                        <Send size={16} color="var(--accent)" />
                    </button>
                </div>
            </div>
            
            <style>{`
                .pulse {
                    animation: pulse-animation 1.5s infinite ease-in-out;
                }
                @keyframes pulse-animation {
                    0% { transform: scale(0.95); opacity: 0.5; }
                    50% { transform: scale(1.1); opacity: 1; }
                    100% { transform: scale(0.95); opacity: 0.5; }
                }
            `}</style>
        </div>
    );
};

export default AIPanel;
