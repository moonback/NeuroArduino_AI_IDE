# 🎛️ Composant Settings - Documentation

## Vue d'Ensemble

Le composant **Settings** est un panneau de configuration complet qui permet aux utilisateurs de personnaliser leur expérience avec AI NeuroArduino IDE.

---

## 🎯 Fonctionnalités

### 4 Onglets Principaux

#### 1. 🌍 Général (General)
- **Langue** : Choix entre Anglais et Français
- **Sauvegarde Automatique** : Active/désactive la sauvegarde automatique
- **Compilation Automatique** : Compile automatiquement lors de la sauvegarde

#### 2. 📝 Éditeur (Editor)
- **Taille de Police** : 10-24px (défaut: 14px)
- **Taille de Tabulation** : 2, 4 ou 8 espaces
- **Numéros de Ligne** : Afficher/masquer les numéros de ligne
- **Retour à la Ligne** : Activer/désactiver le word wrap

#### 3. 🎨 Apparence (Appearance)
- **Thème** : Dark (actuel), Light et High Contrast (à venir)
- **Minimap** : Afficher/masquer la minimap de code

#### 4. ℹ️ À propos (About)
- Informations sur l'application
- Version actuelle
- Technologies utilisées
- Liens vers documentation et GitHub

---

## 🎨 Interface Utilisateur

### Structure
```
┌─────────────────────────────────────────────┐
│  ⚡ Settings                           [X]  │
├──────────┬──────────────────────────────────┤
│ 🌍 Général│                                 │
│ 📝 Éditeur│  [Contenu de l'onglet actif]   │
│ 🎨 Apparence│                               │
│ ℹ️ À propos│                                │
├──────────┴──────────────────────────────────┤
│ [Reset to Defaults]  [Cancel] [Save Settings]│
└─────────────────────────────────────────────┘
```

### Éléments Visuels

#### Toggle Switch
```css
OFF: ⚪━━━━  (gris)
ON:  ━━━━⚪  (cyan)
```

#### Select Dropdown
```
┌──────────────────┐
│ English        ▼ │
└──────────────────┘
```

#### Number Input
```
┌──────┐
│  14  │ px
└──────┘
```

---

## 💾 Stockage des Paramètres

### LocalStorage
Tous les paramètres sont sauvegardés dans `localStorage` :

```javascript
localStorage.setItem('language', 'fr');
localStorage.setItem('theme', 'dark');
localStorage.setItem('fontSize', '14');
localStorage.setItem('tabSize', '2');
localStorage.setItem('autoSave', 'true');
localStorage.setItem('autoCompile', 'false');
localStorage.setItem('lineNumbers', 'true');
localStorage.setItem('minimap', 'false');
localStorage.setItem('wordWrap', 'true');
```

### Valeurs par Défaut
```javascript
{
  language: 'en',
  theme: 'dark',
  fontSize: 14,
  tabSize: 2,
  autoSave: false,
  autoCompile: false,
  lineNumbers: true,
  minimap: false,
  wordWrap: true
}
```

---

## 🔧 Utilisation

### Ouvrir les Paramètres
1. Cliquez sur l'icône ⚙️ dans l'Activity Bar (en bas à gauche)
2. Le modal Settings s'ouvre au centre de l'écran

### Modifier un Paramètre
1. Naviguez entre les onglets (Général, Éditeur, Apparence, À propos)
2. Modifiez les paramètres souhaités
3. Le bouton "Save Settings" devient actif (avec animation pulse)
4. Cliquez sur "Save Settings" pour enregistrer

### Réinitialiser
1. Cliquez sur "Reset to Defaults"
2. Confirmez l'action
3. Tous les paramètres reviennent aux valeurs par défaut
4. Cliquez sur "Save Settings" pour appliquer

### Annuler
- Cliquez sur "Cancel" ou sur [X] pour fermer sans sauvegarder
- Les modifications non sauvegardées sont perdues

---

## 🎯 Intégration dans App.jsx

### Import
```javascript
import Settings from './components/Settings';
import { Settings as SettingsIcon } from 'lucide-react';
```

### State
```javascript
const [showSettings, setShowSettings] = useState(false);
```

### Bouton d'Ouverture
```javascript
<button 
  onClick={() => setShowSettings(true)}
  className="activity-btn"
  title={t('settings')}
>
  <SettingsIcon size={20} />
</button>
```

### Rendu Conditionnel
```javascript
{showSettings && <Settings onClose={() => setShowSettings(false)} />}
```

---

## 🌐 Internationalisation (i18n)

### Clés de Traduction Ajoutées

#### Anglais (en.json)
```json
{
  "general": "General",
  "editor": "Editor",
  "appearance": "Appearance",
  "about": "About",
  "language": "Language",
  "autoSave": "Auto Save",
  "fontSize": "Font Size",
  "theme": "Theme",
  "settingsSaved": "Settings saved successfully!",
  "saveSettings": "Save Settings"
}
```

#### Français (fr.json)
```json
{
  "general": "Général",
  "editor": "Éditeur",
  "appearance": "Apparence",
  "about": "À propos",
  "language": "Langue",
  "autoSave": "Sauvegarde Automatique",
  "fontSize": "Taille de Police",
  "theme": "Thème",
  "settingsSaved": "Paramètres enregistrés avec succès !",
  "saveSettings": "Enregistrer les Paramètres"
}
```

---

## 🎨 Styles CSS

### Classes Principales

#### Modal
- `.settings-overlay` : Fond semi-transparent avec blur
- `.settings-modal` : Container principal du modal
- `.settings-header` : En-tête avec titre et bouton fermer
- `.settings-content` : Zone de contenu (sidebar + panel)
- `.settings-footer` : Pied avec boutons d'action

#### Navigation
- `.settings-sidebar` : Barre latérale avec onglets
- `.settings-tab` : Bouton d'onglet
- `.settings-tab-active` : Onglet actif (cyan)

#### Contenu
- `.settings-panel` : Zone de contenu principal
- `.settings-section` : Section d'un onglet
- `.settings-item` : Ligne de paramètre
- `.settings-label` : Label du paramètre
- `.settings-description` : Description du paramètre

#### Contrôles
- `.settings-select` : Select dropdown
- `.settings-input` : Input numérique
- `.settings-toggle` : Toggle switch
- `.settings-toggle-slider` : Slider du toggle

#### Boutons
- `.settings-btn-primary` : Bouton principal (Save)
- `.settings-btn-secondary` : Bouton secondaire (Reset)
- `.settings-btn-cancel` : Bouton annuler

---

## 📱 Responsive Design

### Desktop (>768px)
- Modal : 900px × 700px
- Sidebar : 200px
- Tous les labels visibles

### Mobile (<768px)
- Modal : 95% × 90vh
- Sidebar : 60px (icônes seulement)
- Labels masqués dans la sidebar
- Items en colonne
- Footer en colonne

---

## ✨ Animations

### Entrée du Modal
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}
```

### Bouton Save Actif
```css
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 12px rgba(37, 99, 235, 0.4); }
  50% { box-shadow: 0 0 20px rgba(37, 99, 235, 0.6); }
}
```

### Toggle Switch
```css
transition: all 0.3s ease;
transform: translateX(22px); /* when checked */
```

---

## 🔮 Fonctionnalités Futures

### À Implémenter
- [ ] Thème Light et High Contrast
- [ ] Raccourcis clavier personnalisables
- [ ] Paramètres de l'assistant IA
- [ ] Paramètres de compilation avancés
- [ ] Export/Import des paramètres
- [ ] Profils de paramètres
- [ ] Synchronisation cloud (optionnelle)

### Améliorations Possibles
- [ ] Recherche dans les paramètres
- [ ] Catégories de paramètres avancés
- [ ] Prévisualisation en temps réel
- [ ] Historique des modifications
- [ ] Paramètres par projet

---

## 🐛 Gestion des Erreurs

### Validation
- Font size : min 10px, max 24px
- Tab size : 2, 4 ou 8 espaces uniquement
- Language : 'en' ou 'fr' uniquement

### Confirmation
- Reset to defaults : Demande confirmation
- Fermeture avec modifications : Pas de confirmation (comportement standard)

### Messages
- Succès : Alert "Settings saved successfully!"
- Erreur : Console.error pour debug

---

## 📊 Performance

### Optimisations
- Rendu conditionnel des onglets
- LocalStorage pour persistance légère
- Pas de re-render inutiles
- Animations CSS (GPU accelerated)

### Taille
- Component : ~8KB (non minifié)
- Styles : ~6KB (non minifié)
- Total impact : ~14KB

---

## 🎉 Résumé

Le composant Settings offre :
- ✅ Interface moderne et intuitive
- ✅ 4 catégories de paramètres
- ✅ Persistance avec localStorage
- ✅ Internationalisation complète
- ✅ Responsive design
- ✅ Animations fluides
- ✅ Facile à étendre

**Le choix de langue est maintenant dans les paramètres, comme demandé !** 🚀

---

**Date de création** : 2026-05-11
**Version** : 1.0.0
