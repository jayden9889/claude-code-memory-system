#!/usr/bin/env python3
"""
Vinuchi Blog Generator - Deep Learning Edition
Generates blogs that perfectly match Vinuchi's distinctive writing style.

Uses:
- Deep style analysis from 235+ existing blogs
- Persistent memory for preferences and duplicate prevention
- Reference blogs for tone matching
- Pre-delivery review against existing blog database

SECURITY NOTE:
- ANTHROPIC_API_KEY loaded from .env (local) or st.secrets (Streamlit Cloud)
- API calls are made via Python's anthropic library (server-side)
- No browser/client ever receives or uses the API key
- .env is in .gitignore and should NEVER be committed
"""

import json
import os
import sys
import random
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from difflib import SequenceMatcher

# Load .env for local development
load_dotenv()


def _ensure_api_key_from_secrets():
    """
    Ensure ANTHROPIC_API_KEY is in environment, checking Streamlit secrets first.
    This allows the app to work both locally (.env) and on Streamlit Cloud (st.secrets).
    """
    # If already in environment (from .env), we're good
    if os.getenv("ANTHROPIC_API_KEY"):
        return

    # Try to get from Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
            os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass  # Not running in Streamlit context


# Ensure API key is available before Anthropic client is created
_ensure_api_key_from_secrets()

# HARD LIMITS
MIN_WORDS = 550  # Absolute minimum - blogs MUST be over 500 words
MAX_WORDS = 600  # Absolute maximum (590 + 10 leeway)
TARGET_WORDS = 570  # Target to aim for (550-590 range)
SIMILARITY_THRESHOLD = 0.6  # Block if 60%+ similar to existing blog

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from persistent_memory import get_memory
from usage_limiter import check_limit, record_usage, get_usage_stats

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class UsageLimitExceeded(Exception):
    """Raised when the usage limit has been exceeded."""
    pass

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
STYLE_ANALYSIS_FILE = BASE_DIR / ".tmp" / "vinuchi" / "deep_style_analysis.json"
BLOGS_FILE = BASE_DIR / ".tmp" / "vinuchi" / "scraped_blogs.json"


class VinuchiBlogGenerator:
    """
    Advanced blog generator that perfectly replicates Vinuchi's writing style.
    """

    def __init__(self):
        """Initialize with all knowledge sources."""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        self.client = anthropic.Anthropic()
        self.memory = get_memory()
        self.style_analysis = self._load_style_analysis()
        self.existing_blogs = self._load_existing_blogs()

    def _load_style_analysis(self) -> dict:
        """Load the deep style analysis."""
        if STYLE_ANALYSIS_FILE.exists():
            with open(STYLE_ANALYSIS_FILE, 'r') as f:
                return json.load(f)
        return {}

    def _load_existing_blogs(self) -> list:
        """Load existing blogs for reference."""
        if BLOGS_FILE.exists():
            with open(BLOGS_FILE, 'r') as f:
                return json.load(f)
        return []

    def _get_reference_blogs(self, topic: str, n: int = 3) -> list:
        """Get relevant reference blogs to guide style."""
        if not self.existing_blogs:
            return []

        topic_words = set(topic.lower().split())
        scored_blogs = []

        for blog in self.existing_blogs:
            title_words = set(blog['title'].lower().split())
            content_words = set(blog['content'].lower().split()[:100])
            overlap = len(topic_words & (title_words | content_words))
            scored_blogs.append((overlap, blog))

        scored_blogs.sort(key=lambda x: x[0], reverse=True)

        if scored_blogs and scored_blogs[0][0] > 0:
            return [blog for _, blog in scored_blogs[:n]]

        return random.sample(self.existing_blogs, min(n, len(self.existing_blogs)))

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt from deep analysis with Brand Anchor protection."""
        sa = self.style_analysis
        prefs = self.memory.get_all_preferences()

        # =================================================================
        # BRAND IDENTITY GROUND TRUTH (IMMUTABLE - CANNOT BE OVERWRITTEN)
        # =================================================================
        prompt = """
################################################################################
#                    BRAND IDENTITY GROUND TRUTH (IMMUTABLE)                   #
#         These core brand pillars CANNOT be overwritten by user feedback      #
################################################################################

You are the blog writer for Vinuchi, a South African custom tie and scarf manufacturer with 30+ years experience.

## CORE BRAND PILLARS (PROTECTED - NEVER CHANGE THESE)

### PILLAR 1: AUTHENTIC VOICE
- You ARE Vinuchi's founder speaking directly to the reader
- First-person perspective ALWAYS ("I", "we", "our", "my")
- Conversational, like chatting with a customer over coffee
- Passionate and opinionated - you LOVE this industry
- Stream of consciousness writing - let thoughts meander naturally

### PILLAR 2: DISTINCTIVE WRITING STYLE
- LONG, flowing sentences with multiple comma-separated clauses
- Run-on sentences are INTENTIONAL - they create your signature flow
- Parenthetical asides (like this) and dashes - for tangential thoughts
- Single-sentence paragraphs for emphasis
- NO bullet points or numbered lists - EVER - use flowing prose only

### PILLAR 3: SIGNATURE LANGUAGE
- Use "aswell" (not "as well")
- Use "thankyou" (not "thank you")
- British spellings: colour, honour, recognise, organisation
- Signature phrases: "and so the list goes on", "I have to say", "quite frankly"
- Openers: "When it comes to...", "So...", "I thought I would..."
- Transitions: "Having said that...", "Anyway, I digress...", "In my opinion..."

### PILLAR 4: CORE THEMES (ALWAYS WEAVE IN)
- Belonging and Recognition - ties create identity and community
- Tradition - schools, clubs, and companies carry legacy through accessories
- Craftsmanship - your expertise in printed vs woven ties
- South African pride - local manufacturing, supporting local

### PILLAR 5: SEO KEYWORDS (CRITICAL FOR SUCCESS)
Primary (always use): custom ties, custom scarves, corporate ties, school ties, club ties, matric ties, promotional ties, branded ties, company ties
Secondary: corporate socks, corporate jewellery, woven ties, printed ties
Pattern: Weave keywords naturally into flowing sentences - never stuff them artificially

### PILLAR 6: STRUCTURE
- **CRITICAL: Write 550-590 words** - NOT less, NOT more. Count your words!
- This is LONGER than typical blog posts - be expansive and thorough
- 8-12 paragraphs of flowing prose
- Jump straight into the topic - no generic intros
- End with emphatic statement or trailing thought
- NEVER be brief or punchy - be EXPANSIVE and conversational
- If your draft is under 550 words, ADD MORE DETAIL and EXPAND your points

### PILLAR 7: GRAMMAR & SPELLING CORRECTNESS (CRITICAL)
**NOTE:** The original Vinuchi blogs contain some grammar errors (they were written manually).
YOU MUST NOT REPLICATE THESE ERRORS. Match the STYLE but use CORRECT GRAMMAR.

GRAMMAR RULES:
- Use consistent first person throughout (don't switch between "I" and "we" mid-paragraph)
- Ensure subject-verb agreement (singular subjects take singular verbs)
- Use correct plural/singular forms ("tie" vs "ties" - match the noun to the context)
- Keep verb tenses consistent within paragraphs
- Proper pronoun agreement (don't switch between "you", "one", "they" randomly)

SPELLING:
- Use British spellings as specified (colour, honour) - these are INTENTIONAL
- But fix any actual spelling mistakes - the reference blogs may have typos
- "aswell" and "thankyou" are Vinuchi's signature spellings - KEEP these
- All other words should be spelled correctly

The goal: Sound like Vinuchi, but polished. Match the voice and style perfectly,
but write like a professional would - with correct grammar and consistent language.

################################################################################
#                         END OF GROUND TRUTH                                  #
################################################################################

"""
        # =================================================================
        # LEARNED STYLE PATTERNS (FROM 235+ SCRAPED BLOGS)
        # =================================================================
        prompt += f"""
## STYLE PATTERNS (Learned from {sa.get('total_blogs_analyzed', 235)} existing Vinuchi blogs)

These patterns reinforce the Ground Truth above:

### Tone Analysis
- {sa.get('tone_of_voice', {}).get('overall', 'Conversational, passionate, educational, and authoritative')}
- Formality: {sa.get('tone_of_voice', {}).get('formality_level', 'Informal/casual but knowledgeable')}

### Common Openers (use these)
{chr(10).join('- ' + opener for opener in sa.get('writing_patterns', {}).get('common_openers', ['When it comes to', 'So', 'I thought I would'])[:8])}

### Common Transitions (use these)
{chr(10).join('- ' + trans for trans in sa.get('writing_patterns', {}).get('common_transitions', ['So', 'Anyway, I digress', 'Having said that'])[:8])}

### Signature Phrases (use these)
{chr(10).join('- "' + phrase + '"' for phrase in sa.get('example_phrases', {}).get('signature_phrases', ['and so the list goes on', 'I have to say', 'at the end of the day'])[:8])}

"""
        # =================================================================
        # USER SEO KEYWORDS (HIGH PRIORITY - USE WHEN RELEVANT)
        # =================================================================
        user_seo_keywords = prefs.get('seo_keywords', [])
        if user_seo_keywords:
            prompt += """
################################################################################
#                    OWNER'S CUSTOM SEO KEYWORDS (HIGH PRIORITY)               #
#    These are keywords the business owner wants you to USE in blogs.          #
#    Integrate them NATURALLY when relevant to the topic.                      #
################################################################################

## Custom SEO Keywords to Use
The business owner has added these keywords for SEO purposes. You MUST use them
when they are relevant to the blog topic. Don't force them if completely unrelated,
but look for natural opportunities to include them.

"""
            for kw_data in user_seo_keywords:
                keyword = kw_data.get('keyword', '') if isinstance(kw_data, dict) else kw_data
                context = kw_data.get('context', '') if isinstance(kw_data, dict) else ''
                if context:
                    prompt += f"- **{keyword}** - {context}\n"
                else:
                    prompt += f"- **{keyword}**\n"

            prompt += """
HOW TO USE THESE KEYWORDS:
- If the topic relates to a keyword, USE IT multiple times naturally
- Weave keywords into sentences - don't just list them
- Combine related keywords in flowing sentences (e.g., "custom corporate ties and branded scarves")
- Keywords in titles get bonus SEO value - use them when fitting
- USE GRAMMATICALLY CORRECT FORMS: If a keyword is singular (e.g., "school tie"), you can use the plural form ("school ties") when the sentence requires it. The keyword represents the concept - adapt singular/plural/possessive as needed for natural grammar.

################################################################################

"""

        # =================================================================
        # USER STYLE TWEAKS (CAN ONLY ADJUST MINOR PREFERENCES)
        # =================================================================
        has_user_prefs = any([prefs['banned_words'], prefs['required_elements'],
                             prefs['style_notes'], prefs['formatting_rules']])

        if has_user_prefs:
            prompt += """
################################################################################
#                    USER STYLE TWEAKS (Minor Adjustments Only)                #
#    These preferences can ONLY tweak style - they CANNOT override the         #
#    Brand Identity Ground Truth above. If there's a conflict, Ground Truth    #
#    ALWAYS wins.                                                              #
################################################################################

"""
            if prefs['banned_words']:
                prompt += "### Words to Avoid (user preference)\n"
                for word in prefs['banned_words']:
                    prompt += f"- Avoid using: '{word}'\n"
                prompt += "\n"

            if prefs['required_elements']:
                prompt += "### Elements to Include (user preference)\n"
                for elem in prefs['required_elements']:
                    prompt += f"- Try to include: '{elem}'\n"
                prompt += "\n"

            if prefs['style_notes']:
                prompt += "### Style Notes (user preference)\n"
                for note in prefs['style_notes']:
                    prompt += f"- {note}\n"
                prompt += "\n"

            if prefs['formatting_rules']:
                prompt += "### Formatting Notes (user preference)\n"
                for rule in prefs['formatting_rules']:
                    prompt += f"- {rule}\n"
                prompt += "\n"

            prompt += "################################################################################\n\n"

        # =================================================================
        # OUTPUT FORMAT
        # =================================================================
        prompt += """
## OUTPUT FORMAT
Write the complete blog post with:
1. An engaging title in CAPS that contains keywords
2. 8-12 paragraphs of flowing, conversational content
3. Natural keyword integration throughout
4. A strong closing statement

REMEMBER: The Brand Identity Ground Truth is SACRED. User tweaks are suggestions only.
DO NOT include any metadata, just the blog content starting with the title.
"""

        return prompt

    def _build_user_prompt(self, topic: str, reference_blogs: list) -> str:
        """Build user prompt with topic and references - Brand Anchor enforced."""
        # Check for similar topics already written
        existing_topics = self.memory.get_all_blog_topics()
        existing_titles = self.memory.get_all_blog_titles()

        # Get user's custom SEO keywords
        prefs = self.memory.get_all_preferences()
        user_seo_keywords = prefs.get('seo_keywords', [])

        prompt = f"""################################################################################
#                    USER'S REQUESTED TOPIC (MUST FOLLOW THIS)                 #
################################################################################

Write a new blog post about: **{topic}**

IMPORTANT: This blog MUST be specifically about "{topic}".
Do NOT write about a different topic. The entire blog content should directly
address and explore this specific subject matter.

"""
        # Add SEO keywords reminder if user has added any
        if user_seo_keywords:
            keyword_list = [kw.get('keyword', '') if isinstance(kw, dict) else kw for kw in user_seo_keywords]
            prompt += f"""## SEO KEYWORDS TO USE IN THIS BLOG
The owner wants these keywords used when relevant. Look for natural ways to include:
{', '.join(keyword_list)}

"""
        # =================================================================
        # ORIGINAL BLOG SAMPLES (PRIMARY SOURCE OF TRUTH)
        # These come FIRST and take priority over any user feedback
        # =================================================================
        if reference_blogs:
            prompt += """################################################################################
#              ORIGINAL VINUCHI BLOG SAMPLES (PRIMARY SOURCE OF TRUTH)         #
#     Study these examples carefully. They ARE the authentic Vinuchi voice.    #
#     Match this tone EXACTLY. User preferences are secondary to this style.   #
################################################################################

"""
            for i, blog in enumerate(reference_blogs[:2], 1):
                excerpt = blog['content'][:700] + "..." if len(blog['content']) > 700 else blog['content']
                prompt += f"### AUTHENTIC EXAMPLE {i}: {blog['title']}\n{excerpt}\n\n"

            prompt += """CRITICAL: The examples above represent the REAL Vinuchi voice from 235+ published
blogs. Your output MUST sound like it was written by the same person. Any user
preferences in the system prompt are minor tweaks - they do NOT override this voice.

⚠️ IMPORTANT LENGTH NOTE: The example blogs above are ~450-500 words, but YOUR blog
MUST BE 550-590 WORDS. Match the STYLE and TONE exactly, but write LONGER and more
thoroughly. Add more detail, more examples, more exploration of the topic.

################################################################################

"""

        if existing_topics:
            prompt += f"\n## TOPICS ALREADY COVERED (create something NEW):\n"
            for t in existing_topics[-10:]:
                prompt += f"- {t}\n"

        # Build requirements with SEO keyword reminder
        seo_reminder = ""
        if user_seo_keywords:
            keyword_list = [kw.get('keyword', '') if isinstance(kw, dict) else kw for kw in user_seo_keywords[:5]]
            seo_reminder = f"\n- **USE OWNER'S SEO KEYWORDS** when relevant: {', '.join(keyword_list)}"

        prompt += f"""

## REQUIREMENTS:
- **TOPIC: Write specifically about "{topic}"** - this is the user's chosen topic, follow it closely
- **⚠️ MANDATORY WORD COUNT: 550-590 WORDS ⚠️** - This is NON-NEGOTIABLE. Count your words!
  - Under 550 words = TOO SHORT, expand your points
  - Over 590 words = TOO LONG, trim slightly
  - Aim for exactly 570 words
- Match the conversational, meandering style of the examples ABOVE
- Your voice must be INDISTINGUISHABLE from the original blog samples
- Include relevant SEO keywords naturally (custom ties, school ties, etc.){seo_reminder}
- Write in first person, sharing your expert opinions
- NO bullet points - use flowing prose only
- Make it engaging and passionate
- BE THOROUGH - this is a longer-form blog post, not a quick snippet

Write the complete blog now about "{topic}" (MUST BE 550-590 words - count them!), starting with the title in CAPS:"""

        return prompt

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Normalize texts
        t1 = ' '.join(text1.lower().split())
        t2 = ' '.join(text2.lower().split())
        return SequenceMatcher(None, t1, t2).ratio()

    def _review_blog(self, title: str, content: str) -> dict:
        """
        Review generated blog against existing database.
        Returns review result with pass/fail and issues.
        """
        issues = []
        warnings = []

        word_count = len(content.split())

        # 1. WORD COUNT CHECK (HARD LIMITS - MIN AND MAX)
        if word_count < MIN_WORDS:
            issues.append(f"WORD COUNT TOO LOW: {word_count} words (minimum {MIN_WORDS} required)")
        elif word_count > MAX_WORDS:
            issues.append(f"WORD COUNT EXCEEDED: {word_count} words (max {MAX_WORDS})")
        elif word_count > 590:
            warnings.append(f"Word count slightly high: {word_count} words (target: 550-590)")

        # NOTE: Title/content similarity checks REMOVED
        # User explicitly wants to allow similar/duplicate blogs for SEO purposes
        # The blogs are 100% for SEO, so duplicates and similar topics are allowed

        return {
            "passed": len(issues) == 0,
            "word_count": word_count,
            "issues": issues,
            "warnings": warnings
        }

    def generate(self, topic: str, save: bool = True, max_attempts: int = 3) -> dict:
        """
        Generate a new blog matching Vinuchi's style.

        Args:
            topic: What the blog should be about
            save: Whether to save to persistent memory
            max_attempts: Max regeneration attempts if review fails

        Returns:
            Dict with title, content, and metadata

        Raises:
            UsageLimitExceeded: If the usage limit has been reached
        """
        # CHECK USAGE LIMIT FIRST (Financial Kill Switch)
        allowed, remaining, limit_msg = check_limit()
        if not allowed:
            print(f"\n{'='*60}")
            print(f"USAGE LIMIT EXCEEDED")
            print(f"{'='*60}")
            print(f"   {limit_msg}")
            raise UsageLimitExceeded(limit_msg)

        print(f"\n{'='*60}")
        print(f"GENERATING BLOG: {topic}")
        print(f"Usage: {remaining} posts remaining in this window")
        print(f"{'='*60}")

        # Get reference blogs
        print("\n1. Finding style references...")
        reference_blogs = self._get_reference_blogs(topic)
        print(f"   Using {len(reference_blogs)} reference blogs")

        # Build prompts
        print("\n2. Building prompts with learned preferences...")
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(topic, reference_blogs)

        prefs = self.memory.get_all_preferences()
        print(f"   Banned words: {len(prefs['banned_words'])}")
        print(f"   Required elements: {len(prefs['required_elements'])}")
        print(f"   Style notes: {len(prefs['style_notes'])}")
        print(f"   Formatting rules: {len(prefs['formatting_rules'])}")

        # Generation loop with review
        for attempt in range(1, max_attempts + 1):
            print(f"\n3. Generating with Claude (attempt {attempt}/{max_attempts})...")

            # Adjust prompt if retrying due to word count issues
            current_user_prompt = user_prompt
            if attempt > 1 and hasattr(self, '_last_word_count'):
                if self._last_word_count < MIN_WORDS:
                    # Previous was too short - ask for more
                    current_user_prompt = user_prompt.replace(
                        "550-590 words",
                        f"STRICTLY 570-590 words - previous attempt was only {self._last_word_count} words, WRITE MORE"
                    )
                elif self._last_word_count > MAX_WORDS:
                    # Previous was too long - ask for less
                    current_user_prompt = user_prompt.replace(
                        "550-590 words",
                        f"STRICTLY 550-580 words - previous attempt was too long"
                    )

            try:
                # Adjust tokens based on previous attempt
                if attempt > 1 and hasattr(self, '_last_word_count') and self._last_word_count < MIN_WORDS:
                    max_tokens = 2500  # More tokens if previous was too short
                elif attempt > 1:
                    max_tokens = 1500  # Fewer tokens if previous was too long
                else:
                    max_tokens = 2000  # Default for first attempt

                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": current_user_prompt}]
                )
                generated = response.content[0].text

            except Exception as e:
                print(f"   ERROR: {e}")
                return None

            # Parse title and content
            lines = generated.strip().split('\n')
            title = lines[0].replace('#', '').strip()
            content = '\n'.join(lines[1:]).strip()

            # 4. REVIEW AGAINST DATABASE
            print(f"\n4. Reviewing blog against database...")
            review = self._review_blog(title, content)
            self._last_word_count = review['word_count']  # Store for retry logic
            print(f"   Word count: {review['word_count']} (min: {MIN_WORDS}, max: {MAX_WORDS})")

            if review['issues']:
                print("   REVIEW FAILED:")
                for issue in review['issues']:
                    print(f"     - {issue}")

                if attempt < max_attempts:
                    print(f"   Regenerating...")
                    continue
                else:
                    print(f"   Max attempts reached. Returning best effort.")
            else:
                print("   REVIEW PASSED!")

            if review['warnings']:
                print("   Warnings:")
                for warning in review['warnings']:
                    print(f"     - {warning}")

            # Review passed or max attempts reached
            break

        # 5. Validate against learned rules
        print("\n5. Validating against learned rules...")
        validation = self.memory.validate_content(generated)

        if not validation['valid']:
            print("   ISSUES FOUND:")
            for issue in validation['issues']:
                print(f"     - {issue}")
        else:
            print("   All rules passed!")

        # Merge review issues into validation
        validation['issues'].extend(review['issues'])
        validation['warnings'].extend(review['warnings'])
        validation['valid'] = validation['valid'] and review['passed']

        # Build result
        result = {
            "title": title,
            "content": content,
            "full_text": generated,
            "topic_requested": topic,
            "word_count": review['word_count'],
            "generated_at": datetime.now().isoformat(),
            "validation": validation,
            "references_used": [b['title'] for b in reference_blogs],
            "attempts": attempt
        }

        # Save to memory if valid
        if save and validation['valid']:
            print("\n6. Saving to persistent memory...")
            blog_id = self.memory.save_generated_blog(
                title=title,
                content=content,
                topic=topic,
                status="draft"
            )
            result["blog_id"] = blog_id
            print(f"   Saved as: {blog_id}")
        elif not validation['valid']:
            print("\n6. NOT SAVED - Review/validation failed")

        # RECORD USAGE (counts against limit regardless of validation)
        record_usage(topic)
        stats = get_usage_stats()
        result["usage"] = {
            "remaining": stats["remaining"],
            "limit": stats["limit"]
        }

        print(f"\n{'='*60}")
        print(f"GENERATION COMPLETE")
        print(f"Title: {title}")
        print(f"Words: {result['word_count']} (target: {MIN_WORDS}-590)")
        print(f"Valid: {validation['valid']}")
        print(f"Attempts: {attempt}")
        print(f"{'='*60}")

        return result

    def _try_simple_replacement(self, title: str, content: str, instruction: str) -> dict:
        """
        Try to handle simple word replacements directly without LLM.
        Returns None if the instruction is too complex.

        This is the PREFERRED method for spelling fixes, word swaps, etc.
        No LLM means no risk of changing the blog voice.
        """
        import re
        instruction_lower = instruction.lower().strip()

        # Patterns for simple replacements (expanded list):
        # "replace X with Y", "change X to Y", "use X instead of Y"
        # "colour to color", "colour -> color", "colour/color"
        patterns = [
            # Explicit replacement phrases
            (r"replace\s+['\"]?(\w+)['\"]?\s+with\s+['\"]?(\w+)['\"]?", False),
            (r"change\s+['\"]?(\w+)['\"]?\s+to\s+['\"]?(\w+)['\"]?", False),
            (r"use\s+['\"]?(\w+)['\"]?\s+instead\s+of\s+['\"]?(\w+)['\"]?", True),  # swap groups
            (r"swap\s+['\"]?(\w+)['\"]?\s+for\s+['\"]?(\w+)['\"]?", False),
            # Shorthand patterns: "colour to color", "colour -> color"
            (r"^['\"]?(\w+)['\"]?\s+to\s+['\"]?(\w+)['\"]?$", False),
            (r"^['\"]?(\w+)['\"]?\s*[-=]>\s*['\"]?(\w+)['\"]?$", False),
            (r"^['\"]?(\w+)['\"]?\s*/\s*['\"]?(\w+)['\"]?$", False),
            # "fix spelling: colour to color"
            (r"fix\s+(?:the\s+)?spelling[:\s]+['\"]?(\w+)['\"]?\s+to\s+['\"]?(\w+)['\"]?", False),
            (r"spelling[:\s]+['\"]?(\w+)['\"]?\s+to\s+['\"]?(\w+)['\"]?", False),
        ]

        for pattern, swap_groups in patterns:
            match = re.search(pattern, instruction_lower)
            if match:
                if swap_groups:
                    old_word = match.group(2)
                    new_word = match.group(1)
                else:
                    old_word = match.group(1)
                    new_word = match.group(2)

                # Preserve case of the original when replacing
                def case_preserving_replace(match_obj):
                    original = match_obj.group(0)
                    if original.isupper():
                        return new_word.upper()
                    elif original.istitle():
                        return new_word.title()
                    else:
                        return new_word.lower()

                # Do case-insensitive replacement with case preservation
                new_content = re.sub(
                    re.escape(old_word),
                    case_preserving_replace,
                    content,
                    flags=re.IGNORECASE
                )
                new_title = re.sub(
                    re.escape(old_word),
                    case_preserving_replace,
                    title,
                    flags=re.IGNORECASE
                )

                if new_content != content or new_title != title:
                    print(f"   Direct replacement: '{old_word}' -> '{new_word}'")
                    return {
                        "title": new_title,
                        "content": new_content,
                        "word_count": len(new_content.split()),
                        "title_changed": new_title != title,
                        "content_changed": new_content != content,
                        "tweak_instruction": instruction,
                        "method": "direct_replacement",
                        "success": True
                    }

        return None  # Could not handle with simple replacement

    def _calculate_change_ratio(self, original: str, modified: str) -> float:
        """
        Calculate what percentage of the text changed.
        Returns a float between 0 (identical) and 1 (completely different).
        """
        from difflib import SequenceMatcher
        return 1 - SequenceMatcher(None, original, modified).ratio()

    def tweak_blog(self, title: str, content: str, tweak_instruction: str) -> dict:
        """
        Make a SURGICAL edit to an existing blog based on user feedback.

        CRITICAL: This makes ONLY the specific change requested, keeping
        everything else EXACTLY the same. This is NOT a regeneration.

        The tweaker is for minor fixes like:
        - Spelling corrections (colour -> color)
        - Changing a specific word to a synonym
        - Rewriting a specific paragraph (not the whole blog)
        - Changing the heading

        Args:
            title: Current blog title
            content: Current blog content
            tweak_instruction: User's specific request (e.g., "replace 'alumni' with another word")

        Returns:
            Dict with modified title, content, and what was changed
        """
        print(f"\n{'='*60}")
        print(f"TWEAKING BLOG (Surgical Mode)")
        print(f"Instruction: {tweak_instruction}")
        print(f"{'='*60}")

        # Try simple word replacement first (most reliable - no LLM drift risk)
        simple_result = self._try_simple_replacement(title, content, tweak_instruction)
        if simple_result:
            print("   Using direct replacement (no LLM needed)")
            print(f"{'='*60}")
            return simple_result

        # Fall back to LLM for complex tweaks (e.g., "rewrite paragraph 3")
        print("   Using LLM for complex tweak (strict surgical mode)...")

        # EXTREMELY restrictive surgical prompt
        system_prompt = """You are a SURGICAL TEXT EDITOR operating in STRICT MODE.

## YOUR ONE AND ONLY JOB:
Make the EXACT change requested. Touch NOTHING else.

## ABSOLUTE RULES - VIOLATING THESE IS FAILURE:

1. PRESERVE EVERY WORD that isn't part of the requested change
2. PRESERVE the exact writing style, voice, and tone
3. PRESERVE all punctuation, capitalization, and formatting
4. PRESERVE all paragraph breaks exactly where they are
5. PRESERVE British spellings (colour, honour, recognise) unless told to change them
6. PRESERVE sentence structure - do not combine or split sentences
7. PRESERVE the signature phrases and expressions

## WHAT YOU ARE ALLOWED TO DO:
- If asked to change a WORD: change ONLY that word, keep everything else identical
- If asked to rewrite a PARAGRAPH: rewrite ONLY that specific paragraph, keep all other paragraphs word-for-word identical
- If asked to change the TITLE: change ONLY the title, keep content identical
- If asked to fix SPELLING: fix ONLY the specified spelling, keep everything else identical

## WHAT YOU ARE FORBIDDEN TO DO:
- Do NOT "improve" or "enhance" anything
- Do NOT fix grammar that wasn't mentioned
- Do NOT change spellings that weren't mentioned
- Do NOT restructure sentences
- Do NOT add or remove content
- Do NOT change the voice or tone
- Do NOT rewrite sections that weren't specifically mentioned

## OUTPUT:
Return ONLY the modified blog. Title in CAPS on first line, then content.
No explanations, no commentary, no metadata."""

        user_prompt = f"""=== ORIGINAL BLOG (preserve everything except the specific change) ===

{title.upper()}

{content}

=== END OF ORIGINAL BLOG ===

USER REQUEST: {tweak_instruction}

INSTRUCTIONS: Make ONLY this specific change. Everything else must remain WORD-FOR-WORD IDENTICAL to the original above.
If the user asks to rewrite a paragraph, only that paragraph changes - all other paragraphs stay exactly the same.
If the user asks to change a word, only that word changes - the rest of the sentence stays exactly the same.

Return the complete blog now (title in CAPS, then content):"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            modified = response.content[0].text.strip()

            # Parse title and content
            lines = modified.split('\n')
            new_title = lines[0].replace('#', '').replace('TITLE:', '').strip()
            new_content = '\n'.join(lines[1:]).strip()

            # Clean up any "CONTENT:" prefix if present
            if new_content.upper().startswith('CONTENT:'):
                new_content = new_content[8:].strip()

            # VALIDATION: Check if too much changed (guard against LLM drift)
            content_change_ratio = self._calculate_change_ratio(content, new_content)

            # Allow up to 15% change for paragraph rewrites, 5% for word changes
            is_paragraph_rewrite = any(x in tweak_instruction.lower() for x in
                ['paragraph', 'section', 'rewrite', 'redo'])
            max_allowed_change = 0.15 if is_paragraph_rewrite else 0.05

            title_changed = new_title.upper() != title.upper()
            content_changed = new_content != content

            print(f"   Title changed: {title_changed}")
            print(f"   Content changed: {content_changed}")
            print(f"   Content change ratio: {content_change_ratio:.1%}")
            print(f"   Max allowed: {max_allowed_change:.0%}")

            # If LLM changed too much, REJECT and warn user
            if content_change_ratio > max_allowed_change:
                print(f"   WARNING: LLM changed too much! Rejecting edit.")
                print(f"   The change exceeded the allowed threshold.")
                print(f"{'='*60}")
                return {
                    "title": title,
                    "content": content,
                    "word_count": len(content.split()),
                    "success": False,
                    "error": f"The edit changed {content_change_ratio:.0%} of the content, which exceeds the {max_allowed_change:.0%} limit for this type of edit. Please be more specific about exactly what to change, or try a simpler instruction like 'change word X to Y'."
                }

            print(f"   New word count: {len(new_content.split())}")
            print(f"{'='*60}")

            return {
                "title": new_title,
                "content": new_content,
                "word_count": len(new_content.split()),
                "title_changed": title_changed,
                "content_changed": content_changed,
                "tweak_instruction": tweak_instruction,
                "change_ratio": content_change_ratio,
                "method": "llm_surgical",
                "success": True
            }

        except Exception as e:
            print(f"   ERROR: {e}")
            return {
                "title": title,
                "content": content,
                "word_count": len(content.split()),
                "success": False,
                "error": str(e)
            }


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python generate_blog.py '<topic>'")
        print("\nExample:")
        print("  python generate_blog.py 'Why school ties build tradition and pride'")
        return

    topic = sys.argv[1]

    try:
        generator = VinuchiBlogGenerator()
        result = generator.generate(topic)

        if result:
            print("\n" + "=" * 60)
            print("GENERATED BLOG")
            print("=" * 60)
            print(result['full_text'])
            print("\n" + "=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
