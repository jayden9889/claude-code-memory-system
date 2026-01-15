#!/usr/bin/env python3
"""
Vinuchi Blog Writer - Persistent Memory System
Stores ALL learnings, preferences, and generated content FOREVER.

This is the brain of the system. Nothing is ever forgotten.
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
MEMORY_DIR = BASE_DIR / ".tmp" / "vinuchi" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# Memory files (persistent JSON - will migrate to Supabase when ready)
PREFERENCES_FILE = MEMORY_DIR / "preferences.json"
GENERATED_BLOGS_FILE = MEMORY_DIR / "generated_blogs.json"
LEARNING_LOG_FILE = MEMORY_DIR / "learning_log.json"
CONTENT_HASHES_FILE = MEMORY_DIR / "content_hashes.json"


class PersistentMemory:
    """
    Persistent memory system for the Vinuchi Blog Writer.

    Stores:
    - User preferences (banned words, required elements, style notes)
    - All generated blogs (for duplicate detection)
    - Learning log (every piece of feedback)
    - Content hashes (quick duplicate check)
    """

    def __init__(self):
        """Initialize memory system, loading all stored data."""
        self.preferences = self._load_json(PREFERENCES_FILE, default={
            "banned_words": [],
            "required_elements": [],
            "style_notes": [],
            "keywords_to_include": [],
            "topics_to_avoid": [],
            "formatting_rules": [],
            "custom_rules": []
        })

        self.generated_blogs = self._load_json(GENERATED_BLOGS_FILE, default=[])
        self.learning_log = self._load_json(LEARNING_LOG_FILE, default=[])
        self.content_hashes = self._load_json(CONTENT_HASHES_FILE, default=[])

    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON file or return default if not exists."""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return default
        return default

    def _save_json(self, filepath: Path, data: Any) -> None:
        """Save data to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_all(self) -> None:
        """Save all memory to disk."""
        self._save_json(PREFERENCES_FILE, self.preferences)
        self._save_json(GENERATED_BLOGS_FILE, self.generated_blogs)
        self._save_json(LEARNING_LOG_FILE, self.learning_log)
        self._save_json(CONTENT_HASHES_FILE, self.content_hashes)

    # ==================== PREFERENCES ====================

    def add_banned_word(self, word: str, reason: str = "") -> None:
        """
        Add a word that should NEVER be used.
        This will be remembered FOREVER.
        """
        word_lower = word.lower().strip()

        # Check if already exists
        existing = [w for w in self.preferences["banned_words"] if w["word"] == word_lower]
        if existing:
            return  # Already banned

        self.preferences["banned_words"].append({
            "word": word_lower,
            "reason": reason,
            "added_at": datetime.now().isoformat(),
            "active": True
        })

        self._log_learning("banned_word_added", f"Never use: '{word}' - {reason}")
        self._save_all()

    def remove_banned_word(self, word: str) -> None:
        """Remove a banned word (set to inactive, not deleted - we keep history)."""
        word_lower = word.lower().strip()
        for item in self.preferences["banned_words"]:
            if item["word"] == word_lower:
                item["active"] = False
                item["removed_at"] = datetime.now().isoformat()

        self._log_learning("banned_word_removed", f"Unbanned: '{word}'")
        self._save_all()

    def get_banned_words(self) -> List[str]:
        """Get all active banned words."""
        return [w["word"] for w in self.preferences["banned_words"] if w.get("active", True)]

    def add_required_element(self, element: str, reason: str = "") -> None:
        """Add something that MUST be included in every blog."""
        self.preferences["required_elements"].append({
            "element": element,
            "reason": reason,
            "added_at": datetime.now().isoformat(),
            "active": True
        })

        self._log_learning("required_element_added", f"Always include: '{element}'")
        self._save_all()

    def get_required_elements(self) -> List[str]:
        """Get all active required elements."""
        return [e["element"] for e in self.preferences["required_elements"] if e.get("active", True)]

    def remove_required_element(self, element: str) -> None:
        """Remove a required element (set to inactive)."""
        element_lower = element.lower().strip()
        for item in self.preferences["required_elements"]:
            if item["element"].lower().strip() == element_lower:
                item["active"] = False
                item["removed_at"] = datetime.now().isoformat()

        self._log_learning("required_element_removed", f"Removed requirement: '{element}'")
        self._save_all()

    def add_style_note(self, note: str) -> None:
        """Add a style note/preference."""
        self.preferences["style_notes"].append({
            "note": note,
            "added_at": datetime.now().isoformat(),
            "active": True
        })

        self._log_learning("style_note_added", f"Style preference: '{note}'")
        self._save_all()

    def get_style_notes(self) -> List[str]:
        """Get all active style notes."""
        return [n["note"] for n in self.preferences["style_notes"] if n.get("active", True)]

    def remove_style_note(self, note: str) -> None:
        """Remove a style note (set to inactive)."""
        note_lower = note.lower().strip()
        for item in self.preferences["style_notes"]:
            if item["note"].lower().strip() == note_lower:
                item["active"] = False
                item["removed_at"] = datetime.now().isoformat()

        self._log_learning("style_note_removed", f"Removed style note: '{note}'")
        self._save_all()

    def add_formatting_rule(self, rule: str) -> None:
        """Add a formatting rule (e.g., 'never use dashes')."""
        self.preferences["formatting_rules"].append({
            "rule": rule,
            "added_at": datetime.now().isoformat(),
            "active": True
        })

        self._log_learning("formatting_rule_added", f"Formatting rule: '{rule}'")
        self._save_all()

    def get_formatting_rules(self) -> List[str]:
        """Get all active formatting rules."""
        return [r["rule"] for r in self.preferences["formatting_rules"] if r.get("active", True)]

    def remove_formatting_rule(self, rule: str) -> None:
        """Remove a formatting rule (set to inactive)."""
        rule_lower = rule.lower().strip()
        for item in self.preferences["formatting_rules"]:
            if item["rule"].lower().strip() == rule_lower:
                item["active"] = False
                item["removed_at"] = datetime.now().isoformat()

        self._log_learning("formatting_rule_removed", f"Removed formatting rule: '{rule}'")
        self._save_all()

    def add_custom_rule(self, rule_type: str, rule_value: str, reason: str = "") -> None:
        """Add any custom rule."""
        self.preferences["custom_rules"].append({
            "type": rule_type,
            "value": rule_value,
            "reason": reason,
            "added_at": datetime.now().isoformat(),
            "active": True
        })

        self._log_learning("custom_rule_added", f"{rule_type}: '{rule_value}'")
        self._save_all()

    # ==================== SEO KEYWORDS ====================

    def add_seo_keyword(self, keyword: str, context: str = "") -> None:
        """
        Add an SEO keyword that should be used in future blogs.

        These keywords are the MOST IMPORTANT part of the blog writer.
        They will be integrated naturally when relevant to the topic.

        Args:
            keyword: The SEO keyword/phrase to use (e.g., "custom corporate ties")
            context: Optional context for when/how to use this keyword
        """
        keyword_clean = keyword.strip()

        # Check if already exists
        existing = [k for k in self.preferences.get("seo_keywords", [])
                   if k.get("keyword", "").lower() == keyword_clean.lower() and k.get("active", True)]
        if existing:
            return  # Already added

        # Initialize seo_keywords list if not exists
        if "seo_keywords" not in self.preferences:
            self.preferences["seo_keywords"] = []

        self.preferences["seo_keywords"].append({
            "keyword": keyword_clean,
            "context": context,
            "added_at": datetime.now().isoformat(),
            "active": True,
            "times_used": 0
        })

        self._log_learning("seo_keyword_added", f"New SEO keyword: '{keyword_clean}' - {context}")
        self._save_all()

    def remove_seo_keyword(self, keyword: str) -> None:
        """Remove an SEO keyword (set to inactive)."""
        keyword_lower = keyword.lower().strip()

        if "seo_keywords" not in self.preferences:
            return

        for item in self.preferences["seo_keywords"]:
            if item.get("keyword", "").lower() == keyword_lower:
                item["active"] = False
                item["removed_at"] = datetime.now().isoformat()

        self._log_learning("seo_keyword_removed", f"Removed SEO keyword: '{keyword}'")
        self._save_all()

    def get_seo_keywords(self) -> List[Dict]:
        """
        Get all active SEO keywords with their context.
        Returns list of dicts with 'keyword' and 'context' keys.
        """
        if "seo_keywords" not in self.preferences:
            return []

        return [
            {"keyword": k["keyword"], "context": k.get("context", "")}
            for k in self.preferences["seo_keywords"]
            if k.get("active", True)
        ]

    def get_seo_keyword_list(self) -> List[str]:
        """Get just the keyword strings (for simple display)."""
        return [k["keyword"] for k in self.get_seo_keywords()]

    def increment_seo_keyword_usage(self, keyword: str) -> None:
        """Track when an SEO keyword is used in a blog."""
        keyword_lower = keyword.lower().strip()

        if "seo_keywords" not in self.preferences:
            return

        for item in self.preferences["seo_keywords"]:
            if item.get("keyword", "").lower() == keyword_lower and item.get("active", True):
                item["times_used"] = item.get("times_used", 0) + 1
                item["last_used"] = datetime.now().isoformat()

        self._save_all()

    def get_all_preferences(self) -> Dict:
        """Get all preferences organized for the generator."""
        return {
            "banned_words": self.get_banned_words(),
            "required_elements": self.get_required_elements(),
            "style_notes": self.get_style_notes(),
            "formatting_rules": self.get_formatting_rules(),
            "custom_rules": [r for r in self.preferences["custom_rules"] if r.get("active", True)],
            "seo_keywords": self.get_seo_keywords()
        }

    # ==================== GENERATED BLOGS ====================

    def _hash_content(self, content: str) -> str:
        """Generate hash of content for duplicate detection."""
        # Normalize content
        normalized = content.lower().strip()
        normalized = ' '.join(normalized.split())  # Normalize whitespace
        return hashlib.md5(normalized.encode()).hexdigest()

    def save_generated_blog(self, title: str, content: str, topic: str, status: str = "draft") -> str:
        """
        Save a generated blog to memory.
        Returns the blog ID.
        """
        blog_id = f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.generated_blogs)}"
        content_hash = self._hash_content(content)

        blog_entry = {
            "id": blog_id,
            "title": title,
            "content": content,
            "topic_requested": topic,
            "content_hash": content_hash,
            "word_count": len(content.split()),
            "status": status,  # draft, approved, posted
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        self.generated_blogs.append(blog_entry)
        self.content_hashes.append({
            "hash": content_hash,
            "blog_id": blog_id,
            "title": title
        })

        self._log_learning("blog_generated", f"Created: '{title}'")
        self._save_all()

        return blog_id

    def update_blog_status(self, blog_id: str, status: str) -> None:
        """Update the status of a generated blog."""
        for blog in self.generated_blogs:
            if blog["id"] == blog_id:
                blog["status"] = status
                blog["updated_at"] = datetime.now().isoformat()
                break

        self._log_learning("blog_status_updated", f"{blog_id} -> {status}")
        self._save_all()

    def update_blog_content(self, blog_id: str, title: str, content: str) -> None:
        """Update the title and content of a generated blog."""
        for blog in self.generated_blogs:
            if blog["id"] == blog_id:
                blog["title"] = title
                blog["content"] = content
                blog["word_count"] = len(content.split())
                blog["updated_at"] = datetime.now().isoformat()
                break

        self._log_learning("blog_content_updated", f"{blog_id} edited")
        self._save_all()

    def is_duplicate(self, content: str, threshold: float = 0.9) -> Optional[Dict]:
        """
        Check if content is too similar to existing blogs.
        Returns the similar blog if found, None otherwise.
        """
        new_hash = self._hash_content(content)

        # Exact duplicate check
        for entry in self.content_hashes:
            if entry["hash"] == new_hash:
                return {"type": "exact", "blog_id": entry["blog_id"], "title": entry["title"]}

        # Fuzzy duplicate check (simple word overlap)
        new_words = set(content.lower().split())

        for blog in self.generated_blogs:
            existing_words = set(blog["content"].lower().split())
            overlap = len(new_words & existing_words) / max(len(new_words), len(existing_words))

            if overlap > threshold:
                return {"type": "similar", "blog_id": blog["id"], "title": blog["title"], "overlap": overlap}

        return None

    def get_all_blog_titles(self) -> List[str]:
        """Get all generated blog titles (for duplicate topic checking)."""
        return [blog["title"] for blog in self.generated_blogs]

    def get_all_blog_topics(self) -> List[str]:
        """Get all topics that have been written about."""
        return [blog["topic_requested"] for blog in self.generated_blogs]

    def get_generated_blogs_count(self) -> int:
        """Get count of all generated blogs."""
        return len(self.generated_blogs)

    def get_approved_blogs(self) -> List[Dict]:
        """Get all approved blogs, sorted by most recent first."""
        approved = [b for b in self.generated_blogs if b.get("status") == "approved"]
        return sorted(approved, key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_blog_by_id(self, blog_id: str) -> Optional[Dict]:
        """Get a specific blog by its ID."""
        for blog in self.generated_blogs:
            if blog["id"] == blog_id:
                return blog
        return None

    # ==================== LEARNING LOG ====================

    def _log_learning(self, event_type: str, description: str) -> None:
        """Log a learning event."""
        self.learning_log.append({
            "event_type": event_type,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })

    def learn_from_feedback(self, feedback_type: str, feedback: str) -> None:
        """
        Learn from user feedback.
        This is how the system gets smarter over time.
        """
        self._log_learning("user_feedback", f"{feedback_type}: {feedback}")

        # Parse common feedback patterns
        feedback_lower = feedback.lower()

        # "Never use [word]" patterns
        if "never use" in feedback_lower:
            # Extract the word/phrase
            parts = feedback_lower.split("never use")
            if len(parts) > 1:
                word = parts[1].strip().strip('"\'')
                self.add_banned_word(word, "User feedback")

        # "Always include [element]" patterns
        elif "always include" in feedback_lower or "always mention" in feedback_lower:
            parts = feedback_lower.replace("always mention", "always include").split("always include")
            if len(parts) > 1:
                element = parts[1].strip().strip('"\'')
                self.add_required_element(element, "User feedback")

        # "Don't use [format]" patterns
        elif "don't use" in feedback_lower or "do not use" in feedback_lower:
            self.add_formatting_rule(feedback)

        self._save_all()

    def get_learning_stats(self) -> Dict:
        """Get statistics about system learning."""
        return {
            "total_learnings": len(self.learning_log),
            "banned_words_count": len(self.get_banned_words()),
            "required_elements_count": len(self.get_required_elements()),
            "style_notes_count": len(self.get_style_notes()),
            "formatting_rules_count": len(self.get_formatting_rules()),
            "blogs_generated": len(self.generated_blogs),
            "latest_learning": self.learning_log[-1] if self.learning_log else None
        }

    # ==================== CONTENT VALIDATION ====================

    def validate_content(self, content: str) -> Dict:
        """
        Validate content against all rules.
        Returns validation result with any issues found.
        """
        issues = []
        warnings = []

        content_lower = content.lower()

        # Check banned words
        for word in self.get_banned_words():
            if word in content_lower:
                issues.append(f"Contains banned word: '{word}'")

        # Check required elements
        for element in self.get_required_elements():
            if element.lower() not in content_lower:
                warnings.append(f"Missing required element: '{element}'")

        # Check formatting rules
        for rule in self.get_formatting_rules():
            rule_lower = rule.lower()
            if "no dashes" in rule_lower or "never use dash" in rule_lower:
                if " - " in content or " – " in content:
                    issues.append("Contains dashes (formatting rule violation)")
            if "no bullet" in rule_lower:
                if "•" in content or content.strip().startswith("-"):
                    issues.append("Contains bullet points (formatting rule violation)")

        # Check for duplicates
        duplicate = self.is_duplicate(content)
        if duplicate:
            issues.append(f"Content too similar to existing blog: '{duplicate['title']}'")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    def print_memory_summary(self) -> None:
        """Print a summary of all stored memory."""
        stats = self.get_learning_stats()
        prefs = self.get_all_preferences()

        print("\n" + "=" * 60)
        print("VINUCHI BLOG WRITER - PERSISTENT MEMORY")
        print("=" * 60)

        print(f"\nTotal Learnings: {stats['total_learnings']}")
        print(f"Blogs Generated: {stats['blogs_generated']}")

        print(f"\n--- Banned Words ({stats['banned_words_count']}) ---")
        for word in prefs['banned_words'][:10]:
            print(f"  - {word}")
        if len(prefs['banned_words']) > 10:
            print(f"  ... and {len(prefs['banned_words']) - 10} more")

        print(f"\n--- Required Elements ({stats['required_elements_count']}) ---")
        for elem in prefs['required_elements']:
            print(f"  - {elem}")

        print(f"\n--- Style Notes ({stats['style_notes_count']}) ---")
        for note in prefs['style_notes']:
            print(f"  - {note}")

        print(f"\n--- Formatting Rules ({stats['formatting_rules_count']}) ---")
        for rule in prefs['formatting_rules']:
            print(f"  - {rule}")

        print("=" * 60)


# Singleton instance for the application
_memory_instance = None

def get_memory() -> PersistentMemory:
    """Get the singleton memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = PersistentMemory()
    return _memory_instance


if __name__ == "__main__":
    # Test the memory system
    memory = get_memory()
    memory.print_memory_summary()
