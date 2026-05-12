# Guide de Dépannage - Erreur Port Occupé

## 🔴 Erreur : `[WinError 10013]`

Cette erreur signifie qu'un autre processus utilise déjà le port 8001 (ou 8000).

---

## 🔍 Diagnostic

### Étape 1 : Vérifier les ports occupés

Exécutez le script de diagnostic :
```bash
check_ports.bat
```

Ou manuellement dans PowerShell :
```powershell
netstat -ano | findstr :8001
```

Vous verrez quelque chose comme :
```
TCP    0.0.0.0:8001    0.0.0.0:0    LISTENING    12345
```

Le dernier nombre (12345) est le **PID** (Process ID) du processus qui occupe le port.

---

## ✅ Solutions

### Solution 1 : Utiliser le script automatique (RECOMMANDÉ)

Exécutez simplement :
```bash
kill_backend.bat
```

Ce script va :
1. Trouver tous les processus sur les ports 8000 et 8001
2. Les arrêter automatiquement
3. Vous permettre de relancer `start_dev.bat`

### Solution 2 : Arrêter manuellement le processus

#### Méthode A : Avec le PID
```powershell
# Remplacez 12345 par le PID trouvé
taskkill /F /PID 12345
```

#### Méthode B : Arrêter tous les Python
```powershell
taskkill /F /IM python.exe
```

⚠️ **Attention** : Cela arrêtera TOUS les processus Python en cours.

### Solution 3 : Utiliser un port différent

Si vous voulez garder l'ancien backend actif, modifiez le port dans `start_dev.bat` :

```batch
REM Au lieu de --port 8001, utilisez --port 8002
python -m uvicorn main:app --port 8002 --reload
```

Puis modifiez aussi le frontend pour pointer vers le nouveau port :
- Fichier : `frontend/src/services.api.js`
- Changez : `http://localhost:8001` → `http://localhost:8002`

---

## 🔄 Procédure Complète de Redémarrage

### 1. Arrêter tous les processus
```bash
kill_backend.bat
```

### 2. Vérifier que les ports sont libres
```bash
check_ports.bat
```

Vous devriez voir :
```
[OK] Le port 8000 est LIBRE
[OK] Le port 8001 est LIBRE
[OK] Le port 5173 est LIBRE
```

### 3. Relancer l'application
```bash
start_dev.bat
```

---

## 🐛 Problèmes Courants

### Problème 1 : Le script kill_backend.bat ne fonctionne pas

**Solution** : Arrêtez manuellement via le Gestionnaire des tâches
1. Ouvrez le Gestionnaire des tâches (Ctrl+Shift+Esc)
2. Onglet "Détails"
3. Cherchez `python.exe`
4. Clic droit → "Fin de tâche"

### Problème 2 : Le port est toujours occupé après kill

**Cause** : Le processus est bloqué

**Solution** : Redémarrez votre ordinateur (solution radicale mais efficace)

### Problème 3 : Erreur de permission

**Cause** : Vous n'avez pas les droits administrateur

**Solution** : Exécutez le script en tant qu'administrateur
1. Clic droit sur `kill_backend.bat`
2. "Exécuter en tant qu'administrateur"

### Problème 4 : Plusieurs instances de Python

**Cause** : Vous avez lancé `start_dev.bat` plusieurs fois

**Solution** :
```powershell
# Arrêter TOUS les processus Python
taskkill /F /IM python.exe

# Arrêter TOUS les processus Node
taskkill /F /IM node.exe
```

---

## 📋 Checklist de Démarrage

Avant de lancer `start_dev.bat`, vérifiez :

- [ ] Aucun processus Python ne tourne (`tasklist | findstr python.exe`)
- [ ] Le port 8001 est libre (`netstat -ano | findstr :8001`)
- [ ] Le port 5173 est libre (`netstat -ano | findstr :5173`)
- [ ] Vous êtes dans le bon dossier (racine du projet)
- [ ] Les dépendances sont installées (`backend/.installed` existe)

---

## 🚀 Démarrage Propre (Recommandé)

Pour éviter les problèmes, utilisez toujours cette séquence :

```bash
# 1. Nettoyer les processus
kill_backend.bat

# 2. Vérifier les ports
check_ports.bat

# 3. Démarrer l'application
start_dev.bat
```

---

## 🔧 Scripts Utiles

### Créer un raccourci "Démarrage Propre"

Créez un fichier `start_clean.bat` :
```batch
@echo off
echo Nettoyage des processus...
call kill_backend.bat

timeout /t 2 /nobreak >nul

echo Verification des ports...
call check_ports.bat

timeout /t 2 /nobreak >nul

echo Demarrage de l'application...
call start_dev.bat
```

### Créer un raccourci "Arrêt Complet"

Créez un fichier `stop_all.bat` :
```batch
@echo off
echo Arret de tous les processus...

REM Arrêter Python
taskkill /F /IM python.exe 2>nul

REM Arrêter Node
taskkill /F /IM node.exe 2>nul

REM Arrêter Electron
taskkill /F /IM electron.exe 2>nul

echo Tous les processus ont ete arretes.
pause
```

---

## 📞 Support

Si le problème persiste après avoir essayé toutes ces solutions :

1. Vérifiez qu'aucun antivirus ne bloque les ports
2. Vérifiez que le pare-feu Windows autorise Python et Node
3. Essayez de redémarrer votre ordinateur
4. Vérifiez les logs dans les fenêtres de terminal ouvertes

---

## 💡 Prévention

Pour éviter ce problème à l'avenir :

1. **Toujours fermer proprement** : Utilisez Ctrl+C dans les terminaux au lieu de fermer les fenêtres
2. **Un seul start_dev.bat** : Ne lancez pas plusieurs instances
3. **Vérifier avant de lancer** : Utilisez `check_ports.bat` avant chaque démarrage
4. **Utiliser stop_all.bat** : Avant de relancer l'application

---

## ✅ Résolution Rapide

**TL;DR** - Si vous êtes pressé :

```bash
# 1. Tuer tout
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# 2. Attendre 2 secondes
timeout /t 2

# 3. Relancer
start_dev.bat
```

Voilà ! 🎉
