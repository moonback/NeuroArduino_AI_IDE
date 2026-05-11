"""
Script de test pour vérifier l'intégration des outils avec l'IA
"""

import os
import sys
import tempfile
import shutil

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import CodeGeneratorAgent
from tools_registry import ToolRegistry

def test_tool_integration():
    """Test que l'IA utilise bien les outils pour modifier les fichiers"""
    
    print("="*60)
    print("TEST: Intégration des outils avec l'IA")
    print("="*60)
    
    # Create temp workspace
    temp_dir = tempfile.mkdtemp()
    print(f"\n✓ Workspace temporaire créé: {temp_dir}")
    
    try:
        # Create a test Arduino file
        test_file = "blink.ino"
        test_path = os.path.join(temp_dir, test_file)
        
        original_code = """// Blink LED
void setup() {
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
"""
        
        with open(test_path, 'w') as f:
            f.write(original_code)
        
        print(f"✓ Fichier de test créé: {test_file}")
        
        # Create agent with workspace
        agent = CodeGeneratorAgent(workspace_root=temp_dir)
        print(f"✓ Agent créé avec workspace: {temp_dir}")
        
        # Build prompt with file context (simulating what the frontend sends)
        prompt = f"""[CURRENT FILE: '{test_file}' at '{test_file}']
Current file content:
```cpp
{original_code}
```

[USER REQUEST]
Change le délai à 500ms
"""
        
        print("\n" + "-"*60)
        print("PROMPT ENVOYÉ À L'IA:")
        print("-"*60)
        print(prompt[:200] + "...")
        
        # Call AI with tools enabled
        print("\n" + "-"*60)
        print("APPEL DE L'IA (Gemini avec tools)...")
        print("-"*60)
        
        result = agent.generate(
            prompt=prompt,
            board="arduino:avr:uno",
            provider="gemini",  # Changed to Gemini
            history=[],
            enable_tools=True
        )
        
        print("\n" + "-"*60)
        print("RÉSULTAT:")
        print("-"*60)
        print(f"Message: {result.get('message', 'N/A')}")
        print(f"Code généré: {'Oui' if result.get('code') else 'Non'}")
        print(f"Tool calls: {len(result.get('tool_calls', []))}")
        print(f"Tool results: {len(result.get('tool_results', []))}")
        
        if result.get('tool_calls'):
            print("\n✅ L'IA A UTILISÉ DES OUTILS!")
            for i, tool_call in enumerate(result['tool_calls'], 1):
                print(f"\n  Tool {i}: {tool_call['tool']}")
                print(f"  Paramètres: {tool_call['parameters']}")
                
                # Find corresponding result
                tool_result = next(
                    (r for r in result.get('tool_results', []) if r['id'] == tool_call['id']),
                    None
                )
                if tool_result:
                    print(f"  Résultat: {tool_result['result'].get('status', 'unknown')}")
                    if tool_result['result'].get('message'):
                        print(f"  Message: {tool_result['result']['message']}")
            
            # Check if file was modified
            with open(test_path, 'r') as f:
                new_content = f.read()
            
            if new_content != original_code:
                print("\n✅ LE FICHIER A ÉTÉ MODIFIÉ!")
                print("\nContenu modifié:")
                print("-"*60)
                print(new_content)
                print("-"*60)
                
                if "delay(500)" in new_content:
                    print("\n🎉 SUCCÈS! Le délai a bien été changé à 500ms!")
                    return True
                else:
                    print("\n⚠️ Le fichier a été modifié mais le délai n'est pas 500ms")
                    return False
            else:
                print("\n❌ LE FICHIER N'A PAS ÉTÉ MODIFIÉ")
                return False
        else:
            print("\n❌ L'IA N'A PAS UTILISÉ D'OUTILS")
            if result.get('code'):
                print("\n⚠️ L'IA a généré du code au lieu d'utiliser les outils:")
                print("-"*60)
                print(result['code'][:200] + "...")
                print("-"*60)
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n✓ Workspace temporaire supprimé")

def test_smart_modify_directly():
    """Test direct de smart_modify_file"""
    
    print("\n\n" + "="*60)
    print("TEST: smart_modify_file directement")
    print("="*60)
    
    # Create temp workspace
    temp_dir = tempfile.mkdtemp()
    print(f"\n✓ Workspace temporaire créé: {temp_dir}")
    
    try:
        # Create a test Arduino file
        test_file = "blink.ino"
        test_path = os.path.join(temp_dir, test_file)
        
        original_code = """// Blink LED
void setup() {
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
"""
        
        with open(test_path, 'w') as f:
            f.write(original_code)
        
        print(f"✓ Fichier de test créé: {test_file}")
        
        # Create tool registry
        registry = ToolRegistry(workspace_root=temp_dir)
        
        # Execute smart_modify_file
        print("\n" + "-"*60)
        print("EXÉCUTION DE smart_modify_file...")
        print("-"*60)
        
        result = registry.execute_tool("smart_modify_file", {
            "path": test_file,
            "modifications": [
                {
                    "type": "replace",
                    "search": "delay(1000);",
                    "content": "delay(500);"
                }
            ],
            "description": "Changed delay to 500ms"
        })
        
        print(f"\nRésultat: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'N/A')}")
        
        if result.get('status') == 'success':
            print("✅ L'OUTIL A FONCTIONNÉ!")
            
            # Check file content
            with open(test_path, 'r') as f:
                new_content = f.read()
            
            if "delay(500)" in new_content:
                print("✅ Le fichier a bien été modifié!")
                print("\nContenu modifié:")
                print("-"*60)
                print(new_content)
                print("-"*60)
                return True
            else:
                print("❌ Le fichier n'a pas été modifié correctement")
                return False
        else:
            print(f"❌ L'OUTIL A ÉCHOUÉ: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n✓ Workspace temporaire supprimé")

if __name__ == "__main__":
    print("\nTESTS D'INTEGRATION DES OUTILS\n")
    
    # Test 1: Direct tool execution
    test1_passed = test_smart_modify_directly()
    
    # Test 2: AI integration
    test2_passed = test_tool_integration()
    
    # Summary
    print("\n\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"Test 1 (smart_modify_file direct): {'✅ PASSÉ' if test1_passed else '❌ ÉCHOUÉ'}")
    print(f"Test 2 (Intégration IA): {'✅ PASSÉ' if test2_passed else '❌ ÉCHOUÉ'}")
    
    if test1_passed and test2_passed:
        print("\nTOUS LES TESTS SONT PASSES!")
        print("\nLe probleme vient probablement de:")
        print("  1. Le workspace path n'est pas envoye correctement depuis le frontend")
        print("  2. Le chemin du fichier n'est pas construit correctement")
        print("  3. Le fichier n'est pas recharge dans l'editeur apres modification")
    elif test1_passed and not test2_passed:
        print("\nL'outil fonctionne mais l'IA ne l'utilise pas!")
        print("\nCela signifie que:")
        print("  1. Le system prompt doit etre ameliore")
        print("  2. Groq ne supporte peut-etre pas bien les tool calls")
        print("  3. Essayez avec Gemini a la place")
    else:
        print("\nL'OUTIL NE FONCTIONNE PAS CORRECTEMENT")
        print("\nVerifiez:")
        print("  1. Les dependances sont installees")
        print("  2. Le workspace path est correct")
        print("  3. Les permissions de fichiers")
    
    print("\n" + "="*60 + "\n")
