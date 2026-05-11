# 🛠️ Arduino AI IDE : Analyse & Roadmap

## 1. État de l'Art (Analyse Technique)

L'application repose sur une architecture moderne de type **Copilote pour Hardware**. Elle réussit le pari de combiner la rapidité des LLM (Groq/Gemini) avec la puissance de l'écosystème Arduino standard.

### 🏗️ Architecture Actuelle
*   **Frontend** : React 19 + Electron. L'interface est épurée, suivant les principes "Anti-Gravity" (thème sombre profond, accents cyan).
*   **Backend** : FastAPI. Sert de passerelle entre le Web et le système (OS).
*   **Intelligence** : Système multi-agents. Un agent génère le code tandis qu'un second audite la sécurité matérielle.
*   **Tooling** : Wrapper autour de `arduino-cli`.

### ✅ Points Forts
- **Latence Minimale** : Interaction quasi-instantanée via Groq/Gemini.
- **Hardware Integration** : Gestion réelle des ports série, du traçage (Plotter) et des bibliothèques.
- **Multi-Cibles** : Support étendu pour ESP32, ESP8266 et plus via le Board Manager.

### 🏁 Problèmes Résolus
- **Persistance** : Système de fichiers complet implémenté.
- **Feedback Hardware** : Moniteur série et Plotter connectés au hardware réel.
- **Gestion de Dépendances** : Library Manager UI fonctionnel.

---

## 🚀 Roadmap Évolutive

### 📅 Phase 1 : Consolidation (Court Terme)
- [x] **Persistance Locale** : Implémenter un vrai système de gestion de fichiers (Nouveau/Ouvrir/Enregistrer).
- [x] **Vrai Moniteur Série** : Connecter le backend à `pyserial` pour lire les données réelles de la carte Arduino via WebSocket.
- [x] **Historique de Chat** : Permettre à l'IA de "discuter" sur le code existant pour faire des itérations successives.

### 📅 Phase 2 : Deep Hardware (Moyen Terme)
- [x] **Library Manager UI** : Rechercher et installer des bibliothèques (`.zip` ou via registry) sans quitter l'IDE.
- [x] **Serial Plotter** : Visualisation graphique des données de capteurs en temps réel.
- [x] **Multi-Target Support** : Configurer facilement les profils pour ESP32, ESP8266 et STM32.

### 📅 Phase 3 : Intelligence Avancée (Long Terme)
- [x] **Vision-to-Wire** : Pouvoir uploader une photo de son montage pour que l'IA génère le code correspondant.
- [ ] **Audit de Sécurité Profond** : Utiliser un LLM plus puissant (Gemini 1.5 Pro) pour simuler des scénarios de panne basés sur le code.
- [ ] **Wokwi Integration** : Prévisualiser le comportement du code dans un simulateur web avant de flasher.

---

## 🛠️ Stack Technique Recommandée pour l'Évolution
*   **Backend** : Continuer avec Python/FastAPI pour sa flexibilité avec les outils système.
*   **Serial** : Utiliser `serialport` côté Electron pour plus de réactivité ou garder `pyserial` côté backend pour la cohérence.
*   **IA** : Garder Gemini 1.5 Flash pour la vitesse et Groq pour la diversité des modèles.
