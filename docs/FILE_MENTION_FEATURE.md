# Fonctionnalité @Mention de Fichiers

## 🎯 Objectif

Permettre à l'utilisateur de mentionner des fichiers dans le chat AI en utilisant `@` suivi du nom du fichier, similaire à Cursor IDE ou GitHub Copilot.

## 📋 Fonctionnalités

1. **Autocomplete avec `@`** - Afficher une liste de fichiers quand l'utilisateur tape `@`
2. **Recherche fuzzy** - Filtrer les fichiers pendant la frappe
3. **Navigation au clavier** - Flèches haut/bas + Enter pour sélectionner
4. **Affichage des fichiers mentionnés** - Pills/badges pour les fichiers sélectionnés
5. **Envoi du contexte** - Inclure automatiquement le contenu des fichiers mentionnés

## 🔧 Implémentation

### Étape 1: Ajouter les états dans AIPanel.jsx

```javascript
// Ajouter après les états existants
const [showFileSuggestions, setShowFileSuggestions] = useState(false);
const [fileSuggestions, setFileSuggestions] = useState([]);
const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(0);
const [mentionedFiles, setMentionedFiles] = useState([]); // Files mentioned with @
const [searchQuery, setSearchQuery] = useState('');
const inputRef = useRef(null);
const suggestionsRef = useRef(null);
```

### Étape 2: Fonction de détection du `@`

```javascript
const handleInputChange = (e) => {
    const value = e.target.value;
    setInput(value);
    
    // Detect @ symbol for file mention
    const cursorPos = e.target.selectionStart;
    const textBeforeCursor = value.substring(0, cursorPos);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');
    
    if (lastAtIndex !== -1) {
        const textAfterAt = textBeforeCursor.substring(lastAtIndex + 1);
        
        // Check if we're still in a mention (no space after @)
        if (!textAfterAt.includes(' ')) {
            setSearchQuery(textAfterAt);
            setShowFileSuggestions(true);
            filterFiles(textAfterAt);
        } else {
            setShowFileSuggestions(false);
        }
    } else {
        setShowFileSuggestions(false);
    }
};
```

### Étape 3: Fonction de filtrage des fichiers

```javascript
const filterFiles = (query) => {
    if (!fileTree || !fileTree.files) {
        setFileSuggestions([]);
        return;
    }
    
    // Filter only non-directory files
    const allFiles = fileTree.files.filter(f => !f.isDirectory);
    
    if (!query) {
        // Show all files if no query
        setFileSuggestions(allFiles.slice(0, 10));
        setSelectedSuggestionIndex(0);
        return;
    }
    
    // Fuzzy search
    const lowerQuery = query.toLowerCase();
    const filtered = allFiles.filter(file => {
        const fileName = file.name.toLowerCase();
        const filePath = file.path.toLowerCase();
        return fileName.includes(lowerQuery) || filePath.includes(lowerQuery);
    });
    
    setFileSuggestions(filtered.slice(0, 10));
    setSelectedSuggestionIndex(0);
};
```

### Étape 4: Fonction de sélection de fichier

```javascript
const selectFile = (file) => {
    // Add file to mentioned files if not already added
    if (!mentionedFiles.find(f => f.path === file.path)) {
        setMentionedFiles(prev => [...prev, file]);
    }
    
    // Remove @mention from input and replace with file badge
    const cursorPos = inputRef.current.selectionStart;
    const textBeforeCursor = input.substring(0, cursorPos);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');
    
    const newInput = input.substring(0, lastAtIndex) + input.substring(cursorPos);
    setInput(newInput.trim());
    
    setShowFileSuggestions(false);
    setSearchQuery('');
    
    // Focus back on input
    setTimeout(() => inputRef.current?.focus(), 0);
};
```

### Étape 5: Gestion du clavier

```javascript
const handleKeyDown = (e) => {
    if (!showFileSuggestions) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
        return;
    }
    
    // Navigate suggestions with arrow keys
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
            Math.min(prev + 1, fileSuggestions.length - 1)
        );
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedSuggestionIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (fileSuggestions[selectedSuggestionIndex]) {
            selectFile(fileSuggestions[selectedSuggestionIndex]);
        }
    } else if (e.key === 'Escape') {
        setShowFileSuggestions(false);
    }
};
```

### Étape 6: Modifier sendMessage pour inclure les fichiers mentionnés

```javascript
const sendMessage = async () => {
    if (!input.trim() && mentionedFiles.length === 0) return;
    
    // Build message with mentioned files context
    let messageContent = input;
    const mentionedFilesCopy = [...mentionedFiles];
    
    const userMsg = { 
        role: 'user', 
        content: messageContent,
        mentionedFiles: mentionedFilesCopy
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setMentionedFiles([]); // Clear mentioned files after sending
    setLoading(true);

    try {
        // ... existing code ...
        
        // Add mentioned files to context
        if (mentionedFilesCopy.length > 0) {
            context.mentioned_files = [];
            for (const file of mentionedFilesCopy) {
                try {
                    // Read file content from Electron API
                    if (window.api && window.api.readFile) {
                        const fullPath = fileTree.path + '/' + file.path;
                        const content = await window.api.readFile(fullPath);
                        context.mentioned_files.push({
                            name: file.name,
                            path: file.path,
                            content: content
                        });
                    }
                } catch (err) {
                    console.error(`Failed to read mentioned file ${file.name}:`, err);
                }
            }
        }
        
        // ... rest of existing code ...
    } catch (err) {
        // ... existing error handling ...
    }
    setLoading(false);
};
```

### Étape 7: UI - Afficher les fichiers mentionnés

```jsx
{/* Mentioned Files Pills - Add before input */}
{mentionedFiles.length > 0 && (
    <div className="mentioned-files-container">
        {mentionedFiles.map((file, idx) => (
            <div key={idx} className="mentioned-file-pill">
                <span className="mentioned-file-icon">📄</span>
                <span className="mentioned-file-name">{file.name}</span>
                <button 
                    className="mentioned-file-remove"
                    onClick={() => setMentionedFiles(prev => 
                        prev.filter((_, i) => i !== idx)
                    )}
                    title="Remove file"
                >
                    ×
                </button>
            </div>
        ))}
    </div>
)}
```

### Étape 8: UI - Autocomplete dropdown

```jsx
{/* File Suggestions Dropdown - Add after input */}
{showFileSuggestions && fileSuggestions.length > 0 && (
    <div className="file-suggestions-dropdown" ref={suggestionsRef}>
        <div className="file-suggestions-header">
            <span>📁 Fichiers ({fileSuggestions.length})</span>
        </div>
        {fileSuggestions.map((file, idx) => (
            <div
                key={idx}
                className={`file-suggestion-item ${
                    idx === selectedSuggestionIndex ? 'selected' : ''
                }`}
                onClick={() => selectFile(file)}
                onMouseEnter={() => setSelectedSuggestionIndex(idx)}
            >
                <span className="file-suggestion-icon">
                    {file.name.endsWith('.ino') ? '🔧' : 
                     file.name.endsWith('.h') ? '📋' :
                     file.name.endsWith('.cpp') ? '⚙️' : '📄'}
                </span>
                <div className="file-suggestion-info">
                    <div className="file-suggestion-name">{file.name}</div>
                    <div className="file-suggestion-path">{file.path}</div>
                </div>
            </div>
        ))}
    </div>
)}
```

### Étape 9: Modifier l'input pour utiliser les nouvelles fonctions

```jsx
<input
    ref={inputRef}
    value={input}
    onChange={handleInputChange}
    onKeyDown={handleKeyDown}
    placeholder={`Tapez @ pour mentionner un fichier...`}
    className="ai-input"
/>
```

### Étape 10: Afficher les fichiers mentionnés dans les messages

```jsx
{/* In message display */}
{msg.mentionedFiles && msg.mentionedFiles.length > 0 && (
    <div className="message-mentioned-files">
        <div className="message-mentioned-files-label">
            📎 Fichiers joints:
        </div>
        {msg.mentionedFiles.map((file, idx) => (
            <div key={idx} className="message-mentioned-file">
                <span className="message-file-icon">📄</span>
                <span className="message-file-name">{file.name}</span>
            </div>
        ))}
    </div>
)}
```

## 🎨 CSS Styles

Ajouter dans `App.css` :

```css
/* Mentioned Files Pills */
.mentioned-files-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.03);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.mentioned-file-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 12px;
    font-size: 12px;
    color: #60a5fa;
}

.mentioned-file-icon {
    font-size: 14px;
}

.mentioned-file-name {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.mentioned-file-remove {
    background: none;
    border: none;
    color: #60a5fa;
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
    padding: 0;
    margin-left: 2px;
    opacity: 0.7;
    transition: opacity 0.2s;
}

.mentioned-file-remove:hover {
    opacity: 1;
}

/* File Suggestions Dropdown */
.file-suggestions-dropdown {
    position: absolute;
    bottom: 100%;
    left: 0;
    right: 0;
    max-height: 300px;
    overflow-y: auto;
    background: #1a1f2e;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px 8px 0 0;
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.3);
    z-index: 1000;
}

.file-suggestions-header {
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 12px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.7);
}

.file-suggestion-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    cursor: pointer;
    transition: background 0.2s;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.file-suggestion-item:hover,
.file-suggestion-item.selected {
    background: rgba(59, 130, 246, 0.1);
}

.file-suggestion-icon {
    font-size: 18px;
    flex-shrink: 0;
}

.file-suggestion-info {
    flex: 1;
    min-width: 0;
}

.file-suggestion-name {
    font-size: 13px;
    font-weight: 500;
    color: #e5e7eb;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-suggestion-path {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-top: 2px;
}

/* Message Mentioned Files */
.message-mentioned-files {
    margin-top: 8px;
    padding: 8px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 6px;
    border-left: 3px solid rgba(59, 130, 246, 0.5);
}

.message-mentioned-files-label {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 6px;
    font-weight: 600;
}

.message-mentioned-file {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 0;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
}

.message-file-icon {
    font-size: 14px;
}

.message-file-name {
    font-weight: 500;
}

/* Input wrapper needs relative positioning */
.ai-input-wrapper {
    position: relative;
}
```

## 🧪 Test

1. **Ouvrir un projet** avec plusieurs fichiers
2. **Taper `@`** dans le chat
3. **Vérifier** que la liste des fichiers apparaît
4. **Taper** quelques lettres pour filtrer
5. **Utiliser** les flèches haut/bas pour naviguer
6. **Appuyer** sur Enter pour sélectionner
7. **Vérifier** que le fichier apparaît comme pill
8. **Envoyer** le message
9. **Vérifier** que l'IA reçoit le contenu du fichier

## 📝 Exemple d'utilisation

```
User: @sketch.ino @config.h Explique comment ces deux fichiers interagissent

AI: [Reçoit le contenu de sketch.ino et config.h]
    D'après les fichiers que vous avez partagés:
    
    📄 sketch.ino utilise les constantes définies dans config.h...
    📄 config.h définit les paramètres WiFi et les pins...
    
    Voici comment ils interagissent:
    1. sketch.ino inclut config.h avec #include "config.h"
    2. Les constantes WIFI_SSID et WIFI_PASSWORD sont utilisées...
```

## 🚀 Améliorations Futures

1. **Drag & Drop** - Glisser-déposer des fichiers depuis l'explorateur
2. **Mention de dossiers** - `@folder/` pour inclure tous les fichiers d'un dossier
3. **Historique** - Se souvenir des fichiers récemment mentionnés
4. **Raccourci clavier** - `Ctrl+K` pour ouvrir le sélecteur de fichiers
5. **Preview** - Afficher un aperçu du fichier au survol
6. **Syntax highlighting** - Coloration syntaxique dans les pills
7. **Taille du fichier** - Afficher la taille à côté du nom
8. **Filtres** - Filtrer par extension (.ino, .h, .cpp)

## 📚 Références

- Cursor IDE: https://cursor.sh
- GitHub Copilot Chat
- VS Code @workspace mention
