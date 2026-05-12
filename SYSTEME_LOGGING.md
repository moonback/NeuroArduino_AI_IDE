# Système de Logging - AI Arduino IDE

## 📋 Vue d'ensemble

Un système complet de logging a été mis en place pour enregistrer toutes les activités de l'application dans des fichiers texte. Cela vous permettra de diagnostiquer et corriger les bugs facilement.

## 📁 Emplacement des Logs

### Backend (Python)
Les logs du backend sont sauvegardés dans le dossier `logs/` à la racine du projet :
```
logs/
├── backend_20260512.log          # Tous les logs du jour
├── backend_errors_20260512.log   # Uniquement les erreurs
└── README.md                      # Documentation
```

### Frontend (Electron)
Les logs Electron sont sauvegardés dans le dossier userData de votre système :
- **Windows** : `%APPDATA%\ai-arduino-ide\logs\`
- **Linux** : `~/.config/ai-arduino-ide/logs/`
- **macOS** : `~/Library/Application Support/ai-arduino-ide/logs/`

Fichiers :
```
electron_2026-05-12.log          # Tous les logs
electron_errors_2026-05-12.log   # Uniquement les erreurs
```

## 🔍 Que Contiennent les Logs ?

### Backend
✅ **Requêtes API**
- Endpoints appelés (compile, upload, ai/generate, etc.)
- Méthodes HTTP (GET, POST)
- Paramètres de requête

✅ **Appels AI**
- Provider utilisé (OpenRouter, Gemini)
- Longueur des prompts et réponses
- Appels d'outils (tool calling)
- Résultats des outils

✅ **Opérations Arduino**
- Compilation de sketches
- Upload vers les cartes
- Gestion des ports série
- Recherche et installation de bibliothèques

✅ **Erreurs**
- Messages d'erreur détaillés
- Stack traces complets
- Contexte de l'erreur

### Frontend
✅ **Cycle de vie de l'application**
- Démarrage de l'application
- Chargement des fenêtres
- Fermeture de l'application

✅ **Opérations sur les fichiers**
- Ouverture de dossiers
- Lecture de fichiers
- Sauvegarde de fichiers
- Création de fichiers/dossiers

✅ **Processus Backend**
- Démarrage du backend
- Logs du backend (stdout/stderr)
- Arrêt du backend

✅ **Erreurs**
- Erreurs de chargement de page
- Erreurs d'opérations fichiers
- Erreurs du processus backend

## 🛠️ Utilisation

### 1. Visualiser les Logs avec le Script

Utilisez le script `view_logs.bat` pour consulter facilement les logs :

```batch
view_logs.bat
```

Menu interactif :
1. **Logs Backend (aujourd'hui)** - Voir tous les logs du jour
2. **Erreurs Backend (aujourd'hui)** - Voir uniquement les erreurs
3. **Tous les logs Backend** - Choisir un fichier spécifique
4. **Logs Electron** - Ouvrir le dossier Electron
5. **Dernières 50 lignes** - Voir les logs récents
6. **Rechercher** - Chercher un terme dans les logs
7. **Nettoyer** - Supprimer les logs de plus de 7 jours

### 2. Consulter Manuellement

#### Windows
```batch
# Voir les logs backend du jour
type logs\backend_20260512.log

# Voir les erreurs
type logs\backend_errors_20260512.log

# Voir les dernières lignes
powershell -Command "Get-Content logs\backend_20260512.log -Tail 50"

# Rechercher un terme
findstr /i "error" logs\backend_*.log
```

#### Linux/macOS
```bash
# Voir les logs backend du jour
cat logs/backend_20260512.log

# Voir les erreurs
cat logs/backend_errors_20260512.log

# Voir les dernières lignes
tail -n 50 logs/backend_20260512.log

# Rechercher un terme
grep -i "error" logs/backend_*.log
```

### 3. Ouvrir les Logs Electron

**Windows** :
```batch
start %APPDATA%\ai-arduino-ide\logs
```

**Linux** :
```bash
xdg-open ~/.config/ai-arduino-ide/logs
```

**macOS** :
```bash
open ~/Library/Application\ Support/ai-arduino-ide/logs
```

## 🐛 Déboguer un Bug

### Étape 1 : Reproduire le Bug
Effectuez l'action qui cause le problème dans l'application.

### Étape 2 : Noter l'Heure
Notez l'heure approximative où le bug s'est produit.

### Étape 3 : Consulter les Logs

**Pour les erreurs backend** :
```batch
view_logs.bat
# Choisir option 2 (Erreurs Backend)
```

**Pour les erreurs frontend** :
Ouvrez le dossier Electron logs et consultez `electron_errors_YYYY-MM-DD.log`

### Étape 4 : Analyser

Recherchez les entrées autour de l'heure du bug :
- Les messages `ERROR` indiquent les erreurs
- Les stack traces montrent où l'erreur s'est produite
- Les messages `DEBUG` donnent le contexte

### Exemple de Log d'Erreur

```
2026-05-12 14:30:45 - backend - ERROR - [main.py:234] - Compile Error: arduino-cli not found
Traceback (most recent call last):
  File "main.py", line 230, in compile_sketch
    result = subprocess.run(cmd, capture_output=True, text=True)
FileNotFoundError: [WinError 2] Le fichier spécifié est introuvable
```

Cela indique clairement que `arduino-cli` n'est pas installé ou pas dans le PATH.

## 📊 Format des Logs

```
YYYY-MM-DD HH:MM:SS - LOGGER - LEVEL - [fichier:ligne] - Message
```

**Niveaux de log** :
- `DEBUG` : Informations détaillées pour le débogage
- `INFO` : Informations générales sur le fonctionnement
- `WARNING` : Avertissements (pas d'erreur mais attention)
- `ERROR` : Erreurs qui empêchent une opération
- `CRITICAL` : Erreurs critiques qui peuvent arrêter l'application

## 🔄 Rotation des Fichiers

- **Nouveaux fichiers** : Créés automatiquement chaque jour
- **Taille maximale** : 10 MB par fichier
- **Fichiers de backup** : 5 fichiers conservés
- **Nommage** : Inclut la date (YYYYMMDD ou YYYY-MM-DD)

Quand un fichier atteint 10 MB :
```
backend_20260512.log       → backend_20260512.log.1
backend_20260512.log.1     → backend_20260512.log.2
...
backend_20260512.log.5     → supprimé
```

## 🧹 Nettoyage

### Automatique
Les fichiers sont automatiquement archivés quand ils dépassent 10 MB.

### Manuel
Pour nettoyer les anciens logs :

**Avec le script** :
```batch
view_logs.bat
# Choisir option 7 (Nettoyer)
```

**Manuellement** :
```batch
# Supprimer les logs de plus de 7 jours
forfiles /p logs /s /m *.log /d -7 /c "cmd /c del @path"
```

## 📝 Exemples de Logs

### Requête AI Réussie
```
2026-05-12 14:30:45 - backend - INFO - [main.py:123] - API Request: POST /ai/generate - Params: {'provider': 'openrouter', 'board': 'arduino:avr:uno'}
2026-05-12 14:30:45 - backend - INFO - [agents.py:85] - Generating code with provider: openrouter, board: arduino:avr:uno, tools: True
2026-05-12 14:30:46 - backend - INFO - [agents.py:110] - AI wants to use 2 tool(s)
2026-05-12 14:30:46 - backend - INFO - [agents.py:118] - Executing tool: analyze_code
2026-05-12 14:30:46 - backend - INFO - [agents.py:123] - Tool result: success
2026-05-12 14:30:47 - backend - INFO - [main.py:145] - AI generation completed - Response length: 1234
```

### Erreur de Compilation
```
2026-05-12 14:35:20 - backend - INFO - [main.py:89] - API Request: POST /compile - Params: {'board': 'arduino:avr:uno', 'code_length': 456}
2026-05-12 14:35:20 - backend - INFO - [main.py:102] - Using CLI: C:\...\arduino-cli.exe
2026-05-12 14:35:21 - backend - ERROR - [main.py:108] - Compile Error: exit status 1
Compilation error: 'Serial' was not declared in this scope
```

### Opération Fichier Frontend
```
2026-05-12 14:40:10 - INFO - Ouverture du dossier: C:\Users\...\Arduino
2026-05-12 14:40:10 - INFO - Dossier ouvert: C:\Users\...\Arduino
2026-05-12 14:40:10 - INFO - Total de fichiers trouvés: 23
2026-05-12 14:40:15 - DEBUG - Lecture du fichier: C:\Users\...\Arduino\sketch.ino
2026-05-12 14:40:20 - DEBUG - Sauvegarde du fichier: C:\Users\...\Arduino\sketch.ino
2026-05-12 14:40:20 - INFO - Fichier sauvegardé: C:\Users\...\Arduino\sketch.ino
```

## 🔐 Sécurité

⚠️ **Attention** : Les logs peuvent contenir des informations sensibles :
- Chemins de fichiers
- Noms de projets
- Fragments de code

**Ne partagez pas vos logs publiquement** sans les avoir vérifiés.

Pour partager des logs pour le débogage :
1. Ouvrez le fichier de log
2. Supprimez les informations personnelles
3. Gardez uniquement les parties pertinentes au bug

## 📚 Ressources

- **Documentation complète** : `logs/README.md`
- **Script de visualisation** : `view_logs.bat`
- **Configuration backend** : `backend/logger_config.py`
- **Configuration frontend** : `frontend/electron/main.cjs` (lignes 1-50)

## ✅ Avantages

✨ **Débogage facile** : Tous les événements sont enregistrés
✨ **Historique complet** : Logs conservés avec rotation automatique
✨ **Séparation des erreurs** : Fichiers dédiés pour les erreurs
✨ **Performance** : Logging asynchrone, pas d'impact sur l'application
✨ **Recherche rapide** : Format structuré avec timestamps
✨ **Multi-plateforme** : Fonctionne sur Windows, Linux, macOS

## 🚀 Prochaines Étapes

1. **Lancez l'application** : Les logs commencent automatiquement
2. **Utilisez normalement** : Toutes les actions sont enregistrées
3. **En cas de bug** : Consultez les logs avec `view_logs.bat`
4. **Corrigez** : Utilisez les informations des logs pour identifier le problème

---

**Note** : Le système de logging est maintenant actif. Tous les événements sont automatiquement enregistrés dès le démarrage de l'application.
