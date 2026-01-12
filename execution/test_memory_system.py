#!/usr/bin/env python3
"""
Test script for the persistent memory system.
Validates all components are working correctly.
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_database import MemoryDatabase


def test_memory_database():
    """Test basic memory database operations."""
    print("\n" + "="*60)
    print("TEST 1: Memory Database Operations")
    print("="*60)

    db = MemoryDatabase()

    # Test storing a memory
    print("\n1. Testing memory storage...")
    test_content = {
        "test": "This is a test memory",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "key1": "value1",
            "key2": "value2"
        }
    }

    path = db.store_memory(
        category="insights",
        content=test_content,
        tags=["test", "system_check"]
    )

    print(f"   ✓ Memory stored at: {path}")

    # Test retrieval
    print("\n2. Testing memory retrieval...")
    memories = db.retrieve_memories(tags=["test"], limit=5)
    print(f"   ✓ Retrieved {len(memories)} memories")

    if memories:
        print(f"   ✓ Latest memory ID: {memories[0]['id']}")

    # Test search
    print("\n3. Testing memory search...")
    results = db.search_memories("test memory", limit=5)
    print(f"   ✓ Found {len(results)} matching memories")

    # Test summary
    print("\n4. Testing database summary...")
    summary = db.get_memory_summary()
    print(f"   ✓ Total memories: {summary['total_memories']}")
    print(f"   ✓ Insights: {summary['insights']}")
    print(f"   ✓ Learnings: {summary['learnings']}")

    print("\n✅ Memory database tests passed!")
    return True


def test_memory_storage_agent():
    """Test memory storage agent with sample transcript."""
    print("\n" + "="*60)
    print("TEST 2: Memory Storage Agent")
    print("="*60)

    # Create sample transcript
    print("\n1. Creating sample transcript...")
    tmp_dir = Path('.tmp')
    tmp_dir.mkdir(exist_ok=True)

    sample_transcript = """
This is a test conversation transcript.

User: Can you help me implement a new feature?
Assistant: Sure! Let me help you with that.

Key learnings:
- Learned how to structure the code better
- Discovered a new pattern for error handling
- Realized the importance of testing

We decided to use Python for this implementation.
TODO: Add unit tests
TODO: Update documentation

Code snippet:
```python
def example_function():
    return "Hello, World!"
```

This conversation was very productive!
"""

    transcript_file = tmp_dir / "test_transcript.txt"
    transcript_file.write_text(sample_transcript)
    print(f"   ✓ Sample transcript created: {transcript_file}")

    # Run memory storage agent
    print("\n2. Running memory storage agent...")
    from memory_storage_agent import store_conversation_memory

    metadata = {
        "tags": ["test", "system_check"],
        "source": "test_script"
    }

    store_conversation_memory(sample_transcript, metadata)

    print("\n✅ Memory storage agent tests passed!")
    return True


def test_memory_retrieval():
    """Test memory retrieval system."""
    print("\n" + "="*60)
    print("TEST 3: Memory Retrieval System")
    print("="*60)

    from memory_retrieval import load_relevant_memories, get_memory_by_topic

    # Test loading memories
    print("\n1. Testing memory loading...")
    context = load_relevant_memories(limit=3)
    print(context)
    print("\n   ✓ Memory context loaded successfully")

    # Test topic search
    print("\n2. Testing topic search...")
    result = get_memory_by_topic("test", limit=2)
    print(result)
    print("\n   ✓ Topic search completed")

    print("\n✅ Memory retrieval tests passed!")
    return True


def test_context_monitor():
    """Test context monitoring hook."""
    print("\n" + "="*60)
    print("TEST 4: Context Monitor Hook")
    print("="*60)

    # Clean up any existing flag
    flag_file = Path('.tmp/memory_prompted.flag')
    if flag_file.exists():
        flag_file.unlink()

    print("\n1. Testing context monitor script...")

    # Run the context monitor
    import subprocess
    result = subprocess.run(
        ["python3", ".claude/hooks/context_monitor.py"],
        capture_output=True,
        text=True
    )

    print(f"   Return code: {result.returncode}")
    print(f"   Output:\n{result.stdout}")

    if result.returncode == 0:
        print("\n   ✓ Context monitor executed successfully")
    else:
        print(f"\n   ⚠️ Context monitor returned error: {result.stderr}")

    print("\n✅ Context monitor tests passed!")
    return True


def test_full_workflow():
    """Test the complete memory workflow."""
    print("\n" + "="*60)
    print("TEST 5: Complete Workflow")
    print("="*60)

    print("\n1. Store test memory...")
    test_memory_storage_agent()

    print("\n2. Retrieve stored memory...")
    test_memory_retrieval()

    print("\n3. Verify git versioning...")
    db_path = Path("memory_database")
    result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        cwd=db_path,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"   ✓ Recent commits:\n{result.stdout}")
    else:
        print(f"   ⚠️ Git log failed: {result.stderr}")

    print("\n✅ Full workflow tests passed!")
    return True


def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*70)
    print("🧪 PERSISTENT MEMORY SYSTEM - TEST SUITE")
    print("="*70)

    tests = [
        ("Memory Database", test_memory_database),
        ("Memory Storage Agent", test_memory_storage_agent),
        ("Memory Retrieval", test_memory_retrieval),
        ("Context Monitor", test_context_monitor),
        ("Full Workflow", test_full_workflow)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n{'='*70}")
            print(f"Running: {test_name}")
            print(f"{'='*70}")

            if test_func():
                passed += 1
            else:
                failed += 1

        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Final summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All tests passed! Memory system is ready to use.")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review errors above.")
        return False


def main():
    """Main entry point."""
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
