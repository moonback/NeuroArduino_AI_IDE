import React, { useState, useEffect } from 'react';
import { Search, Download, CheckCircle, Package, Loader2 } from 'lucide-react';
import axios from 'axios';

const LibraryManager = ({ onClose }) => {
    const [query, setQuery] = useState('');
    const [libraries, setLibraries] = useState([]);
    const [installed, setInstalled] = useState([]);
    const [loading, setLoading] = useState(false);
    const [installing, setInstalling] = useState(null);

    const fetchInstalled = async () => {
        try {
            const res = await axios.get('http://localhost:8001/libraries/installed');
            const data = (typeof res.data === 'string' && res.data.trim()) ? JSON.parse(res.data) : res.data;
            setInstalled(data?.libraries || []);
        } catch (err) {
            console.error('Failed to fetch installed libs', err);
        }
    };

    useEffect(() => {
        fetchInstalled();
    }, []);

    const handleSearch = async () => {
        if (!query.trim()) return;
        setLoading(true);
        try {
            const res = await axios.get(`http://localhost:8001/libraries/search?query=${query}`);
            const data = (typeof res.data === 'string' && res.data.trim()) ? JSON.parse(res.data) : res.data;
            setLibraries(data?.libraries || []);
        } catch (err) {
            console.error('Search failed', err);
        }
        setLoading(false);
    };

    const handleInstall = async (libName) => {
        setInstalling(libName);
        try {
            await axios.post('http://localhost:8001/libraries/install', { name: libName });
            await fetchInstalled();
            alert(`${libName} installed successfully!`);
        } catch (err) {
            alert(`Failed to install ${libName}: ${err.response?.data?.detail || err.message}`);
        }
        setInstalling(null);
    };

    const isInstalled = (name) => installed.some(lib => lib.library.name === name);

    return (
        <div style={{ 
            position: 'absolute', left: '250px', top: '52px', bottom: '0', width: '400px', 
            background: '#161b22', borderRight: '1px solid #30363d', zIndex: 50,
            display: 'flex', flexDirection: 'column', boxShadow: '10px 0 30px rgba(0,0,0,0.5)'
        }}>
            <div style={{ padding: '16px', borderBottom: '1px solid #30363d', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Package size={18} color="#3b82f6" />
                    Library Manager
                </h3>
                <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#6e7681', cursor: 'pointer' }}>✕</button>
            </div>

            <div style={{ padding: '12px' }}>
                <div style={{ display: 'flex', gap: '8px', background: '#0d1117', border: '1px solid #30363d', borderRadius: '6px', padding: '4px 8px' }}>
                    <Search size={16} color="#6e7681" style={{ marginTop: '6px' }} />
                    <input 
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSearch()}
                        placeholder="Search libraries (e.g. Servo, WiFi)..."
                        style={{ background: 'transparent', border: 'none', outline: 'none', color: '#fff', flexGrow: 1, fontSize: '13px', padding: '4px 0' }}
                    />
                </div>
            </div>

            <div style={{ flexGrow: 1, overflowY: 'auto', padding: '0 12px 12px' }}>
                {loading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                        <Loader2 className="animate-spin" color="#3b82f6" />
                    </div>
                ) : libraries.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {libraries.map((lib, i) => (
                            <div key={i} style={{ 
                                background: '#21262d', border: '1px solid #30363d', borderRadius: '6px', padding: '10px',
                                display: 'flex', flexDirection: 'column', gap: '4px'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <span style={{ fontWeight: 600, color: '#c9d1d9', fontSize: '13px' }}>{lib.name}</span>
                                    {isInstalled(lib.name) ? (
                                        <span style={{ color: '#238636', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
                                            <CheckCircle size={12} /> Installed
                                        </span>
                                    ) : (
                                        <button 
                                            onClick={() => handleInstall(lib.name)}
                                            disabled={installing === lib.name}
                                            style={{ 
                                                background: '#238636', color: 'white', border: 'none', borderRadius: '4px', 
                                                padding: '2px 8px', fontSize: '11px', cursor: 'pointer',
                                                display: 'flex', alignItems: 'center', gap: '4px'
                                            }}
                                        >
                                            {installing === lib.name ? <Loader2 size={10} className="animate-spin" /> : <Download size={10} />}
                                            Install
                                        </button>
                                    )}
                                </div>
                                <span style={{ fontSize: '11px', color: '#8b949e', lineHeight: '1.4' }}>{lib.sentence}</span>
                                <div style={{ display: 'flex', gap: '8px', fontSize: '10px', color: '#58a6ff', marginTop: '4px' }}>
                                    <span>v{lib.latest.version}</span>
                                    <span>by {lib.author}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', padding: '40px', color: '#6e7681', fontSize: '12px' }}>
                        Search for a library to begin
                    </div>
                )}
            </div>
        </div>
    );
};

export default LibraryManager;
