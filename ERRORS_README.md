# 🚨 Fichier Centralisé des Erreurs - ERRORS.txt

## 📋 Description

Le fichier `ERRORS.txt` à la racine du projet contient **TOUTES les erreurs** de l'application en temps réel, provenant du backend ET du frontend.

## 🎯 Pourquoi ce fichier ?

✅ **Un seul endroit** pour voir toutes les erreurs  
✅ **Accès rapide** sans chercher dans plusieurs dossiers  
✅ **Format simple** facile à lire  
✅ **Mise à jour automatique** en temps réel  
✅ **Historique complet** de toutes les erreurs depuis le démarrage  

## 📍 Emplacement

```
Arduino_AI_IDE/
├── ERRORS.txt          ← TOUTES LES ERREURS ICI
├── logs/
│   ├── backend_20260512.log
│   └── backend_errors_20260512.log
└── ...
```

## 📝 Format du Fichier

### Erreurs Backend
```
================================================================================
2026-05-12 14:30:45 - ERROR - [BACKEND] generate_code
Type: HTTPException
Message: Compilation Failed: exit status 1
================================================================================
```

### Erreurs Frontend
```
2026-05-12 14:35:20 - ERROR - [FRONTEND] Erreur lecture fichier C:\...\sketch.ino: ENOENT
```

## 🔍 Comment Utiliser

### 1. Visualisation Rapide

**Avec le script** (recommandé) :
```batch
view_errors.bat
```

Menu interactif avec 9 options :
1. Voir toutes les erreurs
2. Voir les 20 dernières erreurs
3. Voir les 50 dernières erreurs
4. Rechercher une erreur spécifique
5. Compter le nombre d'erreurs
6. Voir uniquement les erreurs CRITICAL
7. Voir uniquement les erreurs Backend
8. Voir uniquement les erreurs Frontend
9. Effacer toutes les erreurs (réinitialiser)

**Manuellement** :
```batch
# Voir tout le fichier
type ERRORS.txt

# Voir les dernières erreurs
powershell -Command "Get-Content ERRORS.txt -Tail 20"

# Rechercher un terme
findstr /i "compilation" ERRORS.txt
```

### 2. Déboguer un Problème

**Scénario** : L'application plante lors de la compilation

1. **Reproduisez le bug** : Essayez de compiler le sketch
2. **Ouvrez ERRORS.txt** : 
   ```batch
   view_errors.bat
   # Choisir option 2 (20 dernières erreurs)
   ```
3. **Identifiez l'erreur** : Cherchez l'erreur la plus récente
4. **Analysez** : Le message vous indique le problème exact
5. **Corrigez** : Utilisez l'information pour corriger le bug

### 3. Statistiques

Pour voir un résumé des erreurs :
```batch
view_errors.bat
# Choisir option 5 (Compter)
```

Affiche :
- Nombre total d'erreurs ERROR
- Nombre total d'erreurs CRITICAL
- Nombre d'avertissements
- Répartition Backend/Frontend

## 📊 Types d'Erreurs

### ERROR
Erreur qui empêche une opération mais l'application continue.

**Exemples** :
- Échec de compilation d'un sketch
- Fichier introuvable
- Port série non disponible
- Erreur de connexion API

### CRITICAL
Erreur critique qui peut arrêter l'application.

**Exemples** :
- Crash du backend
- Erreur de mémoire
- Corruption de données
- Échec de démarrage

### WARNING
Avertissement, pas une erreur mais nécessite attention.

**Exemples** :
- Clé API manquante
- Fichier de configuration non trouvé
- Timeout de requête

## 🔄 Rotation et Nettoyage

### Rotation Automatique
- **Taille maximale** : 5 MB
- **Fichiers de backup** : 3 (ERRORS.txt.1, ERRORS.txt.2, ERRORS.txt.3)
- **Automatique** : Quand le fichier atteint 5 MB

### Nettoyage Manuel

**Avec le script** :
```batch
view_errors.bat
# Choisir option 9 (Effacer)
```

**Manuellement** :
```batch
# Supprimer le contenu mais garder l'en-tête
del ERRORS.txt
# Le fichier sera recréé automatiquement au prochain démarrage
```

## 🎨 Exemples d'Utilisation

### Exemple 1 : Trouver les erreurs de compilation
```batch
view_errors.bat
# Option 4 (Rechercher)
# Entrer: "compilation"
```

### Exemple 2 : Voir uniquement les erreurs critiques
```batch
view_errors.bat
# Option 6 (CRITICAL uniquement)
```

### Exemple 3 : Comparer Backend vs Frontend
```batch
view_errors.bat
# Option 5 (Statistiques)
```

Résultat :
```
Total d'erreurs ERROR   : 15
Total d'erreurs CRITICAL: 2
Total d'avertissements  : 8

Erreurs Backend         : 12
Erreurs Frontend        : 5
```

### Exemple 4 : Surveiller en temps réel
```batch
# Windows PowerShell
Get-Content ERRORS.txt -Wait -Tail 10

# Affiche les 10 dernières lignes et attend les nouvelles
```

## 🔗 Relation avec les Autres Logs

Le fichier `ERRORS.txt` est un **résumé** des erreurs. Pour plus de détails :

### Backend
- **Logs complets** : `logs/backend_YYYYMMDD.log`
- **Erreurs détaillées** : `logs/backend_errors_YYYYMMDD.log`
- **Contient** : Stack traces, contexte, paramètres

### Frontend
- **Logs complets** : `%APPDATA%\ai-arduino-ide\logs\electron_YYYY-MM-DD.log`
- **Erreurs détaillées** : `%APPDATA%\ai-arduino-ide\logs\electron_errors_YYYY-MM-DD.log`
- **Contient** : Événements système, opérations fichiers

## 📈 Workflow de Débogage

```
1. Bug détecté
   ↓
2. Ouvrir ERRORS.txt (view_errors.bat)
   ↓
3. Identifier l'erreur récente
   ↓
4. Si besoin de plus de détails:
   - Backend: logs/backend_errors_YYYYMMDD.log
   - Frontend: Electron logs
   ↓
5. Corriger le bug
   ↓
6. Tester
   ↓
7. Vérifier que l'erreur ne réapparaît pas dans ERRORS.txt
```

## 🛠️ Maintenance

### Quotidienne
- Vérifier `ERRORS.txt` pour les nouvelles erreurs
- Pas besoin de nettoyer (rotation automatique)

### Hebdomadaire
- Analyser les erreurs récurrentes
- Identifier les patterns
- Prioriser les corrections

### Mensuelle
- Nettoyer les anciens backups si nécessaire
- Archiver les logs importants

## ⚠️ Bonnes Pratiques

✅ **À FAIRE** :
- Consulter ERRORS.txt après chaque bug
- Utiliser `view_errors.bat` pour la visualisation
- Garder le fichier pour l'historique
- Analyser les erreurs récurrentes

❌ **À ÉVITER** :
- Ne pas supprimer ERRORS.txt pendant l'exécution
- Ne pas éditer manuellement le fichier
- Ne pas ignorer les erreurs CRITICAL
- Ne pas partager le fichier publiquement (peut contenir des chemins)

## 🔒 Sécurité

⚠️ Le fichier ERRORS.txt peut contenir :
- Chemins de fichiers locaux
- Noms de projets
- Fragments de code
- Informations système

**Ne partagez pas ce fichier publiquement** sans le vérifier.

## 📞 Support

Si vous voyez une erreur que vous ne comprenez pas :

1. **Copiez l'erreur** depuis ERRORS.txt
2. **Consultez les logs détaillés** pour le contexte
3. **Recherchez** l'erreur dans la documentation
4. **Créez un ticket** avec :
   - Le message d'erreur
   - Les étapes pour reproduire
   - Le contexte (logs détaillés)

## 🎯 Résumé

| Fichier | Contenu | Utilisation |
|---------|---------|-------------|
| `ERRORS.txt` | Toutes les erreurs (résumé) | Diagnostic rapide |
| `logs/backend_errors_*.log` | Erreurs backend (détaillé) | Débogage backend |
| `electron_errors_*.log` | Erreurs frontend (détaillé) | Débogage frontend |

**ERRORS.txt = Votre point d'entrée pour le débogage** 🎯

---

**Créé le** : 2026-05-12  
**Dernière mise à jour** : 2026-05-12  
**Version** : 1.0
