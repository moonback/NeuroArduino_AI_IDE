import React, { useState, useEffect, useRef } from 'react';
import CodeEditor from './components/Editor';
import Sidebar from './components/Sidebar';
import AIPanel from './components/AIPanel';
import Terminal from './components/Terminal';
import SerialMonitor from './components/SerialMonitor';
import SerialPlotter from './components/SerialPlotter';
import InputModal from './components/InputModal';
import LibraryManager from './components/LibraryManager';
import BoardManager from './components/BoardManager';
import VisionPanel from './components/VisionPanel';
import { Play, Upload, Settings, RefreshCw, PlugZap, Terminal as TerminalIcon, Cpu, ListFilter, Save, FilePlus, Package, Activity, Camera, Sparkles } from 'lucide-react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

function App() {
  const { t, i18n } = useTranslation();
  const [code, setCode] = useState('// Welcome to AI NeuroArduino IDE\nvoid setup() {\n  // Put your setup code here, to run once:\n}\n\nvoid loop() {\n  // Put your main code here, to run repeatedly:\n}\n');
  const [logs, setLogs] = useState([]);
  const [board, setBoard] = useState('arduino:avr:uno');
  const [activeTab, setActiveTab] = useState('terminal'); // 'terminal', 'serial', or 'plotter'
  const [showSidebar, setShowSidebar] = useState(true);
  const [showAIPanel, setShowAIPanel] = useState(true);

  // File System State
  const [fileTree, setFileTree] = useState(null);
  const [currentFile, setCurrentFile] = useState(null);
  const [isDirty, setIsDirty] = useState(false);
  const initialCodeRef = useRef(code);

  // Serial Port State
  const [ports, setPorts] = useState([]);
  const [selectedPort, setSelectedPort] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [baudRate, setBaudRate] = useState(9600);

  // Modal State
  const [modal, setModal] = useState({ isOpen: false, type: '', value: '' });
  const [showLibraryManager, setShowLibraryManager] = useState(false);
  const [showBoardManager, setShowBoardManager] = useState(false);
  const [showVisionPanel, setShowVisionPanel] = useState(false);
  const [allBoards, setAllBoards] = useState([
    { name: 'Arduino Uno', fqbn: 'arduino:avr:uno' },
    { name: 'Arduino Nano', fqbn: 'arduino:avr:nano' },
    { name: 'Arduino Mega', fqbn: 'arduino:avr:mega' }
  ]);

  const addLog = (msg, type = 'info') => {
    setLogs(prev => [...prev, { message: msg, type, timestamp: Date.now() }]);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  // Monitor changes for dirty state
  useEffect(() => {
    if (code !== initialCodeRef.current) {
      setIsDirty(true);
    } else {
      setIsDirty(false);
    }
  }, [code]);

  const onCodeChange = (newCode) => {
    setCode(newCode);
  };

  const wsRef = useRef(null);

  // Load Ports
  const refreshPorts = async () => {
    addLog('Scanning for ports (Backend)...', 'info');
    try {
      const res = await axios.get('http://localhost:8001/ports');
      const availablePorts = res.data.map(p => ({ path: p.device, manufacturer: p.description }));
      setPorts(availablePorts);
      addLog(`Found ${availablePorts.length} ports via backend.`, 'success');

      if (availablePorts.length > 0 && !selectedPort) {
        setSelectedPort(availablePorts[0].path);
      }
    } catch (e) {
      addLog(`Error scanning ports: ${e.message}`, 'error');
    }
  };

  useEffect(() => {
    refreshPorts();
    fetchBoards();
  }, []);

  const fetchBoards = async () => {
    try {
      const res = await axios.get('http://localhost:8001/boards/listall');
      const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
      if (data && data.boards) {
        const boardList = data.boards.map(b => ({ name: b.name, fqbn: b.fqbn }));
        setAllBoards(boardList);
      }
    } catch (err) {
      console.error("Failed to fetch boards", err);
    }
  };

  const handleConnect = async () => {
    if (!selectedPort) {
      addLog('No port selected', 'warning');
      return;
    }

    if (isConnected) {
      // Disconnect
      try {
        await axios.post('http://localhost:8001/serial/disconnect');
        if (wsRef.current) wsRef.current.close();
        setIsConnected(false);
        addLog('Disconnected from ' + selectedPort, 'info');
      } catch (err) {
        addLog('Error disconnecting: ' + err.message, 'error');
      }
    } else {
      // Connect
      addLog(`Connecting to ${selectedPort} at ${baudRate} baud...`, 'info');
      try {
        const res = await axios.post('http://localhost:8001/serial/connect', {
          path: selectedPort,
          baudrate: baudRate
        });

        if (res.data.status === 'success') {
          setIsConnected(true);
          addLog('Connected to ' + selectedPort, 'success');
          setActiveTab('serial');

          // Initialize WebSocket
          const ws = new WebSocket('ws://localhost:8001/ws/monitor');
          ws.onmessage = (event) => {
            addLog(event.data, 'serial');
          };
          ws.onclose = () => {
            setIsConnected(false);
            addLog('Serial connection closed', 'warning');
          };
          ws.onerror = (err) => {
            addLog('WebSocket error', 'error');
          };
          wsRef.current = ws;

        }
      } catch (err) {
        const msg = err.response?.data?.detail || 'Connection Failed';
        addLog(msg, 'error');
      }
    }
  };

  const checkForUnsavedChanges = async () => {
    if (isDirty) {
      if (window.confirm('You have unsaved changes. Discard them?')) {
        setIsDirty(false);
        return true;
      }
      return false;
    }
    return true;
  };

  const handleCompile = async () => {
    addLog('Compiling...', 'info');
    setActiveTab('terminal');
    try {
      const res = await axios.post('http://localhost:8001/compile', { code, board });
      addLog(res.data.message, 'success');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Compilation Failed';
      addLog(msg, 'error');
    }
  };

  const handleUpload = async () => {
    if (!selectedPort) {
      addLog('Please select a port first!', 'error');
      return;
    }

    setActiveTab('terminal');

    if (isConnected) {
      addLog('Disconnecting serial for upload...', 'warning');
      if (window.api) await window.api.serial.disconnect();
      setIsConnected(false);
    }

    addLog('Uploading...', 'info');
    try {
      const res = await axios.post('http://localhost:8001/upload', { code, board, port: selectedPort });
      addLog(res.data.message, 'success');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload Failed';
      addLog(msg, 'error');
    }
  };

  const handleOpenFolder = async () => {
    if (!(await checkForUnsavedChanges())) return;

    if (window.api && window.api.fs) {
      const result = await window.api.fs.openFolder();
      if (result) {
        setFileTree({ name: result.path.split(/[\\/]/).pop(), path: result.path, files: result.files });
        addLog(`Opened folder: ${result.path}`, 'success');
      }
    }
  };

  const handleFileClick = async (file) => {
    if (!(await checkForUnsavedChanges())) return;

    if (window.api && window.api.fs) {
      try {
        const content = await window.api.fs.readFile(file.path);
        if (content !== null) {
          initialCodeRef.current = content;
          setCode(content);
          setCurrentFile(file);
          setIsDirty(false);
          addLog(`Opened file: ${file.name}`, 'info');
        } else {
          addLog(`Failed to read file: ${file.name}`, 'error');
        }
      } catch (err) {
        addLog(`Error reading file: ${err}`, 'error');
      }
    }
  };

  const openModal = (type) => {
    if (!fileTree && type !== 'file') return addLog('Open a folder first!', 'warning');
    setModal({ isOpen: true, type, value: '' });
  };

  const closeModal = () => setModal({ isOpen: false, type: '', value: '' });

  const handleModalConfirm = async (name) => {
    if (!name) return;
    closeModal();

    if (modal.type === 'file') {
      if (fileTree) {
        const res = await window.api.fs.createFile(fileTree.path, name);
        if (res.success) {
          addLog(`Created file: ${name}`, 'success');
          refreshFileTree(fileTree.path);
          handleFileClick({ name, path: res.path, isDirectory: false });
        } else {
          addLog(`Error creating file: ${res.error}`, 'error');
        }
      } else {
        handleSaveAs();
      }
    } else if (modal.type === 'folder') {
      const res = await window.api.fs.createFolder(fileTree.path, name);
      if (res.success) {
        addLog(`Created folder: ${name}`, 'success');
        refreshFileTree(fileTree.path);
      } else {
        addLog(`Error creating folder: ${res.error}`, 'error');
      }
    }
  };

  const handleCreateFileClick = () => openModal('file');
  const handleCreateFolderClick = () => openModal('folder');

  const refreshFileTree = async (path) => {
    if (window.api && window.api.fs) {
      const result = await window.api.fs.readFolder(path);
      if (result.success) {
        setFileTree(prev => ({ ...prev, files: result.files }));
      }
    }
  };

  const handleSave = async () => {
    if (!currentFile) {
      return handleSaveAs();
    }
    if (window.api && window.api.fs) {
      try {
        const success = await window.api.fs.saveFile(currentFile.path, code);
        if (success) {
          initialCodeRef.current = code;
          setIsDirty(false);
          addLog(`Saved ${currentFile.name}`, 'success');
        } else {
          addLog(`Failed to save ${currentFile.name}`, 'error');
        }
      } catch (err) {
        addLog(`Error saving: ${err}`, 'error');
      }
    }
  };

  const handleSaveAs = async () => {
    if (window.api && window.api.fs) {
      try {
        const result = await window.api.fs.saveAs(code);
        if (result && result.success) {
          initialCodeRef.current = code;
          setCurrentFile({ name: result.name, path: result.path, isDirectory: false });
          setIsDirty(false);
          addLog(`File saved as: ${result.name}`, 'success');
          if (fileTree) refreshFileTree(fileTree.path);
        }
      } catch (err) {
        addLog(`Error saving as: ${err}`, 'error');
      }
    }
  };

  const handleNewSketch = async () => {
    if (!(await checkForUnsavedChanges())) return;
    const defaultCode = '// New Sketch\nvoid setup() {\n  \n}\n\nvoid loop() {\n  \n}\n';
    initialCodeRef.current = defaultCode;
    setCode(defaultCode);
    setCurrentFile(null);
    setIsDirty(false);
    addLog('New sketch started', 'info');
  };

  useEffect(() => {
    if (window.api && window.api.onMenuAction) {
      const removeListener = window.api.onMenuAction((action) => {
        switch (action) {
          case 'new-file':
            handleNewSketch();
            break;
          case 'new-folder':
            handleCreateFolderClick();
            break;
          case 'open-folder':
            handleOpenFolder();
            break;
          case 'save':
            handleSave();
            break;
          default:
            break;
        }
      });
      return () => removeListener();
    }
  }, [fileTree, currentFile, code, modal, isDirty]);

  const handleSend = async (data) => {
    if (!isConnected) {
      addLog('Not connected to any device.', 'warning');
      return;
    }
    try {
      await axios.post('http://localhost:8001/serial/write', { data });
      addLog(`> ${data}`, 'info');
    } catch (err) {
      addLog(`Error sending: ${err.message}`, 'error');
    }
  };

  return (
    <div className="flex w-full h-full text-white overflow-hidden">
      <InputModal
        isOpen={modal.isOpen}
        title={modal.type === 'file' ? t('newFile') : t('newFolder')}
        placeholder={modal.type === 'file' ? 'sketch.ino' : 'lib_name'}
        onConfirm={handleModalConfirm}
        onCancel={closeModal}
      />

      {/* Activity Bar */}
      <div style={{ width: '48px', minWidth: '48px', background: '#111b27', borderRight: '1px solid #30363d', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '12px 0', gap: '16px', zIndex: 20 }}>
        <button 
          onClick={() => setShowSidebar(!showSidebar)}
          className={`p-2 rounded transition-colors ${showSidebar ? 'text-white' : 'text-gray-500 hover:text-gray-300'}`}
          title={t('explorer')}
        >
          <ListFilter size={20} />
        </button>
        <button 
          onClick={() => { setShowBoardManager(!showBoardManager); setShowLibraryManager(false); }}
          className={`p-2 rounded transition-colors ${showBoardManager ? 'text-white' : 'text-gray-500 hover:text-gray-300'}`}
          title={t('boards')}
        >
          <Cpu size={20} />
        </button>
        <button 
          onClick={() => { setShowLibraryManager(!showLibraryManager); setShowBoardManager(false); }}
          className={`p-2 rounded transition-colors ${showLibraryManager ? 'text-white' : 'text-gray-500 hover:text-gray-300'}`}
          title={t('libraries')}
        >
          <Package size={20} />
        </button>
        <button 
          onClick={() => setShowVisionPanel(true)}
          className="p-2 rounded text-gray-500 hover:text-cyan-400 transition-colors"
          title={t('vision')}
        >
          <Camera size={20} />
        </button>
        <div style={{ flexGrow: 1 }}></div>
        <button 
          className="p-2 rounded text-gray-500 hover:text-gray-300 transition-colors"
          title={t('settings') || "Settings"}
        >
          <Settings size={20} />
        </button>
      </div>

      {/* Left Sidebar */}
      {showSidebar && (
        <Sidebar
          fileTree={fileTree}
          onOpenFolder={handleOpenFolder}
          onFileClick={handleFileClick}
          onCreateFile={handleCreateFileClick}
          onCreateFolder={handleCreateFolderClick}
        />
      )}

      {showLibraryManager && <LibraryManager onClose={() => setShowLibraryManager(false)} />}
      {showBoardManager && <BoardManager onClose={() => setShowBoardManager(false)} />}
      {showVisionPanel && <VisionPanel onApplyCode={onCodeChange} onClose={() => setShowVisionPanel(false)} />}

      {/* Main Content */}
      <div className="flex flex-col grow min-w-0" style={{ background: '#0b0f14' }}>

        {/* Toolbar */}
        <div style={{ minHeight: '44px', borderBottom: '1px solid #30363d', display: 'flex', alignItems: 'center', padding: '8px 16px', gap: '12px', background: '#161b22', zIndex: 10, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded text-sm font-medium transition-colors"
               onClick={handleCompile}
              title={t('verify')}
            >
              <CheckCircleIcon size={16} /> <span className="hide-mobile">{t('verify')}</span>
            </button>
            <button
              className="flex items-center gap-2 px-3 py-1.5 bg-transparent border border-gray-700 hover:border-gray-500 rounded text-sm font-medium transition-colors"
              onClick={handleUpload}
              title={t('upload')}
            >
              <Upload size={16} /> <span className="hide-mobile">{t('upload')}</span>
            </button>
          </div>

          <div className="h-6 w-px bg-gray-700"></div>

          {/* Persistence Controls */}
          <div className="flex items-center gap-1">
            <button onClick={handleNewSketch} className="p-2 hover:bg-white/10 rounded transition-colors text-gray-400 hover:text-white" title={t('newSketch')}>
              <FilePlus size={18} />
            </button>
            <button onClick={handleSave} className={`p-2 hover:bg-white/10 rounded transition-colors ${isDirty ? 'text-accent' : 'text-gray-400 hover:text-white'}`} title={t('save')}>
              <Save size={18} />
            </button>
          </div>

          <div className="h-6 w-px bg-gray-700"></div>

          {/* Hardware Controls */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-[#0d1117] border border-[#30363d] rounded px-2 py-1">
              <Cpu size={14} className="text-gray-400" />
              <select
                value={selectedPort}
                onChange={e => setSelectedPort(e.target.value)}
                className="bg-transparent text-sm outline-none cursor-pointer"
                style={{ minWidth: '100px' }}
              >
                <option value="">{t('selectPort')}</option>
                {ports.map(p => (
                  <option key={p.path} value={p.path}>{p.path} {p.manufacturer ? `(${p.manufacturer})` : ''}</option>
                ))}
              </select>
            </div>

            <button onClick={refreshPorts} className="p-1.5 hover:bg-white/10 rounded transition-colors" title={t('refreshPorts')}>
              <RefreshCw size={14} className="text-gray-400" />
            </button>

            <button
              onClick={handleConnect}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium transition-all ${isConnected
                ? 'bg-red-500/10 text-red-500 border border-red-500/50 hover:bg-red-500/20'
                : 'bg-green-500/10 text-green-500 border border-green-500/50 hover:bg-green-500/20'
                }`}
            >
              <PlugZap size={14} />
              <span className="hide-tablet">{isConnected ? t('disconnect') : t('connect')}</span>
            </button>
          </div>

          <div style={{ flexGrow: 1 }}></div>

          {/* File Status */}
          <div className="flex items-center gap-2 px-3 hide-tablet">
            <span className="text-xs text-gray-400 italic">
              {currentFile ? currentFile.name : t('unsavedSketch')}
              {isDirty ? '*' : ''}
            </span>
          </div>

          <div style={{ flexGrow: 1 }}></div>

          {/* Board Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 uppercase tracking-wider font-bold">{t('board')}</span>
            <select
              value={board}
              onChange={e => setBoard(e.target.value)}
              className="bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-sm outline-none hover:border-gray-500 transition-colors"
              style={{ maxWidth: '200px' }}
            >
              {allBoards.map(b => (
                <option key={b.fqbn} value={b.fqbn}>{b.name}</option>
              ))}
            </select>
          </div>

          <div className="h-6 w-px bg-gray-700"></div>

          {/* Language Switcher */}
          <div className="flex items-center gap-2 px-3">
            <select
              value={i18n.language}
              onChange={e => i18n.changeLanguage(e.target.value)}
              className="bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-xs outline-none hover:border-gray-500 transition-colors"
            >
              <option value="en">EN</option>
              <option value="fr">FR</option>
            </select>
          </div>

          <div className="h-6 w-px bg-gray-700"></div>
          
          <button 
            onClick={() => setShowAIPanel(!showAIPanel)}
            className={`p-2 rounded transition-colors ${showAIPanel ? 'text-accent' : 'text-gray-400'}`}
            title={t('aiAssistant')}
          >
            <Sparkles size={18} />
          </button>
        </div>

        {/* Editor Area */}
        <div style={{ flexGrow: 1, position: 'relative' }}>
          <CodeEditor code={code} setCode={onCodeChange} />
        </div>

        {/* Tabbed Bottom Panel */}
        <div style={{ flexBasis: '200px', minHeight: '150px', borderTop: '1px solid #30363d', display: 'flex', flexDirection: 'column', background: '#0d1117' }}>
          {/* Tab Header */}
          <div className="flex items-center px-4 bg-[#161b22] border-b border-[#30363d]">
            <button
              onClick={() => setActiveTab('terminal')}
              className={`px-4 py-2 text-xs font-bold uppercase tracking-widest flex items-center gap-2 transition-all border-b-2 ${activeTab === 'terminal' ? 'text-blue-400 border-blue-400' : 'text-gray-500 border-transparent hover:text-gray-300'}`}
            >
              <TerminalIcon size={14} /> {t('output')}
            </button>
            <button
              onClick={() => setActiveTab('serial')}
              className={`px-4 py-2 text-xs font-bold uppercase tracking-widest flex items-center gap-2 transition-all border-b-2 ${activeTab === 'serial' ? 'text-blue-400 border-blue-400' : 'text-gray-500 border-transparent hover:text-gray-300'}`}
            >
              <ListFilter size={14} /> {t('serialMonitor')}
            </button>
            <button
              onClick={() => setActiveTab('plotter')}
              className={`px-4 py-2 text-xs font-bold uppercase tracking-widest flex items-center gap-2 transition-all border-b-2 ${activeTab === 'plotter' ? 'text-blue-400 border-blue-400' : 'text-gray-500 border-transparent hover:text-gray-300'}`}
            >
              <Activity size={14} /> {t('plotter')}
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'terminal' && (
              <Terminal
                logs={logs.filter(l => l.type !== 'serial')}
                onSend={handleSend}
                onClear={clearLogs}
                baudRate={baudRate}
                setBaudRate={setBaudRate}
                isConnected={isConnected}
              />
            )}
            {activeTab === 'serial' && (
              <SerialMonitor
                logs={logs}
                onSend={handleSend}
                onClear={clearLogs}
                baudRate={baudRate}
                setBaudRate={setBaudRate}
                isConnected={isConnected}
                onConnect={handleConnect}
                onDisconnect={handleConnect}
                selectedPort={selectedPort}
              />
            )}
            {activeTab === 'plotter' && (
              <SerialPlotter
                logs={logs}
                onClear={clearLogs}
              />
            )}
          </div>
        </div>
      </div>

      {/* Right AI Panel */}
      {showAIPanel && <AIPanel onApplyCode={onCodeChange} onOpenVision={() => setShowVisionPanel(true)} />}
    </div>
  );
}

// Icon Helper
const CheckCircleIcon = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
);

export default App;
