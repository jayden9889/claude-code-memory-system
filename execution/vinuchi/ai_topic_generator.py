#!/usr/bin/env python3
"""
AI-Powered Topic Generator for Vinuchi Blog Writer
Generates fresh, trending topic ideas using Claude AI.
Refreshes daily with new ideas based on corporate fashion trends and Vinuchi's brand.
"""

import json
import os
from pathlib import Path
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()


def _ensure_api_key_from_secrets():
    """
    Ensure ANTHROPIC_API_KEY is in environment, checking Streamlit secrets first.
    This allows the app to work both locally (.env) and on Streamlit Cloud (st.secrets).
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
            os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass


# Ensure API key is available before Anthropic client is created
_ensure_api_key_from_secrets()

from anthropic import Anthropic

# Storage paths
BASE_DIR = Path(__file__).parent.parent.parent
AI_TOPICS_FILE = BASE_DIR / ".tmp" / "vinuchi" / "ai_generated_topics.json"

# Initialize Anthropic client
client = Anthropic()

# Vinuchi brand context for topic generation
BRAND_CONTEXT = """
Vinuchi is a South African custom tie and scarf manufacturer with 30+ years experience.

KEY PRODUCTS:
- Custom corporate ties (printed and woven)
- School ties (matric ties, house ties, prefect ties)
- Club ties (sports clubs, golf clubs, old boys associations)
- Corporate scarves
- Promotional accessories (socks, cufflinks, pin badges)

KEY THEMES:
- Belonging and identity through corporate wear
- School traditions and heritage
- Corporate branding and recognition
- South African business culture
- Quality craftsmanship (printed vs woven)

TARGET AUDIENCES:
- Schools (private, public, universities)
- Corporations looking for branded accessories
- Sports clubs and associations
- Event organizers (golf days, conferences)
"""


def _load_ai_topics() -> dict:
    """Load AI-generated topics from file."""
    if AI_TOPICS_FILE.exists():
        try:
            with open(AI_TOPICS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"last_generated": None, "topics": [], "used_topics": []}


def _save_ai_topics(data: dict):
    """Save AI-generated topics to file."""
    AI_TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AI_TOPICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def _get_approved_blog_titles() -> list:
    """Get titles of approved blogs to avoid repetition."""
    try:
        from persistent_memory import get_memory
        memory = get_memory()
        return memory.get_all_blog_titles()
    except:
        return []


def generate_new_topics(count: int = 5) -> list:
    """
    Use Claude AI to generate fresh, trending topic ideas for Vinuchi blogs.

    Args:
        count: Number of new topics to generate

    Returns:
        List of topic strings
    """
    # Get existing blog titles to avoid repetition
    existing_titles = _get_approved_blog_titles()
    existing_str = "\n".join(f"- {t}" for t in existing_titles[:20]) if existing_titles else "None yet"

    # Get current month/season for seasonal relevance
    now = datetime.now()
    month = now.strftime("%B")
    year = now.year

    # Determine season (Southern Hemisphere - South Africa)
    month_num = now.month
    if month_num in [12, 1, 2]:
        season = "Summer (back-to-school season coming)"
    elif month_num in [3, 4, 5]:
        season = "Autumn (corporate year in full swing)"
    elif month_num in [6, 7, 8]:
        season = "Winter (school uniform season, matric farewells approaching)"
    else:
        season = "Spring (year-end events, recognition ceremonies)"

    prompt = f"""You are a content strategist for Vinuchi, a South African custom tie and scarf manufacturer.

{BRAND_CONTEXT}

CURRENT CONTEXT:
- Month: {month} {year}
- Season: {season}
- South African school calendar: Jan-Dec academic year, Matric farewells in Sept-Nov

EXISTING BLOG TOPICS (avoid these):
{existing_str}

Generate {count} NEW, FRESH blog topic ideas that would interest Vinuchi's target audience.

REQUIREMENTS:
1. Topics should be SPECIFIC and actionable (not generic like "Why ties matter")
2. Include at least 1-2 school-related topics (schools are key customers)
3. Consider current season/timing for relevance
4. Mix of educational, trend-focused, and product-focused topics
5. Topics should inspire a 550-590 word blog post
6. Make topics feel fresh and timely, not evergreen/generic

GOOD EXAMPLES:
- "5 tie colour combinations trending in SA corporate offices this winter"
- "How Johannesburg schools are modernising their tie designs"
- "The rise of sustainable fabrics in custom corporate ties"
- "Why more companies are choosing woven ties over printed in 2025"

BAD EXAMPLES (too generic):
- "Why ties are important"
- "The history of ties"
- "How to choose a tie"

Return ONLY the {count} topics, one per line, no numbers or bullets."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse the response
        content = response.content[0].text.strip()
        topics = [line.strip() for line in content.split('\n') if line.strip()]

        # Filter out any that are too short or look like headers
        topics = [t for t in topics if len(t) > 20 and not t.endswith(':')]

        return topics[:count]

    except Exception as e:
        print(f"Error generating AI topics: {e}")
        return []


def get_fresh_ai_topics(count: int = 4) -> list:
    """
    Get fresh AI-generated topics, generating new ones if needed.
    Generates new topics once per day.

    Args:
        count: Number of topics to return

    Returns:
        List of topic strings
    """
    data = _load_ai_topics()
    today = date.today().isoformat()

    # Check if we need to generate new topics (daily refresh)
    last_generated = data.get("last_generated")
    available_topics = [t for t in data.get("topics", []) if t not in data.get("used_topics", [])]

    # Generate new topics if:
    # 1. Never generated before
    # 2. Last generated on a different day
    # 3. Running low on available topics
    if last_generated != today or len(available_topics) < count:
        print(f"Generating fresh AI topics for {today}...")
        new_topics = generate_new_topics(5)  # Generate 5 new topics daily

        if new_topics:
            # Add new topics to the pool
            all_topics = data.get("topics", []) + new_topics
            # Keep only the most recent 30 topics to prevent bloat
            all_topics = all_topics[-30:]

            data["topics"] = all_topics
            data["last_generated"] = today
            _save_ai_topics(data)

            # Refresh available topics
            available_topics = [t for t in all_topics if t not in data.get("used_topics", [])]

    # Return requested number of topics
    if len(available_topics) >= count:
        import random
        selected = random.sample(available_topics, count)
        return selected
    else:
        return available_topics


def mark_ai_topic_used(topic: str):
    """Mark an AI-generated topic as used (won't appear again until reset)."""
    data = _load_ai_topics()
    used = data.get("used_topics", [])
    if topic not in used:
        used.append(topic)
        data["used_topics"] = used
        _save_ai_topics(data)


def clear_ai_topics():
    """Clear all AI-generated topics (called on system reset)."""
    if AI_TOPICS_FILE.exists():
        AI_TOPICS_FILE.unlink()


def force_refresh_ai_topics(count: int = 5) -> list:
    """Force generate new AI topics immediately."""
    new_topics = generate_new_topics(count)
    if new_topics:
        data = _load_ai_topics()
        data["topics"] = data.get("topics", []) + new_topics
        data["topics"] = data["topics"][-30:]  # Keep recent 30
        data["last_generated"] = date.today().isoformat()
        _save_ai_topics(data)
    return new_topics


def generate_related_topic(used_topic: str) -> str:
    """
    Generate a NEW topic related to the used one but with a different angle.

    For example:
    - "different materials of school ties" → "choosing colours for school ties"
    - "why schools need custom ties" → "how school ties build student identity"

    This keeps the same SEO keyword/concept but explores a fresh angle.
    """
    prompt = f"""You are a content strategist for Vinuchi, a South African custom tie and scarf manufacturer.

A blog was just written about: "{used_topic}"

Generate ONE NEW topic that:
1. Uses the SAME main SEO keyword/concept (e.g., if it was about "school ties", the new topic should also be about school ties)
2. Takes a COMPLETELY DIFFERENT angle or aspect
3. Is specific and actionable (not generic)
4. Would make a good 550-590 word blog post

EXAMPLES of good variations:
- Original: "The different materials used in school ties"
- New: "How to choose the right colours for your school tie"
- Next: "Adding your school crest to a custom tie"
- Next: "Why woven school ties last longer than printed ones"

The key is: SAME core topic (school ties, corporate ties, scarves, etc.) but DIFFERENT angle.

Return ONLY the new topic, nothing else. No explanation, no quotes, just the topic."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        new_topic = response.content[0].text.strip()
        # Clean up any quotes or extra formatting
        new_topic = new_topic.strip('"\'')

        return new_topic if len(new_topic) > 15 else None

    except Exception as e:
        print(f"Error generating related topic: {e}")
        return None


if __name__ == "__main__":
    print("AI Topic Generator")
    print("=" * 50)
    print("\nGenerating fresh topics...")

    topics = get_fresh_ai_topics(4)

    print("\nGenerated topics:")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic}")
