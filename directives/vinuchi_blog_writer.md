# Vinuchi Blog Writer System

## Goal
AI-powered blog writer that learns from Vinuchi's existing content library, replicates their exact tone/style/keywords, and generates new SEO-optimized blogs while preventing duplicates.

## Inputs
- **Topic/prompt**: What the user wants to write about
- **Existing blogs**: Scraped from vinuchi.co.za (stored in Supabase)
- **Learned preferences**: Rules accumulated over time (banned words, required elements, style notes)

## Execution Tools
- `execution/vinuchi/scrape_all_blogs.py` - Scrapes all blogs from vinuchi.co.za
- `execution/vinuchi/analyze_style.py` - Extracts style patterns, keywords, tone markers
- `execution/vinuchi/store_embeddings.py` - Creates and stores blog embeddings in Supabase
- `execution/vinuchi/generate_blog.py` - Generates new blogs matching learned style
- `execution/vinuchi/check_duplicates.py` - Compares against existing content
- `execution/vinuchi/manage_preferences.py` - Handles learned rules and preferences

## Database Schema (Supabase)

### Table: `vinuchi_blogs`
- `id` (uuid, primary key)
- `url` (text, unique)
- `title` (text)
- `content` (text)
- `published_date` (date)
- `word_count` (int)
- `keywords_extracted` (text[])
- `embedding` (vector(1536))
- `scraped_at` (timestamp)

### Table: `vinuchi_style_profile`
- `id` (uuid, primary key)
- `category` (text) - e.g., "keywords", "tone", "structure", "phrases"
- `value` (jsonb) - the actual style data
- `updated_at` (timestamp)

### Table: `vinuchi_preferences`
- `id` (uuid, primary key)
- `rule_type` (text) - e.g., "banned_word", "required_element", "style_note"
- `rule_value` (text)
- `reason` (text) - why this rule exists
- `created_at` (timestamp)
- `active` (boolean)

### Table: `vinuchi_generated_blogs`
- `id` (uuid, primary key)
- `title` (text)
- `content` (text)
- `topic_requested` (text)
- `embedding` (vector(1536))
- `status` (text) - "draft", "approved", "posted"
- `created_at` (timestamp)

## Process Flow

### Initial Setup (One-time)
1. Run `scrape_all_blogs.py` to collect all existing Vinuchi blogs
2. Run `analyze_style.py` to extract style patterns and keywords
3. Run `store_embeddings.py` to create searchable vector store

### Blog Generation (Each use)
1. User provides topic/prompt
2. System loads style profile and preferences from Supabase
3. System finds similar existing blogs (for tone reference)
4. System generates new blog matching style
5. System checks for duplicates against all existing + generated content
6. If duplicate detected, regenerate with different angle
7. Present to user for approval/editing
8. Store in generated_blogs table

### Learning (Continuous)
- When user says "never use [word]" → add to preferences
- When user edits a blog → analyze what they changed, update style profile
- When user approves → reinforce current patterns

## Style Profile Structure

```json
{
  "keywords": {
    "primary": ["custom ties", "school ties", "corporate identity", "South Africa"],
    "secondary": ["quality", "tradition", "professional", "branding"],
    "frequency": {"custom ties": 0.85, "school ties": 0.72}
  },
  "tone": {
    "formality": "professional-warm",
    "perspective": "first-person-plural",
    "sentiment": "positive-authoritative"
  },
  "structure": {
    "avg_paragraphs": 6,
    "avg_words_per_paragraph": 80,
    "has_intro": true,
    "has_conclusion": true,
    "uses_questions": true
  },
  "phrases": {
    "common_openers": ["At Vinuchi", "When it comes to", "In the world of"],
    "common_closers": ["Contact us today", "Get in touch"],
    "signature_phrases": []
  }
}
```

## Outputs
- Generated blog in markdown format
- Similarity score showing how well it matches existing style
- List of keywords included
- Duplicate check result

## Edge Cases & Error Handling
- **Topic too similar to existing**: Suggest alternative angle or offer to "refresh" old content
- **Style drift detected**: Alert if generated content deviates significantly from profile
- **New keyword requested**: Add to style profile for future use

## Success Criteria
- Generated blogs score 85%+ similarity to existing content style
- Zero duplicate content (cosine similarity < 0.85 to any existing blog)
- All user preferences respected
- Keywords naturally integrated

## Brand Anchor (Model Drift Protection)

The Brand Anchor system prevents the AI from drifting away from the authentic Vinuchi voice over time. It uses a strict hierarchy:

### Hierarchy (Priority Order)
1. **Brand Identity Ground Truth** (IMMUTABLE) - Hard-coded core pillars that can NEVER be overridden
2. **Original Blog Samples** - Reference material from scraped vinuchi.co.za blogs
3. **User Feedback/Preferences** - Minor tweaks only, cannot override pillars 1 or 2

### The 7 Core Brand Pillars (Protected)

1. **AUTHENTIC VOICE** - First-person perspective, speaking as founder to reader
2. **SOUTH AFRICAN IDENTITY** - SA-specific language, local references, Rand currency
3. **PRODUCT EXPERTISE** - Deep knowledge of ties, scarves, corporate wear
4. **CONVERSATIONAL AUTHORITY** - Expert but approachable tone
5. **SEO NATURAL INTEGRATION** - Keywords woven naturally, never stuffed
6. **STRUCTURE** - 500 words max, proper formatting, compelling title
7. **GRAMMAR CORRECTNESS** - Match the STYLE but use CORRECT grammar. The original blogs have some errors (first-person inconsistency, plural/singular mistakes) - don't replicate these. Sound like Vinuchi but polished.

### How It Works

When generating a blog:
1. System loads Brand Identity Ground Truth (immutable, hard-coded)
2. System retrieves similar original blogs as tone reference
3. System applies user preferences as "minor style tweaks"
4. If conflict between user preference and Ground Truth → Ground Truth wins

### What User Feedback CAN Change
- Banned words (word choice adjustments)
- Minor style notes (phrasing preferences)
- Formatting details (list styles, etc.)

### What User Feedback CANNOT Change
- First-person voice (cannot switch to third-person)
- South African identity (cannot remove SA references)
- Product expertise framing
- Word count limits
- Core structural elements

This ensures the system can learn and improve while protecting the authentic Vinuchi brand voice.

## MANDATORY: Disaster Recovery Updates

**CRITICAL RULE:** Whenever ANY change is made to the Vinuchi Blog Writer system, you MUST update the disaster recovery documentation files:

1. **`execution/vinuchi/README.md`** - Update if architecture, components, or data flow changes
2. **`execution/vinuchi/REDEPLOY.md`** - Update if dependencies, setup steps, or environment variables change
3. **`execution/vinuchi/PROMPT_LOG.txt`** - Update if ANY system prompt, brand directive, or AI instruction changes

This is non-negotiable. The user has no dev background and needs these files to be accurate for future maintenance.

## Notes & Learnings
(Updated as system learns)
- 2026-01-14: Initial system creation
- 2026-01-15: Added Brand Anchor protection to prevent model drift
- 2026-01-15: Created disaster recovery docs (README.md, REDEPLOY.md, PROMPT_LOG.txt)
- 2026-01-15: Added mandatory rule to always update disaster recovery files on changes
- 2026-01-15: Added confirmation dialog for SEO keyword deletion (prevents accidental removal)
- 2026-01-15: Unified deletion UX - all rules now use same clickable button + confirmation dialog pattern as SEO keywords
- 2026-01-15: Reset system now also resets usage limit (daily posts counter)
- 2026-01-15: Added manual Edit feature for approved blogs (edit title/content, cancel confirmation dialog)
- 2026-01-15: Quick topics now populate text box instead of immediately generating (allows user to edit topic first)
- 2026-01-15: Added user-friendly error messages (plain English, no technical jargon)
- 2026-01-15: Added loading spinner with "Writing your blog..." message during generation
- 2026-01-15: Hidden Streamlit header toolbar (Stop, Deploy, accessibility buttons) for cleaner UI
- 2026-01-15: Fixed quick topics bug - removed form wrapper (clear_on_submit caused state conflicts), now uses direct text_area with deferred state clearing via `clear_topic_next_render` flag
- 2026-01-15: Added PILLAR 7 (Grammar Correctness) - AI now matches Vinuchi's style but uses correct grammar/spelling. Original blogs have some errors (first-person inconsistency, plural/singular) that the AI will NOT replicate
- 2026-01-15: Strengthened topic guidance in prompts - topic now appears prominently at start, in requirements, and at end of prompt to ensure AI follows user's requested topic
- 2026-01-15: Quick topics now auto-replace with fresh topic after being used (prevents duplicate generation)
- 2026-01-15: Fixed blog editing - manual edits now save correctly when approving drafts or editing approved blogs
- 2026-01-15: Added used topics tracking - quick topics now reset on every app open, approved topics are permanently excluded until system reset
- 2026-01-16: Fixed word count display - now shows live count from actual text area content, updates as user types
- 2026-01-16: Added school topic priority - every quick topics batch now includes at least one school-related topic (schools are key to Vinuchi brand)
- 2026-01-16: Added AI-powered topic generation - quick topics now mix AI-generated trending topics with curated topics. AI generates 5 fresh topics daily based on corporate fashion trends, seasons, and Vinuchi's brand
- 2026-01-16: Added related topic generation - when a quick topic is approved, the system generates a NEW topic with the same SEO keyword/concept but a different angle (e.g., "materials of school ties" → "colours of school ties" → "logos on school ties"). This keeps SEO momentum while avoiding duplicate content
- 2026-01-16: Verified Windows compatibility - all code uses pathlib.Path and UTF-8 encoding. Updated REDEPLOY.md with Windows-specific commands (PowerShell, Command Prompt equivalents)
- 2026-01-16: Added password protection - optional login screen controlled by APP_PASSWORD env variable. Works with both local .env and Streamlit Cloud st.secrets
- 2026-01-16: Added Streamlit Cloud support - app now works on Streamlit Cloud for free remote hosting. API keys can be set in st.secrets instead of .env. Added deployment guide to REDEPLOY.md
