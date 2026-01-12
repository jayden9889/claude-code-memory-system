#!/usr/bin/env python3
"""
Migrate existing JSON memories to Supabase.
Run this after setting up Supabase to import all local memories.
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_database_supabase import SupabaseMemoryDatabase


def migrate_memories():
    """Migrate all local JSON memories to Supabase."""
    print("\n" + "="*60)
    print("MIGRATING LOCAL MEMORIES TO SUPABASE")
    print("="*60 + "\n")

    db = SupabaseMemoryDatabase()

    if not db.supabase_available:
        print("❌ Supabase is not available!")
        print("   Please add credentials to .env file:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_KEY")
        sys.exit(1)

    # Count existing memories
    local_dir = Path("memory_database")
    categories = ["insights", "learnings", "patterns", "context_history"]

    total_count = 0
    migrated_count = 0
    failed_count = 0

    for category in categories:
        category_dir = local_dir / category
        if not category_dir.exists():
            continue

        json_files = list(category_dir.glob("*.json"))
        total_count += len(json_files)

        print(f"\n📁 Migrating {category} ({len(json_files)} files)...")

        for json_file in json_files:
            try:
                # Read local JSON
                with open(json_file, 'r', encoding='utf-8') as f:
                    memory = json.load(f)

                # Extract components
                memory_id = memory.get('id')
                tags = memory.get('tags', [])
                content = memory.get('content', {})

                # Store in Supabase
                db.store_memory(category, content, tags)

                migrated_count += 1
                print(f"   ✓ Migrated: {memory_id}")

            except Exception as e:
                failed_count += 1
                print(f"   ❌ Failed to migrate {json_file.name}: {e}")

    # Print summary
    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print(f"\n Total memories found: {total_count}")
    print(f"✓ Successfully migrated: {migrated_count}")
    print(f"❌ Failed: {failed_count}")

    # Show Supabase summary
    print("\n📊 Supabase Database Summary:")
    summary = db.get_memory_summary()
    print(json.dumps(summary, indent=2))

    print("\n✅ Migration complete! Your memories are now in the cloud.")
    print("   You can access them from any machine with Supabase credentials.\n")


if __name__ == "__main__":
    migrate_memories()
