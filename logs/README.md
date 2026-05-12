# Dossier des Logs

Ce dossier contient tous les fichiers de log de l'application AI Arduino IDE.

## Structure des Logs

### Backend (Python)
- **backend_YYYYMMDD.log** : Tous les logs du backend (DEBUG, INFO, WARNING, ERROR)
- **backend_errors_YYYYMMDD.log** : Uniquement les erreurs (ERROR, CRITICAL)

### Frontend (Electron)
Les logs Electron sont sauvegardés dans le dossier userData de l'application :
- **Windows** : `%APPDATA%\ai-arduino-ide\logs\`
- **Linux** : `~/.config/ai-arduino-ide/logs/`
- **macOS** : `~/Library/Application Support/ai-arduino-ide/logs/`

Fichiers :
- **electron_YYYY-MM-DD.log** : Tous les logs du frontend
- **electron_errors_YYYY-MM-DD.log** : Uniquement les erreurs

## Rotation des Fichiers

- Les fichiers de log sont créés quotidiennement avec la date dans le nom
- Taille maximale par fichier : 10 MB
- Nombre de fichiers de backup : 5
- Les anciens fichiers sont automatiquement archivés

## Que Contiennent les Logs ?

### Backend
- Requêtes API (endpoints, méthodes, paramètres)
- Appels d'outils AI (tool calling)
- Requêtes AI (provider, longueur des prompts/réponses)
- Compilation et upload Arduino
- Connexions série
- Erreurs avec stack traces complets

### Frontend
- Démarrage de l'application
- Chargement des fenêtres
- Opérations sur les fichiers (lecture, écriture, création)
- Ouverture de dossiers
- Processus backend (démarrage, arrêt, erreurs)
- Erreurs de chargement de page

## Comment Utiliser les Logs pour Déboguer

1. **Reproduire le bug** : Effectuez l'action qui cause le problème
2. **Identifier l'heure** : Notez l'heure approximative du bug
3. **Consulter les logs** :
   - Pour les erreurs backend : `backend_errors_YYYYMMDD.log`
   - Pour les erreurs frontend : `electron_errors_YYYY-MM-DD.log`
   - Pour le contexte complet : fichiers principaux
4. **Rechercher** : Utilisez l'heure pour trouver les entrées pertinentes
5. **Analyser** : Les stack traces et messages d'erreur vous guideront

## Exemple de Recherche

```bash
# Rechercher une erreur spécifique dans les logs backend
grep -i "error" backend_20260512.log

# Voir les dernières lignes du log
tail -n 50 backend_20260512.log

# Rechercher toutes les requêtes AI
grep "AI Request" backend_20260512.log
```

## Nettoyage

Les logs peuvent devenir volumineux. Pour nettoyer :
- Supprimez manuellement les anciens fichiers .log
- Ou gardez uniquement les 7 derniers jours

## Format des Logs

```
YYYY-MM-DD HH:MM:SS - LOGGER_NAME - LEVEL - [fichier.py:ligne] - Message
```

Exemple :
```
2026-05-12 14:30:45 - backend - INFO - [main.py:123] - API Request: POST /ai/generate - Params: {'provider': 'groq'}
```
