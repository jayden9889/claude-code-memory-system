# Cross-Agent Memory Access Guide

## 🌐 For Any AI Agent (Claude, Gemini, GPT, etc.)

This memory system is **agent-agnostic**. Any AI that can read files in this project can access all stored memories.

---

## Quick Start for New Agent

When you (Gemini, GPT, or any AI) start a conversation in this project:

### 1. Load All Memories
```bash
python3 execution/memory_retrieval.py load
```

This will show you:
- Recent conversation summaries
- Key learnings from past sessions
- Technical decisions made
- Code patterns discovered
- Action items pending

### 2. Search for Specific Topics
```bash
# Search for memories about a specific topic
python3 execution/memory_retrieval.py load "topic keyword"

# Example: Find memories about APIs
python3 execution/memory_retrieval.py load "API"

# Get memories by tag
python3 execution/memory_retrieval.py topic "python"
```

### 3. Check What's Stored
```bash
python3 execution/memory_database.py summary
```

Shows total memories, categories, and last update time.

---

## What You'll Find in Memories

Each memory contains:
- **Summary**: What the conversation was about
- **Key Topics**: Technical keywords and themes
- **Learnings**: Important insights discovered
- **Action Items**: TODOs and follow-ups
- **Code Snippets**: Reusable patterns
- **Decisions**: Technical choices and rationale
- **Tags**: For easy searching

---

## Example: Continuing Work from Claude

**Scenario**: User was working with Claude, ran out of credits, now using you (Gemini).

### Step 1: Load Context
```bash
python3 execution/memory_retrieval.py load
```

You'll see output like:
```
============================================================
📚 PERSISTENT MEMORY CONTEXT
============================================================

Total stored memories: 12
  - Insights: 2
  - Learnings: 4
  - Patterns: 2
  - Context history: 4

## Recent Memories:

### Memory 3:
**ID**: 20260112_135648
**Tags**: claude, memory, database, api, agent, mcp, hook
**Learnings**:
  - Learned how to use AssemblyAI API for video transcription
  - Discovered MCP servers for transcription
  - Realized importance of background processing
  - Found that git versioning adds time dimension

**Action Items**:
  - TODO: Test in real conversation when context hits 80%
  - TODO: Monitor memory accumulation over time
```

### Step 2: Reference the Memories
Now you can say to the user:
> "I see from the memory system that you were working with Claude on building a persistent memory system. The last session covered:
> - Transcribing Instagram videos
> - Building memory database with git versioning
> - Creating 7 Python scripts for memory management
>
> There are 2 pending action items:
> 1. Test when context hits 80%
> 2. Monitor memory accumulation
>
> Would you like to continue with testing or move on to something else?"

### Step 3: Add Your Own Memories
When your session ends, save new memories:
```bash
# Create a transcript of your conversation
echo "Your conversation here" > .tmp/gemini_session_$(date +%Y%m%d).txt

# Save to memory database
python3 execution/memory_storage_agent.py .tmp/gemini_session_$(date +%Y%m%d).txt
```

---

## Direct File Access (Advanced)

If you want to read memories directly:

### Memory Locations
```
memory_database/
├── insights/           # JSON files with key insights
├── learnings/          # JSON files with learnings
├── patterns/           # JSON files with code patterns
└── context_history/    # JSON files with full contexts
```

### Read a Specific Memory
```bash
cat memory_database/context_history/20260112_135648.json
```

Returns structured JSON:
```json
{
  "id": "20260112_135648",
  "timestamp": "2026-01-12T13:56:48",
  "tags": ["claude", "memory", "database", "api"],
  "content": {
    "insights": {
      "summary": "Built persistent memory system...",
      "key_topics": ["claude", "memory", "database"],
      "learnings": ["Learned how to use AssemblyAI..."],
      "action_items": ["TODO: Test at 80%..."]
    }
  }
}
```

---

## Git History

All memories are version-controlled in git:

```bash
cd memory_database

# See what was learned recently
git log --since="3 days ago" --oneline

# View a specific memory commit
git show <commit-hash>

# See full timeline
git log --graph --oneline
```

---

## Cross-Agent Workflow Example

### Claude Session 1 (Morning)
- Builds feature X
- Saves memory: "Implemented feature X using pattern Y"

### Gemini Session 2 (Afternoon)
- Loads memories: Sees Claude built feature X
- User asks: "Can you improve feature X?"
- Gemini: "I see Claude implemented feature X this morning. I can improve it by..."
- Saves memory: "Enhanced feature X with optimization Z"

### GPT Session 3 (Evening)
- Loads memories: Sees both Claude and Gemini's work
- User asks: "What did we do today?"
- GPT: "Looking at the memory database:
  - Morning: Claude built feature X
  - Afternoon: Gemini optimized it
  - Here's the complete timeline..."

---

## For Anti-Gravity Agent Manager

When switching between agents in the anti-gravity system:

### 1. Each Agent Should Load Memories on Start
Add to your agent's initialization:
```python
import subprocess

def load_project_memories():
    result = subprocess.run(
        ["python3", "execution/memory_retrieval.py", "load"],
        capture_output=True,
        text=True
    )
    return result.stdout

# At agent startup
memories = load_project_memories()
print("📚 Loading project memories...")
print(memories)
```

### 2. Save Memories on Agent Switch
Before switching agents:
```bash
# Save current agent's session
python3 execution/trigger_memory_storage.py
```

---

## Benefits of Cross-Agent Memory

✅ **Continuity**: No context lost when switching agents
✅ **Collaboration**: Different AIs can build on each other's work
✅ **Credit Management**: Switch agents when credits run out
✅ **Best Tool for Job**: Use Claude for code, Gemini for research, etc.
✅ **Knowledge Accumulation**: All agents contribute to shared knowledge base

---

## Current Memory Stats

Run this anytime to see what's stored:
```bash
python3 execution/memory_database.py summary
```

Current database (as of Jan 12, 2026):
- Total memories: 12
- Insights: 2
- Learnings: 4
- Patterns: 2
- Context history: 4
- Git commits: 17

---

## Testing Cross-Agent Access

### Test 1: Can Gemini Read Claude's Memories?
```bash
# Run this from Gemini
python3 execution/memory_retrieval.py load "Claude"
```

Should show all memories tagged with "claude".

### Test 2: Can Gemini Add Memories?
```bash
# Create test transcript
echo "Gemini test session" > .tmp/gemini_test.txt

# Save memory
python3 execution/memory_storage_agent.py .tmp/gemini_test.txt '{"tags": ["gemini", "test"], "source": "gemini_agent"}'

# Verify it saved
python3 execution/memory_database.py summary
```

---

## Important Notes

1. **All agents share the same database** - be careful not to corrupt it
2. **Git tracks everything** - you can always rollback bad memories
3. **JSON format is standard** - any agent can parse it
4. **Scripts are agent-agnostic** - written in Python, work for anyone
5. **No API keys needed** - everything is local

---

## Quick Reference Commands

```bash
# Load memories at session start
python3 execution/memory_retrieval.py load

# Search for specific topic
python3 execution/memory_retrieval.py load "keyword"

# Check database status
python3 execution/memory_database.py summary

# Save current session
python3 execution/trigger_memory_storage.py

# Run system tests
python3 execution/test_memory_system.py
```

---

## For Agent Developers

If you're building agents for this system, include this in your startup prompt:

```markdown
# Project Memory Context

This project has a persistent memory system. Before starting work:

1. Load memories: Run `python3 execution/memory_retrieval.py load`
2. Review recent context, learnings, and action items
3. Reference past decisions in your responses
4. At session end, save new insights

The user can switch between different AI agents, and all share the same memory database.
```

---

**The memory system enables true AI continuity across different models and sessions!**
