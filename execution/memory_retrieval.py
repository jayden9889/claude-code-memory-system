#!/usr/bin/env python3
"""
Memory retrieval system for Claude Code.
Loads relevant memories at conversation start.
"""

import sys
import os
from pathlib import Path
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_database import MemoryDatabase


def load_relevant_memories(query: str = None, limit: int = 5) -> str:
    """
    Load relevant memories for current conversation context.

    Args:
        query: Optional search query
        limit: Maximum memories to retrieve

    Returns:
        str: Formatted memory context for Claude
    """
    db = MemoryDatabase()

    # Get database summary
    summary = db.get_memory_summary()

    # Build context string
    context = []
    context.append("=" * 60)
    context.append("📚 PERSISTENT MEMORY CONTEXT")
    context.append("=" * 60)
    context.append("")
    context.append(f"Total stored memories: {summary['total_memories']}")
    context.append(f"  - Insights: {summary['insights']}")
    context.append(f"  - Learnings: {summary['learnings']}")
    context.append(f"  - Patterns: {summary['patterns']}")
    context.append(f"  - Context history: {summary['context_history']}")

    if summary['last_updated']:
        context.append(f"  - Last updated: {summary['last_updated']}")

    context.append("")

    # Retrieve relevant memories
    if query:
        memories = db.search_memories(query, limit=limit)
        context.append(f"## Relevant Memories (query: '{query}'):")
    else:
        memories = db.retrieve_memories(limit=limit)
        context.append(f"## Recent Memories:")

    context.append("")

    if not memories:
        context.append("No stored memories found yet.")
    else:
        for i, memory in enumerate(memories, 1):
            context.append(f"### Memory {i}:")
            context.append(f"**ID**: {memory.get('id', 'unknown')}")
            context.append(f"**Timestamp**: {memory.get('timestamp', 'unknown')}")

            if memory.get('tags'):
                context.append(f"**Tags**: {', '.join(memory['tags'])}")

            content = memory.get('content', {})

            # Display insights if available
            if 'insights' in content:
                insights = content['insights']

                if insights.get('summary'):
                    context.append(f"**Summary**: {insights['summary']}")

                if insights.get('key_topics'):
                    topics = ', '.join(insights['key_topics'][:5])
                    context.append(f"**Topics**: {topics}")

                if insights.get('learnings'):
                    context.append(f"**Key Learnings**:")
                    for learning in insights['learnings'][:3]:
                        context.append(f"  - {learning}")

                if insights.get('action_items'):
                    context.append(f"**Action Items**:")
                    for action in insights['action_items'][:3]:
                        context.append(f"  - {action}")

            # Display learnings if this is a learning memory
            elif 'learnings' in content:
                context.append(f"**Learnings**:")
                for learning in content['learnings'][:5]:
                    context.append(f"  - {learning}")

            # Display patterns if this is a pattern memory
            elif 'code_patterns' in content:
                context.append(f"**Code Patterns**: {len(content['code_patterns'])} patterns stored")

            context.append("")

    context.append("=" * 60)
    context.append("")

    return "\n".join(context)


def get_memory_by_topic(topic: str, limit: int = 3) -> str:
    """
    Get memories related to a specific topic.

    Args:
        topic: Topic to search for
        limit: Maximum memories to return

    Returns:
        str: Formatted memory results
    """
    db = MemoryDatabase()
    memories = db.retrieve_memories(tags=[topic], limit=limit)

    if not memories:
        return f"No memories found for topic: {topic}"

    result = []
    result.append(f"## Memories for topic: {topic}")
    result.append("")

    for memory in memories:
        content = memory.get('content', {})
        if 'insights' in content:
            insights = content['insights']
            if insights.get('summary'):
                result.append(f"- {insights['summary']}")

    return "\n".join(result)


def export_memory_summary(output_file: str = None):
    """
    Export a summary of all memories to a file.

    Args:
        output_file: Path to output file (optional)
    """
    db = MemoryDatabase()

    summary = {
        "overview": db.get_memory_summary(),
        "recent_memories": db.retrieve_memories(limit=10),
        "all_tags": []
    }

    # Collect all unique tags
    tags_set = set()
    for memory in summary['recent_memories']:
        tags_set.update(memory.get('tags', []))

    summary['all_tags'] = sorted(list(tags_set))

    # Determine output location
    if not output_file:
        output_file = '.tmp/memory_summary.json'

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write summary
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✓ Memory summary exported to: {output_path}")

    return str(output_path)


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Memory Retrieval System")
        print("\nUsage:")
        print("  python memory_retrieval.py load [query]")
        print("  python memory_retrieval.py topic <topic_name>")
        print("  python memory_retrieval.py export [output_file]")
        print("  python memory_retrieval.py summary")
        sys.exit(0)

    command = sys.argv[1]

    if command == "load":
        query = sys.argv[2] if len(sys.argv) > 2 else None
        context = load_relevant_memories(query)
        print(context)

    elif command == "topic" and len(sys.argv) > 2:
        topic = sys.argv[2]
        result = get_memory_by_topic(topic)
        print(result)

    elif command == "export":
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        export_memory_summary(output_file)

    elif command == "summary":
        db = MemoryDatabase()
        summary = db.get_memory_summary()
        print(json.dumps(summary, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
