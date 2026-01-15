#!/usr/bin/env python3
"""
Vinuchi Style Analyzer
Analyzes all scraped blogs to extract writing patterns, keywords, and tone.

Outputs a comprehensive style profile that the blog generator uses.
"""

import json
import re
from collections import Counter
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
INPUT_FILE = BASE_DIR / ".tmp" / "vinuchi" / "scraped_blogs.json"
OUTPUT_FILE = BASE_DIR / ".tmp" / "vinuchi" / "style_profile.json"


def extract_keywords(text: str, top_n: int = 50) -> dict:
    """
    Extract frequently used keywords and phrases from text.

    Returns dict with:
    - primary: Top single keywords
    - phrases: Common 2-3 word phrases
    - frequency: Normalized frequency of each keyword
    """
    # Clean text
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)

    # Common stopwords to filter out
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'dare', 'ought', 'used', 'it', 'its', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'our', 'their', 'mine', 'yours', 'hers', 'ours',
        'theirs', 'what', 'which', 'who', 'whom', 'whose', 'when', 'where',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there',
        'then', 'once', 'one', 'two', 'three', 'first', 'last', 'long', 'great',
        'new', 'good', 'right', 'well', 'even', 'back', 'any', 'way', 'take',
        'come', 'make', 'know', 'get', 'go', 'see', 'look', 'think', 'give',
        'use', 'find', 'tell', 'say', 'said', 'many', 'much', 'over', 'after',
        'being', 'through', 'about', 'into', 'before', 'between', 'under',
        'again', 'further', 'always', 'never', 'often', 'still', 'really',
        'something', 'anything', 'nothing', 'everything', 'someone', 'anyone',
        'everyone', 'people', 'person', 'thing', 'things', 'time', 'times',
        'year', 'years', 'day', 'days', 'today', 'yesterday', 'tomorrow',
        'comments', 'comment', 'read', 'continue', 'article', 'articles',
        'post', 'posts', 'blog', 'website', 'page', 'click', 'share'
    }

    # Extract words
    words = text.split()
    words = [w for w in words if len(w) > 2 and w not in stopwords]

    # Count single words
    word_counts = Counter(words)

    # Count 2-word phrases
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    bigram_counts = Counter(bigrams)

    # Count 3-word phrases
    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
    trigram_counts = Counter(trigrams)

    # Get top keywords
    total_words = len(words)
    primary_keywords = []
    keyword_frequency = {}

    for word, count in word_counts.most_common(top_n):
        if count > 3:  # Minimum occurrence threshold
            primary_keywords.append(word)
            keyword_frequency[word] = round(count / total_words * 100, 2)

    # Get meaningful phrases (those appearing multiple times)
    phrases = []
    for phrase, count in bigram_counts.most_common(30):
        if count > 5:
            phrases.append(phrase)

    for phrase, count in trigram_counts.most_common(20):
        if count > 3:
            phrases.append(phrase)

    return {
        "primary": primary_keywords[:30],
        "phrases": phrases[:20],
        "frequency": keyword_frequency
    }


def analyze_tone(blogs: list) -> dict:
    """
    Analyze the overall tone and voice of the blog content.
    """
    all_content = " ".join(blog['content'] for blog in blogs)

    # Check for first person plural (we, our, us)
    first_person_plural = len(re.findall(r'\b(we|our|us)\b', all_content.lower()))
    # Check for first person singular (I, my, me)
    first_person_singular = len(re.findall(r'\b(i|my|me)\b', all_content.lower()))
    # Check for second person (you, your)
    second_person = len(re.findall(r'\b(you|your)\b', all_content.lower()))

    total = first_person_plural + first_person_singular + second_person + 1

    # Determine primary perspective
    if first_person_plural > first_person_singular and first_person_plural > second_person:
        perspective = "first-person-plural"
    elif second_person > first_person_plural:
        perspective = "second-person"
    else:
        perspective = "first-person-singular"

    # Check formality markers
    formal_words = len(re.findall(r'\b(therefore|furthermore|consequently|moreover|however|nevertheless)\b', all_content.lower()))
    informal_words = len(re.findall(r'\b(gonna|wanna|kinda|stuff|basically|actually|really|pretty)\b', all_content.lower()))

    if formal_words > informal_words:
        formality = "professional-formal"
    elif informal_words > formal_words * 2:
        formality = "casual"
    else:
        formality = "professional-warm"

    # Check sentiment
    positive_words = len(re.findall(r'\b(excellent|amazing|wonderful|great|best|quality|perfect|beautiful|proud|passion)\b', all_content.lower()))
    negative_words = len(re.findall(r'\b(bad|poor|terrible|worst|cheap|problem|issue|unfortunately)\b', all_content.lower()))

    if positive_words > negative_words * 2:
        sentiment = "positive-authoritative"
    elif negative_words > positive_words:
        sentiment = "neutral-cautious"
    else:
        sentiment = "positive-balanced"

    return {
        "formality": formality,
        "perspective": perspective,
        "sentiment": sentiment,
        "perspective_ratios": {
            "first_person_plural": round(first_person_plural / total * 100, 1),
            "first_person_singular": round(first_person_singular / total * 100, 1),
            "second_person": round(second_person / total * 100, 1)
        }
    }


def analyze_structure(blogs: list) -> dict:
    """
    Analyze the typical structure of blog posts.
    """
    paragraph_counts = []
    word_counts = []
    words_per_paragraph = []
    uses_questions = 0
    uses_lists = 0

    for blog in blogs:
        content = blog['content']

        # Count paragraphs (split by double newline)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_counts.append(len(paragraphs))

        # Word count
        words = len(content.split())
        word_counts.append(words)

        # Words per paragraph
        if paragraphs:
            words_per_paragraph.append(words / len(paragraphs))

        # Check for questions
        if '?' in content:
            uses_questions += 1

        # Check for lists (lines starting with - or *)
        if re.search(r'^\s*[-*•]\s', content, re.MULTILINE):
            uses_lists += 1

    total_blogs = len(blogs)

    return {
        "avg_paragraphs": round(sum(paragraph_counts) / len(paragraph_counts), 1) if paragraph_counts else 0,
        "avg_word_count": round(sum(word_counts) / len(word_counts), 0) if word_counts else 0,
        "avg_words_per_paragraph": round(sum(words_per_paragraph) / len(words_per_paragraph), 0) if words_per_paragraph else 0,
        "min_word_count": min(word_counts) if word_counts else 0,
        "max_word_count": max(word_counts) if word_counts else 0,
        "uses_questions_percent": round(uses_questions / total_blogs * 100, 1),
        "uses_lists_percent": round(uses_lists / total_blogs * 100, 1)
    }


def extract_common_phrases(blogs: list) -> dict:
    """
    Extract common opening phrases, closing phrases, and signature expressions.
    """
    openers = []
    closers = []
    signature_phrases = []

    for blog in blogs:
        content = blog['content']
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        if paragraphs:
            # Get first sentence of first paragraph
            first_para = paragraphs[0]
            first_sentence = first_para.split('.')[0] if '.' in first_para else first_para[:100]

            # Extract opener pattern (first 3-5 words)
            words = first_sentence.split()[:5]
            if len(words) >= 3:
                opener = ' '.join(words[:3])
                openers.append(opener.lower())

            # Get last paragraph for closer
            last_para = paragraphs[-1]
            last_sentence = last_para.split('.')[-2] if '.' in last_para else last_para[-100:]

            # Extract closer pattern
            closer_words = last_sentence.split()[:4]
            if len(closer_words) >= 3:
                closer = ' '.join(closer_words[:3])
                closers.append(closer.lower())

    # Count most common patterns
    opener_counts = Counter(openers)
    closer_counts = Counter(closers)

    return {
        "common_openers": [phrase for phrase, count in opener_counts.most_common(10) if count > 2],
        "common_closers": [phrase for phrase, count in closer_counts.most_common(10) if count > 2],
        "signature_phrases": signature_phrases
    }


def analyze_topics(blogs: list) -> list:
    """
    Extract the main topics covered in the blogs.
    """
    all_titles = " ".join(blog['title'].lower() for blog in blogs)

    # Common topic words in titles
    topic_words = re.findall(r'\b\w+\b', all_titles)
    topic_counts = Counter(topic_words)

    # Filter stopwords and short words
    stopwords = {'the', 'a', 'an', 'and', 'or', 'for', 'to', 'of', 'in', 'is', 'are', 'with', 'why', 'how', 'what'}
    topics = [(word, count) for word, count in topic_counts.most_common(30)
              if word not in stopwords and len(word) > 2]

    return [word for word, count in topics[:15]]


def main():
    """Main analysis routine."""
    print("=" * 60)
    print("VINUCHI STYLE ANALYZER")
    print("=" * 60)

    # Load scraped blogs
    if not INPUT_FILE.exists():
        print(f"\nERROR: Input file not found: {INPUT_FILE}")
        print("Run scrape_all_blogs.py first.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        blogs = json.load(f)

    print(f"\nAnalyzing {len(blogs)} blog posts...")

    # Combine all content for keyword analysis
    all_content = " ".join(blog['content'] for blog in blogs)

    # Perform analysis
    print("\n1. Extracting keywords...")
    keywords = extract_keywords(all_content)
    print(f"   Found {len(keywords['primary'])} primary keywords, {len(keywords['phrases'])} phrases")

    print("\n2. Analyzing tone...")
    tone = analyze_tone(blogs)
    print(f"   Perspective: {tone['perspective']}, Formality: {tone['formality']}")

    print("\n3. Analyzing structure...")
    structure = analyze_structure(blogs)
    print(f"   Avg {structure['avg_word_count']} words, {structure['avg_paragraphs']} paragraphs per post")

    print("\n4. Extracting common phrases...")
    phrases = extract_common_phrases(blogs)
    print(f"   Found {len(phrases['common_openers'])} opener patterns")

    print("\n5. Identifying main topics...")
    topics = analyze_topics(blogs)
    print(f"   Main topics: {', '.join(topics[:5])}")

    # Compile full style profile
    style_profile = {
        "analyzed_at": datetime.now().isoformat(),
        "total_blogs_analyzed": len(blogs),
        "total_words_analyzed": len(all_content.split()),
        "keywords": keywords,
        "tone": tone,
        "structure": structure,
        "phrases": phrases,
        "main_topics": topics
    }

    # Save profile
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(style_profile, f, indent=2)

    print(f"\n{'='*60}")
    print("STYLE PROFILE SUMMARY")
    print(f"{'='*60}")
    print(f"\nTop Keywords: {', '.join(keywords['primary'][:10])}")
    print(f"Top Phrases: {', '.join(keywords['phrases'][:5])}")
    print(f"\nTone: {tone['formality']} | {tone['perspective']} | {tone['sentiment']}")
    print(f"\nStructure:")
    print(f"  - Average: {structure['avg_word_count']:.0f} words, {structure['avg_paragraphs']} paragraphs")
    print(f"  - Uses questions: {structure['uses_questions_percent']}% of posts")
    print(f"\nCommon Openers: {', '.join(phrases['common_openers'][:3])}")
    print(f"\nMain Topics: {', '.join(topics[:5])}")
    print(f"\nStyle profile saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
