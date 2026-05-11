# 🔧 Guide d'Intégration - AI Tool Calling System

## 📋 Vue d'Ensemble

Ce guide explique comment intégrer et utiliser le système de Tool Calling dans NeuroArduino AI IDE. Le système permet à l'assistant IA de créer, modifier et gérer des fichiers de manière autonome.

---

## 🚀 Démarrage Rapide

### 1. Backend - Activer le Tool Calling

Le système est activé par défaut. Pour le désactiver :

```python
# Dans backend/main.py
@app.post("/ai/generate")
async def generate_code(query: AIQuery):
    result = process_ai_request(
        query.prompt, 
        query.board, 
        query.provider, 
        query.history,
        enable_tools=False  # Désactiver les tools
    )
    return result
```

### 2. Frontend - Afficher les Tool Calls

```jsx
// Dans AIPanel.jsx
const aiMsg = {
    role: 'assistant',
    content: res.data.message,
    code: res.data.code,
    tool_calls: res.data.tool_calls || [],
    tool_results: res.data.tool_results || []
};
```

---

## 📝 Exemples d'Utilisation

### Exemple 1 : Créer un Fichier Simple

**Prompt Utilisateur** :
```
Crée un fichier blink.ino qui fait clignoter une LED sur la pin 13
```

**Réponse IA** :
```json
{
  "message": "Je vais créer le fichier blink.ino avec le code de clignotement.",
  "tool_calls": [
    {
      "id": "call_1",
      "tool": "create_file",
      "parameters": {
        "path": "blink.ino",
        "content": "void setup() {\n  pinMode(13, OUTPUT);\n}\n\nvoid loop() {\n  digitalWrite(13, HIGH);\n  delay(1000);\n  digitalWrite(13, LOW);\n  delay(1000);\n}"
      }
    }
  ],
  "tool_results": [
    {
      "id": "call_1",
      "tool": "create_file",
      "result": {
        "status": "success",
        "message": "File created: blink.ino",
        "path": "blink.ino",
        "size": 156
      }
    }
  ]
}
```

---

### Exemple 2 : Modifier un Fichier Existant

**Prompt Utilisateur** :
```
Change le délai à 500ms dans blink.ino
```

**Réponse IA** :
```json
{
  "message": "Je modifie les délais à 500ms.",
  "tool_calls": [
    {
      "id": "call_1",
      "tool": "read_file",
      "parameters": {
        "path": "blink.ino"
      }
    },
    {
      "id": "call_2",
      "tool": "modify_file",
      "parameters": {
        "path": "blink.ino",
        "operation": "replace",
        "search": "delay(1000);",
        "content": "delay(500);"
      }
    }
  ]
}
```

---

### Exemple 3 : Créer un Projet Complet

**Prompt Utilisateur** :
```
Crée un projet complet pour lire un capteur de température DHT22 et afficher sur Serial
```

**Réponse IA** :
```json
{
  "message": "Je crée un projet complet avec le code, la documentation et le schéma de câblage.",
  "tool_calls": [
    {
      "tool": "create_directory",
      "parameters": {
        "path": "dht22_project"
      }
    },
    {
      "tool": "create_file",
      "parameters": {
        "path": "dht22_project/dht22_project.ino",
        "content": "#include <DHT.h>\n\n#define DHTPIN 2\n#define DHTTYPE DHT22\n\nDHT dht(DHTPIN, DHTTYPE);\n\nvoid setup() {\n  Serial.begin(9600);\n  dht.begin();\n}\n\nvoid loop() {\n  float h = dht.readHumidity();\n  float t = dht.readTemperature();\n  \n  Serial.print(\"Humidity: \");\n  Serial.print(h);\n  Serial.print(\"%  Temperature: \");\n  Serial.print(t);\n  Serial.println(\"°C\");\n  \n  delay(2000);\n}"
      }
    },
    {
      "tool": "create_file",
      "parameters": {
        "path": "dht22_project/README.md",
        "content": "# DHT22 Temperature & Humidity Sensor\n\n## Composants Requis\n- Arduino Uno\n- Capteur DHT22\n- Résistance 10kΩ (pull-up)\n- Câbles de connexion\n\n## Câblage\n- DHT22 VCC → Arduino 5V\n- DHT22 GND → Arduino GND\n- DHT22 DATA → Arduino Pin 2\n- Résistance 10kΩ entre VCC et DATA\n\n## Installation\n1. Installer la bibliothèque DHT sensor library\n2. Téléverser le code\n3. Ouvrir le moniteur série à 9600 baud\n\n## Utilisation\nLe capteur affiche la température et l'humidité toutes les 2 secondes."
      }
    },
    {
      "tool": "create_file",
      "parameters": {
        "path": "dht22_project/wiring.txt",
        "content": "Schéma de Câblage DHT22:\n\nDHT22          Arduino Uno\n-----          -----------\nVCC    ------>  5V\nDATA   ------>  Pin 2 (avec résistance 10kΩ vers 5V)\nGND    ------>  GND\n\nNote: La résistance pull-up de 10kΩ est obligatoire entre VCC et DATA."
      }
    }
  ]
}
```

---

## 🎨 Interface Utilisateur

### Affichage des Tool Calls

Le composant `ToolCallDisplay` affiche chaque opération :

```jsx
<ToolCallDisplay 
    toolCall={toolCall}
    toolResult={toolResult}
    onOpenFile={(path) => {
        // Ouvrir le fichier dans l'éditeur
        handleFileClick({ path, name: path.split('/').pop() });
    }}
/>
```

**Apparence** :
```
┌─────────────────────────────────────────┐
│ ▼ 📄 Create File              ✓        │
├─────────────────────────────────────────┤
│ Parameters                              │
│ path: blink.ino                         │
│ content: void setup() {...              │
│                                         │
│ Result                                  │
│ ✓ File created: blink.ino               │
│                                         │
│ [Open File]                             │
└─────────────────────────────────────────┘
```

---

## 🔒 Sécurité

### Validation des Chemins

Tous les chemins sont validés pour empêcher :
- **Path Traversal** : `../../../etc/passwd` ❌
- **Accès système** : `/etc`, `C:\Windows` ❌
- **Sortie du workspace** : Tous les fichiers doivent être dans le workspace ✅

### Confirmation Utilisateur

Les opérations destructives nécessitent confirmation :

```jsx
// Avant de supprimer un fichier
if (window.confirm(`Êtes-vous sûr de vouloir supprimer ${path} ?`)) {
    // Procéder à la suppression
}
```

### Limites

- **Taille de fichier** : Maximum 1MB
- **Nombre de tool calls** : Maximum 10 par requête
- **Rate limiting** : À implémenter selon les besoins

---

## 🧪 Tests

### Test 1 : Création de Fichier

```bash
curl -X POST http://localhost:8001/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Crée un fichier test.ino avec un simple blink",
    "provider": "groq",
    "enable_tools": true
  }'
```

### Test 2 : Modification de Fichier

```bash
curl -X POST http://localhost:8001/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Change le délai à 200ms dans test.ino",
    "provider": "groq",
    "enable_tools": true
  }'
```

### Test 3 : Lecture de Fichier

```bash
curl -X POST http://localhost:8001/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Lis le contenu de test.ino",
    "provider": "groq",
    "enable_tools": true
  }'
```

---

## 🐛 Debugging

### Activer les Logs

```python
# Dans backend/agents.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Dans execute_tool
logger.debug(f"Executing tool: {tool_name} with params: {parameters}")
```

### Vérifier les Tool Calls

```jsx
// Dans AIPanel.jsx
console.log('Tool Calls:', aiMsg.tool_calls);
console.log('Tool Results:', aiMsg.tool_results);
```

---

## 📊 Métriques

### Suivre l'Utilisation

```python
# Dans backend/tools_registry.py
import time

class ToolRegistry:
    def __init__(self):
        self.metrics = {
            "total_calls": 0,
            "success_count": 0,
            "error_count": 0,
            "execution_times": []
        }
    
    def execute_tool(self, tool_name, parameters):
        start_time = time.time()
        self.metrics["total_calls"] += 1
        
        result = self._execute_tool_internal(tool_name, parameters)
        
        execution_time = time.time() - start_time
        self.metrics["execution_times"].append(execution_time)
        
        if result["status"] == "success":
            self.metrics["success_count"] += 1
        else:
            self.metrics["error_count"] += 1
        
        return result
```

---

## 🚀 Prochaines Étapes

### Fonctionnalités à Venir

1. **Undo/Redo** : Annuler les modifications
2. **Diff Viewer** : Voir les changements avant application
3. **Batch Operations** : Modifier plusieurs fichiers en une fois
4. **Git Integration** : Commit automatique après modifications
5. **Template System** : Créer des projets à partir de templates

### Améliorations

1. **Streaming** : Afficher les tool calls en temps réel
2. **Confirmation UI** : Modal pour confirmer les actions
3. **History** : Historique des opérations
4. **Rollback** : Restaurer l'état précédent

---

## 📚 Ressources

- [Documentation Tool Calling](AI_TOOL_CALLING.md)
- [API Reference](../backend/tools_registry.py)
- [Frontend Components](../frontend/src/components/ToolCallDisplay.jsx)

---

## 🤝 Contribution

Pour ajouter un nouveau tool :

1. **Définir le tool** dans `tools_registry.py`
2. **Implémenter la logique** dans `_execute_tool_internal`
3. **Ajouter les tests** dans `tests/test_tools.py`
4. **Mettre à jour la documentation**

---

**Dernière mise à jour** : 11 Mai 2026  
**Version** : 1.0
