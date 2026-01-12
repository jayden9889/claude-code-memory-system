# Claude Code Persistent Memory System - User Guide

## 🎉 System Status: FULLY OPERATIONAL

All tests passed! Your persistent memory system is ready to use.

---

## What This System Does

Solves Claude Code's stateless memory problem by automatically:
1. **Monitoring** conversation context usage (triggers at 80%)
2. **Prompting** you to save memories when context is nearly full
3. **Distilling** key insights from the entire conversation
4. **Storing** memories in a git-versioned database
5. **Retrieving** relevant memories in future conversations

---

## File Structure

```
memory_database/               # Git-versioned memory storage
├── insights/                  # Key insights
├── learnings/                 # Learnings and discoveries
├── patterns/                  # Code patterns and snippets
└── context_history/           # Full conversation contexts

execution/
├── memory_database.py         # Database manager (CRUD operations)
├── memory_storage_agent.py    # Distills & stores memories
├── memory_retrieval.py        # Retrieves memories for context
├── trigger_memory_storage.py  # Triggered when user says "yes"
└── test_memory_system.py      # Test suite (all tests passing!)

.claude/
├── hooks/
│   └── context_monitor.py     # Monitors context at 80%
└── hooks_config.json          # Hook configuration
```

---

## How to Use

### Automatic Operation (Recommended)

The system works automatically when integrated with Claude Code hooks:

1. **You chat normally** with Claude Code
2. **At 80% context**, Claude will ask: "Would you like to save memories from this conversation?"
3. **You respond** "Yes" or "No"
4. **If yes**, a background agent automatically:
   - Saves the full transcript
   - Extracts key insights, learnings, patterns
   - Commits everything to git
   - You can continue chatting immediately

### Manual Commands

You can also use the system manually:

#### Save Current Conversation
```bash
# Save a transcript file manually
python3 execution/memory_storage_agent.py path/to/transcript.txt
```

#### Retrieve Memories
```bash
# Load recent memories
python3 execution/memory_retrieval.py load

# Search for specific topic
python3 execution/memory_retrieval.py load "API implementation"

# Get memories by topic tag
python3 execution/memory_retrieval.py topic "python"

# Export summary
python3 execution/memory_retrieval.py export
```

#### Check Memory Database
```bash
# Get database summary
python3 execution/memory_database.py summary

# Search memories
python3 execution/memory_database.py search "error handling"
```

#### Run Tests
```bash
# Verify system is working
python3 execution/test_memory_system.py
```

---

## What Gets Stored

For each conversation, the system automatically extracts and stores:

### 1. **Summary**
- Brief overview of conversation topic

### 2. **Key Topics**
- Technical keywords and themes discussed
- Auto-tagged for easy retrieval

### 3. **Action Items**
- TODOs mentioned in conversation
- Tasks that need follow-up

### 4. **Learnings**
- Insights discovered during conversation
- "Aha!" moments and realizations
- Best practices identified

### 5. **Code Snippets**
- Code blocks from the conversation
- Stored as reusable patterns

### 6. **Decisions Made**
- Technical choices and rationale
- Architecture decisions

---

## Git Versioning

All memories are automatically committed to git:

```bash
# View memory history
cd memory_database
git log --oneline

# See what was learned on a specific date
git log --since="2 days ago" --oneline

# See full details of a memory commit
git show <commit-hash>

# Revert a memory if needed
git revert <commit-hash>
```

This gives you:
- **Time dimension**: Track how knowledge evolved
- **Audit trail**: See what was learned when
- **Rollback**: Undo bad memories if needed

---

## Example Workflow

### Scenario: You're implementing a new feature

1. **Start coding** with Claude Code
2. **Work normally** - Claude helps you build the feature
3. **At 80% context**, Claude asks: "Save memories?"
4. **You say "Yes"**
5. **Background agent** extracts:
   - The feature you built
   - Learnings about the codebase
   - Code patterns used
   - Decisions made (which library, approach, etc.)
6. **Next conversation**, Claude loads these memories
7. **Claude remembers** what you built and learned!

---

## Advanced Usage

### Custom Memory Storage

```python
from memory_database import MemoryDatabase

db = MemoryDatabase()

# Store custom memory
db.store_memory(
    category="insights",
    content={
        "insight": "Discovered that async/await improves performance",
        "context": "Working on API endpoints",
        "impact": "20% performance improvement"
    },
    tags=["performance", "async", "api"]
)
```

### Programmatic Retrieval

```python
from memory_database import MemoryDatabase

db = MemoryDatabase()

# Get recent memories
memories = db.retrieve_memories(limit=5)

# Search for specific content
results = db.search_memories("async performance")

# Filter by tags
tagged = db.retrieve_memories(tags=["api", "performance"])
```

---

## Configuration

Edit `.claude/hooks_config.json` to customize:

```json
{
  "memory_system": {
    "enabled": true,
    "threshold_percent": 80,        # When to trigger (default: 80%)
    "auto_save": false,             # Auto-save without asking (default: false)
    "memory_database_path": "memory_database"
  }
}
```

---

## Troubleshooting

### Hook not triggering?

1. Check if hooks are enabled in your Claude Code settings
2. Verify `.claude/hooks/context_monitor.py` is executable:
   ```bash
   chmod +x .claude/hooks/context_monitor.py
   ```

### Memories not saving?

1. Run test suite to diagnose:
   ```bash
   python3 execution/test_memory_system.py
   ```
2. Check git is initialized in `memory_database/`:
   ```bash
   cd memory_database && git status
   ```

### Can't retrieve old memories?

1. Check database summary:
   ```bash
   python3 execution/memory_database.py summary
   ```
2. List memory files:
   ```bash
   ls -la memory_database/*/
   ```

---

## Test Results

```
✅ Passed: 5/5 tests
🎉 All tests passed! Memory system is ready to use.

Tests:
✅ Memory Database Operations
✅ Memory Storage Agent
✅ Memory Retrieval System
✅ Context Monitor Hook
✅ Full Workflow with Git Versioning
```

Current database stats:
- **Total memories**: 10
- **Insights**: 2
- **Learnings**: 3
- **Patterns**: 2
- **Context history**: 3

---

## Integration with Claude Code

To enable hooks in your IDE:

1. **VSCode**: Hooks should auto-load from `.claude/hooks_config.json`
2. **CLI**: Set environment variable:
   ```bash
   export CLAUDE_HOOKS_CONFIG=.claude/hooks_config.json
   ```

---

## Next Steps

1. ✅ System is ready - just use Claude Code normally!
2. When prompted at 80% context, say "Yes" to save memories
3. Watch your knowledge base grow over time
4. In future conversations, Claude will reference past learnings

---

## Benefits You'll See

- **No more repeating context** - Claude remembers past conversations
- **Faster development** - Reuse patterns and solutions you've discovered
- **Knowledge accumulation** - Build a personal AI knowledge base
- **Better decisions** - Reference past architectural choices
- **Learning tracker** - See what you've learned over time

---

## Support

If you encounter issues:
1. Run the test suite: `python3 execution/test_memory_system.py`
2. Check the logs in `.tmp/`
3. Review git history: `cd memory_database && git log`

The system is self-annealing - it will try to fix issues automatically!

---

**System built and tested: January 12, 2026**
**Status: All tests passing ✅**
