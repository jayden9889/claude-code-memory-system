#!/usr/bin/env python3
"""
Vinuchi Preferences Manager
Handles persistent rules and preferences for the blog writer.

This is the "learning" component - stores rules like:
- "Never use the word 'cheap'"
- "Always mention 'South Africa' in the first paragraph"
- "Preferred tone: professional but warm"
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent
PREFERENCES_FILE = BASE_DIR / ".tmp" / "vinuchi" / "preferences.json"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Preference types
RULE_TYPES = {
    "banned_word": "Words that should NEVER be used",
    "required_element": "Elements that MUST be included",
    "style_note": "General style guidance",
    "keyword": "SEO keywords to include when relevant",
    "topic_restriction": "Topics to avoid or handle carefully"
}


class PreferencesManager:
    """Manages persistent preferences for the blog writer."""

    def __init__(self, use_supabase: bool = True):
        """
        Initialize the preferences manager.

        Args:
            use_supabase: If True, use Supabase for storage. Otherwise use local JSON.
        """
        self.use_supabase = use_supabase and SUPABASE_URL and SUPABASE_KEY
        self.preferences = self._load_preferences()

    def _get_headers(self) -> dict:
        """Get Supabase API headers."""
        return {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

    def _load_preferences(self) -> list:
        """Load all preferences from storage."""
        if self.use_supabase:
            return self._load_from_supabase()
        else:
            return self._load_from_file()

    def _load_from_supabase(self) -> list:
        """Load preferences from Supabase."""
        try:
            url = f"{SUPABASE_URL}/rest/v1/vinuchi_preferences?active=eq.true"
            response = requests.get(url, headers=self._get_headers())

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Could not load from Supabase ({response.status_code})")
                return self._load_from_file()
        except Exception as e:
            print(f"Warning: Supabase error: {e}")
            return self._load_from_file()

    def _load_from_file(self) -> list:
        """Load preferences from local JSON file."""
        if PREFERENCES_FILE.exists():
            with open(PREFERENCES_FILE, 'r') as f:
                return json.load(f)
        return []

    def _save_to_file(self):
        """Save preferences to local JSON file (backup)."""
        PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(self.preferences, f, indent=2)

    def add_rule(self, rule_type: str, rule_value: str, reason: str = "") -> dict:
        """
        Add a new rule/preference.

        Args:
            rule_type: Type of rule (banned_word, required_element, etc.)
            rule_value: The actual rule value
            reason: Why this rule was added

        Returns:
            The created rule dict
        """
        if rule_type not in RULE_TYPES:
            raise ValueError(f"Invalid rule type. Must be one of: {list(RULE_TYPES.keys())}")

        rule = {
            "rule_type": rule_type,
            "rule_value": rule_value.lower() if rule_type == "banned_word" else rule_value,
            "reason": reason,
            "created_at": datetime.now().isoformat(),
            "active": True
        }

        if self.use_supabase:
            try:
                url = f"{SUPABASE_URL}/rest/v1/vinuchi_preferences"
                response = requests.post(
                    url,
                    headers={**self._get_headers(), "Prefer": "return=representation"},
                    json=rule
                )

                if response.status_code in [200, 201]:
                    rule = response.json()[0]
                    print(f"Rule saved to Supabase: {rule_type} = {rule_value}")
            except Exception as e:
                print(f"Warning: Could not save to Supabase: {e}")

        self.preferences.append(rule)
        self._save_to_file()

        return rule

    def remove_rule(self, rule_value: str):
        """Deactivate a rule by its value."""
        for pref in self.preferences:
            if pref.get('rule_value') == rule_value:
                pref['active'] = False

        if self.use_supabase:
            try:
                url = f"{SUPABASE_URL}/rest/v1/vinuchi_preferences?rule_value=eq.{rule_value}"
                requests.patch(url, headers=self._get_headers(), json={"active": False})
            except Exception as e:
                print(f"Warning: Could not update Supabase: {e}")

        self._save_to_file()

    def get_banned_words(self) -> list:
        """Get all banned words."""
        return [p['rule_value'] for p in self.preferences
                if p.get('rule_type') == 'banned_word' and p.get('active', True)]

    def get_required_elements(self) -> list:
        """Get all required elements."""
        return [p['rule_value'] for p in self.preferences
                if p.get('rule_type') == 'required_element' and p.get('active', True)]

    def get_style_notes(self) -> list:
        """Get all style notes."""
        return [p['rule_value'] for p in self.preferences
                if p.get('rule_type') == 'style_note' and p.get('active', True)]

    def get_keywords(self) -> list:
        """Get all SEO keywords."""
        return [p['rule_value'] for p in self.preferences
                if p.get('rule_type') == 'keyword' and p.get('active', True)]

    def get_all_active(self) -> dict:
        """Get all active preferences organized by type."""
        return {
            "banned_words": self.get_banned_words(),
            "required_elements": self.get_required_elements(),
            "style_notes": self.get_style_notes(),
            "keywords": self.get_keywords()
        }

    def check_content(self, content: str) -> dict:
        """
        Check content against all rules.

        Returns dict with violations and suggestions.
        """
        violations = []
        suggestions = []

        # Check banned words
        content_lower = content.lower()
        for word in self.get_banned_words():
            if word in content_lower:
                violations.append(f"Contains banned word: '{word}'")

        # Check required elements
        for element in self.get_required_elements():
            if element.lower() not in content_lower:
                suggestions.append(f"Missing required element: '{element}'")

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "suggestions": suggestions
        }

    def print_summary(self):
        """Print a summary of all preferences."""
        prefs = self.get_all_active()

        print("\n" + "=" * 50)
        print("VINUCHI BLOG WRITER PREFERENCES")
        print("=" * 50)

        print(f"\nBanned Words ({len(prefs['banned_words'])}):")
        for word in prefs['banned_words']:
            print(f"  - {word}")

        print(f"\nRequired Elements ({len(prefs['required_elements'])}):")
        for elem in prefs['required_elements']:
            print(f"  - {elem}")

        print(f"\nStyle Notes ({len(prefs['style_notes'])}):")
        for note in prefs['style_notes']:
            print(f"  - {note}")

        print(f"\nSEO Keywords ({len(prefs['keywords'])}):")
        for kw in prefs['keywords']:
            print(f"  - {kw}")


def main():
    """CLI interface for managing preferences."""
    manager = PreferencesManager()

    if len(sys.argv) < 2:
        manager.print_summary()
        print("\nUsage:")
        print("  python manage_preferences.py list")
        print("  python manage_preferences.py add banned_word <word> [reason]")
        print("  python manage_preferences.py add required_element <element> [reason]")
        print("  python manage_preferences.py add style_note <note>")
        print("  python manage_preferences.py add keyword <keyword>")
        print("  python manage_preferences.py remove <value>")
        print("  python manage_preferences.py check '<content>'")
        return

    command = sys.argv[1]

    if command == "list":
        manager.print_summary()

    elif command == "add" and len(sys.argv) >= 4:
        rule_type = sys.argv[2]
        rule_value = sys.argv[3]
        reason = sys.argv[4] if len(sys.argv) > 4 else ""

        try:
            rule = manager.add_rule(rule_type, rule_value, reason)
            print(f"Added: {rule_type} = {rule_value}")
        except ValueError as e:
            print(f"Error: {e}")

    elif command == "remove" and len(sys.argv) >= 3:
        rule_value = sys.argv[2]
        manager.remove_rule(rule_value)
        print(f"Removed: {rule_value}")

    elif command == "check" and len(sys.argv) >= 3:
        content = sys.argv[2]
        result = manager.check_content(content)

        if result['passed']:
            print("Content passed all checks!")
        else:
            print("Content has issues:")
            for v in result['violations']:
                print(f"  ERROR: {v}")
            for s in result['suggestions']:
                print(f"  SUGGESTION: {s}")

    else:
        print("Invalid command. Run without arguments for usage.")


if __name__ == "__main__":
    main()
