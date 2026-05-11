# 🛠️ AI Tool Calling System - Documentation Technique

## 📋 Vue d'Ensemble

Le système de Tool Calling permet à l'assistant IA d'interagir directement avec le système de fichiers et l'environnement de développement. L'IA peut créer, modifier, lire et supprimer des fichiers de manière autonome.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
├─────────────────────────────────────────────────────────┤
│  AIPanel.jsx                                            │
│  ├─ User Input                                          │
│  ├─ Message History                                     │
│  └─ Tool Execution Display                              │
│                    │                                     │
│                    ▼                                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Tool Calling Handler                     │   │
│  │  - Detect tool calls in AI response              │   │
│  │  - Execute tools via API                         │   │
│  │  - Display results to user                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                      │
├─────────────────────────────────────────────────────────┤
│  /api/ai/generate (Enhanced)                            │
│  ├─ Process user prompt                                 │
│  ├─ Include tool definitions in system prompt           │
│  ├─ Parse AI response for tool calls                    │
│  └─ Return structured response                          │
│                                                          │
│  /api/tools/execute                                     │
│  ├─ Validate tool call                                  │
│  ├─ Execute tool with parameters                        │
│  ├─ Return execution result                             │
│  └─ Handle errors gracefully                            │
│                                                          │
│  Tool Registry                                          │
│  ├─ create_file                                         │
│  ├─ modify_file                                         │
│  ├─ read_file                                           │
│  ├─ delete_file                                         │
│  ├─ list_files                                          │
│  ├─ compile_sketch                                      │
│  └─ upload_sketch                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Outils Disponibles

### 1. `create_file`
**Description** : Crée un nouveau fichier avec le contenu spécifié

**Paramètres** :
```json
{
  "path": "string (required)",
  "content": "string (required)",
  "overwrite": "boolean (optional, default: false)"
}
```

**Exemple** :
```json
{
  "tool": "create_file",
  "parameters": {
    "path": "src/blink.ino",
    "content": "void setup() {\n  pinMode(13, OUTPUT);\n}\n\nvoid loop() {\n  digitalWrite(13, HIGH);\n  delay(1000);\n  digitalWrite(13, LOW);\n  delay(1000);\n}"
  }
}
```

---

### 2. `modify_file`
**Description** : Modifie un fichier existant (remplacement ou insertion)

**Paramètres** :
```json
{
  "path": "string (required)",
  "operation": "replace | insert | append (required)",
  "search": "string (required for replace)",
  "content": "string (required)",
  "line": "number (optional, for insert)"
}
```

**Exemples** :

**Replace** :
```json
{
  "tool": "modify_file",
  "parameters": {
    "path": "src/blink.ino",
    "operation": "replace",
    "search": "delay(1000);",
    "content": "delay(500);"
  }
}
```

**Insert** :
```json
{
  "tool": "modify_file",
  "parameters": {
    "path": "src/blink.ino",
    "operation": "insert",
    "line": 2,
    "content": "  Serial.begin(9600);"
  }
}
```

**Append** :
```json
{
  "tool": "modify_file",
  "parameters": {
    "path": "src/blink.ino",
    "operation": "append",
    "content": "\n// End of file"
  }
}
```

---

### 3. `read_file`
**Description** : Lit le contenu d'un fichier

**Paramètres** :
```json
{
  "path": "string (required)"
}
```

---

### 4. `delete_file`
**Description** : Supprime un fichier

**Paramètres** :
```json
{
  "path": "string (required)",
  "confirm": "boolean (required, must be true)"
}
```

---

### 5. `list_files`
**Description** : Liste les fichiers dans un répertoire

**Paramètres** :
```json
{
  "path": "string (optional, default: current directory)",
  "recursive": "boolean (optional, default: false)",
  "pattern": "string (optional, glob pattern)"
}
```

---

### 6. `compile_sketch`
**Description** : Compile le sketch Arduino actuel

**Paramètres** :
```json
{
  "path": "string (required)",
  "board": "string (optional, default: arduino:avr:uno)"
}
```

---

### 7. `upload_sketch`
**Description** : Téléverse le sketch sur la carte

**Paramètres** :
```json
{
  "path": "string (required)",
  "board": "string (required)",
  "port": "string (required)"
}
```

---

## 📝 Format de Réponse de l'IA

L'IA doit retourner ses réponses dans un format structuré :

```json
{
  "message": "Je vais créer un fichier blink.ino pour vous.",
  "tool_calls": [
    {
      "id": "call_1",
      "tool": "create_file",
      "parameters": {
        "path": "blink.ino",
        "content": "void setup() {...}"
      }
    }
  ]
}
```

---

## 🔄 Flux d'Exécution

### Scénario 1 : Création de Fichier

```
User: "Crée un fichier blink.ino qui fait clignoter une LED"

1. Frontend → Backend: POST /api/ai/generate
   {
     "prompt": "Crée un fichier blink.ino qui fait clignoter une LED",
     "provider": "groq"
   }

2. Backend → AI Model: System prompt + User prompt + Tool definitions

3. AI Model → Backend: Response with tool_calls
   {
     "message": "Je crée le fichier blink.ino avec le code de clignotement.",
     "tool_calls": [{
       "tool": "create_file",
       "parameters": {
         "path": "blink.ino",
         "content": "void setup() {...}"
       }
     }]
   }

4. Backend: Execute tool_calls
   - Create file via filesystem
   - Return execution results

5. Backend → Frontend: Complete response
   {
     "message": "Je crée le fichier blink.ino...",
     "tool_calls": [...],
     "tool_results": [{
       "id": "call_1",
       "status": "success",
       "result": "File created: blink.ino"
     }]
   }

6. Frontend: Display results + Update file tree
```

---

### Scénario 2 : Modification de Fichier

```
User: "Change le délai à 500ms dans blink.ino"

1. AI reads current file content
2. AI identifies the change needed
3. AI calls modify_file with replace operation
4. Backend executes modification
5. Frontend updates editor if file is open
```

---

## 🎨 Interface Utilisateur

### Affichage des Tool Calls

```jsx
<div className="ai-tool-execution">
  <div className="tool-header">
    <ToolIcon name={tool.name} />
    <span className="tool-name">{tool.name}</span>
    <span className="tool-status">{status}</span>
  </div>
  
  <div className="tool-parameters">
    {Object.entries(tool.parameters).map(([key, value]) => (
      <div className="param">
        <span className="param-key">{key}:</span>
        <span className="param-value">{value}</span>
      </div>
    ))}
  </div>
  
  <div className="tool-result">
    {result.status === 'success' ? (
      <SuccessMessage>{result.message}</SuccessMessage>
    ) : (
      <ErrorMessage>{result.error}</ErrorMessage>
    )}
  </div>
  
  {tool.name === 'create_file' && (
    <button onClick={() => openFile(tool.parameters.path)}>
      Open File
    </button>
  )}
</div>
```

---

## 🔒 Sécurité

### Restrictions

1. **Sandbox de fichiers** : L'IA ne peut accéder qu'aux fichiers du workspace
2. **Confirmation utilisateur** : Actions destructives nécessitent confirmation
3. **Validation des chemins** : Empêcher l'accès à des chemins système
4. **Limite de taille** : Fichiers limités à 1MB
5. **Rate limiting** : Maximum 10 tool calls par requête

### Chemins Interdits

```python
FORBIDDEN_PATHS = [
    "/etc",
    "/sys",
    "/proc",
    "C:\\Windows",
    "C:\\Program Files",
    "../",  # Path traversal
]
```

---

## 🧪 Exemples d'Usage

### Exemple 1 : Projet Complet

**User** : "Crée un projet complet pour contrôler un servo avec un potentiomètre"

**AI Response** :
```json
{
  "message": "Je vais créer un projet complet avec le code et la documentation.",
  "tool_calls": [
    {
      "tool": "create_file",
      "parameters": {
        "path": "servo_control/servo_control.ino",
        "content": "#include <Servo.h>\n\nServo myServo;\nint potPin = A0;\n..."
      }
    },
    {
      "tool": "create_file",
      "parameters": {
        "path": "servo_control/README.md",
        "content": "# Servo Control\n\n## Composants\n- Arduino Uno\n- Servo moteur\n- Potentiomètre 10kΩ\n..."
      }
    },
    {
      "tool": "create_file",
      "parameters": {
        "path": "servo_control/wiring.txt",
        "content": "Servo:\n- Signal → Pin 9\n- VCC → 5V\n- GND → GND\n\nPotentiomètre:\n- Pin central → A0\n..."
      }
    }
  ]
}
```

---

### Exemple 2 : Refactoring

**User** : "Refactorise le code pour utiliser des fonctions"

**AI Response** :
```json
{
  "message": "Je vais refactoriser le code en créant des fonctions séparées.",
  "tool_calls": [
    {
      "tool": "read_file",
      "parameters": {
        "path": "blink.ino"
      }
    },
    {
      "tool": "modify_file",
      "parameters": {
        "path": "blink.ino",
        "operation": "replace",
        "search": "void loop() {\n  digitalWrite(13, HIGH);\n  delay(1000);\n  digitalWrite(13, LOW);\n  delay(1000);\n}",
        "content": "void blinkLED(int pin, int delayTime) {\n  digitalWrite(pin, HIGH);\n  delay(delayTime);\n  digitalWrite(pin, LOW);\n  delay(delayTime);\n}\n\nvoid loop() {\n  blinkLED(13, 1000);\n}"
      }
    }
  ]
}
```

---

### Exemple 3 : Debugging

**User** : "Ajoute des Serial.println pour debugger"

**AI Response** :
```json
{
  "message": "J'ajoute des instructions de debug au code.",
  "tool_calls": [
    {
      "tool": "modify_file",
      "parameters": {
        "path": "sensor_read.ino",
        "operation": "insert",
        "line": 1,
        "content": "  Serial.begin(9600);\n  Serial.println(\"Starting sensor reading...\");"
      }
    },
    {
      "tool": "modify_file",
      "parameters": {
        "path": "sensor_read.ino",
        "operation": "insert",
        "line": 5,
        "content": "  Serial.print(\"Sensor value: \");\n  Serial.println(sensorValue);"
      }
    }
  ]
}
```

---

## 📊 Métriques & Monitoring

### Logs d'Exécution

```json
{
  "timestamp": "2026-05-11T10:30:00Z",
  "user_id": "user_123",
  "tool": "create_file",
  "parameters": {...},
  "status": "success",
  "execution_time_ms": 45,
  "file_size_bytes": 1024
}
```

### Statistiques

- Nombre de tool calls par session
- Taux de succès/échec
- Outils les plus utilisés
- Temps d'exécution moyen

---

## 🚀 Roadmap

### Phase 1 (Actuel)
- [x] Définition de l'architecture
- [ ] Implémentation backend
- [ ] Implémentation frontend
- [ ] Tests unitaires

### Phase 2
- [ ] Outils avancés (git, refactoring)
- [ ] Confirmation utilisateur pour actions destructives
- [ ] Undo/Redo des modifications
- [ ] Diff viewer pour modifications

### Phase 3
- [ ] Multi-file operations
- [ ] Batch operations
- [ ] Template system
- [ ] AI-powered code review

---

## 🔗 Références

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use](https://docs.anthropic.com/claude/docs/tool-use)
- [Groq Function Calling](https://console.groq.com/docs/tool-use)

---

**Dernière mise à jour** : 11 Mai 2026  
**Version** : 1.0
