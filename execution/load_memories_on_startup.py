#!/usr/bin/env python3
"""
Load memories at conversation startup.
This gives Claude context from previous conversations.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_retrieval import load_relevant_memories


def main():
    """Load and display memories for Claude."""
    print("\n🧠 Loading persistent memories...\n")

    # Load recent memories
    context = load_relevant_memories(limit=5)

    print(context)

    print("\nℹ️  These memories are from your previous conversations.")
    print("   Claude can reference them to provide better context.\n")


if __name__ == "__main__":
    main()
