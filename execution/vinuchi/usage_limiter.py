#!/usr/bin/env python3
"""
Usage Limiter - Financial Kill Switch
Prevents excessive API usage by enforcing strict limits.

Limits:
- 10 blog posts per 12-hour window
- Tracks usage in a local JSON file
- Admin reset via CLI only (not exposed in UI)
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple

# Configuration
MAX_POSTS_PER_WINDOW = 10
WINDOW_HOURS = 12

# Storage path
BASE_DIR = Path(__file__).parent.parent.parent
USAGE_FILE = BASE_DIR / ".tmp" / "vinuchi" / "usage_tracking.json"


def _ensure_dir_exists():
    """Create usage directory if it doesn't exist."""
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_usage() -> dict:
    """Load usage data from file."""
    _ensure_dir_exists()
    if not USAGE_FILE.exists():
        return {"requests": [], "admin_reset_at": None}
    try:
        with open(USAGE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"requests": [], "admin_reset_at": None}


def _save_usage(data: dict):
    """Save usage data to file."""
    _ensure_dir_exists()
    with open(USAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def _get_window_start() -> datetime:
    """Get the start of the current 12-hour window."""
    now = datetime.now()
    # Windows start at midnight and noon
    if now.hour < 12:
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return now.replace(hour=12, minute=0, second=0, microsecond=0)


def _clean_old_requests(data: dict) -> dict:
    """Remove requests older than the current window."""
    window_start = _get_window_start()

    # Also respect admin reset time
    admin_reset = data.get("admin_reset_at")
    if admin_reset:
        admin_reset_time = datetime.fromisoformat(admin_reset)
        # Use the later of window_start or admin_reset
        if admin_reset_time > window_start:
            window_start = admin_reset_time

    valid_requests = []
    for req in data.get("requests", []):
        req_time = datetime.fromisoformat(req["timestamp"])
        if req_time >= window_start:
            valid_requests.append(req)

    data["requests"] = valid_requests
    return data


def check_limit() -> Tuple[bool, int, str]:
    """
    Check if user can make another request.

    Returns:
        Tuple of (allowed: bool, remaining: int, message: str)
    """
    data = _load_usage()
    data = _clean_old_requests(data)
    _save_usage(data)

    current_count = len(data["requests"])
    remaining = MAX_POSTS_PER_WINDOW - current_count

    if remaining <= 0:
        window_end = _get_window_start() + timedelta(hours=WINDOW_HOURS)
        time_left = window_end - datetime.now()
        hours_left = int(time_left.total_seconds() // 3600)
        mins_left = int((time_left.total_seconds() % 3600) // 60)

        return (
            False,
            0,
            f"Daily Limit Reached! You've used all {MAX_POSTS_PER_WINDOW} posts. "
            f"Resets in {hours_left}h {mins_left}m."
        )

    return (True, remaining, f"{remaining} posts remaining in this window")


def record_usage(topic: str = ""):
    """Record a successful blog generation."""
    data = _load_usage()
    data = _clean_old_requests(data)

    data["requests"].append({
        "timestamp": datetime.now().isoformat(),
        "topic": topic[:100] if topic else "unknown"
    })

    _save_usage(data)


def get_usage_stats() -> dict:
    """Get current usage statistics."""
    data = _load_usage()
    data = _clean_old_requests(data)
    _save_usage(data)

    window_start = _get_window_start()
    window_end = window_start + timedelta(hours=WINDOW_HOURS)

    return {
        "used": len(data["requests"]),
        "limit": MAX_POSTS_PER_WINDOW,
        "remaining": MAX_POSTS_PER_WINDOW - len(data["requests"]),
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "recent_topics": [r["topic"] for r in data["requests"][-5:]]
    }


def admin_reset():
    """
    ADMIN ONLY: Reset the usage counter.
    This is intentionally NOT exposed in the UI.
    Run from command line: python usage_limiter.py reset
    """
    data = _load_usage()
    data["requests"] = []
    data["admin_reset_at"] = datetime.now().isoformat()
    _save_usage(data)
    return "Usage limit reset successfully"


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        print(admin_reset())
        print(f"All {MAX_POSTS_PER_WINDOW} posts are now available.")
    elif len(sys.argv) > 1 and sys.argv[1] == "status":
        stats = get_usage_stats()
        print(f"Usage: {stats['used']}/{stats['limit']}")
        print(f"Remaining: {stats['remaining']}")
        print(f"Window: {stats['window_start']} to {stats['window_end']}")
        if stats['recent_topics']:
            print(f"Recent: {', '.join(stats['recent_topics'])}")
    else:
        print("Usage Limiter - Admin Commands")
        print("=" * 40)
        print("  python usage_limiter.py reset   - Reset the limit")
        print("  python usage_limiter.py status  - Check current usage")
