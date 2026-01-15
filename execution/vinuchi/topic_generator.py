#!/usr/bin/env python3
"""
Smart Topic Generator for Vinuchi Blog Writer
Generates relevant, varied topics based on Vinuchi's themes and industry.
Topics refresh when the 12-hour usage window resets.
"""

import json
import random
from pathlib import Path
from datetime import datetime

# Storage path
BASE_DIR = Path(__file__).parent.parent.parent
TOPICS_FILE = BASE_DIR / ".tmp" / "vinuchi" / "generated_topics.json"

# Vinuchi's core themes and product categories
THEMES = {
    "belonging": [
        "The psychology of belonging through wearing custom ties",
        "How corporate ties create team unity",
        "Why wearing your company's tie builds pride",
        "The emotional connection to club ties",
        "Creating identity through corporate scarves",
    ],
    "tradition": [
        "Preserving school traditions through custom ties",
        "The role of matric ties in school heritage",
        "Old boys ties and the connection to alumni",
        "How traditions are carried through corporate uniforms",
        "The timeless appeal of woven ties",
    ],
    "history": [
        "From Croatian soldiers to modern ties - a journey",
        "The evolution of the cravat to custom ties",
        "Why ties have survived for over 400 years",
        "The French aristocracy and the birth of fashion ties",
        "How tie manufacturing has changed over 30 years",
    ],
    "manufacturing": [
        "Printed ties vs woven ties - which is better",
        "The art of sublimation printing on ties",
        "Why quality fabric matters in custom scarves",
        "Understanding tie widths and when to use them",
        "The process of creating a custom corporate tie",
    ],
    "branding": [
        "Ties as the ultimate corporate branding tool",
        "How custom scarves elevate your brand identity",
        "Using promotional ties for marketing success",
        "The advertising power of branded accessories",
        "Why uniform ties boost company image",
    ],
    "occasions": [
        "Recognition awards and the role of ties",
        "Long service gifts - why ties are perfect",
        "Sports teams and their custom ties",
        "Golf day accessories and branded ties",
        "Conference giveaways that make an impact",
    ],
    "products": [
        "Custom scarves for the modern professional woman",
        "Corporate jewellery as the perfect complement to ties",
        "Branded socks - the underrated uniform piece",
        "Cufflinks and pin badges for recognition",
        "Matching accessories for complete corporate identity",
    ],
    "insights": [
        "What makes a tie design memorable",
        "Choosing colours for your corporate tie",
        "The difference between printed and woven quality",
        "Why South African companies choose local tie makers",
        "Trends in corporate accessories for 2025",
    ],
}

# Product focus variations (to ensure variety)
PRODUCT_FOCUSES = [
    "corporate ties", "custom scarves", "club ties", "promotional ties",
    "branded accessories", "matric ties", "sports ties", "uniform ties",
    "corporate jewellery", "branded socks", "company ties", "fashion ties"
]


def _get_window_id() -> str:
    """Get current 12-hour window ID for caching."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    period = "AM" if now.hour < 12 else "PM"
    return f"{date_str}_{period}"


def _load_cached_topics() -> dict:
    """Load cached topics from file."""
    if TOPICS_FILE.exists():
        try:
            with open(TOPICS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"window_id": None, "topics": []}


def _save_topics(window_id: str, topics: list):
    """Save topics to file."""
    TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOPICS_FILE, 'w') as f:
        json.dump({"window_id": window_id, "topics": topics}, f, indent=2)


def generate_fresh_topics(count: int = 4) -> list:
    """
    Generate fresh, varied topics from different themes.
    Ensures no two topics are from the same theme.
    """
    # Pick random themes (without replacement)
    available_themes = list(THEMES.keys())
    random.shuffle(available_themes)
    selected_themes = available_themes[:count]

    topics = []
    for theme in selected_themes:
        topic = random.choice(THEMES[theme])
        topics.append(topic)

    return topics


def get_quick_topics(count: int = 4) -> list:
    """
    Get quick topics for the UI.
    Returns cached topics if still in the same 12-hour window,
    otherwise generates fresh topics.
    """
    current_window = _get_window_id()
    cached = _load_cached_topics()

    # Check if we have valid cached topics for this window
    if cached.get("window_id") == current_window and cached.get("topics"):
        topics = cached["topics"]
        # If we have enough topics, return them
        if len(topics) >= count:
            return topics[:count]

    # Generate fresh topics
    topics = generate_fresh_topics(count)
    _save_topics(current_window, topics)

    return topics


def refresh_topics(count: int = 4) -> list:
    """Force refresh topics (for the refresh button)."""
    topics = generate_fresh_topics(count)
    current_window = _get_window_id()
    _save_topics(current_window, topics)
    return topics


if __name__ == "__main__":
    print("Quick Topics Generator")
    print("=" * 40)
    print("\nGenerated topics:")
    for i, topic in enumerate(get_quick_topics(), 1):
        print(f"  {i}. {topic}")
