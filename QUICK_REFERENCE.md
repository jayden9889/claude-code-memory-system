# Memory System - Quick Reference Card

## 🚀 Status: OPERATIONAL ✅

---

## How It Works (User View)

1. **Chat normally** with Claude Code
2. **At 80% context**, Claude asks: "Save memories?"
3. **Say "Yes"** → Memories saved automatically in background
4. **Next chat** → Claude remembers and references past learnings

---

## Key Commands

### Check Memory Status
```bash
python3 execution/memory_database.py summary
```

### Load Memories
```bash
# Recent memories
python3 execution/memory_retrieval.py load

# Search memories
python3 execution/memory_retrieval.py load "topic keyword"

# Memories by tag
python3 execution/memory_retrieval.py topic "python"
```

### Manual Save
```bash
# Save a conversation transcript
python3 execution/memory_storage_agent.py path/to/transcript.txt
```

### Test System
```bash
python3 execution/test_memory_system.py
```

---

## What's Stored

- ✅ **Conversation summaries**
- ✅ **Key topics & tags**
- ✅ **Learnings & insights**
- ✅ **Action items & TODOs**
- ✅ **Code snippets & patterns**
- ✅ **Technical decisions**

---

## File Locations

```
memory_database/          # Your memories (git-versioned)
├── insights/            # Key insights
├── learnings/           # What you learned
├── patterns/            # Code patterns
└── context_history/     # Full conversation contexts

.claude/hooks/           # Hook scripts
execution/               # Memory management scripts
```

---

## Current Stats

**Total Memories**: 10
- Insights: 2
- Learnings: 3
- Patterns: 2
- Context History: 3

**Git Commits**: 15 (tracking knowledge over time)

**Test Status**: 5/5 passing ✅

---

## Troubleshooting

**Memories not saving?**
```bash
python3 execution/test_memory_system.py
```

**Can't retrieve memories?**
```bash
python3 execution/memory_database.py summary
ls -la memory_database/*/
```

**Hook not triggering?**
```bash
chmod +x .claude/hooks/context_monitor.py
```

---

## Git Time Machine

```bash
cd memory_database

# View memory history
git log --oneline

# What was learned today?
git log --since="today"

# See a specific memory
git show <commit-hash>
```

---

**Full Guide**: [MEMORY_SYSTEM_GUIDE.md](MEMORY_SYSTEM_GUIDE.md)

Built: January 12, 2026
