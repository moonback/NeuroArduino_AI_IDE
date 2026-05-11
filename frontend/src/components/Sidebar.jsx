import { ChevronDown, ChevronRight, FileCode, Folder, FolderOpen, Plus, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

const FileTreeItem = ({ item, level = 0, onFileClick, onFolderToggle, expandedFolders }) => {
    const isExpanded = expandedFolders.has(item.path);
    const isFolder = item.isDirectory;
    
    const handleClick = () => {
        if (isFolder) {
            onFolderToggle(item.path);
        } else {
            onFileClick(item);
        }
    };
    
    return (
        <div>
            <div
                onClick={handleClick}
                style={{
                    padding: '4px 12px',
                    paddingLeft: `${12 + level * 16}px`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    cursor: 'pointer',
                    color: isFolder ? '#9ca3af' : '#d1d5db',
                    transition: 'all 0.15s',
                }}
                className="file-tree-item hover:bg-[#1f2937]"
            >
                {isFolder && (
                    <span style={{ width: '14px', display: 'flex', alignItems: 'center' }}>
                        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    </span>
                )}
                {!isFolder && <span style={{ width: '14px' }}></span>}
                
                {isFolder ? (
                    isExpanded ? <FolderOpen size={14} color="#60a5fa" /> : <Folder size={14} color="#60a5fa" />
                ) : (
                    <FileCode size={14} color={item.name.endsWith('.ino') ? '#10b981' : '#8b949e'} />
                )}
                
                <span style={{ 
                    whiteSpace: 'nowrap', 
                    overflow: 'hidden', 
                    textOverflow: 'ellipsis',
                    fontSize: '13px',
                    fontWeight: isFolder ? 500 : 400
                }}>
                    {item.name}
                </span>
            </div>
            
            {isFolder && isExpanded && item.children && (
                <div>
                    {item.children.map((child, idx) => (
                        <FileTreeItem
                            key={idx}
                            item={child}
                            level={level + 1}
                            onFileClick={onFileClick}
                            onFolderToggle={onFolderToggle}
                            expandedFolders={expandedFolders}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

const Sidebar = ({ fileTree, onFileClick, onOpenFolder, onCreateFile, onCreateFolder, onCloseFolder }) => {
    const { t } = useTranslation();
    const [expandedFolders, setExpandedFolders] = useState(new Set());
    
    const handleFolderToggle = (path) => {
        setExpandedFolders(prev => {
            const newSet = new Set(prev);
            if (newSet.has(path)) {
                newSet.delete(path);
            } else {
                newSet.add(path);
            }
            return newSet;
        });
    };
    
    // Build tree structure from flat file list
    const buildTree = (files, basePath = '') => {
        if (!files) return [];
        
        // Create a map to store all items by path
        const itemMap = new Map();
        
        // First, add all items to the map
        files.forEach(file => {
            itemMap.set(file.path, {
                ...file,
                children: []
            });
        });
        
        // Build the tree structure
        const rootItems = [];
        
        itemMap.forEach((item, filePath) => {
            // Use forward slashes since we normalized in backend
            const pathParts = filePath.split('/').filter(p => p);
            
            if (pathParts.length === 1) {
                // Root level item
                rootItems.push(item);
            } else {
                // Find parent
                const parentPath = pathParts.slice(0, -1).join('/');
                const parent = itemMap.get(parentPath);
                
                if (parent) {
                    parent.children.push(item);
                } else {
                    // Parent not found, add to root (shouldn't happen with proper recursive read)
                    console.warn('Parent not found for:', filePath, 'expected parent:', parentPath);
                    rootItems.push(item);
                }
            }
        });
        
        // Sort function: folders first, then files, alphabetically
        const sortItems = (items) => {
            return items.sort((a, b) => {
                if (a.isDirectory && !b.isDirectory) return -1;
                if (!a.isDirectory && b.isDirectory) return 1;
                return a.name.localeCompare(b.name);
            });
        };
        
        // Recursively sort all levels
        const sortTree = (items) => {
            const sorted = sortItems([...items]);
            sorted.forEach(item => {
                if (item.children && item.children.length > 0) {
                    item.children = sortTree(item.children);
                }
            });
            return sorted;
        };
        
        return sortTree(rootItems);
    };
    
    const treeStructure = fileTree ? buildTree(fileTree.files) : [];
    
    // Debug: log the tree structure
    useEffect(() => {
        if (fileTree) {
            console.log('File tree received:', fileTree);
            console.log('Tree structure built:', treeStructure);
        }
    }, [fileTree, treeStructure]);
    
    return (
        <div className="panel-sidebar" style={{ 
            width: '250px', 
            background: 'var(--bg-panel)', 
            borderRight: '1px solid var(--border)', 
            display: 'flex', 
            flexDirection: 'column', 
            fontSize: '0.85rem' 
        }}>
            {/* Header */}
            <div style={{ 
                padding: '8px 12px', 
                background: '#111b27', 
                borderBottom: '1px solid var(--border)', 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center' 
            }}>
                <span style={{ 
                    fontWeight: 600, 
                    letterSpacing: '0.5px', 
                    color: '#8b9bb4',
                    fontSize: '11px',
                    textTransform: 'uppercase'
                }}>
                    {t('explorer')}
                </span>
                <div style={{ display: 'flex', gap: '2px' }}>
                    <button 
                        onClick={onCreateFile} 
                        title={t('newFile')} 
                        className="sidebar-icon-btn"
                    >
                        <FileCode size={14} />
                    </button>
                    <button 
                        onClick={onCreateFolder} 
                        title={t('newFolder')} 
                        className="sidebar-icon-btn"
                    >
                        <Folder size={14} />
                    </button>
                    <button 
                        onClick={onOpenFolder} 
                        title={t('openFolder')} 
                        className="sidebar-icon-btn"
                    >
                        <Plus size={14} />
                    </button>
                </div>
            </div>

            {/* File Tree */}
            <div style={{ 
                flexGrow: 1, 
                overflowY: 'auto', 
                overflowX: 'hidden',
                paddingTop: '4px' 
            }}>
                {fileTree ? (
                    <div>
                        {/* Root folder */}
                        <div style={{ 
                            padding: '6px 12px', 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: '6px', 
                            color: '#e5e7eb', 
                            fontWeight: 600,
                            background: 'rgba(59, 130, 246, 0.1)',
                            borderBottom: '1px solid rgba(59, 130, 246, 0.2)',
                            justifyContent: 'space-between'
                        }}>
                            <div style={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '6px',
                                flex: 1,
                                minWidth: 0
                            }}>
                                <FolderOpen size={16} color="#60a5fa" />
                                <span style={{ 
                                    whiteSpace: 'nowrap', 
                                    overflow: 'hidden', 
                                    textOverflow: 'ellipsis',
                                    fontSize: '13px'
                                }}>
                                    {fileTree.name || 'Project'}
                                </span>
                            </div>
                            <button 
                                onClick={onCloseFolder}
                                className="sidebar-icon-btn"
                                title={t('closeFolder')}
                                style={{
                                    padding: '2px',
                                    opacity: 0.7,
                                    transition: 'opacity 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
                                onMouseLeave={(e) => e.currentTarget.style.opacity = '0.7'}
                            >
                                <X size={14} />
                            </button>
                        </div>

                        {/* File tree */}
                        <div style={{ paddingTop: '4px' }}>
                            {treeStructure.map((item, idx) => (
                                <FileTreeItem
                                    key={idx}
                                    item={item}
                                    level={0}
                                    onFileClick={onFileClick}
                                    onFolderToggle={handleFolderToggle}
                                    expandedFolders={expandedFolders}
                                />
                            ))}
                        </div>
                    </div>
                ) : (
                    <div style={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        height: '100%', 
                        color: '#6b7280', 
                        gap: '12px',
                        padding: '20px'
                    }}>
                        <Folder size={48} opacity={0.3} />
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ 
                                marginBottom: '12px',
                                fontSize: '13px',
                                color: '#8b949e'
                            }}>
                                {t('noFolderOpen')}
                            </div>
                            <button
                                onClick={onOpenFolder}
                                style={{ 
                                    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                                    color: 'white', 
                                    border: 'none', 
                                    padding: '8px 16px', 
                                    borderRadius: '6px', 
                                    cursor: 'pointer', 
                                    fontSize: '13px',
                                    fontWeight: 600,
                                    boxShadow: '0 2px 8px rgba(59, 130, 246, 0.3)',
                                    transition: 'all 0.2s'
                                }}
                                className="open-folder-btn"
                            >
                                {t('openFolder')}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Sidebar;
