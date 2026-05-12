# Scripts Utiles - AI Arduino IDE

## 📋 Liste des Scripts

Voici tous les scripts disponibles pour gérer l'application :

---

## 🚀 Scripts de Démarrage

### `start_dev.bat` - Démarrage Normal
Lance l'application en mode développement.

**Utilisation** :
```bash
start_dev.bat
```

**Ce qu'il fait** :
1. Vérifie et installe les dépendances backend (Python)
2. Vérifie et installe les dépendances frontend (Node)
3. Lance le backend sur le port 8001
4. Lance Electron avec Vite

**Quand l'utiliser** :
- Première fois que vous lancez l'application
- Démarrage normal après un arrêt propre

---

### `start_clean.bat` - Démarrage Propre (RECOMMANDÉ)
Nettoie tous les processus existants avant de lancer l'application.

**Utilisation** :
```bash
start_clean.bat
```

**Ce qu'il fait** :
1. Arrête tous les processus Python, Node et Electron
2. Vérifie que les ports 8001 et 5173 sont libres
3. Lance `start_dev.bat`

**Quand l'utiliser** :
- Quand vous avez l'erreur `[WinError 10013]`
- Après un crash de l'application
- Quand vous n'êtes pas sûr si des processus tournent encore
- **RECOMMANDÉ pour éviter les problèmes**

---

## 🛑 Scripts d'Arrêt

### `stop_all.bat` - Arrêt Complet
Arrête tous les processus liés à l'application.

**Utilisation** :
```bash
stop_all.bat
```

**Ce qu'il fait** :
1. Arrête tous les processus Python
2. Arrête tous les processus Node
3. Arrête tous les processus Electron
4. Ferme les fenêtres de terminal

**Quand l'utiliser** :
- Avant de fermer votre ordinateur
- Quand vous voulez arrêter complètement l'application
- Avant de relancer avec `start_clean.bat`

---

### `kill_backend.bat` - Arrêt Backend Uniquement
Arrête uniquement les processus backend sur les ports 8000 et 8001.

**Utilisation** :
```bash
kill_backend.bat
```

**Ce qu'il fait** :
1. Trouve les processus sur le port 8000
2. Trouve les processus sur le port 8001
3. Les arrête

**Quand l'utiliser** :
- Quand seul le backend pose problème
- Quand vous voulez garder le frontend actif
- Pour libérer rapidement les ports

---

## 🔍 Scripts de Diagnostic

### `check_ports.bat` - Vérification des Ports
Vérifie l'état des ports utilisés par l'application.

**Utilisation** :
```bash
check_ports.bat
```

**Ce qu'il affiche** :
- État du port 8000 (backend alternatif)
- État du port 8001 (backend principal)
- État du port 5173 (Vite dev server)
- Liste des processus Python en cours
- Liste des processus Node en cours

**Quand l'utiliser** :
- Avant de lancer l'application
- Pour diagnostiquer un problème de port occupé
- Pour vérifier que tout est bien arrêté

---

## 🏗️ Scripts de Build

### `build_app.bat` - Compilation pour Distribution
Compile l'application pour la distribution (version standalone).

**Utilisation** :
```bash
build_app.bat
```

**Ce qu'il fait** :
1. Installe PyInstaller et les dépendances
2. Compile le backend Python en .exe
3. Build le frontend React
4. Package l'application Electron
5. Crée un installateur dans `frontend/dist_app/`

**Quand l'utiliser** :
- Quand vous voulez créer une version distribuable
- Pour tester la version production
- Pour partager l'application avec d'autres

---

## 📊 Tableau Récapitulatif

| Script | Usage | Quand l'utiliser |
|--------|-------|------------------|
| `start_dev.bat` | Démarrage normal | Première fois, démarrage après arrêt propre |
| `start_clean.bat` | Démarrage propre | **RECOMMANDÉ**, après crash, si erreur port |
| `stop_all.bat` | Arrêt complet | Avant de fermer PC, arrêt complet |
| `kill_backend.bat` | Arrêt backend | Problème de port backend uniquement |
| `check_ports.bat` | Diagnostic | Vérifier état des ports, diagnostiquer |
| `build_app.bat` | Compilation | Créer version distribuable |

---

## 🔄 Workflows Recommandés

### Workflow 1 : Démarrage Quotidien (RECOMMANDÉ)
```bash
# Toujours utiliser le démarrage propre
start_clean.bat
```

### Workflow 2 : Après un Crash
```bash
# 1. Arrêter tout
stop_all.bat

# 2. Vérifier les ports
check_ports.bat

# 3. Redémarrer proprement
start_clean.bat
```

### Workflow 3 : Problème de Port
```bash
# 1. Diagnostic
check_ports.bat

# 2. Tuer le backend
kill_backend.bat

# 3. Redémarrer
start_dev.bat
```

### Workflow 4 : Fin de Journée
```bash
# Arrêt complet avant de fermer le PC
stop_all.bat
```

### Workflow 5 : Build pour Distribution
```bash
# 1. Arrêter tout
stop_all.bat

# 2. Build
build_app.bat

# 3. Tester l'installateur dans frontend/dist_app/
```

---

## ⚠️ Erreurs Courantes et Solutions

### Erreur : `[WinError 10013]`
**Cause** : Port 8001 déjà utilisé

**Solution** :
```bash
start_clean.bat
```

### Erreur : `Port 5173 is already in use`
**Cause** : Vite dev server déjà lancé

**Solution** :
```bash
stop_all.bat
start_clean.bat
```

### Erreur : `Module not found`
**Cause** : Dépendances manquantes

**Solution** :
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Erreur : `Cannot find module 'electron'`
**Cause** : Electron pas installé

**Solution** :
```bash
cd frontend
npm install
```

---

## 💡 Conseils et Astuces

### Astuce 1 : Créer des Raccourcis
Créez des raccourcis sur votre bureau pour un accès rapide :
- Clic droit sur `start_clean.bat` → "Créer un raccourci"
- Renommez en "🚀 Lancer AI Arduino IDE"

### Astuce 2 : Toujours Utiliser start_clean.bat
Pour éviter 99% des problèmes, utilisez toujours `start_clean.bat` au lieu de `start_dev.bat`.

### Astuce 3 : Vérifier Avant de Lancer
Prenez l'habitude de vérifier les ports avant de lancer :
```bash
check_ports.bat
```

### Astuce 4 : Arrêt Propre
Utilisez toujours Ctrl+C dans les terminaux au lieu de fermer les fenêtres brutalement.

### Astuce 5 : Logs de Debug
Gardez les fenêtres de terminal ouvertes pour voir les logs en cas de problème.

---

## 🆘 Aide Rapide

**Problème** : L'application ne démarre pas
```bash
start_clean.bat
```

**Problème** : Port occupé
```bash
kill_backend.bat
```

**Problème** : Tout est cassé
```bash
stop_all.bat
# Attendre 5 secondes
start_clean.bat
```

**Problème** : Rien ne fonctionne
```bash
# Solution radicale
stop_all.bat
# Redémarrer votre ordinateur
# Puis
start_clean.bat
```

---

## 📚 Documentation Complète

Pour plus de détails sur le dépannage, consultez :
- `DEPANNAGE_PORTS.md` - Guide complet de dépannage des ports
- `README.md` - Documentation générale du projet

---

## ✅ Checklist de Démarrage

Avant chaque démarrage, vérifiez :

- [ ] Aucune fenêtre de terminal ouverte avec l'application
- [ ] Aucun processus Python/Node/Electron en cours (`check_ports.bat`)
- [ ] Vous êtes dans le bon dossier (racine du projet)
- [ ] Les dépendances sont installées

Puis lancez :
```bash
start_clean.bat
```

---

## 🎉 Résumé

**Pour 99% des cas, utilisez simplement** :
```bash
start_clean.bat
```

**Pour arrêter** :
```bash
stop_all.bat
```

**En cas de problème** :
```bash
check_ports.bat
```

C'est tout ! 🚀
