# 🎨 Guide de l'Interface - AI NeuroArduino IDE

## Vue d'Ensemble

L'interface a été complètement repensée pour offrir une expérience utilisateur moderne et intuitive.

---

## 📐 Structure de l'Interface

```
┌─────────────────────────────────────────────────────────────────┐
│  [Activity Bar] [Sidebar] [     Main Content     ] [AI Panel]   │
│                                                                   │
│      ⚡           📁         ┌──────────────┐         💬         │
│      📋                      │   Toolbar    │                    │
│      📦                      ├──────────────┤                    │
│      📷                      │              │                    │
│                              │    Editor    │                    │
│                              │              │                    │
│                              ├──────────────┤                    │
│                              │   Terminal   │                    │
│                              └──────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Le Nouveau Header (Toolbar)

### Section Gauche - Actions Principales
```
[🔧 AI NeuroArduino] | [📄] [💾] | [✓ Vérifier] [⬆ Upload]
```

- **Logo** : Identité de l'application
- **📄 Nouveau** : Créer un nouveau sketch
- **💾 Sauvegarder** : Sauvegarder le fichier actuel (devient cyan si modifié)
- **✓ Vérifier** : Compiler le code (bouton bleu)
- **⬆ Upload** : Téléverser vers la carte (bouton avec bordure)

### Section Centre - Statut
```
[sketch.ino ●]
```
- Affiche le nom du fichier actuel
- Le point **●** indique des modifications non sauvegardées

### Section Droite - Matériel & Paramètres
```
[COM3 (Arduino)] [🔄] [🔌 Connecter] | [Board: Arduino Uno] | [FR] [✨]
```

- **Sélecteur de Port** : Choisir le port série
- **🔄 Rafraîchir** : Scanner les ports disponibles
- **🔌 Connecter** : Se connecter au port (vert) / Déconnecter (rouge)
- **Board** : Sélectionner la carte Arduino
- **FR/EN** : Changer la langue
- **✨ IA** : Toggle l'assistant IA

---

## 💬 Assistant IA Amélioré

### Fonctionnalités

#### 1. Bouton de Minimisation
```
[<] ← Cliquez pour minimiser
[>] ← Cliquez pour agrandir
```
- Permet de gagner de l'espace à l'écran
- Le panel se réduit à 48px de largeur
- Toujours accessible via le bouton

#### 2. Sélecteur de Modèle
```
┌─────────────────────────┐
│ Model: [Groq Llama 3 ▼] │
└─────────────────────────┘
```
- **Groq Llama 3** : Rapide et efficace
- **Gemini 2.5** : Plus avancé

#### 3. Messages avec Avatars
```
┌─────────────────────────┐
│ [U] Bonjour!            │  ← Vous (dégradé cyan)
│                         │
│ [🔧] Salut! Comment     │  ← IA (fond gris)
│      puis-je aider?     │
└─────────────────────────┘
```

#### 4. Blocs de Code
```
┌─────────────────────────────────┐
│ ✨ Arduino C++  [Apply to Editor]│
├─────────────────────────────────┤
│ void setup() {                  │
│   pinMode(13, OUTPUT);          │
│ }                               │
└─────────────────────────────────┘
```
- Cliquez sur **Apply to Editor** pour insérer le code

#### 5. Zone de Saisie
```
┌─────────────────────────────────┐
│ Ask Groq anything... [📷] [➤]  │
└─────────────────────────────────┘
```
- **📷 Vision** : Analyser une image de circuit
- **➤ Send** : Envoyer le message (ou appuyez sur Entrée)

---

## 🎨 Codes Couleurs

### États des Boutons
- **Bleu** (#2563eb) : Action principale (Vérifier)
- **Cyan** (#00e5ff) : Accent, éléments actifs
- **Vert** (#22c55e) : Connexion établie
- **Rouge** (#ef4444) : Déconnexion
- **Gris** : Éléments inactifs

### Messages IA
- **Dégradé Cyan** : Vos messages
- **Gris Foncé** : Messages de l'IA
- **Bordure Cyan** : Input actif (focus)

---

## ⌨️ Raccourcis Utiles

### Dans le Chat IA
- **Entrée** : Envoyer le message
- **Maj + Entrée** : Nouvelle ligne (à venir)

### Général
- **Ctrl + S** : Sauvegarder
- **Ctrl + N** : Nouveau fichier
- **Ctrl + O** : Ouvrir un dossier

---

## 📱 Responsive

### Sur Écran Large (>1400px)
- Tout est visible
- Panel IA : 380px
- Sidebar : 250px

### Sur Tablette (1024px - 1400px)
- Panel IA : 320px
- Sidebar : 200px
- Certains labels masqués

### Sur Mobile (<768px)
- Panel IA masqué
- Sidebar masquée
- Interface simplifiée

---

## 💡 Astuces

### Gagner de l'Espace
1. Minimisez le panel IA avec le bouton `<`
2. Fermez la sidebar avec l'icône ⚡ dans l'Activity Bar
3. Maximisez l'éditeur pour vous concentrer sur le code

### Utiliser l'IA Efficacement
1. Posez des questions précises : "Comment faire clignoter une LED sur la pin 13?"
2. Utilisez le bouton **Apply to Editor** pour insérer le code généré
3. Changez de modèle si les résultats ne sont pas satisfaisants

### Workflow Recommandé
1. **Ouvrir un dossier** : Cliquez sur l'icône 📁 dans l'Activity Bar
2. **Créer/Ouvrir un fichier** : Utilisez la sidebar
3. **Coder** : Utilisez l'éditeur principal
4. **Demander de l'aide** : Utilisez l'assistant IA
5. **Vérifier** : Compilez avec le bouton Vérifier
6. **Upload** : Téléversez vers votre carte Arduino

---

## 🐛 Résolution de Problèmes

### Le Panel IA est Caché
- Cliquez sur l'icône ✨ dans le toolbar
- Ou cherchez le bouton `>` sur le bord droit

### Le Toolbar est Trop Chargé
- Sur petit écran, certains éléments se cachent automatiquement
- Utilisez le mode paysage sur tablette

### Les Boutons ne Répondent Pas
- Vérifiez que le backend est lancé (port 8001)
- Redémarrez l'application si nécessaire

---

## 🎉 Profitez de Votre Nouvelle Interface !

L'interface a été conçue pour être :
- **Intuitive** : Tout est à portée de clic
- **Moderne** : Design professionnel et élégant
- **Efficace** : Workflow optimisé pour Arduino
- **Flexible** : Adaptable à vos besoins

**Bon codage ! 🚀**
