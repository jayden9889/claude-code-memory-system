# Claude Code Persistent Memory System

## Goal
Solve Claude Code's stateless memory problem by creating a hook-based system that automatically converts short-term conversation insights into long-term stored memory, mimicking how the human brain consolidates daily memories during sleep.

---

## 5-Step Implementation

### 1. **Monitor Context Usage with Hook**
Set up a Claude Code hook that continuously monitors the conversation transcript length. Trigger when context reaches 80% capacity (before auto-compaction occurs).

### 2. **Prompt User for Memory Storage**
When triggered, the hook sends a prompt to Claude Code instructing it to use the `AskUserQuestion` tool, asking: "Do you want to save a memory about this conversation?"

### 3. **Launch Background Memory Agent**
If user responds "yes", Claude Code triggers a memory storage background subagent that operates independently without blocking the main conversation.

### 4. **Distill & Store Insights**
The background subagent reads the entire conversation transcript, extracts key insights and learnings, then stores them in the appropriate locations within your persistent memory storage database.

### 5. **Version Control with Git**
Store the persistent memory database in a git repository to add a time dimension—tracking how knowledge evolves, when insights were learned, and enabling rollback if needed.

---

## Key Components

**Hook Configuration:**
- **Trigger**: 80% context usage
- **Action**: Prompt Claude to ask user about memory storage
- **Location**: `.claude/hooks/` or project hooks config

**Memory Storage Database:**
- **Format**: Structured files (JSON, Markdown, or database)
- **Organization**: Categorized by topic/domain
- **Version Control**: Git repository for temporal tracking

**Background Subagent:**
- **Input**: Full conversation transcript
- **Process**: Distill insights, identify learnings
- **Output**: Stored memories in persistent database

---

## Execution Tools

Create these scripts in `execution/`:
- `hooks/monitor_context.py` - Monitors context usage percentage
- `hooks/trigger_memory_prompt.py` - Triggers AskUserQuestion when threshold hit
- `memory_agent.py` - Background subagent that distills and stores memories
- `memory_database.py` - CRUD operations for persistent memory storage

---

## Success Metrics
- Claude remembers insights from previous conversations
- New conversations reference stored knowledge
- Memory database grows with high-quality distilled insights
- Git history shows knowledge evolution over time
- Zero interruption to user workflow (runs in background)

---

## Source
**Video**: https://www.instagram.com/p/DTO6HfSjTnE/
**Transcript**: `.tmp/transcript_instagram_DTO6HfSjTnE.txt`

---

## Implementation Status

✅ **SYSTEM FULLY OPERATIONAL** - All components built and tested

- [x] Set up context monitoring hook (80% threshold) - `.claude/hooks/context_monitor.py`
- [x] Configure AskUserQuestion prompt trigger - Integrated in hook
- [x] Build background memory storage subagent - `execution/memory_storage_agent.py`
- [x] Create persistent memory database structure - `memory_database/` (4 categories)
- [x] Initialize git repository for memory storage - Active with 15+ commits
- [x] Test full memory consolidation workflow - ✅ 5/5 tests passing
- [x] Validate memory retrieval in new conversations - `execution/memory_retrieval.py`

**Test Results**: 5/5 tests passed (100%)
**Current Database**: 10 memories stored
  - Insights: 2
  - Learnings: 3
  - Patterns: 2
  - Context History: 3

**Git Versioning**: 15 commits tracking knowledge evolution

---

## Quick Start

```bash
# Run the test suite
python3 execution/test_memory_system.py

# Load current memories
python3 execution/memory_retrieval.py load

# Check database status
python3 execution/memory_database.py summary
```

**Full Documentation**: See [MEMORY_SYSTEM_GUIDE.md](../MEMORY_SYSTEM_GUIDE.md)
