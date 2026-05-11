import React, { useState, useRef, useCallback } from 'react';
import { Camera, Upload, X, Sparkles, Eye, Cpu, Zap, RefreshCw, Copy, Check, ImagePlus } from 'lucide-react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const VisionPanel = ({ onApplyCode, onClose }) => {
    const { t } = useTranslation();
    const [image, setImage] = useState(null); // { src: dataURL, file: File }
    const [preview, setPreview] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState(null); // { code, explanation, components }
    const [error, setError] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [additionalPrompt, setAdditionalPrompt] = useState('');
    const [copied, setCopied] = useState(false);
    const fileInputRef = useRef(null);
    const dropZoneRef = useRef(null);

    const handleFile = useCallback((file) => {
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            setError(t('errorFileType'));
            return;
        }
        if (file.size > 20 * 1024 * 1024) {
            setError(t('errorFileSize'));
            return;
        }

        setError(null);
        setResult(null);

        const reader = new FileReader();
        reader.onload = (e) => {
            setPreview(e.target.result);
            setImage({ src: e.target.result, file });
        };
        reader.readAsDataURL(file);
    }, []);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }, [handleFile]);

    const handleFileSelect = (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    };

    const clearImage = () => {
        setImage(null);
        setPreview(null);
        setResult(null);
        setError(null);
        setAdditionalPrompt('');
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const analyzeImage = async () => {
        if (!image) return;

        setAnalyzing(true);
        setError(null);
        setResult(null);

        try {
            const res = await axios.post('http://localhost:8001/ai/vision', {
                image_data: image.src,
                prompt: additionalPrompt || '',
                board: 'arduino:avr:uno'
            });

            setResult({
                code: res.data.code,
                explanation: res.data.explanation,
                components: res.data.components || []
            });
        } catch (err) {
            const msg = err.response?.data?.detail || t('errorVision');
            setError(msg);
        } finally {
            setAnalyzing(false);
        }
    };

    const handleCopyCode = () => {
        if (result?.code) {
            navigator.clipboard.writeText(result.code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div style={styles.overlay}>
            <div style={styles.panel}>
                {/* Header */}
                <div style={styles.header}>
                    <div style={styles.headerTitle}>
                        <div style={styles.iconBadge}>
                            <Camera size={16} />
                        </div>
                        <div>
                            <div style={styles.title}>{t('visionToWire')}</div>
                            <div style={styles.subtitle}>{t('uploadPhotoGetCode')}</div>
                        </div>
                    </div>
                    <button onClick={onClose} style={styles.closeBtn}>
                        <X size={18} />
                    </button>
                </div>

                <div style={styles.body}>
                    {/* Upload Area */}
                    {!preview ? (
                        <div
                            ref={dropZoneRef}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                            style={{
                                ...styles.dropZone,
                                ...(isDragging ? styles.dropZoneActive : {})
                            }}
                        >
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileSelect}
                                style={{ display: 'none' }}
                            />
                            <div style={styles.dropIcon}>
                                <ImagePlus size={40} strokeWidth={1.5} />
                            </div>
                            <div style={styles.dropTitle}>
                                {isDragging ? t('dropImageHere') : t('uploadWiringPhoto')}
                            </div>
                            <div style={styles.dropHint}>
                                {t('dragDropClick')}
                            </div>
                            <div style={styles.dropFormats}>
                                JPG, PNG, WebP • {t('maxSize')}
                            </div>
                        </div>
                    ) : (
                        /* Preview + Controls */
                        <div style={styles.previewSection}>
                            <div style={styles.previewContainer}>
                                <img src={preview} alt="Wiring preview" style={styles.previewImage} />
                                <button onClick={clearImage} style={styles.removeImageBtn} title="Remove image">
                                    <X size={14} />
                                </button>
                                {result && (
                                    <div style={styles.analyzedBadge}>
                                        <Check size={12} /> {t('analyzed')}
                                    </div>
                                )}
                            </div>

                            {/* Additional prompt */}
                            <div style={styles.promptRow}>
                                <input
                                    value={additionalPrompt}
                                    onChange={(e) => setAdditionalPrompt(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && !analyzing && analyzeImage()}
                                    placeholder={t('optionalDescribe')}
                                    style={styles.promptInput}
                                />
                            </div>

                            {/* Analyze Button */}
                            <button
                                onClick={analyzeImage}
                                disabled={analyzing}
                                style={{
                                    ...styles.analyzeBtn,
                                    ...(analyzing ? styles.analyzeBtnDisabled : {})
                                }}
                            >
                                {analyzing ? (
                                    <>
                                        <RefreshCw size={16} className="vision-spin" />
                                        <span>{t('analyzingWiring')}</span>
                                    </>
                                ) : (
                                    <>
                                        <Eye size={16} />
                                        <span>{result ? t('reAnalyze') : t('analyzeWiring')}</span>
                                    </>
                                )}
                            </button>
                        </div>
                    )}

                    {/* Error */}
                    {error && (
                        <div style={styles.errorBox}>
                            <Zap size={14} />
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Analyzing Animation */}
                    {analyzing && (
                        <div style={styles.analyzingBox}>
                            <div style={styles.analyzingDots}>
                                <div className="vision-dot" style={{ ...styles.dot, animationDelay: '0ms' }}></div>
                                <div className="vision-dot" style={{ ...styles.dot, animationDelay: '150ms' }}></div>
                                <div className="vision-dot" style={{ ...styles.dot, animationDelay: '300ms' }}></div>
                            </div>
                            <div style={styles.analyzingSteps}>
                                <div style={styles.stepItem}>
                                    <Sparkles size={12} color="var(--accent)" />
                                    <span>{t('identifyingComponents')}</span>
                                </div>
                                <div style={styles.stepItem}>
                                    <Cpu size={12} color="#a78bfa" />
                                    <span>{t('tracingConnections')}</span>
                                </div>
                                <div style={styles.stepItem}>
                                    <Zap size={12} color="#fbbf24" />
                                    <span>{t('generatingCode')}</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Results */}
                    {result && (
                        <div style={styles.resultSection}>
                            {/* Components Detected */}
                            {result.components && result.components.length > 0 && (
                                <div style={styles.componentsBox}>
                                    <div style={styles.sectionLabel}>
                                        <Cpu size={13} />
                                        {t('componentsDetected')}
                                    </div>
                                    <div style={styles.componentsList}>
                                        {result.components.map((comp, i) => (
                                            <span key={i} style={styles.componentTag}>{comp}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Explanation */}
                            <div style={styles.explanationBox}>
                                <div style={styles.sectionLabel}>
                                    <Sparkles size={13} />
                                    {t('analysis')}
                                </div>
                                <div style={styles.explanationText}>{result.explanation}</div>
                            </div>

                            {/* Generated Code */}
                            <div style={styles.codeBox}>
                                <div style={styles.codeHeader}>
                                    <div style={styles.sectionLabel}>
                                        <Zap size={13} />
                                        {t('generatedCode')}
                                    </div>
                                    <div style={{ display: 'flex', gap: '4px' }}>
                                        <button onClick={handleCopyCode} style={styles.codeActionBtn} title="Copy">
                                            {copied ? <Check size={13} color="#2ecc71" /> : <Copy size={13} />}
                                        </button>
                                    </div>
                                </div>
                                <pre style={styles.codeContent}>
                                    <code>{result.code}</code>
                                </pre>
                                <button
                                    onClick={() => onApplyCode(result.code)}
                                    style={styles.applyBtn}
                                >
                                    <Sparkles size={14} />
                                    {t('applyToEditor')}
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Animations */}
                <style>{`
                    .vision-spin {
                        animation: vision-spin 1s linear infinite;
                    }
                    @keyframes vision-spin {
                        from { transform: rotate(0deg); }
                        to { transform: rotate(360deg); }
                    }
                    .vision-dot {
                        animation: vision-bounce 1.2s ease-in-out infinite;
                    }
                    @keyframes vision-bounce {
                        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
                        40% { transform: scale(1); opacity: 1; }
                    }
                    @keyframes vision-glow-pulse {
                        0%, 100% { box-shadow: 0 0 20px rgba(0, 229, 255, 0.1); }
                        50% { box-shadow: 0 0 40px rgba(0, 229, 255, 0.25); }
                    }
                    @keyframes vision-border-pulse {
                        0%, 100% { border-color: var(--accent); }
                        50% { border-color: #a78bfa; }
                    }
                `}</style>
            </div>
        </div>
    );
};

const styles = {
    overlay: {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        animation: 'fadeIn 0.2s ease',
    },
    panel: {
        width: '520px',
        maxHeight: '85vh',
        background: 'linear-gradient(145deg, #131920 0%, #0d1117 100%)',
        border: '1px solid #30363d',
        borderRadius: '16px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxShadow: '0 25px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 229, 255, 0.05)',
    },
    header: {
        padding: '16px 20px',
        borderBottom: '1px solid #30363d',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(22, 27, 34, 0.8)',
    },
    headerTitle: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
    },
    iconBadge: {
        width: '36px',
        height: '36px',
        borderRadius: '10px',
        background: 'linear-gradient(135deg, #00e5ff 0%, #a78bfa 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#000',
        flexShrink: 0,
    },
    title: {
        fontSize: '15px',
        fontWeight: 700,
        color: '#e6edf3',
        letterSpacing: '0.3px',
    },
    subtitle: {
        fontSize: '11px',
        color: '#8b949e',
        marginTop: '1px',
    },
    closeBtn: {
        background: 'none',
        border: 'none',
        color: '#8b949e',
        cursor: 'pointer',
        padding: '6px',
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.15s',
    },
    body: {
        padding: '16px 20px',
        overflowY: 'auto',
        flexGrow: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
    },

    // Drop Zone
    dropZone: {
        border: '2px dashed #30363d',
        borderRadius: '12px',
        padding: '40px 20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '10px',
        cursor: 'pointer',
        transition: 'all 0.25s ease',
        background: 'rgba(13, 17, 23, 0.6)',
    },
    dropZoneActive: {
        borderColor: 'var(--accent)',
        background: 'rgba(0, 229, 255, 0.05)',
        boxShadow: '0 0 30px rgba(0, 229, 255, 0.1)',
    },
    dropIcon: {
        color: '#30363d',
        marginBottom: '4px',
    },
    dropTitle: {
        fontSize: '15px',
        fontWeight: 600,
        color: '#e6edf3',
    },
    dropHint: {
        fontSize: '13px',
        color: '#8b949e',
    },
    dropFormats: {
        fontSize: '11px',
        color: '#484f58',
        marginTop: '4px',
    },

    // Preview
    previewSection: {
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
    },
    previewContainer: {
        position: 'relative',
        borderRadius: '10px',
        overflow: 'hidden',
        border: '1px solid #30363d',
        background: '#0d1117',
    },
    previewImage: {
        width: '100%',
        maxHeight: '220px',
        objectFit: 'contain',
        display: 'block',
        background: '#0a0e13',
    },
    removeImageBtn: {
        position: 'absolute',
        top: '8px',
        right: '8px',
        width: '28px',
        height: '28px',
        borderRadius: '8px',
        background: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(4px)',
        border: '1px solid rgba(255,255,255,0.1)',
        color: '#fff',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.15s',
    },
    analyzedBadge: {
        position: 'absolute',
        bottom: '8px',
        left: '8px',
        background: 'rgba(46, 204, 113, 0.15)',
        border: '1px solid rgba(46, 204, 113, 0.3)',
        color: '#2ecc71',
        fontSize: '11px',
        fontWeight: 600,
        padding: '3px 8px',
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
    },
    promptRow: {
        display: 'flex',
        gap: '6px',
    },
    promptInput: {
        flex: 1,
        background: '#0d1117',
        border: '1px solid #30363d',
        borderRadius: '8px',
        padding: '9px 12px',
        color: '#e6edf3',
        fontSize: '13px',
        outline: 'none',
        transition: 'border-color 0.2s',
        fontFamily: 'inherit',
    },

    // Analyze Button
    analyzeBtn: {
        width: '100%',
        padding: '11px',
        borderRadius: '10px',
        background: 'linear-gradient(135deg, #00e5ff 0%, #00b4d8 100%)',
        color: '#000',
        fontWeight: 700,
        fontSize: '14px',
        border: 'none',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        transition: 'all 0.2s',
        boxShadow: '0 4px 15px rgba(0, 229, 255, 0.2)',
    },
    analyzeBtnDisabled: {
        opacity: 0.7,
        cursor: 'not-allowed',
        boxShadow: 'none',
    },

    // Error
    errorBox: {
        background: 'rgba(255, 71, 87, 0.08)',
        border: '1px solid rgba(255, 71, 87, 0.25)',
        borderRadius: '8px',
        padding: '10px 14px',
        color: '#ff6b7a',
        fontSize: '13px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '8px',
    },

    // Analyzing
    analyzingBox: {
        background: 'rgba(0, 229, 255, 0.04)',
        border: '1px solid rgba(0, 229, 255, 0.12)',
        borderRadius: '10px',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '16px',
        animation: 'vision-glow-pulse 2s ease infinite',
    },
    analyzingDots: {
        display: 'flex',
        gap: '8px',
    },
    dot: {
        width: '10px',
        height: '10px',
        borderRadius: '50%',
        background: 'var(--accent)',
    },
    analyzingSteps: {
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        width: '100%',
    },
    stepItem: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '12px',
        color: '#8b949e',
        paddingLeft: '20px',
    },

    // Results
    resultSection: {
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
    },
    componentsBox: {
        background: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '10px',
        padding: '12px 14px',
    },
    sectionLabel: {
        fontSize: '11px',
        fontWeight: 700,
        color: '#8b949e',
        textTransform: 'uppercase',
        letterSpacing: '0.8px',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        marginBottom: '8px',
    },
    componentsList: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '6px',
    },
    componentTag: {
        background: 'rgba(0, 229, 255, 0.08)',
        border: '1px solid rgba(0, 229, 255, 0.2)',
        color: '#00e5ff',
        fontSize: '12px',
        fontWeight: 500,
        padding: '3px 10px',
        borderRadius: '20px',
    },
    explanationBox: {
        background: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '10px',
        padding: '12px 14px',
    },
    explanationText: {
        fontSize: '13px',
        lineHeight: '1.6',
        color: '#c9d1d9',
    },
    codeBox: {
        background: '#0d1117',
        border: '1px solid #30363d',
        borderRadius: '10px',
        overflow: 'hidden',
    },
    codeHeader: {
        background: '#161b22',
        padding: '8px 14px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid #30363d',
    },
    codeActionBtn: {
        background: 'none',
        border: 'none',
        color: '#8b949e',
        cursor: 'pointer',
        padding: '4px',
        borderRadius: '4px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'color 0.15s',
    },
    codeContent: {
        padding: '12px 14px',
        fontSize: '12px',
        lineHeight: '1.5',
        fontFamily: "'JetBrains Mono', monospace",
        color: '#e6edf3',
        overflowX: 'auto',
        margin: 0,
        maxHeight: '200px',
        overflowY: 'auto',
    },
    applyBtn: {
        width: '100%',
        padding: '10px',
        background: 'linear-gradient(135deg, #00e5ff 0%, #00b4d8 100%)',
        color: '#000',
        fontWeight: 700,
        fontSize: '13px',
        border: 'none',
        borderTop: '1px solid #30363d',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
        transition: 'all 0.2s',
    },
};

export default VisionPanel;
