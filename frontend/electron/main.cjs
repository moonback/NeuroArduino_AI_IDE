const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

const { initSerialHandlers } = require('./serial.cjs');

let backendProcess = null;
let ipcHandlersRegistered = false;

// ===== LOGGING SYSTEM =====
const logsDir = path.join(app.getPath('userData'), 'logs');
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

const logFile = path.join(logsDir, `electron_${new Date().toISOString().split('T')[0]}.log`);
const errorLogFile = path.join(logsDir, `electron_errors_${new Date().toISOString().split('T')[0]}.log`);

function formatLogMessage(level, message) {
    const timestamp = new Date().toISOString();
    return `${timestamp} - ${level} - ${message}\n`;
}

function writeLog(level, message, isError = false) {
    const logMessage = formatLogMessage(level, message);
    
    // Write to console
    if (isError) {
        console.error(logMessage.trim());
    } else {
        console.log(logMessage.trim());
    }
    
    // Write to main log file
    fs.appendFileSync(logFile, logMessage, 'utf8');
    
    // Write to error log file if it's an error
    if (isError) {
        fs.appendFileSync(errorLogFile, logMessage, 'utf8');
    }
}

function logInfo(message) {
    writeLog('INFO', message);
}

function logError(message) {
    writeLog('ERROR', message, true);
}

function logDebug(message) {
    writeLog('DEBUG', message);
}

function logWarning(message) {
    writeLog('WARNING', message);
}

// Log startup
logInfo('='.repeat(60));
logInfo('Electron Frontend - Démarrage');
logInfo(`Logs sauvegardés dans: ${logsDir}`);
logInfo(`Version Electron: ${app.getVersion()}`);
logInfo(`Plateforme: ${process.platform}`);
logInfo('='.repeat(60));

function startBackend() {
    logInfo('Tentative de démarrage du backend...');
    
    if (app.isPackaged) {
        // In production, spawn the compiled backend executable
        // We will place the backend executable in resources/backend/
        const backendPath = path.join(process.resourcesPath, 'backend', 'backend.exe'); // Windows
        // For Linux usually just 'backend'
        const executable = process.platform === 'win32' ? 'backend.exe' : 'backend';
        const finalPath = path.join(process.resourcesPath, 'backend', executable);

        logInfo(`Lancement du backend depuis: ${finalPath}`);

        backendProcess = spawn(finalPath, [], {
            cwd: path.dirname(finalPath)
        });

        backendProcess.stdout.on('data', (data) => {
            logInfo(`[Backend]: ${data.toString().trim()}`);
        });

        backendProcess.stderr.on('data', (data) => {
            logError(`[Backend Err]: ${data.toString().trim()}`);
        });
        
        backendProcess.on('error', (error) => {
            logError(`[Backend Process Error]: ${error.message}`);
        });
        
        backendProcess.on('exit', (code, signal) => {
            logWarning(`[Backend Process Exit]: Code=${code}, Signal=${signal}`);
        });
    } else {
        // In dev, we assume start_dev.bat launched it, OR we could launch it here.
        // For now, let's just log.
        logInfo('Mode développement: Backend devrait être lancé en externe.');
    }
}

function stopBackend() {
    if (backendProcess) {
        logInfo('Arrêt du backend...');
        backendProcess.kill();
        backendProcess = null;
    }
}



function setupMenu(win) {
    const isMac = process.platform === 'darwin';

    const template = [
        // { role: 'appMenu' }
        ...(isMac ? [{
            label: app.name,
            submenu: [
                { role: 'about' },
                { type: 'separator' },
                { role: 'services' },
                { type: 'separator' },
                { role: 'hide' },
                { role: 'hideOthers' },
                { role: 'unhide' },
                { type: 'separator' },
                { role: 'quit' }
            ]
        }] : []),
        // { role: 'fileMenu' }
        {
            label: 'File',
            submenu: [
                {
                    label: 'New File',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => win.webContents.send('menu:action', 'new-file')
                },
                {
                    label: 'New Folder',
                    accelerator: 'CmdOrCtrl+Shift+N',
                    click: () => win.webContents.send('menu:action', 'new-folder')
                },
                { type: 'separator' },
                {
                    label: 'Open Folder',
                    accelerator: 'CmdOrCtrl+O',
                    click: () => win.webContents.send('menu:action', 'open-folder')
                },
                { type: 'separator' },
                {
                    label: 'Save',
                    accelerator: 'CmdOrCtrl+S',
                    click: () => win.webContents.send('menu:action', 'save')
                },
                { type: 'separator' },
                isMac ? { role: 'close' } : { role: 'quit' }
            ]
        },
        // { role: 'editMenu' }
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' },
                ...(isMac ? [
                    { role: 'pasteAndMatchStyle' },
                    { role: 'delete' },
                    { role: 'selectAll' },
                    { type: 'separator' },
                    {
                        label: 'Speech',
                        submenu: [
                            { role: 'startSpeaking' },
                            { role: 'stopSpeaking' }
                        ]
                    }
                ] : [
                    { role: 'delete' },
                    { type: 'separator' },
                    { role: 'selectAll' }
                ])
            ]
        },
        // { role: 'viewMenu' }
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        // { role: 'windowMenu' }
        {
            label: 'Window',
            submenu: [
                { role: 'minimize' },
                { role: 'zoom' },
                ...(isMac ? [
                    { type: 'separator' },
                    { role: 'front' },
                    { type: 'separator' },
                    { role: 'window' }
                ] : [
                    { role: 'close' }
                ])
            ]
        },
        {
            role: 'help',
            submenu: [
                {
                    label: 'Learn More',
                    click: async () => {
                        const { shell } = require('electron');
                        await shell.openExternal('https://electronjs.org');
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}


function createWindow() {
    logDebug('createWindow() appelé');
    
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.cjs')
        },
        // Use dark theme frame for cleaner look
        backgroundColor: '#0b0f14',
        icon: path.join(__dirname, '../public/favicon.ico')
    });

    logDebug('BrowserWindow créée');

    // Prevent window from closing accidentally
    win.on('close', (event) => {
        logDebug('Événement de fermeture de fenêtre');
    });

    win.on('closed', () => {
        logDebug('Fenêtre fermée');
    });

    // In development, load from Vite dev server
    if (process.env.ELECTRON_START_URL) {
        logInfo(`Chargement depuis le serveur dev: ${process.env.ELECTRON_START_URL}`);
        win.loadURL(process.env.ELECTRON_START_URL);
    } else {
        // In production, load the local index.html
        const indexPath = path.join(__dirname, '../dist/index.html');
        logInfo(`Chargement depuis le fichier: ${indexPath}`);
        win.loadFile(indexPath);
    }

    // Setup Application Menu
    setupMenu(win);

    // Launch Backend Process
    startBackend();

    // Initialize Serial Handlers
    initSerialHandlers(win);

    // File System Handlers
    const { ipcMain, dialog } = require('electron');
    const fs = require('fs');

    if (!ipcHandlersRegistered) {
    ipcHandlersRegistered = true;

    ipcMain.handle('fs:open-folder', async () => {
        logDebug('fs:open-folder appelé');
        const { canceled, filePaths } = await dialog.showOpenDialog(win, {
            properties: ['openDirectory']
        });
        if (canceled) {
            logDebug('Ouverture de dossier annulée');
            return null;
        }

        const dirPath = filePaths[0];
        logInfo(`Ouverture du dossier: ${dirPath}`);
        
        // Recursive function to read directory tree
        const readDirRecursive = async (currentPath, relativePath = '') => {
            try {
                const files = await fs.promises.readdir(currentPath, { withFileTypes: true });
                const fileList = [];
                
                for (const file of files) {
                    const fullPath = path.join(currentPath, file.name);
                    const relPath = relativePath ? path.join(relativePath, file.name) : file.name;
                    
                    fileList.push({
                        name: file.name,
                        isDirectory: file.isDirectory(),
                        path: relPath
                    });
                    
                    // If it's a directory, read its contents recursively
                    if (file.isDirectory()) {
                        const subFiles = await readDirRecursive(fullPath, relPath);
                        fileList.push(...subFiles);
                    }
                }
                
                return fileList;
            } catch (err) {
                console.error(`Error reading directory ${currentPath}:`, err);
                return [];
            }
        };
        
        try {
            const allFiles = await readDirRecursive(dirPath);
            
            // Normalize paths to use forward slashes for consistency
            const normalizedFiles = allFiles.map(file => ({
                ...file,
                path: file.path.replace(/\\/g, '/')
            }));
            
            // Sort: directories first, then alphabetically
            normalizedFiles.sort((a, b) => {
                if (a.isDirectory === b.isDirectory) {
                    return a.name.localeCompare(b.name);
                }
                return a.isDirectory ? -1 : 1;
            });
            
            logInfo(`Dossier ouvert: ${dirPath}`);
            logInfo(`Total de fichiers trouvés: ${normalizedFiles.length}`);
            
            return { path: dirPath, files: normalizedFiles };
        } catch (err) {
            logError(`Erreur lors de l'ouverture du dossier: ${err.message}`);
            return null;
        }
    });

    ipcMain.handle('fs:read-file', async (event, filePath) => {
        try {
            logDebug(`Lecture du fichier: ${filePath}`);
            const content = await fs.promises.readFile(filePath, 'utf-8');
            return content;
        } catch (err) {
            logError(`Erreur lecture fichier ${filePath}: ${err.message}`);
            return null;
        }
    });

    ipcMain.handle('fs:save-file', async (event, filePath, content) => {
        try {
            logDebug(`Sauvegarde du fichier: ${filePath}`);
            await fs.promises.writeFile(filePath, content, 'utf-8');
            logInfo(`Fichier sauvegardé: ${filePath}`);
            return true;
        } catch (err) {
            logError(`Erreur sauvegarde fichier ${filePath}: ${err.message}`);
            return false;
        }
    });

    ipcMain.handle('fs:create-file', async (event, folderPath, fileName) => {
        try {
            const filePath = path.join(folderPath, fileName);
            logDebug(`Création du fichier: ${filePath}`);
            // Don't overwrite existing
            if (fs.existsSync(filePath)) {
                logWarning(`Le fichier existe déjà: ${filePath}`);
                return { success: false, error: 'File already exists' };
            }

            await fs.promises.writeFile(filePath, '', 'utf-8');
            logInfo(`Fichier créé: ${filePath}`);
            return { success: true, path: filePath };
        } catch (err) {
            logError(`Erreur création fichier: ${err.message}`);
            return { success: false, error: err.message };
        }
    });

    ipcMain.handle('fs:create-folder', async (event, folderPath, folderName) => {
        try {
            const dirPath = path.join(folderPath, folderName);
            logDebug(`Création du dossier: ${dirPath}`);

            if (fs.existsSync(dirPath)) {
                logWarning(`Le dossier existe déjà: ${dirPath}`);
                return { success: false, error: 'Folder already exists' };
            }

            await fs.promises.mkdir(dirPath, { recursive: true });
            logInfo(`Dossier créé: ${dirPath}`);
            return { success: true, path: dirPath };
        } catch (err) {
            logError(`Erreur création dossier: ${err.message}`);
            return { success: false, error: err.message };
        }
    });

    ipcMain.handle('fs:save-as', async (event, content) => {
        const { canceled, filePath } = await dialog.showSaveDialog(win, {
            filters: [
                { name: 'Arduino Sketch', extensions: ['ino'] },
                { name: 'C++ Source', extensions: ['cpp', 'h'] },
                { name: 'All Files', extensions: ['*'] }
            ]
        });
        if (canceled) return null;

        try {
            await fs.promises.writeFile(filePath, content, 'utf-8');
            return { success: true, path: filePath, name: path.basename(filePath) };
        } catch (err) {
            return { success: false, error: err.message };
        }
    });

    ipcMain.handle('fs:read-folder', async (event, dirPath) => {
        try {
            const files = await fs.promises.readdir(dirPath, { withFileTypes: true });
            const fileList = files.map(file => ({
                name: file.name,
                isDirectory: file.isDirectory(),
                path: path.join(dirPath, file.name)
            }));
            fileList.sort((a, b) => (a.isDirectory === b.isDirectory ? 0 : a.isDirectory ? -1 : 1));
            return { success: true, files: fileList };
        } catch (err) {
            return { success: false, error: err.message };
        }
    });

    }

    // Open DevTools in dev mode only
    if (!app.isPackaged) {
        logDebug('Ouverture des DevTools (mode dev)');
        win.webContents.openDevTools();
    }
    
    // Log when page finishes loading
    win.webContents.on('did-finish-load', () => {
        logInfo('Page chargée avec succès');
    });
    
    win.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
        logError(`Échec du chargement de la page: ${errorCode} - ${errorDescription}`);
    });
    
    logDebug('createWindow() terminé');
}

app.whenReady().then(() => {
    logInfo('Application Electron prête');
    createWindow();
});

app.on('window-all-closed', () => {
    logDebug('Toutes les fenêtres fermées');
    stopBackend();
    if (process.platform !== 'darwin') {
        logInfo('Fermeture de l\'application (non-macOS)');
        app.quit();
    }
});

app.on('activate', () => {
    logDebug('Application activée');
    if (BrowserWindow.getAllWindows().length === 0) {
        logDebug('Aucune fenêtre, création d\'une nouvelle fenêtre');
        createWindow();
    }
});

app.on('before-quit', () => {
    logInfo('Application sur le point de se fermer');
});

app.on('will-quit', () => {
    logInfo('Application va se fermer');
});

app.on('quit', () => {
    logInfo('Application fermée');
});
