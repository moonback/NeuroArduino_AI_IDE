# 🛠️ Smart Modify File Tool - Documentation

## Vue d'ensemble

Le nouvel outil `smart_modify_file` permet de faire des modifications partielles et précises sur les fichiers, contrairement à `modify_file` qui nécessite de remplacer tout le contenu du fichier.

## Avantages

✅ **Plus sûr** - Modifications ciblées sans risque de perdre du code  
✅ **Plus précis** - Opérations multiples en une seule commande  
✅ **Plus flexible** - 5 types d'opérations différentes  
✅ **Meilleure gestion d'erreurs** - Validation avant application  
✅ **Rollback automatique** - Restauration en cas d'échec  

## Types d'opérations

### 1. `replace` - Rechercher et remplacer

Remplace du texte dans le fichier.

```json
{
  "type": "replace",
  "search": "delay(1000)",
  "content": "delay(500)",
  "count": -1  // -1 = toutes les occurrences, ou nombre spécifique
}
```

**Cas d'usage:**
- Changer des valeurs (delays, pins, constantes)
- Renommer des variables
- Corriger des typos

### 2. `insert_after` - Insérer après

Insère du contenu après une ligne trouvée.

```json
{
  "type": "insert_after",
  "search": "void setup() {",
  "content": "  Serial.begin(9600);"
}
```

**Cas d'usage:**
- Ajouter des initialisations dans setup()
- Ajouter des déclarations après une ligne spécifique
- Insérer du code de debug

### 3. `insert_before` - Insérer avant

Insère du contenu avant une ligne trouvée.

```json
{
  "type": "insert_before",
  "search": "digitalWrite(LED_PIN, HIGH);",
  "content": "  Serial.println(\"LED ON\");"
}
```

**Cas d'usage:**
- Ajouter du logging avant une action
- Insérer des vérifications
- Ajouter des commentaires

### 4. `delete_lines` - Supprimer des lignes

Supprime une plage de lignes.

```json
{
  "type": "delete_lines",
  "start_line": 10,
  "end_line": 12  // Optionnel, si omis = start_line
}
```

**Cas d'usage:**
- Supprimer du code obsolète
- Retirer des commentaires
- Nettoyer du code de debug

### 5. `replace_lines` - Remplacer des lignes

Remplace une plage de lignes par du nouveau contenu.

```json
{
  "type": "replace_lines",
  "start_line": 15,
  "end_line": 20,
  "content": "  // New code\n  digitalWrite(LED_PIN, !digitalRead(LED_PIN));"
}
```

**Cas d'usage:**
- Refactoriser une section de code
- Remplacer une implémentation
- Optimiser du code

## Exemples complets

### Exemple 1: Ajouter Serial debugging

**Requête utilisateur:** "Ajoute du Serial debugging"

**Outil appelé:**
```json
{
  "path": "blink.ino",
  "modifications": [
    {
      "type": "insert_after",
      "search": "void setup() {",
      "content": "  Serial.begin(9600);\n  Serial.println(\"Sketch started\");"
    },
    {
      "type": "insert_before",
      "search": "digitalWrite(LED_PIN, HIGH);",
      "content": "  Serial.println(\"LED ON\");"
    },
    {
      "type": "insert_before",
      "search": "digitalWrite(LED_PIN, LOW);",
      "content": "  Serial.println(\"LED OFF\");"
    }
  ],
  "description": "Added Serial debugging for LED states"
}
```

### Exemple 2: Changer le délai et optimiser

**Requête utilisateur:** "Change le délai à 500ms et utilise des constantes"

**Outil appelé:**
```json
{
  "path": "blink.ino",
  "modifications": [
    {
      "type": "insert_after",
      "search": "// Blink LED sketch",
      "content": "const int LED_PIN = 13;\nconst int DELAY_MS = 500;"
    },
    {
      "type": "replace",
      "search": "pinMode(13, OUTPUT);",
      "content": "pinMode(LED_PIN, OUTPUT);"
    },
    {
      "type": "replace",
      "search": "digitalWrite(13,",
      "content": "digitalWrite(LED_PIN,",
      "count": -1
    },
    {
      "type": "replace",
      "search": "delay(1000);",
      "content": "delay(DELAY_MS);",
      "count": -1
    }
  ],
  "description": "Changed delay to 500ms and refactored to use constants"
}
```

### Exemple 3: Refactoriser en fonctions

**Requête utilisateur:** "Refactorise le code en fonctions"

**Outil appelé:**
```json
{
  "path": "blink.ino",
  "modifications": [
    {
      "type": "insert_before",
      "search": "void setup() {",
      "content": "void blinkLED(int pin, int delayTime) {\n  digitalWrite(pin, HIGH);\n  delay(delayTime);\n  digitalWrite(pin, LOW);\n  delay(delayTime);\n}\n"
    },
    {
      "type": "replace_lines",
      "start_line": 15,
      "end_line": 20,
      "content": "  blinkLED(LED_PIN, 1000);"
    }
  ],
  "description": "Refactored blink logic into reusable function"
}
```

### Exemple 4: Corriger plusieurs bugs

**Requête utilisateur:** "Corrige les bugs dans le code"

**Outil appelé:**
```json
{
  "path": "sensor.ino",
  "modifications": [
    {
      "type": "replace",
      "search": "int sensorValue;",
      "content": "int sensorValue = 0;  // Initialize to 0"
    },
    {
      "type": "replace",
      "search": "if (sensorValue > 500)",
      "content": "if (sensorValue > 500 && sensorValue < 1024)"
    },
    {
      "type": "insert_after",
      "search": "sensorValue = analogRead(A0);",
      "content": "  delay(10);  // Small delay for stable reading"
    },
    {
      "type": "delete_lines",
      "start_line": 25,
      "end_line": 27
    }
  ],
  "description": "Fixed uninitialized variable, added bounds check, added stabilization delay, removed debug code"
}
```

## Gestion d'erreurs

Le tool `smart_modify_file` valide chaque modification avant de l'appliquer:

### Erreurs courantes

1. **"Search text not found"**
   - Le texte recherché n'existe pas dans le fichier
   - Solution: Vérifier l'orthographe exacte

2. **"Invalid line number"**
   - Le numéro de ligne est hors limites
   - Solution: Vérifier le nombre de lignes du fichier

3. **"File not found"**
   - Le chemin du fichier est incorrect
   - Solution: Utiliser le chemin relatif correct

### Rollback automatique

Si une erreur se produit pendant l'écriture du fichier, le contenu original est automatiquement restauré.

## Comparaison avec modify_file

| Critère | modify_file | smart_modify_file |
|---------|-------------|-------------------|
| **Opérations multiples** | ❌ Non | ✅ Oui |
| **Modifications partielles** | ⚠️ Limitées | ✅ Complètes |
| **Sécurité** | ⚠️ Moyenne | ✅ Élevée |
| **Flexibilité** | ⚠️ 3 types | ✅ 5 types |
| **Validation** | ⚠️ Basique | ✅ Avancée |
| **Rollback** | ❌ Non | ✅ Oui |
| **Cas d'usage** | Simple | Complexe |

## Quand utiliser quel outil?

### Utilisez `modify_file` pour:
- ✅ Remplacer tout le contenu d'un fichier
- ✅ Ajouter du contenu à la fin
- ✅ Insérer à une ligne spécifique (simple)
- ✅ Une seule opération simple

### Utilisez `smart_modify_file` pour:
- ✅ Modifications multiples en une fois
- ✅ Refactoring de code
- ✅ Ajout de fonctionnalités complexes
- ✅ Corrections de bugs multiples
- ✅ Optimisations
- ✅ Toute modification nécessitant précision

## Bonnes pratiques

### 1. Ordre des modifications

Appliquez les modifications dans l'ordre logique:
```json
{
  "modifications": [
    // 1. D'abord les insertions en haut du fichier
    {"type": "insert_after", "search": "// Header", "content": "const int PIN = 13;"},
    
    // 2. Ensuite les remplacements
    {"type": "replace", "search": "13", "content": "PIN"},
    
    // 3. Puis les suppressions
    {"type": "delete_lines", "start_line": 50, "end_line": 52},
    
    // 4. Enfin les insertions en bas
    {"type": "insert_before", "search": "}", "content": "  // Cleanup"}
  ]
}
```

### 2. Descriptions claires

Toujours fournir une description de ce qui est modifié:
```json
{
  "description": "Added Serial debugging, changed delay to 500ms, and refactored pin definitions"
}
```

### 3. Recherches précises

Utilisez des chaînes de recherche uniques:
```json
// ❌ Mauvais - trop générique
{"search": "delay", "content": "delay(500)"}

// ✅ Bon - spécifique
{"search": "delay(1000);", "content": "delay(500);"}
```

### 4. Gestion des espaces

Respectez l'indentation existante:
```json
{
  "type": "insert_after",
  "search": "void setup() {",
  "content": "  Serial.begin(9600);  // 2 espaces d'indentation"
}
```

## Limitations

1. **Numéros de ligne dynamiques**: Les numéros de ligne changent après chaque modification. Utilisez plutôt la recherche de texte.

2. **Modifications conflictuelles**: Si deux modifications affectent la même zone, l'ordre est important.

3. **Fichiers binaires**: Ne fonctionne qu'avec des fichiers texte.

4. **Taille de fichier**: Limité à 1MB par fichier.

## Exemples d'utilisation par l'IA

### Prompt utilisateur: "Améliore mon code"

**Réponse de l'IA:**
```
Je vais améliorer votre code en:
- Ajoutant des constantes pour les pins
- Utilisant millis() au lieu de delay()
- Ajoutant du Serial debugging
- Améliorant les commentaires

[Utilise smart_modify_file avec 8 modifications]

✅ Terminé! Votre code a été optimisé avec:
- Constantes nommées pour meilleure lisibilité
- Code non-bloquant avec millis()
- Debugging Serial pour faciliter le développement
- Commentaires explicatifs
```

### Prompt utilisateur: "Change le délai à 200ms"

**Réponse de l'IA:**
```
Je vais changer tous les délais à 200ms.

[Utilise smart_modify_file avec 1 modification de type replace]

✅ Terminé! Tous les delay() ont été changés à 200ms.
```

## Conclusion

Le tool `smart_modify_file` est l'outil privilégié pour toutes les modifications de fichiers complexes. Il offre:

- 🎯 **Précision** - Modifications ciblées
- 🛡️ **Sécurité** - Validation et rollback
- ⚡ **Efficacité** - Opérations multiples en une fois
- 🔧 **Flexibilité** - 5 types d'opérations

Utilisez-le pour toutes vos modifications de code Arduino!
