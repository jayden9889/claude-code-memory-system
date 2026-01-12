"""
Memory storage background subagent.
Reads conversation transcript, distills insights, and stores in memory database.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_database import MemoryDatabase


def read_conversation_transcript(transcript_path: str = None) -> str:
    """
    Read the current conversation transcript.

    Args:
        transcript_path: Path to transcript file (optional)

    Returns:
        str: Full conversation transcript
    """
    # Try to find transcript in common locations
    possible_paths = [
        transcript_path,
        ".claude/conversation.txt",
        ".claude/transcript.txt",
        ".tmp/current_conversation.txt"
    ]

    for path in possible_paths:
        if path and Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

    # If no transcript file found, return empty
    return ""


def distill_insights(transcript: str) -> dict:
    """
    Distill key insights from conversation transcript.

    This is a simple extraction - in production, this would use
    Claude API or another LLM to intelligently extract insights.

    Args:
        transcript: Full conversation text

    Returns:
        dict: Extracted insights
    """
    # Simple keyword-based extraction for now
    insights = {
        "summary": extract_summary(transcript),
        "key_topics": extract_topics(transcript),
        "action_items": extract_action_items(transcript),
        "learnings": extract_learnings(transcript),
        "code_snippets": extract_code_snippets(transcript),
        "decisions_made": extract_decisions(transcript)
    }

    return insights


def extract_summary(transcript: str) -> str:
    """Extract a brief summary from transcript."""
    lines = [l.strip() for l in transcript.split('\n') if l.strip()]

    if not lines:
        return "Empty conversation"

    # Take first few meaningful lines as summary
    summary_lines = []
    for line in lines[:10]:
        if len(line) > 20 and not line.startswith('#'):
            summary_lines.append(line)
            if len(summary_lines) >= 3:
                break

    return ' '.join(summary_lines[:3]) if summary_lines else "Brief conversation"


def extract_topics(transcript: str) -> list:
    """Extract key topics discussed."""
    topics = set()

    # Simple keyword extraction
    keywords = ['api', 'database', 'function', 'class', 'error', 'bug',
                'feature', 'implementation', 'test', 'memory', 'hook',
                'agent', 'directive', 'execution', 'mcp', 'claude']

    transcript_lower = transcript.lower()
    for keyword in keywords:
        if keyword in transcript_lower:
            topics.add(keyword)

    return list(topics)[:10]


def extract_action_items(transcript: str) -> list:
    """Extract action items from conversation."""
    actions = []

    # Look for TODO patterns
    for line in transcript.split('\n'):
        line_lower = line.lower()
        if any(marker in line_lower for marker in ['todo', '[ ]', 'need to', 'should', 'must']):
            actions.append(line.strip())

    return actions[:10]


def extract_learnings(transcript: str) -> list:
    """Extract key learnings from conversation."""
    learnings = []

    # Look for learning indicators
    learning_markers = ['learned', 'discovered', 'found that', 'realized',
                       'insight:', 'important:', 'note:']

    for line in transcript.split('\n'):
        line_lower = line.lower()
        if any(marker in line_lower for marker in learning_markers):
            learnings.append(line.strip())

    return learnings[:10]


def extract_code_snippets(transcript: str) -> list:
    """Extract code snippets from conversation."""
    snippets = []

    # Look for code blocks
    lines = transcript.split('\n')
    in_code_block = False
    current_snippet = []

    for line in lines:
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                if current_snippet:
                    snippets.append('\n'.join(current_snippet))
                current_snippet = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
        elif in_code_block:
            current_snippet.append(line)

    return snippets[:5]  # Limit to 5 snippets


def extract_decisions(transcript: str) -> list:
    """Extract decisions made during conversation."""
    decisions = []

    decision_markers = ['decided to', 'chosen', 'selected', 'going with',
                       'will use', 'opted for']

    for line in transcript.split('\n'):
        line_lower = line.lower()
        if any(marker in line_lower for marker in decision_markers):
            decisions.append(line.strip())

    return decisions[:10]


def store_conversation_memory(transcript: str, metadata: dict = None):
    """
    Main function: Distill and store conversation memory.

    Args:
        transcript: Full conversation transcript
        metadata: Optional metadata about the conversation
    """
    print("🧠 Memory Storage Agent Started")
    print("=" * 60)

    # Initialize database
    db = MemoryDatabase()

    # Distill insights
    print("\n📊 Distilling insights from conversation...")
    insights = distill_insights(transcript)

    print(f"   - Summary: {insights['summary'][:100]}...")
    print(f"   - Topics: {len(insights['key_topics'])} identified")
    print(f"   - Action items: {len(insights['action_items'])} found")
    print(f"   - Learnings: {len(insights['learnings'])} extracted")
    print(f"   - Code snippets: {len(insights['code_snippets'])} captured")
    print(f"   - Decisions: {len(insights['decisions_made'])} recorded")

    # Prepare memory content
    memory_content = {
        "transcript_length": len(transcript),
        "insights": insights,
        "metadata": metadata or {},
        "stored_at": datetime.now().isoformat()
    }

    # Store in database
    print("\n💾 Storing in memory database...")

    tags = insights['key_topics']
    if metadata:
        tags.extend(metadata.get('tags', []))

    path = db.store_memory(
        category="context_history",
        content=memory_content,
        tags=list(set(tags))  # Remove duplicates
    )

    print(f"✓ Memory stored: {path}")

    # Store key learnings separately
    if insights['learnings']:
        learning_content = {
            "learnings": insights['learnings'],
            "context": insights['summary']
        }
        db.store_memory(
            category="learnings",
            content=learning_content,
            tags=tags
        )
        print(f"✓ Learnings stored separately")

    # Store patterns if code snippets found
    if insights['code_snippets']:
        pattern_content = {
            "code_patterns": insights['code_snippets'],
            "context": insights['summary']
        }
        db.store_memory(
            category="patterns",
            content=pattern_content,
            tags=tags
        )
        print(f"✓ Code patterns stored")

    print("\n" + "=" * 60)
    print("🎉 Memory storage complete!")
    print("\nDatabase summary:")
    summary = db.get_memory_summary()
    print(json.dumps(summary, indent=2))


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python memory_storage_agent.py <transcript_file>")
        print("   Or: python memory_storage_agent.py <transcript_file> <metadata_json>")
        sys.exit(1)

    transcript_file = sys.argv[1]

    # Read transcript
    print(f"📖 Reading transcript from: {transcript_file}")
    transcript = read_conversation_transcript(transcript_file)

    if not transcript:
        print("❌ Error: Could not read transcript")
        sys.exit(1)

    print(f"✓ Transcript loaded ({len(transcript)} characters)")

    # Read metadata if provided
    metadata = None
    if len(sys.argv) > 2:
        try:
            metadata = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print("Warning: Could not parse metadata JSON")

    # Process and store
    store_conversation_memory(transcript, metadata)


if __name__ == "__main__":
    main()
