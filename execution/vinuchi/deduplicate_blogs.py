#!/usr/bin/env python3
"""
Deduplicate scraped blogs.
The scraper picks up some duplicate URLs (article + "No Comments" links).
This script removes duplicates based on URL and content similarity.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
INPUT_FILE = BASE_DIR / ".tmp" / "vinuchi" / "scraped_blogs.json"
OUTPUT_FILE = BASE_DIR / ".tmp" / "vinuchi" / "scraped_blogs_clean.json"


def main():
    print("Loading scraped blogs...")

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        blogs = json.load(f)

    print(f"Total blogs before dedup: {len(blogs)}")

    # Deduplicate by URL
    seen_urls = set()
    seen_content_hashes = set()
    unique_blogs = []

    for blog in blogs:
        url = blog.get('url', '')
        content = blog.get('content', '')

        # Skip if we've seen this URL
        if url in seen_urls:
            continue

        # Skip if content is too similar (hash first 500 chars)
        content_hash = hash(content[:500])
        if content_hash in seen_content_hashes:
            continue

        # Skip very short content (likely navigation/error pages)
        if len(content.split()) < 100:
            continue

        seen_urls.add(url)
        seen_content_hashes.add(content_hash)
        unique_blogs.append(blog)

    print(f"Total blogs after dedup: {len(unique_blogs)}")
    print(f"Removed {len(blogs) - len(unique_blogs)} duplicates")

    # Sort by date (newest first)
    unique_blogs.sort(key=lambda x: x.get('date', ''), reverse=True)

    # Save cleaned version
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_blogs, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {OUTPUT_FILE}")

    # Also overwrite the original for convenience
    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_blogs, f, indent=2, ensure_ascii=False)

    print(f"Also updated: {INPUT_FILE}")

    # Print stats
    total_words = sum(b.get('word_count', 0) for b in unique_blogs)
    print(f"\nStats:")
    print(f"  Total unique blogs: {len(unique_blogs)}")
    print(f"  Total words: {total_words:,}")
    print(f"  Average words/blog: {total_words // len(unique_blogs) if unique_blogs else 0}")
    print(f"  Date range: {unique_blogs[-1].get('date', 'N/A')} to {unique_blogs[0].get('date', 'N/A')}")


if __name__ == "__main__":
    main()
