import React, { useState } from 'react';
import { X, Globe, Palette, Code, Zap, Info, Save, RotateCcw } from 'lucide-react';
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
    });

    const [activeTab, setActiveTab] = useState('general');
    const [hasChanges, setHasChanges] = useState(false);

    const handleChange = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: value }));
        setHasChanges(true);
    };

    const handleSave = () => {
        // Save to localStorage
        Object.keys(settings).forEach(key => {
            localStorage.setItem(key, settings[key].toString());
        });

        // Apply language change
        if (settings.language !== i18n.language) {
            i18n.changeLanguage(settings.language);
        }

        // Apply theme (if implemented)
        document.documentElement.setAttribute('data-theme', settings.theme);

        setHasChanges(false);
        
        // Show success message
        alert(t('settingsSaved') || 'Settings saved successfully!');
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
