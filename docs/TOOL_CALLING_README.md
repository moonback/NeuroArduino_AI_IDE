# 🛠️ AI Tool Calling System - README

## 🎯 Vue d'Ensemble

Le système de Tool Calling permet à l'assistant IA de NeuroArduino IDE d'interagir directement avec le système de fichiers. L'IA peut créer, modifier, lire et gérer des fichiers de manière autonome, transformant l'IDE en un véritable assistant de développement actif.

---

## ✨ Fonctionnalités

### 🔧 Outils Disponibles

| Outil | Description | Cas d'Usage |
|-------|-------------|-------------|
| `create_file` | Crée un nouveau fichier | Générer du code Arduino |
| `modify_file` | Modifie un fichier existant | Changer des paramètres, refactoring |
| `read_file` | Lit le contenu d'un fichier | Analyser le code existant |
| `delete_file` | Supprime un fichier | Nettoyer le projet |
| `list_files` | Liste les fichiers | Explorer la structure |
| `create_directory` | Crée un dossier | Organiser le projet |
| `rename_file` | Renomme/déplace un fichier | Réorganiser |

### 🎨 Capacités de l'IA

- ✅ **Création de projets complets** en une seule requête
- ✅ **Modification intelligente** du code existant
- ✅ **Organisation automatique** de la structure de fichiers
- ✅ **Documentation générée** automatiquement
- ✅ **Refactoring** et optimisation du code

---

## 🚀 Démarrage Rapide

### 1. Installation

Le système est déjà intégré dans NeuroArduino IDE. Aucune installation supplémentaire requise.

### 2. Activation

Le Tool Calling est **activé par défaut**. Pour le désactiver :

1. Cliquez sur l'icône 🔧 dans le header du panel IA
2. Le bouton devient gris quand désactivé

### 3. Premier Test

Essayez ce prompt :

```
Crée un fichier blink.ino qui fait clignoter une LED sur la pin 13
```

L'IA va :
1. Créer le fichier `blink.ino`
2. Générer le code Arduino
3. Afficher le résultat dans le chat

---

## 📝 Exemples d'Utilisation

### Exemple 1 : Création Simple

**Prompt** :
```
Crée test.ino avec un simple blink
```

**Résultat** :
- ✅ Fichier `test.ino` créé
- ✅ Code fonctionnel généré
- ✅ Prêt à compiler

### Exemple 2 : Projet Complet

**Prompt** :
```
Crée un projet servo_control avec le code, un README et le schéma de câblage
```

**Résultat** :
```
servo_control/
├── servo_control.ino    # Code principal
├── README.md            # Documentation
└── wiring.txt           # Schéma de câblage
```

### Exemple 3 : Modification

**Prompt** :
```
Dans blink.ino, change le délai à 500ms
```

**Résultat** :
- ✅ Fichier lu
- ✅ Délai modifié
- ✅ Fichier sauvegardé

---

## 🔒 Sécurité

### Protections Intégrées

1. **Sandbox** : L'IA ne peut accéder qu'au workspace du projet
2. **Validation des chemins** : Empêche l'accès aux fichiers système
3. **Confirmation** : Les opérations destructives nécessitent confirmation
4. **Limites** : Taille de fichier limitée à 1MB

### Chemins Interdits

- ❌ `/etc`, `/sys`, `/proc` (Linux)
- ❌ `C:\Windows`, `C:\Program Files` (Windows)
- ❌ `../` (Path traversal)

---

## 🧪 Tests

### Test Automatique

Lancez le script de test :

```bash
python test_tool_calling.py
```

Options :
1. **Test Tool Registry** : Teste les outils directement
2. **Test AI Agent** : Teste avec l'IA (nécessite API key)
3. **Interactive Mode** : Mode interactif pour tester manuellement

### Test Manuel

1. Démarrez l'IDE
2. Ouvrez le panel IA
3. Essayez les prompts d'exemple dans `EXAMPLE_PROMPTS.md`

### Tests Unitaires

```bash
cd backend
pytest tests/test_tools.py -v
```

---

## 📚 Documentation

### Fichiers de Documentation

- **[AI_TOOL_CALLING.md](AI_TOOL_CALLING.md)** : Documentation technique complète
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** : Guide d'intégration
- **[EXAMPLE_PROMPTS.md](EXAMPLE_PROMPTS.md)** : 100+ exemples de prompts

### API Reference

Voir `backend/tools_registry.py` pour la documentation des outils.

---

## 🐛 Dépannage

### Problème : L'IA ne crée pas de fichiers

**Solution** :
1. Vérifiez que le Tool Calling est activé (icône 🔧)
2. Vérifiez les logs du backend
3. Essayez avec un prompt plus explicite

### Problème : Erreur "Path outside workspace"

**Solution** :
- Utilisez des chemins relatifs uniquement
- Ne commencez pas par `/` ou `C:\`
- Évitez `../`

### Problème : Fichier non trouvé

**Solution** :
1. Vérifiez que le fichier existe avec `list_files`
2. Utilisez le chemin relatif correct
3. Vérifiez l'orthographe du nom de fichier

---

## 🎯 Bonnes Pratiques

### ✅ À Faire

- Soyez spécifique dans vos prompts
- Demandez la création de documentation
- Organisez votre code en modules
- Utilisez des noms de fichiers descriptifs

### ❌ À Éviter

- Prompts trop vagues
- Chemins absolus
- Noms de fichiers avec caractères spéciaux
- Fichiers trop volumineux (>1MB)

---

## 🔄 Workflow Recommandé

### 1. Planification

```
Crée la structure de mon projet capteur_temperature avec tous les dossiers nécessaires
```

### 2. Développement

```
Crée le code principal dans src/main.ino pour lire un capteur DHT22
```

### 3. Documentation

```
Crée un README.md complet avec le câblage et les instructions
```

### 4. Tests

```
Crée un fichier de tests dans tests/test_sensor.ino
```

### 5. Finalisation

```
Crée un CHANGELOG.md avec l'historique des versions
```

---

## 📊 Statistiques

### Capacités Actuelles

- **7 outils** disponibles
- **Support multi-provider** (Groq, Gemini)
- **Validation de sécurité** complète
- **Interface utilisateur** intuitive

### Performance

- Création de fichier : ~50ms
- Modification : ~100ms
- Lecture : ~30ms
- Opérations complexes : ~500ms

---

## 🚀 Roadmap

### Version 1.1 (Prochaine)

- [ ] Undo/Redo des modifications
- [ ] Diff viewer avant application
- [ ] Confirmation UI pour actions destructives
- [ ] Historique des opérations

### Version 1.2

- [ ] Batch operations (modifier plusieurs fichiers)
- [ ] Template system
- [ ] Git integration
- [ ] Code review automatique

### Version 2.0

- [ ] Multi-file refactoring
- [ ] AI-powered code analysis
- [ ] Collaborative editing
- [ ] Cloud sync

---

## 🤝 Contribution

### Comment Contribuer

1. **Ajouter un outil** :
   - Définir dans `tools_registry.py`
   - Implémenter la logique
   - Ajouter les tests
   - Documenter

2. **Améliorer l'IA** :
   - Optimiser les prompts
   - Ajouter des exemples
   - Améliorer le parsing

3. **Documentation** :
   - Ajouter des exemples
   - Traduire
   - Créer des tutoriels

---

## 📞 Support

### Besoin d'Aide ?

- 📖 **Documentation** : Consultez les fichiers dans `docs/`
- 🐛 **Bug** : Ouvrez une issue sur GitHub
- 💬 **Question** : Utilisez GitHub Discussions
- 📧 **Contact** : support@neuroarduino.dev

---

## 📜 Licence

Ce système est sous licence MIT. Voir [LICENSE](../LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **OpenAI** pour le concept de Function Calling
- **Anthropic** pour l'inspiration Tool Use
- **Groq** et **Google** pour les APIs IA
- **Communauté Arduino** pour le support

---

<div align="center">

**Fait avec ❤️ par l'équipe NeuroArduino**

⭐ **N'oubliez pas de mettre une étoile si vous aimez le projet !** ⭐

[⬆ Retour en haut](#-ai-tool-calling-system---readme)

</div>
