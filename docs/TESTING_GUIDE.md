# Guide de Test des Corrections Critiques

## 🎯 Objectif
Vérifier que les 3 bugs critiques ont été corrigés :
1. ✅ OpenRouter NoneType
2. ✅ smart_modify_file erreurs silencieuses
3. ✅ Electron fermeture immédiate

---

## 📋 Prérequis

```bash
# 1. Vérifier les variables d'environnement
cd backend
cat .env

# Doit contenir :
# OPENROUTER_API_KEY=sk-or-v1-...
# GEMINI_API_KEY=... (optionnel)
```

---

## 🧪 Test 1 : smart_modify_file Error Handling

### Test Automatique
```bash
cd backend
python test_critical_fixes.py
```

### Ce que vous devriez voir :
```
TEST 1: smart_modify_file Error Handling
=========================================
✓ Created test file: test_workspace/test.ino

--- Test 1a: Pattern not found ---
[DEBUG] Searching for: delay(2000);...
[DEBUG] Search found in content: False
[WARNING] Search pattern not found in file
Status: error
✓ Error correctly detected
Error message: Modification 0: Search text not found in file...
✓ Search pattern included in error: delay(2000);
✓ File preview included in error

--- Test 1b: Successful modification ---
[DEBUG] Searching for: delay(1000);...
[DEBUG] Search found in content: True
[DEBUG] Replaced 1 occurrence(s)
Status: success
✓ Modification successful

--- Test 1c: Pattern no longer exists after modification ---
[DEBUG] Searching for: delay(1000);...
[DEBUG] Search found in content: False
Status: error
✓ Error correctly detected (pattern was already modified)
```

### ✅ Succès si :
- Les erreurs sont détectées avec messages explicites
- Les logs `[DEBUG]` apparaissent
- Le preview du fichier est inclus dans les erreurs
- Les modifications réussies sont confirmées

---

## 🧪 Test 2 : OpenRouter NoneType Handling

### Test Automatique
```bash
cd backend
python test_critical_fixes.py
```

### Ce que vous devriez voir :
```
TEST 2: OpenRouter NoneType Handling
====================================
✓ OPENROUTER_API_KEY found
✓ CodeGeneratorAgent initialized

--- Test 2a: Simple code generation ---
✓ Request completed
Message present: True
Code present: True
✓ Response handling works correctly

--- Test 2b: Tool calling enabled ---
[DEBUG] Calling OpenRouter with tools enabled
[DEBUG] Number of tools available: 9
[DEBUG] Content: I'll help you add LED blink code...
[DEBUG] Response has tool_calls: True
[DEBUG] AI wants to use 1 tool(s)
[DEBUG] Executing tool: smart_modify_file
[DEBUG] Tool result: success
✓ Request completed
Tool calls: 1
✓ Tool calling works
  - Tool: smart_modify_file
```

### ✅ Succès si :
- Aucune erreur `NoneType`
- Les logs `[DEBUG] Content:` montrent le contenu (ou "None" géré)
- Les tool calls fonctionnent
- Les messages sont présents même si `content = None`

### Test Manuel avec l'Application

1. **Démarrer le backend** :
```bash
cd backend
python main.py
```

2. **Démarrer le frontend** :
```bash
cd frontend
npm run dev
```

3. **Démarrer Electron** :
```bash
cd frontend
npm run electron:dev
```

4. **Dans l'application** :
   - Créer un fichier `test.ino`
   - Demander à l'IA : "Add LED blink code"
   - Vérifier les logs backend :
```
[DEBUG] Calling OpenRouter with tools enabled
[DEBUG] Content: I'll add LED blink code...
[DEBUG] Response has tool_calls: True
[DEBUG] Executing tool: smart_modify_file
[DEBUG] Searching for: void setup()...
[DEBUG] Search found in content: True
[DEBUG] Tool result: success
```

### ✅ Succès si :
- Aucune erreur `expected string or bytes-like object, got 'NoneType'`
- Les modifications de fichiers fonctionnent
- Les messages de l'IA s'affichent correctement

---

## 🧪 Test 3 : Electron Lifecycle

### Test Manuel

1. **Démarrer Vite dev server** :
```bash
cd frontend
npm run dev
```
Attendre :
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

2. **Dans un autre terminal, démarrer Electron** :
```bash
cd frontend
npm run electron:dev
```

### Ce que vous devriez voir dans la console :

```
[DEBUG] createWindow() called
[DEBUG] BrowserWindow created
[DEBUG] Loading from dev server: http://localhost:5173
Development mode: Backend should be running externally.
[DEBUG] createWindow() completed
[DEBUG] Page finished loading
```

### ✅ Succès si :
- La fenêtre Electron s'ouvre
- La fenêtre reste ouverte (ne se ferme pas immédiatement)
- L'interface se charge correctement
- Aucun message `[DEBUG] All windows closed event triggered` immédiat
- Aucun message `[DEBUG] Quitting app`

### ❌ Échec si vous voyez :
```
[DEBUG] createWindow() called
[DEBUG] BrowserWindow created
[DEBUG] Loading from dev server: http://localhost:5173
[DEBUG] All windows closed event triggered
[DEBUG] Quitting app (not macOS)
[DEBUG] App is about to quit
```

### Diagnostic en cas d'échec :

1. **Vérifier que Vite tourne** :
```bash
curl http://localhost:5173
# Devrait retourner du HTML
```

2. **Vérifier ELECTRON_START_URL** :
```bash
# Dans frontend/package.json, section "scripts":
"electron:dev": "cross-env ELECTRON_START_URL=http://localhost:5173 electron ."
```

3. **Chercher les erreurs de chargement** :
```
[ERROR] Page failed to load: -3 ERR_ABORTED
[ERROR] Page failed to load: -102 ERR_CONNECTION_REFUSED
```

4. **Vérifier les événements de fermeture** :
```
[DEBUG] Window close event
[DEBUG] Window closed event
```

---

## 🔍 Logs à Surveiller

### Backend (terminal backend) :
```bash
cd backend
python main.py

# Logs attendus :
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000

# Lors d'une requête IA :
[DEBUG] Calling OpenRouter with tools enabled
[DEBUG] Content: ...
[DEBUG] Response has tool_calls: True/False
[DEBUG] Executing tool: ...
[DEBUG] Searching for: ...
[DEBUG] Search found in content: True/False
[DEBUG] Tool result: success/error
```

### Frontend Vite (terminal frontend) :
```bash
cd frontend
npm run dev

# Logs attendus :
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Electron (terminal electron) :
```bash
cd frontend
npm run electron:dev

# Logs attendus :
[DEBUG] createWindow() called
[DEBUG] BrowserWindow created
[DEBUG] Loading from dev server: http://localhost:5173
[DEBUG] Page finished loading
[DEBUG] createWindow() completed
```

---

## 📊 Checklist de Validation

### ✅ Test 1 : smart_modify_file
- [ ] Les erreurs sont détectées et loggées
- [ ] Les messages d'erreur sont explicites
- [ ] Le preview du fichier est inclus
- [ ] Les patterns manquants sont identifiés
- [ ] Les modifications réussies sont confirmées

### ✅ Test 2 : OpenRouter
- [ ] Aucune erreur `NoneType`
- [ ] Les réponses vides sont gérées
- [ ] Les tool calls fonctionnent
- [ ] Les logs `[DEBUG] Content:` apparaissent
- [ ] Les messages sont toujours présents

### ✅ Test 3 : Electron
- [ ] La fenêtre s'ouvre
- [ ] La fenêtre reste ouverte
- [ ] La page se charge
- [ ] Les logs de cycle de vie apparaissent
- [ ] Aucune fermeture immédiate

---

## 🐛 Problèmes Connus et Solutions

### Problème : "Search pattern not found"
**Cause** : Le fichier a déjà été modifié
**Solution** : Vérifier le contenu actuel du fichier avec `read_file` avant de modifier

### Problème : "NoneType object has no attribute"
**Cause** : OpenRouter retourne `content = None`
**Solution** : ✅ Corrigé - le code utilise maintenant `content or ""`

### Problème : Electron se ferme immédiatement
**Causes possibles** :
1. Vite dev server pas démarré → `npm run dev` d'abord
2. ELECTRON_START_URL incorrect → vérifier package.json
3. Page ne charge pas → vérifier les logs `did-fail-load`

**Solution** : ✅ Logs ajoutés pour identifier la cause exacte

---

## 📝 Rapport de Test

Après avoir exécuté tous les tests, remplir ce rapport :

```
Date : ___________
Testeur : ___________

Test 1 - smart_modify_file :
[ ] ✅ Réussi
[ ] ❌ Échoué - Détails : ___________

Test 2 - OpenRouter :
[ ] ✅ Réussi
[ ] ❌ Échoué - Détails : ___________

Test 3 - Electron :
[ ] ✅ Réussi
[ ] ❌ Échoué - Détails : ___________

Observations :
___________________________________________
___________________________________________
___________________________________________

Bugs additionnels découverts :
___________________________________________
___________________________________________
___________________________________________
```

---

## 🚀 Prochaines Étapes

Si tous les tests passent :
1. ✅ Système prêt pour utilisation
2. 📝 Documenter les cas d'usage
3. 🔧 Implémenter les améliorations recommandées (voir CRITICAL_FIXES_APPLIED.md)

Si des tests échouent :
1. 🔍 Analyser les logs
2. 🐛 Identifier la cause racine
3. 🔧 Appliquer les corrections
4. 🔄 Re-tester

---

## 📞 Support

En cas de problème :
1. Vérifier les logs dans les 3 terminaux (backend, frontend, electron)
2. Consulter `CRITICAL_FIXES_APPLIED.md` pour les détails techniques
3. Vérifier les variables d'environnement (`.env`)
4. Tester avec les scripts automatiques (`test_critical_fixes.py`)
