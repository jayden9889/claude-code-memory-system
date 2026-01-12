#!/usr/bin/env python3
"""
Trigger memory storage workflow.
Called when user confirms they want to save memories.
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime


def save_current_transcript():
    """
    Save current conversation transcript for processing.

    Returns:
        str: Path to saved transcript
    """
    # Create .tmp directory
    tmp_dir = Path('.tmp')
    tmp_dir.mkdir(exist_ok=True)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    transcript_path = tmp_dir / f"conversation_{timestamp}.txt"

    # Try to get transcript from Claude Code's internal storage
    possible_sources = [
        '.claude/conversation.txt',
        '.claude/current_session.txt',
    ]

    transcript_content = ""

    for source in possible_sources:
        source_path = Path(source)
        if source_path.exists():
            transcript_content = source_path.read_text()
            break

    # If no transcript found, create one from environment or stdin
    if not transcript_content:
        # Try to read from stdin if available
        if not sys.stdin.isatty():
            transcript_content = sys.stdin.read()
        else:
            # Last resort: indicate transcript unavailable
            transcript_content = f"Transcript saved at {datetime.now().isoformat()}\n"
            transcript_content += "Note: Full transcript not available, using environment data.\n"

    # Save transcript
    transcript_path.write_text(transcript_content)

    print(f"📝 Transcript saved: {transcript_path}")
    return str(transcript_path)


def launch_memory_agent(transcript_path: str):
    """
    Launch the memory storage agent in the background.

    Args:
        transcript_path: Path to conversation transcript
    """
    print("🚀 Launching memory storage agent...")

    # Prepare metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "source": "claude_code_hook",
        "tags": ["auto_saved", "context_threshold"]
    }

    # Build command
    script_path = Path(__file__).parent / "memory_storage_agent.py"
    cmd = [
        sys.executable,
        str(script_path),
        transcript_path,
        f'{metadata}'  # Will be parsed as JSON
    ]

    # Run in background
    # On Unix-like systems, use subprocess with background process
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True  # Detach from parent
        )

        print(f"✓ Memory agent launched (PID: {process.pid})")
        print(f"  Agent will process transcript in background")
        print(f"  Check memory_database/ for stored memories")

        return process.pid

    except Exception as e:
        print(f"❌ Error launching memory agent: {e}")
        # Fallback: run synchronously
        print("  Running synchronously instead...")
        subprocess.run(cmd)
        return None


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("💾 MEMORY STORAGE TRIGGER")
    print("="*60 + "\n")

    # Step 1: Save transcript
    transcript_path = save_current_transcript()

    # Step 2: Launch memory agent
    pid = launch_memory_agent(transcript_path)

    # Clear the flag so next conversation can trigger again
    flag_file = Path('.tmp/memory_prompted.flag')
    if flag_file.exists():
        flag_file.unlink()
        print("\n✓ Memory prompt flag cleared for next conversation")

    print("\n" + "="*60)
    print("✅ Memory storage workflow initiated!")
    print("="*60 + "\n")

    if pid:
        print(f"Background process running with PID: {pid}")
    print("You can continue your conversation normally.\n")


if __name__ == "__main__":
    main()
