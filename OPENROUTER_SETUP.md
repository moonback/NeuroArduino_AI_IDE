# Configuration OpenRouter - Instructions

## Modifications effectuées

J'ai remplacé Groq par OpenRouter dans votre application Arduino AI IDE. Voici ce qui a été modifié :

### 1. Fichiers Backend modifiés
- **`backend/agents.py`** : Remplacé le client Groq par OpenRouter (utilise l'API compatible OpenAI)
- **`backend/requirements.txt`** : Remplacé `groq` par `openai`
- **`backend/.env`** : Remplacé `GROQ_API_KEY` par `OPENROUTER_API_KEY`

### 2. Fichiers Frontend modifiés
- **`frontend/src/components/AIPanel.jsx`** : Mis à jour l'interface pour afficher "OpenRouter" au lieu de "Groq"

## Étapes pour terminer la configuration

### 1. Obtenir une clé API OpenRouter (GRATUIT)

1. Allez sur https://openrouter.ai/
2. Créez un compte (gratuit)
3. Allez dans "Keys" : https://openrouter.ai/keys
4. Créez une nouvelle clé API
5. Copiez la clé (elle commence par `sk-or-v1-...`)

### 2. Configurer la clé API

Ouvrez le fichier `backend/.env` et remplacez :
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Par votre vraie clé :
```
OPENROUTER_API_KEY=sk-or-v1-votre-cle-ici
```

### 3. Installer les dépendances Python

Ouvrez un terminal dans le dossier `backend` et exécutez :

```bash
pip install -r requirements.txt
```

Ou si vous utilisez un environnement virtuel :

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Redémarrer l'application

1. Arrêtez le backend s'il est en cours d'exécution (Ctrl+C)
2. Redémarrez-le :
   ```bash
   cd backend
   python main.py
   ```
3. Redémarrez le frontend si nécessaire

## Modèle gratuit utilisé

Le modèle configuré est : **`meta-llama/llama-3.1-8b-instruct:free`**

C'est un modèle gratuit sur OpenRouter. Vous pouvez le changer dans `backend/agents.py` ligne ~45 :

```python
self.openrouter_model = "meta-llama/llama-3.1-8b-instruct:free"
```

### Autres modèles gratuits disponibles sur OpenRouter :

- `meta-llama/llama-3.1-8b-instruct:free` (recommandé)
- `google/gemma-2-9b-it:free`
- `mistralai/mistral-7b-instruct:free`
- `microsoft/phi-3-mini-128k-instruct:free`

Voir la liste complète : https://openrouter.ai/models?order=newest&supported_parameters=tools

## Avantages d'OpenRouter

✅ **Gratuit** : Modèles gratuits disponibles  
✅ **Compatible OpenAI** : Utilise la même API que OpenAI  
✅ **Function Calling** : Support des outils (analyze_code, modify_file, etc.)  
✅ **Plusieurs modèles** : Accès à de nombreux modèles différents  
✅ **Pas de limite stricte** : Plus flexible que Groq pour les modèles gratuits  

## Vérification

Pour vérifier que tout fonctionne :

1. Ouvrez l'application
2. Dans le panneau AI, vous devriez voir "OpenRouter Llama 3.1" dans le sélecteur de modèle
3. Essayez d'envoyer un message : "Génère un code pour faire clignoter une LED"
4. Le modèle devrait répondre normalement

## Dépannage

### Erreur "No module named 'openai'"
```bash
pip install openai
```

### Erreur "OPENROUTER_API_KEY not found"
Vérifiez que vous avez bien mis votre clé dans `backend/.env`

### Erreur "Invalid API key"
Vérifiez que votre clé commence par `sk-or-v1-` et qu'elle est valide sur https://openrouter.ai/keys

### Le modèle ne répond pas
- Vérifiez votre connexion internet
- Vérifiez que vous avez des crédits sur OpenRouter (les modèles gratuits ne nécessitent pas de crédits)
- Essayez un autre modèle gratuit

## Support

Si vous avez des questions, consultez :
- Documentation OpenRouter : https://openrouter.ai/docs
- Liste des modèles : https://openrouter.ai/models
