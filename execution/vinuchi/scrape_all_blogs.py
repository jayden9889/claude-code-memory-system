#!/usr/bin/env python3
"""
Vinuchi Blog Scraper
Scrapes all blog posts from vinuchi.co.za and stores them for analysis.

This script:
1. Iterates through all blog pages (24 pages, ~240 posts)
2. Extracts full content from each post
3. Saves to JSON for further processing
"""

import sys
# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
from pathlib import Path
import sys

# Configuration
BASE_URL = "https://vinuchi.co.za"
BLOG_URL = f"{BASE_URL}/blog/"
OUTPUT_DIR = Path(__file__).parent.parent.parent / ".tmp" / "vinuchi"
OUTPUT_FILE = OUTPUT_DIR / "scraped_blogs.json"

# Request headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def get_blog_list_page(page_num: int) -> list[dict]:
    """
    Get all blog post URLs and metadata from a single listing page.

    Args:
        page_num: Page number (1-indexed)

    Returns:
        List of dicts with 'url', 'title', 'date' for each post
    """
    if page_num == 1:
        url = BLOG_URL
    else:
        url = f"{BLOG_URL}page/{page_num}/"

    print(f"  Fetching page {page_num}: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR fetching page {page_num}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'lxml')
    posts = []

    # Find all article links - WordPress typically uses article tags or specific classes
    # Looking at the structure, blogs are in article elements or div with post class
    articles = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'post'))

    if not articles:
        # Try finding links that match the blog URL pattern
        links = soup.find_all('a', href=re.compile(r'/\d{4}/\d{2}/\d{2}/'))
        seen_urls = set()
        for link in links:
            href = link.get('href', '')
            if href and href not in seen_urls:
                seen_urls.add(href)
                title = link.get_text(strip=True) or "Untitled"
                # Extract date from URL
                date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', href)
                date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else None
                posts.append({
                    'url': href if href.startswith('http') else BASE_URL + href,
                    'title': title,
                    'date': date_str
                })
    else:
        for article in articles:
            # Find the main link
            link = article.find('a', href=re.compile(r'/\d{4}/\d{2}/\d{2}/'))
            if not link:
                continue

            href = link.get('href', '')
            title_elem = article.find(['h1', 'h2', 'h3', 'h4']) or link
            title = title_elem.get_text(strip=True) if title_elem else "Untitled"

            # Extract date from URL
            date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', href)
            date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else None

            posts.append({
                'url': href if href.startswith('http') else BASE_URL + href,
                'title': title,
                'date': date_str
            })

    return posts


def get_blog_content(url: str) -> dict:
    """
    Get the full content of a single blog post.

    Args:
        url: Full URL to the blog post

    Returns:
        Dict with full blog data including content
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"    ERROR fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    # Extract title
    title_elem = soup.find('h1', class_=re.compile(r'entry-title|post-title|title')) or soup.find('h1')
    title = title_elem.get_text(strip=True) if title_elem else "Untitled"

    # Extract main content - try multiple selectors
    content_selectors = [
        ('div', {'class': re.compile(r'entry-content|post-content|article-content|content')}),
        ('article', {}),
        ('div', {'class': 'content'}),
    ]

    content = ""
    for tag, attrs in content_selectors:
        content_elem = soup.find(tag, attrs)
        if content_elem:
            # Remove script and style tags
            for script in content_elem.find_all(['script', 'style', 'nav', 'aside']):
                script.decompose()

            # Get text with paragraph separation
            paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4', 'li'])
            if paragraphs:
                content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            else:
                content = content_elem.get_text(separator="\n\n", strip=True)

            if len(content) > 100:  # Found meaningful content
                break

    # Extract date from URL if not found elsewhere
    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else None

    # Count words
    word_count = len(content.split()) if content else 0

    return {
        'url': url,
        'title': title,
        'content': content,
        'date': date_str,
        'word_count': word_count,
        'scraped_at': datetime.now().isoformat()
    }


def scrape_all_blogs(max_pages: int = 24) -> list[dict]:
    """
    Scrape all blog posts from the Vinuchi website.

    Args:
        max_pages: Maximum number of pages to scrape (default 24)

    Returns:
        List of all blog posts with full content
    """
    print(f"\n{'='*60}")
    print("VINUCHI BLOG SCRAPER")
    print(f"{'='*60}")
    print(f"Target: {BLOG_URL}")
    print(f"Max pages: {max_pages}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"{'='*60}\n")

    # Phase 1: Collect all blog URLs
    print("PHASE 1: Collecting blog URLs from listing pages...")
    all_posts = []
    seen_urls = set()

    for page_num in range(1, max_pages + 1):
        posts = get_blog_list_page(page_num)

        for post in posts:
            if post['url'] not in seen_urls:
                seen_urls.add(post['url'])
                all_posts.append(post)

        print(f"    Found {len(posts)} posts on page {page_num} (total unique: {len(all_posts)})")
        time.sleep(0.5)  # Polite delay

        # Stop if we got no posts (reached end)
        if not posts:
            print(f"    No posts found on page {page_num}, stopping.")
            break

    print(f"\nTotal unique blog posts found: {len(all_posts)}")

    # Phase 2: Fetch full content for each post
    print(f"\nPHASE 2: Fetching full content for {len(all_posts)} posts...")
    full_blogs = []

    for i, post in enumerate(all_posts, 1):
        print(f"  [{i}/{len(all_posts)}] {post['title'][:50]}...")

        blog_data = get_blog_content(post['url'])
        if blog_data and blog_data.get('content'):
            full_blogs.append(blog_data)
            print(f"    OK - {blog_data['word_count']} words")
        else:
            print(f"    SKIP - No content extracted")

        time.sleep(0.3)  # Polite delay

    print(f"\nSuccessfully scraped {len(full_blogs)} blogs with content")

    return full_blogs


def save_blogs(blogs: list[dict]) -> None:
    """Save scraped blogs to JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(blogs, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(blogs)} blogs to {OUTPUT_FILE}")


def main():
    """Main entry point."""
    # Check for command line args
    max_pages = 24
    if len(sys.argv) > 1:
        try:
            max_pages = int(sys.argv[1])
        except ValueError:
            print(f"Invalid max_pages argument: {sys.argv[1]}")
            sys.exit(1)

    # Scrape all blogs
    blogs = scrape_all_blogs(max_pages=max_pages)

    if blogs:
        save_blogs(blogs)

        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total blogs scraped: {len(blogs)}")
        print(f"Total words: {sum(b['word_count'] for b in blogs):,}")
        print(f"Average words per blog: {sum(b['word_count'] for b in blogs) // len(blogs):,}")
        print(f"Date range: {min(b['date'] for b in blogs if b['date'])} to {max(b['date'] for b in blogs if b['date'])}")
        print(f"{'='*60}")
    else:
        print("\nERROR: No blogs scraped!")
        sys.exit(1)


if __name__ == "__main__":
    main()
