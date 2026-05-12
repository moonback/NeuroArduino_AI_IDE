import { Code, Eye, EyeOff, Globe, Info, Key, Palette, RotateCcw, Save, Search, X, Zap } from 'lucide-react';
import { useState } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const Settings = ({ onClose }) => {
    const { t, i18n } = useTranslation();
    
    // Settings State
    const [settings, setSettings] = useState({
        language: i18n.language || 'en',
        theme: localStorage.getItem('theme') || 'dark',
        fontSize: parseInt(localStorage.getItem('fontSize')) || 14,
        tabSize: parseInt(localStorage.getItem('tabSize')) || 2,
        autoSave: localStorage.getItem('autoSave') === 'true',
        autoCompile: localStorage.getItem('autoCompile') === 'true',
        lineNumbers: localStorage.getItem('lineNumbers') !== 'false',
        minimap: localStorage.getItem('minimap') === 'true',
        wordWrap: localStorage.getItem('wordWrap') === 'true',
        // Code Analysis Settings
        autoAnalysis: localStorage.getItem('autoAnalysis') !== 'false', // Default true
        analysisErrors: localStorage.getItem('analysisErrors') !== 'false',
        analysisWarnings: localStorage.getItem('analysisWarnings') !== 'false',
        analysisSuggestions: localStorage.getItem('analysisSuggestions') !== 'false',
        analysisOptimizations: localStorage.getItem('analysisOptimizations') !== 'false',
        memoryThreshold: parseInt(localStorage.getItem('memoryThreshold')) || 50,
        targetBoard: localStorage.getItem('targetBoard') || 'arduino:avr:uno',
    });

    const [activeTab, setActiveTab] = useState('general');
    const [hasChanges, setHasChanges] = useState(false);

    // API Keys state (stored separately, never fully exposed)
    const [apiKeys, setApiKeys] = useState({
        openrouterKey: localStorage.getItem('openrouter_key_set') === 'true' ? '••••••••••••••••••••••••••••••••' : '',
        geminiKey: localStorage.getItem('gemini_key_set') === 'true' ? '••••••••••••••••••••••••••••••••' : '',
    });
    const [showKeys, setShowKeys] = useState({ openrouter: false, gemini: false });
    const [keyStatus, setKeyStatus] = useState({ message: '', type: '' });
    const [savingKeys, setSavingKeys] = useState(false);

    const handleChange = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: value }));
        setHasChanges(true);
    };

    const handleSave = async () => {
        // Save settings to localStorage
        Object.keys(settings).forEach(key => {
            localStorage.setItem(key, settings[key].toString());
        });

        // Apply language change
        if (settings.language !== i18n.language) {
            i18n.changeLanguage(settings.language);
        }

        // Apply theme
        document.documentElement.setAttribute('data-theme', settings.theme);

        setHasChanges(false);
        alert(t('settingsSaved') || 'Settings saved successfully!');
    };

    const handleSaveKeys = async () => {
        // Don't send masked placeholder values
        const keysToSave = {};
        if (apiKeys.openrouterKey && !apiKeys.openrouterKey.startsWith('•')) {
            keysToSave.openrouter_api_key = apiKeys.openrouterKey.trim();
        }
        if (apiKeys.geminiKey && !apiKeys.geminiKey.startsWith('•')) {
            keysToSave.gemini_api_key = apiKeys.geminiKey.trim();
        }

        if (Object.keys(keysToSave).length === 0) {
            setKeyStatus({ message: 'No new keys to save.', type: 'info' });
            return;
        }

        setSavingKeys(true);
        setKeyStatus({ message: '', type: '' });

        try {
            await axios.post('http://localhost:8001/api/keys', keysToSave);
            // Mark as saved in localStorage (without storing actual key)
            if (keysToSave.openrouter_api_key) localStorage.setItem('openrouter_key_set', 'true');
            if (keysToSave.gemini_api_key) localStorage.setItem('gemini_key_set', 'true');
            setKeyStatus({ message: '✅ API keys saved and applied successfully! Restart backend to use new keys.', type: 'success' });
            // Mask keys after save
            setApiKeys(prev => ({
                openrouterKey: keysToSave.openrouter_api_key ? '••••••••••••••••••••••••••••••••' : prev.openrouterKey,
                geminiKey: keysToSave.gemini_api_key ? '••••••••••••••••••••••••••••••••' : prev.geminiKey,
            }));
        } catch (err) {
            setKeyStatus({ message: `❌ Failed to save keys: ${err.message}`, type: 'error' });
        }
        setSavingKeys(false);
    };

    const handleReset = () => {
        if (window.confirm(t('confirmReset') || 'Reset all settings to default?')) {
            const defaults = {
                language: 'en',
                theme: 'dark',
                fontSize: 14,
                tabSize: 2,
                autoSave: false,
                autoCompile: false,
                lineNumbers: true,
                minimap: false,
                wordWrap: true,
                // Code Analysis Defaults
                autoAnalysis: true,
                analysisErrors: true,
                analysisWarnings: true,
                analysisSuggestions: true,
                analysisOptimizations: true,
                memoryThreshold: 50,
                targetBoard: 'arduino:avr:uno',
            };
            setSettings(defaults);
            setHasChanges(true);
        }
    };

    return (
        <div className="settings-overlay">
            <div className="settings-modal">
                {/* Header */}
                <div className="settings-header">
                    <div className="settings-title">
                        <Zap size={20} className="settings-icon" />
                        <h2>{t('settings') || 'Settings'}</h2>
                    </div>
                    <button onClick={onClose} className="settings-close-btn">
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="settings-content">
                    {/* Sidebar Tabs */}
                    <div className="settings-sidebar">
                        <button
                            className={`settings-tab ${activeTab === 'general' ? 'settings-tab-active' : ''}`}
                            onClick={() => setActiveTab('general')}
                        >
                            <Globe size={16} />
                            <span>{t('general') || 'General'}</span>
                        </button>
                        <button
                            className={`settings-tab ${activeTab === 'editor' ? 'settings-tab-active' : ''}`}
                            onClick={() => setActiveTab('editor')}
                        >
                            <Code size={16} />
                            <span>{t('editor') || 'Editor'}</span>
                        </button>
                        <button
                            className={`settings-tab ${activeTab === 'analysis' ? 'settings-tab-active' : ''}`}
                            onClick={() => setActiveTab('analysis')}
                        >
                            <Search size={16} />
                            <span>{t('codeAnalysis') || 'Code Analysis'}</span>
                        </button>
                        <button
                            className={`settings-tab ${activeTab === 'apikeys' ? 'settings-tab-active' : ''}`}
                            onClick={() => setActiveTab('apikeys')}
                        >
                            <Key size={16} />
                            <span>AI Keys</span>
                        </button>
                        <button
                            className={`settings-tab ${activeTab === 'appearance' ? 'settings-tab-active' : ''}`}
                            onClick={() => setActiveTab('appearance')}
                        >
                            <Palette size={16} />
                            <span>{t('appearance') || 'Appearance'}</span>
                        </button>
                        <button
                            className={`settings-tab ${activeTab === 'about' ? 'settings-tab-active' : ''}`}
                            onClick={() => setActiveTab('about')}
                        >
                            <Info size={16} />
                            <span>{t('about') || 'About'}</span>
                        </button>
                    </div>

                    {/* Main Panel */}
                    <div className="settings-panel">
                        {/* General Tab */}
                        {activeTab === 'general' && (
                            <div className="settings-section">
                                <h3 className="settings-section-title">{t('generalSettings') || 'General Settings'}</h3>
                                
                                {/* Language */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            <Globe size={16} />
                                            {t('language') || 'Language'}
                                        </label>
                                        <p className="settings-description">
                                            {t('languageDescription') || 'Choose your preferred language'}
                                        </p>
                                    </div>
                                    <select
                                        value={settings.language}
                                        onChange={(e) => handleChange('language', e.target.value)}
                                        className="settings-select"
                                    >
                                        <option value="en">English</option>
                                        <option value="fr">Français</option>
                                    </select>
                                </div>

                                {/* Auto Save */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('autoSave') || 'Auto Save'}
                                        </label>
                                        <p className="settings-description">
                                            {t('autoSaveDescription') || 'Automatically save files after changes'}
                                        </p>
                                    </div>
                                    <label className="settings-toggle">
                                        <input
                                            type="checkbox"
                                            checked={settings.autoSave}
                                            onChange={(e) => handleChange('autoSave', e.target.checked)}
                                        />
                                        <span className="settings-toggle-slider"></span>
                                    </label>
                                </div>

                                {/* Auto Compile */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('autoCompile') || 'Auto Compile'}
                                        </label>
                                        <p className="settings-description">
                                            {t('autoCompileDescription') || 'Compile code automatically on save'}
                                        </p>
                                    </div>
                                    <label className="settings-toggle">
                                        <input
                                            type="checkbox"
                                            checked={settings.autoCompile}
                                            onChange={(e) => handleChange('autoCompile', e.target.checked)}
                                        />
                                        <span className="settings-toggle-slider"></span>
                                    </label>
                                </div>
                            </div>
                        )}

                        {/* Editor Tab */}
                        {activeTab === 'editor' && (
                            <div className="settings-section">
                                <h3 className="settings-section-title">{t('editorSettings') || 'Editor Settings'}</h3>
                                
                                {/* Font Size */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('fontSize') || 'Font Size'}
                                        </label>
                                        <p className="settings-description">
                                            {t('fontSizeDescription') || 'Editor font size in pixels'}
                                        </p>
                                    </div>
                                    <div className="settings-number-input">
                                        <input
                                            type="number"
                                            min="10"
                                            max="24"
                                            value={settings.fontSize}
                                            onChange={(e) => handleChange('fontSize', parseInt(e.target.value))}
                                            className="settings-input"
                                        />
                                        <span className="settings-unit">px</span>
                                    </div>
                                </div>

                                {/* Tab Size */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('tabSize') || 'Tab Size'}
                                        </label>
                                        <p className="settings-description">
                                            {t('tabSizeDescription') || 'Number of spaces per tab'}
                                        </p>
                                    </div>
                                    <select
                                        value={settings.tabSize}
                                        onChange={(e) => handleChange('tabSize', parseInt(e.target.value))}
                                        className="settings-select"
                                    >
                                        <option value="2">2 spaces</option>
                                        <option value="4">4 spaces</option>
                                        <option value="8">8 spaces</option>
                                    </select>
                                </div>

                                {/* Line Numbers */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('lineNumbers') || 'Line Numbers'}
                                        </label>
                                        <p className="settings-description">
                                            {t('lineNumbersDescription') || 'Show line numbers in editor'}
                                        </p>
                                    </div>
                                    <label className="settings-toggle">
                                        <input
                                            type="checkbox"
                                            checked={settings.lineNumbers}
                                            onChange={(e) => handleChange('lineNumbers', e.target.checked)}
                                        />
                                        <span className="settings-toggle-slider"></span>
                                    </label>
                                </div>

                                {/* Word Wrap */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('wordWrap') || 'Word Wrap'}
                                        </label>
                                        <p className="settings-description">
                                            {t('wordWrapDescription') || 'Wrap long lines in editor'}
                                        </p>
                                    </div>
                                    <label className="settings-toggle">
                                        <input
                                            type="checkbox"
                                            checked={settings.wordWrap}
                                            onChange={(e) => handleChange('wordWrap', e.target.checked)}
                                        />
                                        <span className="settings-toggle-slider"></span>
                                    </label>
                                </div>
                            </div>
                        )}

                        {/* Code Analysis Tab */}
                        {activeTab === 'analysis' && (
                            <div className="settings-section">
                                <h3 className="settings-section-title">{t('codeAnalysisSettings') || 'Code Analysis Settings'}</h3>
                                
                                {/* Automatic Analysis */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('automaticAnalysis') || 'Automatic Analysis'}
                                        </label>
                                        <p className="settings-description">
                                            {t('automaticAnalysisDescription') || 'Automatically analyze code when files are saved or opened'}
                                        </p>
                                    </div>
                                    <label className="settings-toggle">
                                        <input
                                            type="checkbox"
                                            checked={settings.autoAnalysis}
                                            onChange={(e) => handleChange('autoAnalysis', e.target.checked)}
                                        />
                                        <span className="settings-toggle-slider"></span>
                                    </label>
                                </div>

                                {/* Check Categories */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('checkCategories') || 'Check Categories'}
                                        </label>
                                        <p className="settings-description">
                                            {t('checkCategoriesDescription') || 'Select which types of issues to detect'}
                                        </p>
                                    </div>
                                    <div className="settings-checkbox-group">
                                        <label className="settings-checkbox">
                                            <input
                                                type="checkbox"
                                                checked={settings.analysisErrors}
                                                onChange={(e) => handleChange('analysisErrors', e.target.checked)}
                                            />
                                            <span>{t('errors') || 'Errors'}</span>
                                        </label>
                                        <label className="settings-checkbox">
                                            <input
                                                type="checkbox"
                                                checked={settings.analysisWarnings}
                                                onChange={(e) => handleChange('analysisWarnings', e.target.checked)}
                                            />
                                            <span>{t('warnings') || 'Warnings'}</span>
                                        </label>
                                        <label className="settings-checkbox">
                                            <input
                                                type="checkbox"
                                                checked={settings.analysisSuggestions}
                                                onChange={(e) => handleChange('analysisSuggestions', e.target.checked)}
                                            />
                                            <span>{t('suggestions') || 'Suggestions'}</span>
                                        </label>
                                        <label className="settings-checkbox">
                                            <input
                                                type="checkbox"
                                                checked={settings.analysisOptimizations}
                                                onChange={(e) => handleChange('analysisOptimizations', e.target.checked)}
                                            />
                                            <span>{t('optimizations') || 'Optimizations'}</span>
                                        </label>
                                    </div>
                                </div>

                                {/* Memory Threshold */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('memoryThreshold') || 'Memory Usage Warning Threshold'}
                                        </label>
                                        <p className="settings-description">
                                            {t('memoryThresholdDescription') || 'Warn when global variables exceed this percentage of RAM'}
                                        </p>
                                    </div>
                                    <div className="settings-slider-container">
                                        <input
                                            type="range"
                                            min="25"
                                            max="90"
                                            step="5"
                                            value={settings.memoryThreshold}
                                            onChange={(e) => handleChange('memoryThreshold', parseInt(e.target.value))}
                                            className="settings-slider"
                                        />
                                        <span className="settings-slider-value">{settings.memoryThreshold}%</span>
                                    </div>
                                </div>

                                {/* Target Board */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('targetBoard') || 'Target Board'}
                                        </label>
                                        <p className="settings-description">
                                            {t('targetBoardDescription') || 'Board type for context-aware analysis'}
                                        </p>
                                    </div>
                                    <select
                                        value={settings.targetBoard}
                                        onChange={(e) => handleChange('targetBoard', e.target.value)}
                                        className="settings-select"
                                    >
                                        <option value="arduino:avr:uno">Arduino Uno</option>
                                        <option value="arduino:avr:nano">Arduino Nano</option>
                                        <option value="arduino:avr:mega">Arduino Mega</option>
                                        <option value="esp32:esp32:esp32">ESP32</option>
                                        <option value="esp8266:esp8266:generic">ESP8266</option>
                                    </select>
                                </div>
                            </div>
                        )}

                        {/* AI Keys Tab */}
                        {activeTab === 'apikeys' && (
                            <div className="settings-section">
                                <h3 className="settings-section-title">
                                    <Key size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
                                    AI Provider API Keys
                                </h3>
                                <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '20px', lineHeight: 1.5 }}>
                                    Enter your own API keys for OpenRouter and/or Google Gemini. Keys are saved securely to the backend <code>.env</code> file and never exposed in the UI.
                                </p>

                                {/* OpenRouter Key */}
                                <div className="settings-item" style={{ flexDirection: 'column', alignItems: 'stretch', gap: '12px' }}>
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            🔑 OpenRouter API Key
                                        </label>
                                        <p className="settings-description">
                                            Get your free key at{' '}
                                            <a href="https://openrouter.ai/keys" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', textDecoration: 'underline' }}>
                                                openrouter.ai/keys
                                            </a>
                                            {' '}— enables Llama 3.1, Gemma and many other models.
                                        </p>
                                    </div>
                                    <div style={{ position: 'relative', display: 'flex', gap: '8px', alignItems: 'center' }}>
                                        <input
                                            id="openrouter-key-input"
                                            type={showKeys.openrouter ? 'text' : 'password'}
                                            value={apiKeys.openrouterKey}
                                            onChange={e => { setApiKeys(prev => ({ ...prev, openrouterKey: e.target.value })); setKeyStatus({ message: '', type: '' }); }}
                                            placeholder="sk-or-v1-xxxxxxxxxxxxxxxx"
                                            className="settings-input"
                                            style={{ flex: 1, fontFamily: 'monospace', letterSpacing: apiKeys.openrouterKey.startsWith('•') ? '2px' : 'normal' }}
                                            autoComplete="off"
                                            spellCheck={false}
                                        />
                                        <button
                                            onClick={() => setShowKeys(prev => ({ ...prev, openrouter: !prev.openrouter }))}
                                            className="settings-btn settings-btn-secondary"
                                            style={{ padding: '6px 10px', minWidth: 0 }}
                                            title={showKeys.openrouter ? 'Hide key' : 'Show key'}
                                        >
                                            {showKeys.openrouter ? <EyeOff size={16} /> : <Eye size={16} />}
                                        </button>
                                        {localStorage.getItem('openrouter_key_set') === 'true' && (
                                            <span style={{ color: '#4ade80', fontSize: '12px', whiteSpace: 'nowrap' }}>✓ Saved</span>
                                        )}
                                    </div>
                                </div>

                                {/* Gemini Key */}
                                <div className="settings-item" style={{ flexDirection: 'column', alignItems: 'stretch', gap: '12px', marginTop: '16px' }}>
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            🤖 Google Gemini API Key
                                        </label>
                                        <p className="settings-description">
                                            Get your free key at{' '}
                                            <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', textDecoration: 'underline' }}>
                                                aistudio.google.com/apikey
                                            </a>
                                            {' '}— enables Gemini 1.5 Flash with vision capabilities.
                                        </p>
                                    </div>
                                    <div style={{ position: 'relative', display: 'flex', gap: '8px', alignItems: 'center' }}>
                                        <input
                                            id="gemini-key-input"
                                            type={showKeys.gemini ? 'text' : 'password'}
                                            value={apiKeys.geminiKey}
                                            onChange={e => { setApiKeys(prev => ({ ...prev, geminiKey: e.target.value })); setKeyStatus({ message: '', type: '' }); }}
                                            placeholder="AIzaSy-xxxxxxxxxxxxxxxx"
                                            className="settings-input"
                                            style={{ flex: 1, fontFamily: 'monospace', letterSpacing: apiKeys.geminiKey.startsWith('•') ? '2px' : 'normal' }}
                                            autoComplete="off"
                                            spellCheck={false}
                                        />
                                        <button
                                            onClick={() => setShowKeys(prev => ({ ...prev, gemini: !prev.gemini }))}
                                            className="settings-btn settings-btn-secondary"
                                            style={{ padding: '6px 10px', minWidth: 0 }}
                                            title={showKeys.gemini ? 'Hide key' : 'Show key'}
                                        >
                                            {showKeys.gemini ? <EyeOff size={16} /> : <Eye size={16} />}
                                        </button>
                                        {localStorage.getItem('gemini_key_set') === 'true' && (
                                            <span style={{ color: '#4ade80', fontSize: '12px', whiteSpace: 'nowrap' }}>✓ Saved</span>
                                        )}
                                    </div>
                                </div>

                                {/* Status message */}
                                {keyStatus.message && (
                                    <div style={{
                                        marginTop: '16px',
                                        padding: '10px 14px',
                                        borderRadius: '8px',
                                        fontSize: '13px',
                                        background: keyStatus.type === 'success' ? 'rgba(74,222,128,0.12)' : keyStatus.type === 'error' ? 'rgba(248,113,113,0.12)' : 'rgba(148,163,184,0.1)',
                                        border: `1px solid ${keyStatus.type === 'success' ? '#4ade80' : keyStatus.type === 'error' ? '#f87171' : '#94a3b8'}44`,
                                        color: keyStatus.type === 'success' ? '#4ade80' : keyStatus.type === 'error' ? '#f87171' : '#94a3b8',
                                    }}>
                                        {keyStatus.message}
                                    </div>
                                )}

                                {/* Save Keys Button */}
                                <button
                                    onClick={handleSaveKeys}
                                    disabled={savingKeys}
                                    className="settings-btn settings-btn-primary"
                                    style={{ marginTop: '20px', width: '100%', justifyContent: 'center', opacity: savingKeys ? 0.7 : 1 }}
                                >
                                    <Key size={16} />
                                    {savingKeys ? 'Saving...' : 'Save API Keys'}
                                </button>
                            </div>
                        )}

                        {/* Appearance Tab */}
                        {activeTab === 'appearance' && (
                            <div className="settings-section">
                                <h3 className="settings-section-title">{t('appearanceSettings') || 'Appearance Settings'}</h3>
                                
                                {/* Theme */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            <Palette size={16} />
                                            {t('theme') || 'Theme'}
                                        </label>
                                        <p className="settings-description">
                                            {t('themeDescription') || 'Choose your color theme'}
                                        </p>
                                    </div>
                                    <select
                                        value={settings.theme}
                                        onChange={(e) => handleChange('theme', e.target.value)}
                                        className="settings-select"
                                    >
                                        <option value="dark">Dark</option>
                                        <option value="light">Light (Coming Soon)</option>
                                        <option value="high-contrast">High Contrast (Coming Soon)</option>
                                    </select>
                                </div>

                                {/* Minimap */}
                                <div className="settings-item">
                                    <div className="settings-item-info">
                                        <label className="settings-label">
                                            {t('minimap') || 'Minimap'}
                                        </label>
                                        <p className="settings-description">
                                            {t('minimapDescription') || 'Show code minimap in editor'}
                                        </p>
                                    </div>
                                    <label className="settings-toggle">
                                        <input
                                            type="checkbox"
                                            checked={settings.minimap}
                                            onChange={(e) => handleChange('minimap', e.target.checked)}
                                        />
                                        <span className="settings-toggle-slider"></span>
                                    </label>
                                </div>
                            </div>
                        )}

                        {/* About Tab */}
                        {activeTab === 'about' && (
                            <div className="settings-section">
                                <h3 className="settings-section-title">{t('about') || 'About'}</h3>
                                
                                <div className="settings-about">
                                    <div className="settings-about-logo">
                                        <Zap size={48} className="text-accent" />
                                    </div>
                                    <h2 className="settings-about-title">AI NeuroArduino IDE</h2>
                                    <p className="settings-about-version">Version 2.0.0</p>
                                    <p className="settings-about-description">
                                        {t('aboutDescription') || 'An intelligent Arduino IDE powered by AI assistants for faster and smarter development.'}
                                    </p>
                                    
                                    <div className="settings-about-info">
                                        <div className="settings-about-item">
                                            <strong>Backend:</strong> Python + FastAPI + Uvicorn
                                        </div>
                                        <div className="settings-about-item">
                                            <strong>Frontend:</strong> React + Vite + Electron
                                        </div>
                                        <div className="settings-about-item">
                                            <strong>AI Models:</strong> Groq (Llama 3) + Gemini 2.5
                                        </div>
                                        <div className="settings-about-item">
                                            <strong>Arduino CLI:</strong> Integrated
                                        </div>
                                    </div>

                                    <div className="settings-about-links">
                                        <a href="#" className="settings-link">Documentation</a>
                                        <a href="#" className="settings-link">GitHub Repository</a>
                                        <a href="#" className="settings-link">Report Issue</a>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="settings-footer">
                    <button onClick={handleReset} className="settings-btn settings-btn-secondary">
                        <RotateCcw size={16} />
                        {t('resetToDefaults') || 'Reset to Defaults'}
                    </button>
                    <div className="settings-footer-actions">
                        <button onClick={onClose} className="settings-btn settings-btn-cancel">
                            {t('cancel') || 'Cancel'}
                        </button>
                        <button 
                            onClick={handleSave} 
                            className={`settings-btn settings-btn-primary ${hasChanges ? 'settings-btn-highlight' : ''}`}
                            disabled={!hasChanges}
                        >
                            <Save size={16} />
                            {t('saveSettings') || 'Save Settings'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Settings;
