import {
    AlertCircle, AlertTriangle,
    CheckCircle,
    ChevronDown, ChevronRight,
    Edit,
    File,
    FileText,
    FolderPlus,
    Lightbulb,
    Loader2,
    Search,
    Trash2,
    XCircle,
    Zap
} from 'lucide-react';
import React from 'react';

const ToolCallDisplay = ({ toolCall, toolResult, onOpenFile }) => {
    const [isExpanded, setIsExpanded] = React.useState(true);
    const [expandedCategories, setExpandedCategories] = React.useState({
        errors: true,
        warnings: true,
        suggestions: true,
        optimizations: true
    });
    
    const toggleCategory = (category) => {
        setExpandedCategories(prev => ({
            ...prev,
            [category]: !prev[category]
        }));
    };
    
    const getToolIcon = (toolName) => {
        switch (toolName) {
            case 'create_file':
                return <File size={14} />;
            case 'modify_file':
                return <Edit size={14} />;
            case 'delete_file':
                return <Trash2 size={14} />;
            case 'create_directory':
                return <FolderPlus size={14} />;
            case 'read_file':
                return <FileText size={14} />;
            case 'analyze_code':
                return <Search size={14} />;
            default:
                return <File size={14} />;
        }
    };
    
    const getToolColor = (toolName) => {
        switch (toolName) {
            case 'create_file':
            case 'create_directory':
                return '#2ecc71';
            case 'modify_file':
                return '#3498db';
            case 'delete_file':
                return '#e74c3c';
            case 'read_file':
                return '#9b59b6';
            case 'analyze_code':
                return '#f39c12';
            default:
                return '#95a5a6';
        }
    };
    
    const getStatusIcon = (status) => {
        if (!status) return <Loader2 size={14} className="animate-spin" />;
        if (status === 'success') return <CheckCircle size={14} color="#2ecc71" />;
        return <XCircle size={14} color="#e74c3c" />;
    };
    
    const formatToolName = (name) => {
        return name.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    };
    
    const getAnalysisTypeBadgeColor = (type) => {
        switch (type) {
            case 'full':
                return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            case 'quick':
                return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
            case 'security':
                return 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)';
            case 'performance':
                return 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)';
            default:
                return '#95a5a6';
        }
    };
    
    const getCategoryIcon = (category) => {
        switch (category) {
            case 'errors':
                return <AlertCircle size={14} />;
            case 'warnings':
                return <AlertTriangle size={14} />;
            case 'suggestions':
                return <Lightbulb size={14} />;
            case 'optimizations':
                return <Zap size={14} />;
            default:
                return <File size={14} />;
        }
    };
    
    const getCategoryColor = (category) => {
        switch (category) {
            case 'errors':
                return '#e74c3c';
            case 'warnings':
                return '#f39c12';
            case 'suggestions':
                return '#3498db';
            case 'optimizations':
                return '#2ecc71';
            default:
                return '#95a5a6';
        }
    };
    
    const renderFindingsCategory = (category, findings, isExpanded, toggleCategory) => {
        if (!findings || findings.length === 0) return null;
        
        const color = getCategoryColor(category);
        const icon = getCategoryIcon(category);
        
        return (
            <div key={category} style={styles.categoryContainer}>
                <div 
                    style={{...styles.categoryHeader, borderLeftColor: color}}
                    onClick={() => toggleCategory(category)}
                >
                    <div style={styles.categoryHeaderLeft}>
                        <button style={styles.categoryExpandBtn}>
                            {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                        </button>
                        <div style={{...styles.categoryIcon, color: color}}>
                            {icon}
                        </div>
                        <span style={styles.categoryTitle}>
                            {category.charAt(0).toUpperCase() + category.slice(1)}
                        </span>
                        <span style={{...styles.categoryCount, background: color}}>
                            {findings.length}
                        </span>
                    </div>
                </div>
                
                {isExpanded && (
                    <div style={styles.categoryBody}>
                        {findings.map((finding, index) => (
                            <div key={index} style={styles.findingItem}>
                                <div style={styles.findingHeader}>
                                    <span style={{...styles.findingLine, color: color}}>
                                        Line {finding.line}
                                    </span>
                                    {finding.category && (
                                        <span style={styles.findingCategory}>
                                            {finding.category}
                                        </span>
                                    )}
                                </div>
                                <div style={styles.findingMessage}>
                                    {finding.message}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    };
    
    return (
        <div style={styles.container}>
            {/* Header */}
            <div 
                style={styles.header}
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div style={styles.headerLeft}>
                    <button style={styles.expandBtn}>
                        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    </button>
                    <div 
                        style={{
                            ...styles.iconBadge,
                            background: getToolColor(toolCall.tool)
                        }}
                    >
                        {getToolIcon(toolCall.tool)}
                    </div>
                    <span style={styles.toolName}>
                        {formatToolName(toolCall.tool)}
                    </span>
                </div>
                <div style={styles.headerRight}>
                    {getStatusIcon(toolResult?.result?.status)}
                </div>
            </div>
            
            {/* Body (Expandable) */}
            {isExpanded && (
                <div style={styles.body}>
                    {/* Analysis-specific rendering */}
                    {toolCall.tool === 'analyze_code' && toolResult?.result?.status === 'success' ? (
                        <div style={styles.analysisContainer}>
                            {/* Analysis Info */}
                            <div style={styles.analysisInfo}>
                                <div style={styles.analysisInfoItem}>
                                    <span style={styles.analysisLabel}>File:</span>
                                    <span style={styles.analysisValue}>{toolResult.result.path}</span>
                                </div>
                                <div style={styles.analysisInfoItem}>
                                    <span style={styles.analysisLabel}>Type:</span>
                                    <span style={{
                                        ...styles.analysisBadge,
                                        background: getAnalysisTypeBadgeColor(toolResult.result.analysis_type)
                                    }}>
                                        {toolResult.result.analysis_type}
                                    </span>
                                </div>
                                <div style={styles.analysisInfoItem}>
                                    <span style={styles.analysisLabel}>Board:</span>
                                    <span style={styles.analysisValue}>{toolResult.result.board}</span>
                                </div>
                            </div>
                            
                            {/* Findings Summary */}
                            <div style={styles.findingsSummary}>
                                <div style={styles.summaryItem}>
                                    <AlertCircle size={14} color="#e74c3c" />
                                    <span style={styles.summaryLabel}>Errors:</span>
                                    <span style={styles.summaryCount}>{toolResult.result.summary.errors}</span>
                                </div>
                                <div style={styles.summaryItem}>
                                    <AlertTriangle size={14} color="#f39c12" />
                                    <span style={styles.summaryLabel}>Warnings:</span>
                                    <span style={styles.summaryCount}>{toolResult.result.summary.warnings}</span>
                                </div>
                                <div style={styles.summaryItem}>
                                    <Lightbulb size={14} color="#3498db" />
                                    <span style={styles.summaryLabel}>Suggestions:</span>
                                    <span style={styles.summaryCount}>{toolResult.result.summary.suggestions}</span>
                                </div>
                                <div style={styles.summaryItem}>
                                    <Zap size={14} color="#2ecc71" />
                                    <span style={styles.summaryLabel}>Optimizations:</span>
                                    <span style={styles.summaryCount}>{toolResult.result.summary.optimizations}</span>
                                </div>
                            </div>
                            
                            {/* Findings by Category */}
                            {renderFindingsCategory('errors', toolResult.result.results.errors, expandedCategories.errors, toggleCategory)}
                            {renderFindingsCategory('warnings', toolResult.result.results.warnings, expandedCategories.warnings, toggleCategory)}
                            {renderFindingsCategory('suggestions', toolResult.result.results.suggestions, expandedCategories.suggestions, toggleCategory)}
                            {renderFindingsCategory('optimizations', toolResult.result.results.optimizations, expandedCategories.optimizations, toggleCategory)}
                        </div>
                    ) : (
                        <>
                            {/* Parameters */}
                            <div style={styles.section}>
                                <div style={styles.sectionLabel}>Parameters</div>
                                <div style={styles.paramsList}>
                                    {Object.entries(toolCall.parameters).map(([key, value]) => (
                                        <div key={key} style={styles.param}>
                                            <span style={styles.paramKey}>{key}:</span>
                                            <span style={styles.paramValue}>
                                                {typeof value === 'string' && value.length > 100
                                                    ? value.substring(0, 100) + '...'
                                                    : String(value)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            
                            {/* Result */}
                            {toolResult && (
                                <div style={styles.section}>
                                    <div style={styles.sectionLabel}>Result</div>
                                    {toolResult.result.status === 'success' ? (
                                        <div style={styles.successResult}>
                                            <CheckCircle size={14} />
                                            <span>{toolResult.result.message || 'Operation completed successfully'}</span>
                                        </div>
                                    ) : (
                                        <div style={styles.errorResult}>
                                            <XCircle size={14} />
                                            <span>{toolResult.result.error || 'Operation failed'}</span>
                                        </div>
                                    )}
                                </div>
                            )}
                            
                            {/* Actions */}
                            {toolResult?.result?.status === 'success' && 
                             (toolCall.tool === 'create_file' || toolCall.tool === 'modify_file') && (
                                <div style={styles.actions}>
                                    <button 
                                        onClick={() => onOpenFile(toolCall.parameters.path)}
                                        style={styles.actionBtn}
                                    >
                                        <FileText size={12} />
                                        Open File
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

const styles = {
    container: {
        background: 'rgba(22, 27, 34, 0.6)',
        border: '1px solid #30363d',
        borderRadius: '8px',
        overflow: 'hidden',
        marginTop: '8px',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px 12px',
        cursor: 'pointer',
        transition: 'background 0.15s',
        ':hover': {
            background: 'rgba(22, 27, 34, 0.8)',
        }
    },
    headerLeft: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
    },
    headerRight: {
        display: 'flex',
        alignItems: 'center',
    },
    expandBtn: {
        background: 'none',
        border: 'none',
        color: '#8b949e',
        cursor: 'pointer',
        padding: '2px',
        display: 'flex',
        alignItems: 'center',
    },
    iconBadge: {
        width: '24px',
        height: '24px',
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#fff',
    },
    toolName: {
        fontSize: '13px',
        fontWeight: 600,
        color: '#e6edf3',
    },
    body: {
        padding: '0 12px 12px 12px',
        borderTop: '1px solid #30363d',
    },
    section: {
        marginTop: '12px',
    },
    sectionLabel: {
        fontSize: '11px',
        fontWeight: 700,
        color: '#8b949e',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        marginBottom: '6px',
    },
    paramsList: {
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
    },
    param: {
        display: 'flex',
        gap: '8px',
        fontSize: '12px',
        padding: '4px 8px',
        background: 'rgba(13, 17, 23, 0.6)',
        borderRadius: '4px',
    },
    paramKey: {
        color: '#8b949e',
        fontWeight: 600,
        minWidth: '80px',
    },
    paramValue: {
        color: '#c9d1d9',
        fontFamily: "'JetBrains Mono', monospace",
        wordBreak: 'break-all',
    },
    successResult: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 10px',
        background: 'rgba(46, 204, 113, 0.1)',
        border: '1px solid rgba(46, 204, 113, 0.3)',
        borderRadius: '6px',
        color: '#2ecc71',
        fontSize: '12px',
    },
    errorResult: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 10px',
        background: 'rgba(231, 76, 60, 0.1)',
        border: '1px solid rgba(231, 76, 60, 0.3)',
        borderRadius: '6px',
        color: '#e74c3c',
        fontSize: '12px',
    },
    actions: {
        marginTop: '12px',
        display: 'flex',
        gap: '8px',
    },
    actionBtn: {
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '6px 12px',
        background: 'linear-gradient(135deg, #00e5ff 0%, #00b4d8 100%)',
        color: '#000',
        border: 'none',
        borderRadius: '6px',
        fontSize: '12px',
        fontWeight: 600,
        cursor: 'pointer',
        transition: 'all 0.2s',
    },
    // Analysis-specific styles
    analysisContainer: {
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
    },
    analysisInfo: {
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        padding: '10px',
        background: 'rgba(13, 17, 23, 0.6)',
        borderRadius: '6px',
        border: '1px solid #30363d',
    },
    analysisInfoItem: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '12px',
    },
    analysisLabel: {
        color: '#8b949e',
        fontWeight: 600,
        minWidth: '50px',
    },
    analysisValue: {
        color: '#c9d1d9',
        fontFamily: "'JetBrains Mono', monospace",
    },
    analysisBadge: {
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '11px',
        fontWeight: 700,
        color: '#fff',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
    },
    findingsSummary: {
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '8px',
    },
    summaryItem: {
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '8px 10px',
        background: 'rgba(13, 17, 23, 0.6)',
        borderRadius: '6px',
        border: '1px solid #30363d',
    },
    summaryLabel: {
        fontSize: '11px',
        color: '#8b949e',
        fontWeight: 600,
        flex: 1,
    },
    summaryCount: {
        fontSize: '13px',
        color: '#e6edf3',
        fontWeight: 700,
    },
    categoryContainer: {
        background: 'rgba(13, 17, 23, 0.4)',
        borderRadius: '6px',
        overflow: 'hidden',
        border: '1px solid #30363d',
    },
    categoryHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 10px',
        cursor: 'pointer',
        borderLeft: '3px solid',
        transition: 'background 0.15s',
        ':hover': {
            background: 'rgba(22, 27, 34, 0.6)',
        }
    },
    categoryHeaderLeft: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
    },
    categoryExpandBtn: {
        background: 'none',
        border: 'none',
        color: '#8b949e',
        cursor: 'pointer',
        padding: '2px',
        display: 'flex',
        alignItems: 'center',
    },
    categoryIcon: {
        display: 'flex',
        alignItems: 'center',
    },
    categoryTitle: {
        fontSize: '12px',
        fontWeight: 700,
        color: '#e6edf3',
        textTransform: 'capitalize',
    },
    categoryCount: {
        padding: '2px 6px',
        borderRadius: '10px',
        fontSize: '10px',
        fontWeight: 700,
        color: '#fff',
    },
    categoryBody: {
        padding: '8px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
    },
    findingItem: {
        padding: '8px 10px',
        background: 'rgba(22, 27, 34, 0.6)',
        borderRadius: '4px',
        border: '1px solid #30363d',
    },
    findingHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '4px',
    },
    findingLine: {
        fontSize: '11px',
        fontWeight: 700,
        fontFamily: "'JetBrains Mono', monospace",
    },
    findingCategory: {
        fontSize: '10px',
        color: '#8b949e',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
    },
    findingMessage: {
        fontSize: '12px',
        color: '#c9d1d9',
        lineHeight: '1.5',
    },
};

export default ToolCallDisplay;
