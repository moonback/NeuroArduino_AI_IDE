# NeuroArduino AI IDE 🚀

[![Download](https://img.shields.io/badge/Télécharger-Dernière_Version_Windows-blueviolet?style=for-the-badge&logo=windows)](https://github.com/Darshan736/vibe-coding-projects/releases/latest)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1-green.svg?style=for-the-badge)](https://github.com/Darshan736/vibe-coding-projects/releases)
[![Tool Calling](https://img.shields.io/badge/Tool_Calling-Enabled-orange.svg?style=for-the-badge)](docs/TOOL_CALLING_USER_GUIDE.md)

> **Un IDE Arduino de nouvelle génération propulsé par l'IA**  
> Développez vos projets Arduino en conversant naturellement avec une intelligence artificielle. Inspiré de Cursor, avec une esthétique "Anti-Gravity" moderne.

![NeuroArduino IDE](https://via.placeholder.com/800x400/0b0f14/00e5ff?text=NeuroArduino+AI+IDE)

---

## 🎉 Nouveautés v2.1 - Tool Calling

### 🛠️ L'IA Modifie Vos Fichiers Directement !

**Fini le copier-coller !** L'assistant IA peut maintenant modifier vos fichiers automatiquement :

```
Vous : "Change le délai à 500ms"
IA : ✅ Fait ! Tous les delay() sont maintenant à 500ms.
     [Fichier mis à jour automatiquement dans l'éditeur]
```

**Nouvelles Capacités** :
- 🎯 **8 outils puissants** : créer, modifier, lire, supprimer fichiers
- 🔧 **Modifications intelligentes** : changements précis et ciblés
- 📁 **Conscience du contexte** : l'IA voit le fichier ouvert
- ⚡ **Instantané** : pas de clic "Appliquer", tout est automatique
- 🔒 **Sécurisé** : sandbox du workspace, validation des chemins

**Exemples d'utilisation** :
- "Améliore mon code" → Refactoring automatique
- "Ajoute Serial debugging" → Modifications appliquées
- "Corrige le bug ligne 15" → Bug corrigé instantanément
- "Change la pin LED de 13 à 9" → Modification précise

[📖 Voir le guide complet](docs/TOOL_CALLING_USER_GUIDE.md)

---

## ✨ Pourquoi NeuroArduino ?

- 🧠 **Intelligence Artificielle Conversationnelle** : Décrivez ce que vous voulez en langage naturel, l'IA génère le code Arduino
- �️ **Tool Calling Avancé** : L'IA modifie vos fichiers directement, sans copier-coller
- 🎯 **Modifications Intelligentes** : Changements précis et automatiques dans votre code
- �🛡️ **Sécurité Matérielle Intégrée** : Détection automatique des risques (court-circuits, surcharge, conflits de pins)
- 📷 **Vision-to-Wire** : Prenez une photo de votre montage, obtenez le code correspondant
- 🎨 **Interface Moderne** : Design sombre premium avec Monaco Editor (VS Code)
- 🌍 **Multilingue** : Interface en Français et Anglais
- 🔌 **Intégration Complète** : Compilation, téléversement, moniteur série, traceur série

---

## 🚀 Démarrage Rapide

### ⬇️ Installation Simple (Recommandé)

**Pour les utilisateurs Windows** :

1. 📥 Téléchargez la [dernière version](https://github.com/Darshan736/vibe-coding-projects/releases/latest)
2. 📦 Extrayez le fichier `AI-Arduino-IDE-Windows.zip`
3. ▶️ Lancez `AI Arduino IDE.exe`
4. 🎉 C'est prêt ! Commencez à coder avec l'IA

**Aucune installation supplémentaire requise** - Arduino CLI et toutes les dépendances sont incluses.

---

### 🛠️ Installation pour Développeurs

**Prérequis** :
- Node.js 18+ et npm
- Python 3.8+
- Git

**Installation** :

```bash
# 1. Cloner le dépôt
git clone https://github.com/Darshan736/vibe-coding-projects.git
cd Arduino_AI_IDE

# 2. Configuration du Backend (Terminal 1)
cd backend
pip install -r requirements.txt

# Créer un fichier .env avec vos clés API
echo "GROQ_API_KEY=votre_clé_groq" > .env
echo "GEMINI_API_KEY=votre_clé_gemini" >> .env

# Lancer le serveur
python -m uvicorn main:app --port 8001 --reload

# 3. Configuration du Frontend (Terminal 2)
cd frontend
npm install
npm run dev

# 4. Accéder à l'application
# Ouvrez http://localhost:5173 dans votre navigateur
```

**Mode Electron (Application Desktop)** :

```bash
cd frontend
npm run electron:dev
```

---

## 🌟 Fonctionnalités Principales

### 🧠 Assistant IA Multi-Modèles avec Tool Calling

Choisissez entre **Groq (Llama 3.3 70B)** ou **Gemini 2.0 Flash** pour générer votre code :

#### 🎯 Génération de Code Classique

```
Vous : "Fais clignoter une LED sur la pin 13 toutes les 500ms"

IA : ✨ Voici le code généré :

void setup() {
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(500);
  digitalWrite(13, LOW);
  delay(500);
}
```

#### 🛠️ **NOUVEAU : Modification Directe de Fichiers (Tool Calling)**

L'IA peut maintenant **modifier vos fichiers directement** sans afficher le code dans la conversation !

```
Vous : "Change le délai à 500ms"

IA : Je vais mettre à jour les valeurs de délai...
     🔧 [Utilise smart_modify_file]
     ✅ Fichier modifié automatiquement dans l'éditeur
     
IA : Terminé ! J'ai changé tous les appels delay() à 500ms.
```

**Plus besoin de :**
- ❌ Copier/coller le code
- ❌ Cliquer sur "Appliquer à l'éditeur"
- ❌ Vérifier manuellement les changements

**Maintenant :**
- ✅ Modifications automatiques et instantanées
- ✅ Conversation propre sans blocs de code
- ✅ Changements précis et ciblés

**Fonctionnalités IA** :
- 💬 Conversation contextuelle (historique maintenu)
- 🔄 Itération sur le code existant
- 🎯 Génération précise et compilable
- 🛠️ **Modification directe de fichiers (Tool Calling)**
- 📁 **Conscience du contexte** (voit le fichier ouvert)
- 🔧 **8 outils disponibles** (créer, modifier, lire, supprimer fichiers)
- 🌐 Mode offline avec génération basique

---

### �️ Système de Tool Calling Avancé

L'IA dispose de **8 outils puissants** pour interagir avec vos fichiers :

| Outil | Description | Exemple d'utilisation |
|-------|-------------|----------------------|
| 🎯 **smart_modify_file** | Modifications intelligentes multi-opérations | "Change le délai et ajoute Serial debugging" |
| 📄 **create_file** | Créer de nouveaux fichiers | "Crée un fichier config.h avec les constantes" |
| ✏️ **modify_file** | Modifications simples (remplacer, insérer) | "Ajoute un commentaire en haut du fichier" |
| 👁️ **read_file** | Lire le contenu d'un fichier | "Lis le fichier utils.h" |
| 📁 **list_files** | Lister les fichiers du projet | "Quels fichiers .ino sont dans ce projet ?" |
| 📂 **create_directory** | Créer des dossiers | "Crée un dossier 'libraries'" |
| 🔄 **rename_file** | Renommer/déplacer des fichiers | "Renomme sketch.ino en blink.ino" |
| 🗑️ **delete_file** | Supprimer des fichiers | "Supprime old_code.ino" |

**Exemples d'utilisation** :

```
Vous : "Améliore mon code"
IA : [Analyse le code, utilise smart_modify_file]
     - Remplace les nombres magiques par des constantes
     - Ajoute des commentaires explicatifs
     - Optimise les boucles
     ✅ Fichier mis à jour automatiquement

Vous : "Ajoute un bouton sur la pin 2"
IA : [Utilise smart_modify_file]
     - Ajoute pinMode(2, INPUT_PULLUP) dans setup()
     - Ajoute la logique de lecture dans loop()
     ✅ Modifications appliquées

Vous : "Corrige le bug ligne 15"
IA : [Analyse le bug, utilise smart_modify_file]
     - Identifie le problème
     - Applique la correction
     ✅ Bug corrigé
```

**Sécurité** :
- 🔒 Validation des chemins (pas de traversée de répertoire)
- 🛡️ Sandbox du workspace
- ⚠️ Confirmation pour les opérations destructives
- 📏 Limites de taille de fichier

---

### �📷 Vision-to-Wire (Révolutionnaire)

**Transformez une photo en code** :

1. 📸 Prenez une photo de votre montage Arduino
2. 🔍 L'IA analyse les composants et les connexions
3. ⚡ Code Arduino généré automatiquement
4. ✅ Prêt à compiler et téléverser

**Détecte** : LEDs, résistances, boutons, capteurs, moteurs, servos, écrans LCD, et plus encore.

---

### 🛡️ Auditeur de Sécurité Matérielle

Protection automatique contre les erreurs dangereuses :

- ⚠️ **Surcharge électrique** : Alerte si moteur sur pin 5V
- 🔌 **Conflits de pins** : Détecte l'utilisation de pins Serial (0/1)
- 🔥 **Risques de court-circuit** : Analyse des connexions
- 💡 **Suggestions** : Recommandations d'alimentation externe

---

### 💻 Éditeur Professionnel

- **Monaco Editor** : Le même éditeur que VS Code
- **Coloration syntaxique** : C/C++ Arduino
- **Thème sombre premium** : Design "Anti-Gravity"
- **Autocomplétion** : Fonctions Arduino intégrées
- **Gestion de fichiers** : Arborescence complète

---

### 🔧 Intégration Arduino Complète

#### Compilation & Téléversement
- ✅ Compilation via Arduino CLI
- 📤 Upload direct sur la carte
- 🎯 Support multi-cartes (Uno, Nano, Mega, ESP32, ESP8266)

#### Gestionnaire de Cartes
- 🔍 Recherche de cores Arduino
- 📥 Installation en un clic
- 🌐 Support ESP32, ESP8266, STM32, et plus

#### Gestionnaire de Bibliothèques
- 📚 Recherche dans le registre Arduino
- ⬇️ Installation automatique
- 📦 Gestion des dépendances

---

### 📡 Communication Série Avancée

#### Moniteur Série
- 🔴 Connexion temps réel via WebSocket
- 📨 Envoi/Réception de données
- ⚙️ Configuration du baud rate
- 📋 Export des logs

#### Traceur Série (Serial Plotter)
- 📊 Visualisation graphique en temps réel
- 📈 Multi-courbes (jusqu'à 6 variables)
- 🎨 Couleurs distinctes par variable
- 🔄 Mise à jour automatique

---

## 🏗️ Architecture Technique

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Desktop App                     │
├──────────────┬──────────────────────────┬───────────────────┤
│  Activity    │   Zone Principale        │   Panel IA        │
│  Bar         │   ┌──────────────────┐   │   ┌───────────┐   │
│  ┌────┐      │   │  Toolbar         │   │   │  Chat     │   │
│  │📁  │      │   │  - Fichiers      │   │   │  - Groq   │   │
│  │🔧  │      │   │  - Compilation   │   │   │  - Gemini │   │
│  │📦  │      │   ├──────────────────┤   │   ├───────────┤   │
│  │📷  │      │   │  Monaco Editor   │   │   │  Vision   │   │
│  │⚙️  │      │   │  - C/C++         │   │   │  Upload   │   │
│  └────┘      │   │  - Syntaxe       │   │   └───────────┘   │
│              │   ├──────────────────┤   │                   │
│              │   │  Terminal        │   │                   │
│              │   │  Serial Monitor  │   │                   │
│              │   │  Serial Plotter  │   │                   │
└──────────────┴──────────────────────────┴───────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   FastAPI Backend     │
              ├───────────────────────┤
              │  🧠 AI Agents         │
              │  - Code Generator     │
              │  - Safety Auditor     │
              │  - Vision Analyzer    │
              ├───────────────────────┤
              │  🔧 Arduino CLI       │
              │  - Compile            │
              │  - Upload             │
              │  - Board Manager      │
              │  - Library Manager    │
              ├───────────────────────┤
              │  📡 PySerial          │
              │  - Serial Monitor     │
              │  - Serial Plotter     │
              └───────────────────────┘
```

**Stack Technique** :
- **Frontend** : React 19, Vite, Electron, Monaco Editor
- **Backend** : Python FastAPI, PyInstaller
- **IA** : Groq (Llama 3.3 70B), Gemini 2.5 Flash
- **Hardware** : Arduino CLI, PySerial
- **i18n** : i18next (FR/EN)

---

## 📁 Structure du Projet

```
Arduino_AI_IDE/
├── frontend/                 # Application React + Electron
│   ├── src/
│   │   ├── components/      # Composants UI
│   │   │   ├── AIPanel.jsx          # Chat IA
│   │   │   ├── VisionPanel.jsx      # Vision-to-Wire
│   │   │   ├── Editor.jsx           # Monaco Editor
│   │   │   ├── SerialMonitor.jsx    # Moniteur série
│   │   │   ├── SerialPlotter.jsx    # Traceur série
│   │   │   ├── LibraryManager.jsx   # Gestionnaire de libs
│   │   │   └── BoardManager.jsx     # Gestionnaire de cartes
│   │   ├── i18n/            # Traductions FR/EN
│   │   └── App.jsx          # Application principale
│   ├── electron/            # Configuration Electron
│   └── package.json
│
├── backend/                  # Serveur FastAPI
│   ├── agents.py            # Agents IA (avec function calling)
│   ├── tools_registry.py    # Système de tool calling (8 outils)
│   ├── system_prompts.py    # Prompts système optimisés
│   ├── main.py              # API REST
│   ├── requirements.txt     # Dépendances Python
│   ├── tests/               # Tests unitaires
│   │   └── test_smart_modify.py  # Tests tool calling
│   └── tools/               # Arduino CLI
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md      # Architecture détaillée
│   ├── ROADMAP.md           # Feuille de route
│   ├── TOOL_CALLING_USER_GUIDE.md  # Guide tool calling
│   ├── AI_ASSISTANT_ANALYSIS.md    # Analyse assistant IA
│   └── UI_IMPROVEMENTS.md   # Améliorations UI
│
└── README.md                # Ce fichier
```

---

## 🎯 Cas d'Usage

### Pour les Débutants
- 🎓 Apprendre Arduino sans connaître la syntaxe
- 🤖 Générer du code par conversation
- 📷 Analyser des montages existants
- 🛡️ Éviter les erreurs matérielles
- 🛠️ **Modifier le code en langage naturel**

### Pour les Développeurs
- ⚡ Prototypage rapide
- 🔄 Itération sur le code
- 🐛 Debugging avec l'IA
- 📊 Visualisation des données série
- 🎯 **Modifications précises avec tool calling**
- 🔧 **Refactoring automatique**

### Pour les Éducateurs
- 👨‍🏫 Enseigner l'électronique
- 📚 Créer des tutoriels interactifs
- 🎯 Projets guidés par l'IA
- 📈 Suivi de progression
- 💡 **Démonstrations en temps réel**

---

## 🤝 Contribution

Nous accueillons toutes les contributions ! Consultez la [ROADMAP.md](ROADMAP.md) pour voir les fonctionnalités planifiées.

### Comment Contribuer

1. 🍴 Fork le projet
2. 🌿 Créez une branche (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. 📤 Push vers la branche (`git push origin feature/AmazingFeature`)
5. 🔀 Ouvrez une Pull Request

### Priorités de Contribution
- 🔥 **Urgent** : Bugs critiques, sécurité
- 🚀 **Important** : Wokwi integration, amélioration Safety Agent
- 💡 **Nice to have** : UI/UX, optimisations

---

## 📚 Documentation

- 📖 [Architecture Complète](docs/ARCHITECTURE.md)
- 🗺️ [Feuille de Route](ROADMAP.md)
- 🎨 [Guide d'Interface](docs/GUIDE_INTERFACE_FR.md)
- 🔧 [Améliorations UI](docs/UI_IMPROVEMENTS.md)
- 🛠️ **[Guide Tool Calling](docs/TOOL_CALLING_USER_GUIDE.md)** - Comment utiliser les outils IA
- 📋 [Analyse de l'Assistant IA](docs/AI_ASSISTANT_ANALYSIS.md)
- ✅ [Implémentation Tool Calling](IMPLEMENTATION_COMPLETE.md)

---

## 🐛 Signaler un Bug

Trouvé un bug ? [Ouvrez une issue](https://github.com/Darshan736/vibe-coding-projects/issues/new) avec :
- 📝 Description détaillée
- 🔄 Étapes pour reproduire
- 💻 Environnement (OS, version)
- 📸 Captures d'écran si possible

---

## 📜 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **Arduino** pour l'écosystème open-source
- **Groq** et **Google Gemini** pour les APIs IA
- **Monaco Editor** pour l'éditeur de code
- **Communauté Open Source** pour l'inspiration

---

## 📞 Contact & Support

- 🐛 **Issues** : [GitHub Issues](https://github.com/Darshan736/vibe-coding-projects/issues)
- 📖 **Wiki** : [Documentation](https://github.com/Darshan736/vibe-coding-projects/wiki)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/Darshan736/vibe-coding-projects/discussions)

---

<div align="center">

**Fait avec ❤️ par l'équipe NeuroArduino**

⭐ **N'oubliez pas de mettre une étoile si vous aimez le projet !** ⭐

[⬆ Retour en haut](#neuroarduino-ai-ide-)

</div>


