# 💬 Exemples de Prompts - AI Tool Calling

## 📋 Guide des Prompts

Ce document contient des exemples de prompts pour tester et utiliser le système de Tool Calling de NeuroArduino AI IDE.

---

## 🎯 Catégorie 1 : Création de Fichiers Simples

### Exemple 1.1 : Blink LED Basique
```
Crée un fichier blink.ino qui fait clignoter une LED sur la pin 13 toutes les secondes
```

**Résultat Attendu** :
- ✅ Fichier `blink.ino` créé
- ✅ Code avec pinMode et digitalWrite
- ✅ Délais de 1000ms

---

### Exemple 1.2 : Lecture de Bouton
```
Crée button_read.ino pour lire un bouton sur la pin 2 et allumer une LED sur la pin 13 quand le bouton est pressé
```

**Résultat Attendu** :
- ✅ Fichier `button_read.ino` créé
- ✅ INPUT_PULLUP pour le bouton
- ✅ Logique if pour contrôler la LED

---

### Exemple 1.3 : Communication Série
```
Crée serial_test.ino qui envoie "Hello Arduino" sur le port série toutes les 2 secondes
```

**Résultat Attendu** :
- ✅ Serial.begin(9600) dans setup
- ✅ Serial.println dans loop
- ✅ delay(2000)

---

## 🏗️ Catégorie 2 : Projets Complets

### Exemple 2.1 : Projet Servo
```
Crée un projet complet pour contrôler un servo moteur avec un potentiomètre. Inclus le code, un README avec le câblage, et un fichier de configuration.
```

**Résultat Attendu** :
- ✅ Dossier `servo_control/`
- ✅ Fichier `servo_control.ino` avec code
- ✅ Fichier `README.md` avec documentation
- ✅ Fichier `wiring.txt` avec schéma

---

### Exemple 2.2 : Projet Capteur DHT22
```
Crée un projet pour lire un capteur DHT22 et afficher température et humidité sur le Serial Monitor. Ajoute aussi un fichier avec les bibliothèques nécessaires.
```

**Résultat Attendu** :
- ✅ Dossier `dht22_project/`
- ✅ Code avec #include <DHT.h>
- ✅ README avec instructions
- ✅ Fichier `libraries.txt` listant les dépendances

---

### Exemple 2.3 : Projet LCD
```
Crée un projet complet pour afficher "Hello World" sur un écran LCD 16x2 I2C. Inclus le code, la documentation et le schéma de câblage.
```

**Résultat Attendu** :
- ✅ Code avec LiquidCrystal_I2C
- ✅ Documentation complète
- ✅ Schéma I2C (SDA, SCL)

---

## ✏️ Catégorie 3 : Modifications de Code

### Exemple 3.1 : Changer un Délai
```
Dans blink.ino, change tous les délais de 1000ms à 500ms
```

**Résultat Attendu** :
- ✅ Lecture du fichier existant
- ✅ Remplacement de delay(1000) par delay(500)
- ✅ Fichier modifié avec succès

---

### Exemple 3.2 : Ajouter du Debug
```
Ajoute des Serial.println pour debugger dans sensor_read.ino. Affiche la valeur du capteur à chaque lecture.
```

**Résultat Attendu** :
- ✅ Serial.begin ajouté si absent
- ✅ Serial.println ajoutés aux bons endroits
- ✅ Messages de debug clairs

---

### Exemple 3.3 : Refactoring
```
Refactorise blink.ino en créant une fonction blinkLED(pin, delay) réutilisable
```

**Résultat Attendu** :
- ✅ Fonction blinkLED créée
- ✅ Code dans loop() simplifié
- ✅ Paramètres correctement utilisés

---

## 🔧 Catégorie 4 : Gestion de Fichiers

### Exemple 4.1 : Organiser le Code
```
Crée un dossier src/ et déplace tous les fichiers .ino dedans
```

**Résultat Attendu** :
- ✅ Dossier `src/` créé
- ✅ Fichiers .ino déplacés
- ✅ Structure organisée

---

### Exemple 4.2 : Créer une Bibliothèque
```
Crée une bibliothèque personnalisée MyLED dans lib/MyLED/ avec MyLED.h et MyLED.cpp pour contrôler des LEDs
```

**Résultat Attendu** :
- ✅ Dossier `lib/MyLED/` créé
- ✅ Fichier `MyLED.h` avec déclarations
- ✅ Fichier `MyLED.cpp` avec implémentations
- ✅ Classe MyLED fonctionnelle

---

### Exemple 4.3 : Documentation Projet
```
Crée un fichier CHANGELOG.md qui documente les versions du projet avec les changements
```

**Résultat Attendu** :
- ✅ Fichier `CHANGELOG.md` créé
- ✅ Format markdown correct
- ✅ Structure par versions

---

## 🎓 Catégorie 5 : Projets Éducatifs

### Exemple 5.1 : Tutoriel Débutant
```
Crée un tutoriel complet pour débutants avec 5 exercices progressifs sur les LEDs. Chaque exercice dans un fichier séparé avec des commentaires explicatifs.
```

**Résultat Attendu** :
- ✅ Dossier `tutorial/`
- ✅ 5 fichiers (ex1.ino à ex5.ino)
- ✅ Commentaires pédagogiques
- ✅ README avec progression

---

### Exemple 5.2 : Projet Scientifique
```
Crée un projet pour mesurer la température toutes les 10 secondes et sauvegarder les données. Inclus le code et un fichier expliquant comment analyser les données.
```

**Résultat Attendu** :
- ✅ Code de mesure
- ✅ Format de données CSV
- ✅ Guide d'analyse

---

## 🚀 Catégorie 6 : Projets Avancés

### Exemple 6.1 : Système Multi-Capteurs
```
Crée un projet qui lit 3 capteurs différents (température, humidité, lumière) et affiche tout sur un écran OLED. Organise le code en modules séparés.
```

**Résultat Attendu** :
- ✅ Fichier principal
- ✅ Modules par capteur
- ✅ Module affichage
- ✅ Architecture modulaire

---

### Exemple 6.2 : Machine à États
```
Crée un projet avec une machine à états pour contrôler un feu tricolore. Utilise enum pour les états et des fonctions pour chaque état.
```

**Résultat Attendu** :
- ✅ Enum pour états
- ✅ Fonctions par état
- ✅ Transitions logiques
- ✅ Code bien structuré

---

### Exemple 6.3 : Communication I2C
```
Crée un projet maître-esclave I2C avec deux Arduinos. Crée les deux programmes et un README expliquant le protocole.
```

**Résultat Attendu** :
- ✅ `master.ino`
- ✅ `slave.ino`
- ✅ Documentation protocole
- ✅ Schéma de connexion

---

## 🔍 Catégorie 7 : Debugging & Optimisation

### Exemple 7.1 : Ajouter Gestion d'Erreurs
```
Ajoute une gestion d'erreurs complète dans sensor_read.ino avec vérification des valeurs et messages d'erreur
```

**Résultat Attendu** :
- ✅ Vérifications ajoutées
- ✅ Messages d'erreur clairs
- ✅ Gestion des cas limites

---

### Exemple 7.2 : Optimiser la Mémoire
```
Analyse blink.ino et optimise-le pour utiliser moins de mémoire. Ajoute des commentaires expliquant les optimisations.
```

**Résultat Attendu** :
- ✅ Code optimisé
- ✅ Commentaires explicatifs
- ✅ Comparaison avant/après

---

### Exemple 7.3 : Profiling
```
Ajoute du code de profiling dans loop() pour mesurer le temps d'exécution de chaque section
```

**Résultat Attendu** :
- ✅ Variables de timing
- ✅ Mesures micros()
- ✅ Affichage des résultats

---

## 🎨 Catégorie 8 : Projets Créatifs

### Exemple 8.1 : Animation LED
```
Crée un projet avec 8 LEDs qui fait une animation de type "Knight Rider". Organise le code avec des fonctions pour chaque pattern.
```

**Résultat Attendu** :
- ✅ Code d'animation
- ✅ Fonctions par pattern
- ✅ Timing précis

---

### Exemple 8.2 : Jeu Simple
```
Crée un jeu de réflexe avec un bouton et une LED. La LED s'allume aléatoirement et le joueur doit appuyer le plus vite possible.
```

**Résultat Attendu** :
- ✅ Logique de jeu
- ✅ Timing aléatoire
- ✅ Calcul du score

---

### Exemple 8.3 : Synthétiseur Musical
```
Crée un mini synthétiseur avec 4 boutons et un buzzer. Chaque bouton joue une note différente.
```

**Résultat Attendu** :
- ✅ Définition des notes
- ✅ Lecture des boutons
- ✅ Génération de sons

---

## 🧪 Catégorie 9 : Tests & Validation

### Exemple 9.1 : Tests Unitaires
```
Crée un fichier de tests pour valider les fonctions de calcul dans sensor_utils.ino
```

**Résultat Attendu** :
- ✅ Fichier de tests
- ✅ Fonctions de test
- ✅ Assertions

---

### Exemple 9.2 : Benchmark
```
Crée un benchmark pour comparer différentes méthodes de lecture analogique
```

**Résultat Attendu** :
- ✅ Code de benchmark
- ✅ Mesures de performance
- ✅ Comparaison des résultats

---

## 📊 Catégorie 10 : Documentation

### Exemple 10.1 : API Documentation
```
Crée une documentation API complète pour toutes les fonctions de mon projet dans docs/API.md
```

**Résultat Attendu** :
- ✅ Fichier `docs/API.md`
- ✅ Documentation par fonction
- ✅ Exemples d'utilisation

---

### Exemple 10.2 : Guide Utilisateur
```
Crée un guide utilisateur complet pour mon projet de station météo avec captures d'écran et explications
```

**Résultat Attendu** :
- ✅ Guide structuré
- ✅ Instructions claires
- ✅ Troubleshooting

---

## 💡 Conseils pour de Bons Prompts

### ✅ Bonnes Pratiques

1. **Soyez Spécifique** :
   - ❌ "Crée un fichier"
   - ✅ "Crée un fichier blink.ino qui fait clignoter une LED sur la pin 13"

2. **Mentionnez les Détails** :
   - ❌ "Ajoute du debug"
   - ✅ "Ajoute des Serial.println pour afficher la valeur du capteur à chaque lecture"

3. **Demandez la Structure** :
   - ❌ "Crée un projet"
   - ✅ "Crée un projet avec le code, un README et un schéma de câblage"

4. **Précisez les Modifications** :
   - ❌ "Change le code"
   - ✅ "Dans blink.ino, remplace delay(1000) par delay(500)"

### ❌ À Éviter

1. **Prompts Trop Vagues** :
   - "Fais quelque chose avec des LEDs"
   - "Améliore le code"

2. **Demandes Impossibles** :
   - "Crée un fichier en dehors du workspace"
   - "Supprime tous les fichiers système"

3. **Prompts Ambigus** :
   - "Change le délai" (quel délai ?)
   - "Ajoute un capteur" (quel type ?)

---

## 🎯 Prompts de Test Rapide

Pour tester rapidement le système :

```bash
# Test 1 : Création simple
"Crée test.ino avec un blink basique"

# Test 2 : Modification
"Change le délai à 200ms dans test.ino"

# Test 3 : Lecture
"Lis le contenu de test.ino"

# Test 4 : Projet complet
"Crée un projet servo_test avec code et README"

# Test 5 : Organisation
"Crée un dossier examples/ et mets test.ino dedans"
```

---

**Dernière mise à jour** : 11 Mai 2026  
**Version** : 1.0
