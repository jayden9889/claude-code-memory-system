#!/usr/bin/env python3
"""
Smart Topic Generator for Vinuchi Blog Writer
Generates relevant, varied topics based on Vinuchi's themes and industry.

TOPIC SOURCES:
1. AI-generated topics (fresh daily, based on trends and seasons)
2. Curated topics (fallback, organized by theme)

The system prioritizes AI-generated topics for freshness, with curated topics as backup.
"""

import json
import random
from pathlib import Path
from datetime import datetime

# Storage path
BASE_DIR = Path(__file__).parent.parent.parent
TOPICS_FILE = BASE_DIR / ".tmp" / "vinuchi" / "generated_topics.json"
USED_TOPICS_FILE = BASE_DIR / ".tmp" / "vinuchi" / "used_topics.json"

# Flag to track if we should use AI topics (can be disabled if API issues)
USE_AI_TOPICS = True

# Vinuchi's core themes and product categories
# NOTE: "school" is a PRIORITY theme - always include at least one school topic
THEMES = {
    "school": [
        "Why every school needs a custom school tie",
        "The role of matric ties in school heritage",
        "Old boys ties and the connection to alumni",
        "Preserving school traditions through custom ties",
        "School scarves as part of winter uniform",
        "How school ties build student pride and identity",
        "Designing the perfect school tie for your institution",
        "Matric farewell accessories and commemorative ties",
        "Private schools and the tradition of custom ties",
        "School colours and what they mean in tie design",
    ],
    "belonging": [
        "The psychology of belonging through wearing custom ties",
        "How corporate ties create team unity",
        "Why wearing your company's tie builds pride",
        "The emotional connection to club ties",
        "Creating identity through corporate scarves",
    ],
    "tradition": [
        "How traditions are carried through corporate uniforms",
        "The timeless appeal of woven ties",
        "Club ties and the sense of membership they create",
        "Why organisations value custom accessories",
        "Building legacy through branded uniform pieces",
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


def load_used_topics() -> list:
    """Load list of topics that have been used AND approved (permanently excluded until reset)."""
    if USED_TOPICS_FILE.exists():
        try:
            with open(USED_TOPICS_FILE, 'r') as f:
                data = json.load(f)
                return data.get("used_topics", [])
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return []


def save_used_topic(topic: str):
    """Add a topic to the used topics list (called when a blog is approved)."""
    used_topics = load_used_topics()
    # Normalize and check if already saved
    topic_lower = topic.lower().strip()
    existing_lower = [t.lower() for t in used_topics]
    if topic_lower not in existing_lower:
        used_topics.append(topic)
        USED_TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USED_TOPICS_FILE, 'w') as f:
            json.dump({"used_topics": used_topics}, f, indent=2)


def clear_used_topics():
    """Clear all used topics and AI-generated topics (called on system reset)."""
    if USED_TOPICS_FILE.exists():
        USED_TOPICS_FILE.unlink()

    # Also clear AI-generated topics
    try:
        from ai_topic_generator import clear_ai_topics
        clear_ai_topics()
    except Exception as e:
        print(f"Could not clear AI topics: {e}")


def generate_fresh_topics(count: int = 4, exclude_topics: list = None) -> list:
    """
    Generate fresh, varied topics mixing AI-generated and curated topics.

    STRATEGY:
    1. Try to get 2-3 AI-generated topics (fresh, trending)
    2. Always include 1 school topic (curated - schools are key to Vinuchi)
    3. Fill remaining with curated topics from other themes

    Excludes any topics in the exclude list AND any permanently used topics.
    """
    # Build exclusion set from both explicit excludes and used topics
    exclude_topics = exclude_topics or []
    used_topics = load_used_topics()
    all_excluded = set(t.lower() for t in exclude_topics + used_topics)

    topics = []

    # STEP 1: Try to get AI-generated topics (2-3 fresh topics)
    ai_topics_to_get = min(count - 1, 3)  # Leave room for at least 1 curated school topic

    if USE_AI_TOPICS:
        try:
            from ai_topic_generator import get_fresh_ai_topics
            ai_topics = get_fresh_ai_topics(ai_topics_to_get + 2)  # Get extras in case some are excluded

            # Filter out excluded topics
            for topic in ai_topics:
                if len(topics) >= ai_topics_to_get:
                    break
                if topic.lower() not in all_excluded:
                    topics.append(topic)
                    all_excluded.add(topic.lower())

        except Exception as e:
            print(f"AI topic generation failed, using curated topics: {e}")

    # STEP 2: Always include at least 1 school topic (curated)
    if not any('school' in t.lower() or 'matric' in t.lower() for t in topics):
        school_topics = [t for t in THEMES.get("school", []) if t.lower() not in all_excluded]
        if school_topics:
            school_topic = random.choice(school_topics)
            topics.append(school_topic)
            all_excluded.add(school_topic.lower())

    # STEP 3: Fill remaining slots with curated topics from various themes
    available_themes = [t for t in THEMES.keys() if t != "school"]
    random.shuffle(available_themes)

    for theme in available_themes:
        if len(topics) >= count:
            break

        theme_topics = [t for t in THEMES[theme] if t.lower() not in all_excluded]
        if theme_topics:
            topic = random.choice(theme_topics)
            topics.append(topic)
            all_excluded.add(topic.lower())

    # STEP 4: If still need more, pick from any curated theme
    if len(topics) < count:
        all_remaining = []
        for theme_topics in THEMES.values():
            for t in theme_topics:
                if t.lower() not in all_excluded:
                    all_remaining.append(t)
        random.shuffle(all_remaining)
        topics.extend(all_remaining[:count - len(topics)])

    # Shuffle the final list for variety
    random.shuffle(topics)

    return topics


def get_quick_topics(count: int = 4, force_fresh: bool = True) -> list:
    """
    Get quick topics for the UI.
    By default, always generates fresh topics on each call (topics reset on app open).
    Excludes any topics that have been used AND approved.

    Args:
        count: Number of topics to return
        force_fresh: If True (default), always generate new topics. If False, use cache.
    """
    current_window = _get_window_id()

    if not force_fresh:
        # Only use cache if explicitly requested
        cached = _load_cached_topics()
        if cached.get("window_id") == current_window and cached.get("topics"):
            topics = cached["topics"]
            if len(topics) >= count:
                return topics[:count]

    # Generate fresh topics (excluding used ones)
    topics = generate_fresh_topics(count)
    _save_topics(current_window, topics)

    return topics


def refresh_topics(count: int = 4, exclude_current: list = None) -> list:
    """
    Force refresh topics (for the refresh/shuffle button).

    IMPORTANT: Pass the current topics as exclude_current to ensure
    the user gets COMPLETELY NEW topics, not recycled ones.
    """
    # Exclude the current topics so user gets entirely fresh ones
    topics = generate_fresh_topics(count, exclude_topics=exclude_current or [])
    current_window = _get_window_id()
    _save_topics(current_window, topics)
    return topics


def get_single_fresh_topic(exclude_topics: list = None) -> str:
    """
    Get a single fresh topic that's not in the exclude list.
    Used when replacing a used quick topic.
    Also excludes any permanently used (approved) topics.
    """
    exclude_topics = exclude_topics or []
    used_topics = load_used_topics()
    exclude_set = set(t.lower() for t in exclude_topics + used_topics)

    # Try to find a topic from a random theme that's not in exclude list
    all_topics = []
    for theme_topics in THEMES.values():
        all_topics.extend(theme_topics)

    # Shuffle and find one that's not excluded
    random.shuffle(all_topics)
    for topic in all_topics:
        if topic.lower() not in exclude_set:
            return topic

    # Fallback: just pick a random one (shouldn't happen normally)
    return random.choice(all_topics)


if __name__ == "__main__":
    print("Quick Topics Generator")
    print("=" * 40)
    print("\nGenerated topics:")
    for i, topic in enumerate(get_quick_topics(), 1):
        print(f"  {i}. {topic}")
