"""
Persistent memory database manager for Claude Code.
Stores and retrieves conversation insights with git versioning.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Dict, List, Optional


class MemoryDatabase:
    """Manages persistent memory storage with git versioning."""

    def __init__(self, db_path: str = "memory_database"):
        self.db_path = Path(db_path)
        self.insights_dir = self.db_path / "insights"
        self.learnings_dir = self.db_path / "learnings"
        self.patterns_dir = self.db_path / "patterns"
        self.context_dir = self.db_path / "context_history"

        # Ensure directories exist
        for directory in [self.insights_dir, self.learnings_dir,
                         self.patterns_dir, self.context_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def store_memory(self, category: str, content: Dict, tags: List[str] = None) -> str:
        """
        Store a memory in the database.

        Args:
            category: One of 'insights', 'learnings', 'patterns', 'context_history'
            content: Dictionary containing the memory data
            tags: Optional list of tags for categorization

        Returns:
            str: Path to stored memory file
        """
        timestamp = datetime.now().isoformat()
        memory_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        memory_data = {
            "id": memory_id,
            "timestamp": timestamp,
            "tags": tags or [],
            "content": content
        }

        # Determine target directory
        category_map = {
            "insights": self.insights_dir,
            "learnings": self.learnings_dir,
            "patterns": self.patterns_dir,
            "context_history": self.context_dir
        }

        target_dir = category_map.get(category, self.insights_dir)
        file_path = target_dir / f"{memory_id}.json"

        # Write memory file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)

        # Git commit
        self._git_commit(file_path, f"Add {category}: {memory_id}")

        return str(file_path)

    def retrieve_memories(self, category: Optional[str] = None,
                         tags: Optional[List[str]] = None,
                         limit: int = 10) -> List[Dict]:
        """
        Retrieve memories from database.

        Args:
            category: Filter by category (optional)
            tags: Filter by tags (optional)
            limit: Maximum number of memories to return

        Returns:
            List of memory dictionaries
        """
        memories = []

        # Determine which directories to search
        if category:
            dirs_to_search = [self.db_path / category]
        else:
            dirs_to_search = [self.insights_dir, self.learnings_dir,
                            self.patterns_dir, self.context_dir]

        # Read all memory files
        for directory in dirs_to_search:
            if not directory.exists():
                continue

            for file_path in sorted(directory.glob("*.json"), reverse=True):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory = json.load(f)

                    # Filter by tags if specified
                    if tags:
                        if not any(tag in memory.get("tags", []) for tag in tags):
                            continue

                    memories.append(memory)

                    if len(memories) >= limit:
                        return memories

                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
                    continue

        return memories

    def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search memories by text content.

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching memories
        """
        results = []
        query_lower = query.lower()

        for directory in [self.insights_dir, self.learnings_dir,
                         self.patterns_dir, self.context_dir]:
            if not directory.exists():
                continue

            for file_path in directory.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory = json.load(f)

                    # Search in content
                    content_str = json.dumps(memory.get("content", {})).lower()
                    if query_lower in content_str:
                        results.append(memory)

                        if len(results) >= limit:
                            return results

                except Exception:
                    continue

        return results

    def get_memory_summary(self) -> Dict:
        """
        Get summary statistics of the memory database.

        Returns:
            Dictionary with counts and recent activity
        """
        summary = {
            "total_memories": 0,
            "insights": 0,
            "learnings": 0,
            "patterns": 0,
            "context_history": 0,
            "last_updated": None
        }

        for category, directory in [
            ("insights", self.insights_dir),
            ("learnings", self.learnings_dir),
            ("patterns", self.patterns_dir),
            ("context_history", self.context_dir)
        ]:
            if directory.exists():
                count = len(list(directory.glob("*.json")))
                summary[category] = count
                summary["total_memories"] += count

        # Get last commit date
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                cwd=self.db_path,
                capture_output=True,
                text=True,
                check=True
            )
            summary["last_updated"] = result.stdout.strip()
        except Exception:
            pass

        return summary

    def _git_commit(self, file_path: Path, message: str):
        """Commit changes to git repository."""
        try:
            # Add file
            subprocess.run(
                ["git", "add", str(file_path.relative_to(self.db_path))],
                cwd=self.db_path,
                check=True,
                capture_output=True
            )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.db_path,
                check=True,
                capture_output=True
            )

            print(f"✓ Memory committed to git: {message}")

        except subprocess.CalledProcessError as e:
            print(f"Warning: Git commit failed: {e}")
            # Don't raise - memory is still saved even if git fails


# CLI interface for testing
if __name__ == "__main__":
    import sys

    db = MemoryDatabase()

    if len(sys.argv) < 2:
        print("Memory Database Manager")
        print("\nUsage:")
        print("  python memory_database.py summary")
        print("  python memory_database.py search <query>")
        print("  python memory_database.py store <category> <json_content>")
        sys.exit(0)

    command = sys.argv[1]

    if command == "summary":
        summary = db.get_memory_summary()
        print(json.dumps(summary, indent=2))

    elif command == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        results = db.search_memories(query)
        print(json.dumps(results, indent=2))

    elif command == "store" and len(sys.argv) > 3:
        category = sys.argv[2]
        content = json.loads(sys.argv[3])
        path = db.store_memory(category, content)
        print(f"Stored at: {path}")

    else:
        print("Invalid command")
        sys.exit(1)
