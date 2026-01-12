#!/usr/bin/env python3
"""
Context monitoring hook for Claude Code.
Triggers at 80% context usage to prompt memory storage.

This hook is called by Claude Code to monitor conversation context.
"""

import sys
import os
import json
from pathlib import Path


def get_context_usage():
    """
    Calculate current context usage percentage.

    Returns:
        float: Context usage percentage (0-100)
    """
    # Try to read from environment variables passed by Claude Code
    current_tokens = int(os.getenv('CLAUDE_CURRENT_TOKENS', '0'))
    max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', '200000'))

    if current_tokens > 0:
        usage_pct = (current_tokens / max_tokens) * 100
        return usage_pct

    # Fallback: Try to estimate from conversation file
    conversation_file = Path('.claude/conversation.txt')
    if conversation_file.exists():
        content = conversation_file.read_text()
        # Rough estimate: 4 chars per token
        estimated_tokens = len(content) / 4
        usage_pct = (estimated_tokens / max_tokens) * 100
        return usage_pct

    return 0.0


def should_trigger_memory_prompt(usage_pct: float, threshold: float = 80.0) -> bool:
    """
    Determine if we should trigger memory storage prompt.

    Args:
        usage_pct: Current context usage percentage
        threshold: Threshold percentage to trigger (default 80%)

    Returns:
        bool: True if should trigger
    """
    # Check if we've already triggered in this conversation
    flag_file = Path('.tmp/memory_prompted.flag')

    if flag_file.exists():
        # Already prompted in this conversation
        return False

    if usage_pct >= threshold:
        # Create flag file to prevent multiple prompts
        flag_file.parent.mkdir(exist_ok=True)
        flag_file.touch()
        return True

    return False


def create_memory_prompt() -> dict:
    """
    Create the prompt data for Claude Code to ask user about memory storage.

    Returns:
        dict: Prompt configuration for AskUserQuestion
    """
    return {
        "action": "ask_user_question",
        "question": "Would you like to save memories from this conversation?",
        "options": [
            {
                "label": "Yes, save memories",
                "value": "yes",
                "action": "trigger_memory_agent"
            },
            {
                "label": "No, continue without saving",
                "value": "no",
                "action": "continue"
            }
        ],
        "context": {
            "reason": "Context is reaching 80% capacity",
            "recommendation": "Saving memories will preserve insights and learnings"
        }
    }


def main():
    """Main hook execution."""
    # Get current context usage
    usage_pct = get_context_usage()

    # Check if we should trigger
    if should_trigger_memory_prompt(usage_pct):
        # Output prompt configuration for Claude Code
        prompt = create_memory_prompt()

        print(f"CONTEXT_USAGE: {usage_pct:.1f}%")
        print(f"TRIGGER_MEMORY_PROMPT")
        print(json.dumps(prompt, indent=2))

        sys.exit(0)  # Success - prompt should be triggered

    else:
        # No action needed
        print(f"CONTEXT_USAGE: {usage_pct:.1f}%")
        print(f"NO_ACTION_NEEDED")
        sys.exit(0)


if __name__ == "__main__":
    main()
