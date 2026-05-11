import React from 'react';
import { 
    FileText, Edit, Trash2, FolderPlus, File, 
    CheckCircle, XCircle, Loader2, ChevronDown, ChevronRight 
} from 'lucide-react';

const ToolCallDisplay = ({ toolCall, toolResult, onOpenFile }) => {
    const [isExpanded, setIsExpanded] = React.useState(true);
    
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
};

export default ToolCallDisplay;
