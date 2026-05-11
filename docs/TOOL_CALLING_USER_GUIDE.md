# 🛠️ Tool Calling - User Guide

## What is Tool Calling?

Tool calling allows the AI assistant to **directly modify your files** without showing code in the conversation. Instead of generating code that you have to manually apply, the AI uses specialized tools to make precise changes to your files automatically.

## How It Works

### Traditional Way (Without Tools) ❌
```
You: "Change the delay to 500ms"

AI: "Here's the updated code:"
[Shows full code block]

You: [Click "Apply to Editor"]
You: [Manually verify changes]
```

### New Way (With Tools) ✅
```
You: "Change the delay to 500ms"

AI: "I'll update the delay values..."
[Tool executes automatically]
[File updates in editor]

AI: "Done! Changed all delay() calls to 500ms."
```

## Getting Started

### 1. Enable Tools

Make sure the **wrench icon** (🔧) in the AI panel is **active** (highlighted).

- **Active** = Tools enabled ✅
- **Inactive** = Tools disabled ❌

### 2. Open a File

Open any `.ino`, `.cpp`, or `.h` file in the editor. The AI will see the current file and can modify it.

### 3. Ask for Changes

Use natural language to request modifications:

**Examples:**
- "Change the delay to 500ms"
- "Add Serial debugging"
- "Improve this code"
- "Fix the bug on line 10"
- "Add a button on pin 2"
- "Refactor to use constants"

### 4. Watch the Magic ✨

The AI will:
1. Understand your request
2. Call the appropriate tool
3. Modify the file
4. Update the editor automatically
5. Confirm what was changed

## Available Tools

### 1. **smart_modify_file** 🎯
Intelligently modifies specific parts of a file.

**Use cases:**
- Change specific values
- Add new code sections
- Remove old code
- Refactor existing code

**Example:**
```
You: "Change delay(1000) to delay(500)"
AI: Uses smart_modify_file to replace the text
```

### 2. **create_file** 📄
Creates a new file with content.

**Use cases:**
- Generate new sketches
- Create header files
- Add documentation

**Example:**
```
You: "Create a new file called utils.h with helper functions"
AI: Uses create_file to generate the file
```

### 3. **read_file** 👁️
Reads the content of a file.

**Use cases:**
- Analyze other files in the project
- Check dependencies
- Review existing code

**Example:**
```
You: "What's in config.h?"
AI: Uses read_file to read and explain the file
```

### 4. **modify_file** ✏️
Simple file modifications (replace, insert, append).

**Use cases:**
- Simple text replacements
- Append to end of file
- Insert at specific line

**Example:**
```
You: "Append a comment at the end"
AI: Uses modify_file with append operation
```

### 5. **list_files** 📁
Lists files in the project.

**Use cases:**
- Explore project structure
- Find specific files
- Check what files exist

**Example:**
```
You: "What .ino files are in this project?"
AI: Uses list_files to show all .ino files
```

### 6. **create_directory** 📂
Creates a new folder.

**Use cases:**
- Organize project structure
- Create library folders

**Example:**
```
You: "Create a folder called 'libraries'"
AI: Uses create_directory
```

### 7. **rename_file** 🔄
Renames or moves a file.

**Use cases:**
- Rename files
- Move files to different folders

**Example:**
```
You: "Rename sketch.ino to blink.ino"
AI: Uses rename_file
```

### 8. **delete_file** 🗑️
Deletes a file (requires confirmation).

**Use cases:**
- Remove obsolete files
- Clean up project

**Example:**
```
You: "Delete old_code.ino"
AI: Uses delete_file (asks for confirmation)
```

## Best Practices

### ✅ DO:

1. **Be Specific**
   - ✅ "Change delay(1000) to delay(500)"
   - ❌ "Make it faster"

2. **One Change at a Time**
   - ✅ "Add Serial debugging"
   - ✅ "Then change the LED pin to 13"
   - ❌ "Add Serial debugging and change LED pin and add button and..."

3. **Keep Tools Enabled**
   - Always have the wrench icon active for file modifications

4. **Open the File First**
   - Open the file you want to modify before asking

5. **Review Changes**
   - Check the editor after modifications
   - The AI will explain what changed

### ❌ DON'T:

1. **Don't Disable Tools for Modifications**
   - If tools are disabled, AI will show code instead

2. **Don't Ask for Multiple Files at Once**
   - Modify one file at a time for best results

3. **Don't Expect Tools for New Sketches**
   - For completely new code, AI will generate it normally
   - Tools are for modifying existing files

## Choosing a Model

### Groq Llama 3.3 ⚡
- **Speed**: Very fast
- **Reliability**: Excellent
- **Cost**: Free
- **Tool Support**: ✅ Excellent
- **Best for**: Most tasks

### Gemini 2.0 Flash 🧠
- **Speed**: Fast
- **Reliability**: Excellent
- **Cost**: Free (20 requests/day)
- **Tool Support**: ✅ Excellent
- **Best for**: Complex reasoning

**Recommendation**: Use **Groq** for most tasks. Switch to **Gemini** for complex modifications or when you need advanced reasoning.

## Troubleshooting

### Problem: AI Shows Code Instead of Using Tools

**Solutions:**
1. ✅ Check that tools are enabled (wrench icon active)
2. ✅ Make sure a file is open in the editor
3. ✅ Try rephrasing your request
4. ✅ Switch between Groq and Gemini

### Problem: Tool Call Failed

**Solutions:**
1. ✅ Check the error message in the conversation
2. ✅ Verify the file exists and is writable
3. ✅ Try a simpler modification first
4. ✅ Restart the backend if needed

### Problem: File Didn't Update

**Solutions:**
1. ✅ Check if the tool call succeeded (green checkmark)
2. ✅ Refresh the file tree
3. ✅ Close and reopen the file
4. ✅ Check the backend console for errors

### Problem: Gemini Quota Exceeded

**Solutions:**
1. ✅ Switch to Groq (no quota limits)
2. ✅ Wait 24 hours for quota reset
3. ✅ Use a different Gemini API key

## Example Workflows

### Workflow 1: Modify Existing Code

```
1. Open blink.ino
2. You: "Change the LED pin from 13 to 9"
3. AI: [Uses smart_modify_file]
4. Result: File updated, LED now on pin 9
```

### Workflow 2: Add New Feature

```
1. Open sensor.ino
2. You: "Add Serial debugging to show sensor values"
3. AI: [Uses smart_modify_file to add Serial.begin() and Serial.println()]
4. Result: Debugging added to your code
```

### Workflow 3: Refactor Code

```
1. Open motor_control.ino
2. You: "Replace magic numbers with named constants"
3. AI: [Uses smart_modify_file to add constants and replace values]
4. Result: Code is more readable with constants
```

### Workflow 4: Fix Bug

```
1. Open button.ino
2. You: "Fix the button debouncing issue"
3. AI: [Uses smart_modify_file to add debounce logic]
4. Result: Button works reliably
```

## Advanced Usage

### Multiple Modifications

You can ask for multiple changes in one request:

```
You: "Change delay to 500ms and add Serial debugging"

AI: [Uses smart_modify_file with multiple modifications]
- Modification 1: Replace delay(1000) with delay(500)
- Modification 2: Add Serial.begin(9600) in setup()
- Modification 3: Add Serial.println() statements
```

### Project-Wide Context

Enable "Include all project files" to let the AI see your entire project:

```
☑️ Include all project files (5 files)

You: "Make sure all files use the same LED pin constant"

AI: [Reads all files, identifies inconsistencies, modifies them]
```

### Precise Line-Based Edits

For very specific changes, mention line numbers:

```
You: "Delete lines 10-15"
AI: [Uses smart_modify_file with delete_lines operation]
```

## Tips for Best Results

1. **Start Simple**: Begin with small changes to see how it works
2. **Be Clear**: Use specific language about what you want
3. **Check Results**: Always verify the changes in the editor
4. **Iterate**: Make changes incrementally, not all at once
5. **Use Context**: Open the file you want to modify first
6. **Trust the AI**: Let it use tools instead of showing code

## Keyboard Shortcuts

- **Send Message**: `Enter`
- **New Line**: `Shift + Enter`
- **Focus Input**: Click in the AI panel

## FAQ

### Q: Will tools work with any file type?
**A:** Tools work best with `.ino`, `.cpp`, `.h`, and `.c` files. They can also work with text files like `.txt`, `.md`, etc.

### Q: Can I undo tool changes?
**A:** Yes! Use `Ctrl+Z` in the editor to undo changes, or use your version control system (Git).

### Q: Are my files safe?
**A:** Yes! All file operations are validated and sandboxed to your workspace. The AI cannot access files outside your project.

### Q: What if I don't want tools?
**A:** Click the wrench icon to disable tools. The AI will then generate code normally.

### Q: Can tools create entire projects?
**A:** Tools are best for modifying existing files. For new projects, the AI will generate code that you can save manually.

### Q: How do I know if a tool succeeded?
**A:** Look for the green checkmark (✅) next to the tool call in the conversation.

## Getting Help

If you encounter issues:

1. Check the **backend console** for error messages
2. Look at the **tool call results** in the conversation
3. Try **switching models** (Groq ↔ Gemini)
4. **Restart the backend** if needed
5. Check the **documentation** in the `docs/` folder

## Summary

Tool calling makes the AI assistant **much more powerful** by allowing it to:
- ✅ Modify files directly
- ✅ Make precise changes
- ✅ Work faster
- ✅ Reduce manual work
- ✅ Provide a cleaner conversation

**Enable tools, open a file, and start coding with AI!** 🚀
