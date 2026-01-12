"""
Supabase-based persistent memory database for Claude Code.
Uses Supabase MCP server for cloud storage with fallback to local JSON.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess


class SupabaseMemoryDatabase:
    """Manages persistent memory storage using Supabase with local fallback."""

    def __init__(self, use_supabase: bool = True):
        """
        Initialize memory database.

        Args:
            use_supabase: If True, try to use Supabase. Falls back to JSON if unavailable.
        """
        self.use_supabase = use_supabase
        self.supabase_client = None
        self.supabase_available = self._check_supabase_connection()

        # Local fallback paths
        self.db_path = Path("memory_database")
        self.insights_dir = self.db_path / "insights"
        self.learnings_dir = self.db_path / "learnings"
        self.patterns_dir = self.db_path / "patterns"
        self.context_dir = self.db_path / "context_history"

        # Ensure local directories exist (for fallback)
        for directory in [self.insights_dir, self.learnings_dir,
                         self.patterns_dir, self.context_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _check_supabase_connection(self) -> bool:
        """Check if Supabase is available and configured."""
        # Load environment variables if not already loaded
        from dotenv import load_dotenv
        load_dotenv()

        # Check for environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

        if not supabase_url or not supabase_key:
            print("⚠️  Supabase credentials not found. Using local JSON storage.")
            return False

        try:
            from supabase import create_client
            self.supabase_client = create_client(supabase_url, supabase_key)

            # Test connection by checking if table exists
            self.supabase_client.table('memories').select('id', count='exact').limit(0).execute()
            print("✓ Supabase connection established. Cloud storage enabled.")
            return True
        except ImportError:
            print("⚠️  Supabase Python client not installed. Using local JSON storage.")
            return False
        except Exception as e:
            print(f"⚠️  Supabase connection failed: {e}. Using local JSON storage.")
            return False

    def _supabase_query(self, table: str, filters: Dict = None, limit: int = None) -> List[Dict]:
        """
        Query Supabase table.

        Args:
            table: Table name
            filters: Optional filters
            limit: Optional result limit

        Returns:
            List of result rows
        """
        if not self.supabase_available or not self.supabase_client:
            raise Exception("Supabase not available")

        query = self.supabase_client.table(table).select('*')

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        if limit:
            query = query.limit(limit)

        result = query.execute()
        return result.data if result.data else []

    def _supabase_insert(self, table: str, data: Dict) -> str:
        """
        Insert data into Supabase table.

        Args:
            table: Table name
            data: Data to insert

        Returns:
            ID of inserted row
        """
        if not self.supabase_available or not self.supabase_client:
            raise Exception("Supabase not available")

        self.supabase_client.table(table).insert(data).execute()
        return data.get('id', 'unknown')

    def store_memory(self, category: str, content: Dict, tags: List[str] = None) -> str:
        """
        Store a memory in the database.

        Args:
            category: One of 'insights', 'learnings', 'patterns', 'context_history'
            content: Dictionary containing the memory data
            tags: Optional list of tags for categorization

        Returns:
            str: ID of stored memory
        """
        timestamp = datetime.now().isoformat()
        memory_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        memory_data = {
            "id": memory_id,
            "created_at": timestamp,
            "category": category,
            "tags": tags or [],
            "content": content,
            "transcript_length": content.get('transcript_length', 0),
            "metadata": content.get('metadata', {})
        }

        # Try Supabase first
        if self.supabase_available:
            try:
                # Insert into Supabase
                self._supabase_insert('memories', memory_data)
                print(f"✓ Memory stored in Supabase: {memory_id}")
                return memory_id
            except Exception as e:
                print(f"⚠️  Supabase storage failed: {e}. Falling back to local JSON.")
                self.supabase_available = False

        # Fallback to local JSON
        return self._store_local(category, memory_data)

    def _store_local(self, category: str, memory_data: Dict) -> str:
        """Store memory locally as JSON file."""
        category_map = {
            "insights": self.insights_dir,
            "learnings": self.learnings_dir,
            "patterns": self.patterns_dir,
            "context_history": self.context_dir
        }

        target_dir = category_map.get(category, self.insights_dir)
        file_path = target_dir / f"{memory_data['id']}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)

        # Git commit
        self._git_commit(file_path, f"Add {category}: {memory_data['id']}")

        print(f"✓ Memory stored locally: {file_path}")
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
        # Try Supabase first
        if self.supabase_available:
            try:
                return self._retrieve_from_supabase(category, tags, limit)
            except Exception as e:
                print(f"⚠️  Supabase retrieval failed: {e}. Using local JSON.")
                self.supabase_available = False

        # Fallback to local JSON
        return self._retrieve_local(category, tags, limit)

    def _retrieve_from_supabase(self, category: Optional[str],
                                tags: Optional[List[str]],
                                limit: int) -> List[Dict]:
        """Retrieve memories from Supabase."""
        if not self.supabase_client:
            raise Exception("Supabase not available")

        query = self.supabase_client.table('memories').select('*')

        if category:
            query = query.eq('category', category)

        if tags:
            # Use PostgreSQL array overlap operator for tag filtering
            for tag in tags:
                query = query.contains('tags', [tag])

        query = query.order('created_at', desc=True).limit(limit)
        result = query.execute()

        return result.data if result.data else []

    def _retrieve_local(self, category: Optional[str],
                       tags: Optional[List[str]],
                       limit: int) -> List[Dict]:
        """Retrieve memories from local JSON files."""
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
        if self.supabase_available and self.supabase_client:
            try:
                # Use the search_memories function we created
                result = self.supabase_client.rpc('search_memories', {
                    'search_query': query,
                    'result_limit': limit
                }).execute()
                return result.data if result.data else []
            except Exception as e:
                print(f"⚠️  Supabase search failed: {e}. Using local search.")
                self.supabase_available = False

        # Fallback to local search
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

                    content_str = json.dumps(memory.get("content", {})).lower()
                    if query_lower in content_str:
                        results.append(memory)

                        if len(results) >= limit:
                            return results

                except Exception:
                    continue

        return results

    def get_memory_summary(self) -> Dict:
        """Get summary statistics of the memory database."""
        if self.supabase_available and self.supabase_client:
            try:
                # Get all memories and count them
                all_memories = self.supabase_client.table('memories').select('category, created_at').execute()

                by_category = {}
                for memory in all_memories.data:
                    cat = memory['category']
                    by_category[cat] = by_category.get(cat, 0) + 1

                return {
                    "total": len(all_memories.data),
                    "by_category": by_category,
                    "storage": "Supabase (cloud)"
                }

            except Exception as e:
                print(f"⚠️  Supabase summary failed: {e}. Using local summary.")
                self.supabase_available = False

        # Fallback to local summary
        by_category = {}
        total = 0

        for category, directory in [
            ("insights", self.insights_dir),
            ("learnings", self.learnings_dir),
            ("patterns", self.patterns_dir),
            ("context_history", self.context_dir)
        ]:
            if directory.exists():
                count = len(list(directory.glob("*.json")))
                by_category[category] = count
                total += count

        return {
            "total": total,
            "by_category": by_category,
            "storage": "Local JSON"
        }

    def _git_commit(self, file_path: Path, message: str):
        """Commit changes to git repository (local backup)."""
        try:
            subprocess.run(
                ["git", "add", str(file_path.relative_to(self.db_path))],
                cwd=self.db_path,
                check=True,
                capture_output=True
            )

            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.db_path,
                check=True,
                capture_output=True
            )

            print(f"✓ Local git backup: {message}")

        except subprocess.CalledProcessError:
            pass  # Git commit failed, but memory is still saved


# For backwards compatibility
MemoryDatabase = SupabaseMemoryDatabase


if __name__ == "__main__":
    import sys

    db = SupabaseMemoryDatabase()

    if len(sys.argv) < 2:
        print("Supabase Memory Database Manager")
        print("\nStorage:", db.supabase_available and "Supabase (cloud)" or "Local JSON (fallback)")
        print("\nUsage:")
        print("  python memory_database_supabase.py summary")
        print("  python memory_database_supabase.py search <query>")
        sys.exit(0)

    command = sys.argv[1]

    if command == "summary":
        summary = db.get_memory_summary()
        print(json.dumps(summary, indent=2))

    elif command == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        results = db.search_memories(query)
        print(json.dumps(results, indent=2))

    else:
        print("Invalid command")
        sys.exit(1)
