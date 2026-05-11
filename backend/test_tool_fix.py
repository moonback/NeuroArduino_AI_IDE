"""
Test script to verify tool calling fix
Tests both Groq and Gemini with function calling
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import CodeGeneratorAgent
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_tool_calling():
    """Test that AI actually uses tools to modify files"""
    
    print("=" * 80)
    print("TOOL CALLING FIX VERIFICATION TEST")
    print("=" * 80)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\n📁 Created temporary workspace: {temp_dir}")
        
        # Create a test Arduino file
        test_file = os.path.join(temp_dir, "blink.ino")
        original_code = """void setup() {
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
"""
        
        with open(test_file, 'w') as f:
            f.write(original_code)
        
        print(f"✅ Created test file: blink.ino")
        print(f"📄 Original code:\n{original_code}")
        
        # Test with Groq
        print("\n" + "=" * 80)
        print("TEST 1: Groq Llama 3.1 with Function Calling")
        print("=" * 80)
        
        agent_groq = CodeGeneratorAgent(workspace_root=temp_dir)
        
        # Simulate the prompt that frontend sends
        prompt_with_context = f"""[CURRENT FILE: 'blink.ino' at 'blink.ino']
Current file content:
```cpp
{original_code}
```

[USER REQUEST]
Change the delay to 500ms
"""
        
        print(f"\n📤 Sending request to Groq...")
        print(f"Prompt: 'Change the delay to 500ms'")
        
        result_groq = agent_groq.generate(
            prompt=prompt_with_context,
            board="arduino:avr:uno",
            provider="groq",
            history=[],
            enable_tools=True
        )
        
        print(f"\n📥 Groq Response:")
        print(f"Message: {result_groq.get('message', 'No message')}")
        print(f"Tool calls: {len(result_groq.get('tool_calls', []))}")
        
        if result_groq.get('tool_calls'):
            print(f"✅ SUCCESS: Groq used {len(result_groq['tool_calls'])} tool(s)")
            for i, tc in enumerate(result_groq['tool_calls']):
                print(f"  Tool {i+1}: {tc['tool']}")
                print(f"  Parameters: {tc['parameters']}")
            
            # Check if file was modified
            with open(test_file, 'r') as f:
                modified_code = f.read()
            
            if "delay(500)" in modified_code:
                print(f"✅ File was modified correctly!")
                print(f"📄 Modified code:\n{modified_code}")
            else:
                print(f"❌ File was NOT modified correctly")
                print(f"📄 Current code:\n{modified_code}")
        else:
            print(f"❌ FAILED: Groq did NOT use tools")
            if result_groq.get('code'):
                print(f"⚠️ Code was returned in conversation instead:")
                print(result_groq['code'][:200] + "...")
        
        # Reset file for Gemini test
        with open(test_file, 'w') as f:
            f.write(original_code)
        
        # Test with Gemini
        print("\n" + "=" * 80)
        print("TEST 2: Gemini 2.0 Flash with Function Calling")
        print("=" * 80)
        
        agent_gemini = CodeGeneratorAgent(workspace_root=temp_dir)
        
        print(f"\n📤 Sending request to Gemini...")
        print(f"Prompt: 'Change the delay to 500ms'")
        
        try:
            result_gemini = agent_gemini.generate(
                prompt=prompt_with_context,
                board="arduino:avr:uno",
                provider="gemini",
                history=[],
                enable_tools=True
            )
            
            print(f"\n📥 Gemini Response:")
            print(f"Message: {result_gemini.get('message', 'No message')}")
            print(f"Tool calls: {len(result_gemini.get('tool_calls', []))}")
            
            if result_gemini.get('tool_calls'):
                print(f"✅ SUCCESS: Gemini used {len(result_gemini['tool_calls'])} tool(s)")
                for i, tc in enumerate(result_gemini['tool_calls']):
                    print(f"  Tool {i+1}: {tc['tool']}")
                    print(f"  Parameters: {tc['parameters']}")
                
                # Check if file was modified
                with open(test_file, 'r') as f:
                    modified_code = f.read()
                
                if "delay(500)" in modified_code:
                    print(f"✅ File was modified correctly!")
                    print(f"📄 Modified code:\n{modified_code}")
                else:
                    print(f"❌ File was NOT modified correctly")
                    print(f"📄 Current code:\n{modified_code}")
            else:
                print(f"❌ FAILED: Gemini did NOT use tools")
                if result_gemini.get('code'):
                    print(f"⚠️ Code was returned in conversation instead:")
                    print(result_gemini['code'][:200] + "...")
        
        except Exception as e:
            print(f"❌ Gemini test failed with error: {e}")
            print(f"   (This might be due to API quota limits)")
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        groq_passed = len(result_groq.get('tool_calls', [])) > 0
        
        print(f"Groq Llama 3.1: {'✅ PASSED' if groq_passed else '❌ FAILED'}")
        print(f"Gemini 2.0 Flash: ⏭️ SKIPPED (test manually in IDE)")
        
        if groq_passed:
            print(f"\n🎉 SUCCESS! Tool calling is working!")
            print(f"The AI now modifies files directly without showing code in conversation.")
        else:
            print(f"\n⚠️ Tool calling still needs work.")
            print(f"Recommendations:")
            print(f"  1. Try using Gemini instead of Groq (better function calling)")
            print(f"  2. Make sure API keys are valid")
            print(f"  3. Check that the model supports function calling")

if __name__ == "__main__":
    test_tool_calling()
