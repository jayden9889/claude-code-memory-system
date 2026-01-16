# Vinuchi Blog Writer - Technical Documentation

**Last Updated:** January 16, 2026
**Purpose:** AI-powered blog writer that replicates Vinuchi's exact writing style

> **MAINTENANCE NOTE:** This file MUST be updated whenever the system changes.
> Also update: REDEPLOY.md and PROMPT_LOG.txt. See directive for details.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables (see REDEPLOY.md for details)
cp .env.template .env  # Then edit with your keys

# 3. Run the app
cd execution/vinuchi
streamlit run app.py
```

App will be available at: http://localhost:8501

**Password Protection:** Set `APP_PASSWORD` in your `.env` file to require login. Leave empty to disable.

**Windows Compatibility:** This app runs identically on macOS, Linux, and Windows. See REDEPLOY.md for Windows-specific setup commands.

---

## Live Deployment

The app is currently live and accessible to the client:

| Item | Value |
|------|-------|
| **Live URL** | https://jayden9889-claude-code-memory-system-executionvinuchiapp-kbttv1.streamlit.app/ |
| **GitHub Repo** | https://github.com/jayden9889/claude-code-memory-system |
| **Hosting** | Streamlit Cloud (free tier) |
| **Auto-Deploy** | Yes - pushes to `main` trigger auto-deploy |

**To share with a client:** Just send them the Live URL above. They open it in any browser - no installation needed.

---

## Deployment Options

### Local Development
Run `streamlit run app.py` and access at localhost:8501.

### Streamlit Cloud (Current Setup)
Free hosting with auto-deploy from GitHub. See REDEPLOY.md for detailed setup instructions.

1. Code is pushed to GitHub repo
2. Repo is connected to share.streamlit.io
3. Secrets (ANTHROPIC_API_KEY, APP_PASSWORD) are configured in Streamlit Cloud settings
4. Client accesses the app via the public URL

---

## How the 3-Layer Architecture Works

This system uses a **3-layer architecture** to separate human intent from AI decision-making from deterministic code execution. This prevents errors from compounding.

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: DIRECTIVES (What to do)                          │
│  Location: /directives/                                     │
│  Purpose: SOPs written in Markdown - goals, inputs, outputs │
│  Example: directives/vinuchi_blog_writer.md                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: ORCHESTRATION (Decision-making)                   │
│  This is the AI (Claude). Reads directives, decides what    │
│  scripts to run, handles errors, updates directives.        │
│  YOU are the glue between intent and execution.             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: EXECUTION (Doing the work)                        │
│  Location: /execution/vinuchi/                              │
│  Purpose: Deterministic Python scripts that do the work     │
│  Examples: generate_blog.py, app.py, persistent_memory.py   │
└─────────────────────────────────────────────────────────────┘
```

### Why This Works

LLMs are probabilistic (90% accuracy per step). 5 steps = 59% success rate.

**Solution:** Push all complexity into deterministic Python code. The AI only makes routing decisions, while scripts do the actual work reliably.

---

## File Structure

```
/execution/vinuchi/
├── app.py                 # Streamlit UI - the main interface
├── generate_blog.py       # Core blog generation with Claude API
├── persistent_memory.py   # JSON-based memory for rules, blogs, preferences
├── usage_limiter.py       # Financial kill switch (10 posts/12 hours)
├── topic_generator.py     # Smart topic suggestions (curated + AI mix)
├── ai_topic_generator.py  # AI-powered fresh topic generation with Claude
├── scrape_all_blogs.py    # One-time: scrape vinuchi.co.za blogs
├── analyze_style.py       # One-time: extract style patterns
├── manage_preferences.py  # CLI for managing rules
└── README.md              # This file

/directives/
└── vinuchi_blog_writer.md # The master SOP for this system

/.tmp/vinuchi/
├── scraped_blogs.json       # 235+ original Vinuchi blogs
├── deep_style_analysis.json # Extracted style patterns
├── persistent_memory.json   # All learned rules and preferences
├── usage_tracking.json      # API usage tracking
├── ai_generated_topics.json # AI-generated trending topics (refreshed daily)
└── used_topics.json         # Topics that have been approved (permanently excluded)

/.env
└── API keys (NEVER commit this file)
```

---

## Key Components Explained

### 1. generate_blog.py - The Brain

This is the core blog generator. It:

1. **Loads style analysis** from 235+ scraped Vinuchi blogs
2. **Builds a system prompt** with Brand Anchor protection (immutable brand pillars)
3. **Adds user SEO keywords** and preferences as "minor tweaks"
4. **Calls Claude API** to generate the blog
5. **Reviews the output** for word count and duplicates
6. **Validates against rules** (banned words, required elements)

**Brand Anchor System:** Prevents AI drift by hard-coding 7 core brand pillars that can NEVER be overridden by user feedback:
- Authentic first-person voice
- South African identity
- Product expertise
- Conversational authority
- Natural SEO integration
- 550-590 word structure (minimum 550 words enforced)
- Grammar correctness (match style but use proper grammar - original blogs have some errors)

### 2. app.py - The Interface

Streamlit-based UI that provides:

- **Topic input** with quick suggestions
- **Blog preview** with validation warnings
- **Tweaker** for surgical edits (word replacements, paragraph rewrites)
- **SEO Keywords** management with delete confirmation (most important for rankings)
- **Rules management** (banned words, style notes)
- **Approved blogs** gallery with manual editing support
- **Clean UI** - Streamlit header toolbar (Stop, Deploy buttons) hidden via CSS

**Approved Blog Viewer:**
- Open any approved blog to view full content
- Copy button to copy formatted blog to clipboard (uses `st-copy-to-clipboard` package)
- Edit button to manually modify title and content
- Edit mode uses dark blue theme matching the blog view (not light/white)
- Edit mode shows word count validation with color indicators
- Cancel confirmation dialog prevents accidental loss of changes

**Sharing with Clients:**
- Simply share the Streamlit Cloud URL with your client
- They open it in any browser - no installation needed
- Password protection available (set APP_PASSWORD in Streamlit Cloud secrets)

### 3. persistent_memory.py - The Memory

Singleton pattern JSON storage that remembers:

- **User preferences** (banned words, SEO keywords, style notes)
- **Generated blogs** (drafts, approved, with duplicate detection)
- **Learning log** (audit trail of all changes)

All data persists in `/.tmp/vinuchi/persistent_memory.json`

### 4. usage_limiter.py - The Kill Switch

Financial protection:
- **10 posts per 12-hour window**
- Tracks usage in JSON
- Admin can reset via CLI: `python usage_limiter.py reset`

---

## Data Flow: Blog Generation

```
User enters topic
        │
        ▼
┌──────────────────┐
│ Check usage limit │ ─── BLOCKED if over limit
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ Find reference   │ ─── Gets 3 similar blogs from 235 scraped
│ blogs            │
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ Build prompts    │ ─── Brand Anchor + SEO Keywords + User Prefs
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ Call Claude API  │ ─── claude-sonnet-4-20250514
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ Review & Validate│ ─── Word count, rules, duplicates
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ Save to memory   │ ─── Draft status, awaiting approval
└──────────────────┘
        │
        ▼
User reviews, tweaks, approves
```

---

## The Tweaker System

For making surgical edits without regenerating:

1. **Simple replacements** (no AI needed):
   - "change colour to color"
   - "replace X with Y"
   - Direct regex, preserves case

2. **Complex tweaks** (uses Claude in strict mode):
   - "rewrite paragraph 3"
   - "make the intro shorter"
   - Validates change ratio (max 5% for words, 15% for paragraphs)
   - Rejects if AI changed too much

---

## SEO Keywords & Rules Management

The **most important feature** for rankings:

- Stored permanently in persistent_memory.json
- Injected into every blog generation prompt
- Used naturally (can adapt singular/plural)
- Managed via sidebar UI

**Deletion UX (same for SEO keywords and all rules):**
- All items displayed as colored clickable buttons with ✕
- Clicking a button triggers a confirmation dialog
- User must confirm "Yes, Remove" or cancel
- Colors: Gold (SEO), Red (banned words), Green (required), Blue (style), Purple (format)

---

## Topic Generator System

The Quick Topics feature helps users find relevant blog ideas:

### How It Works

**Two Sources of Topics:**
1. **AI-Generated Topics** (via `ai_topic_generator.py`)
   - Fresh topics generated daily using Claude
   - Based on corporate fashion trends, seasons, school calendar
   - Stored in `.tmp/vinuchi/ai_generated_topics.json`
   - 5 new topics added each day

2. **Curated Topics** (via `topic_generator.py`)
   - Hand-crafted topics organized by theme
   - Categories: school, belonging, tradition, history, manufacturing, branding, occasions, products, insights
   - Used as fallback if AI generation fails

**Topic Mix Strategy:**
- 2-3 AI-generated trending topics
- At least 1 school-related topic (schools are key customers)
- Remaining slots filled with curated topics from various themes

### School Topic Priority

Schools are a significant part of Vinuchi's customer base, so:
- Every quick topics batch includes at least one school-related topic
- School topics cover: matric ties, old boys ties, school traditions, uniforms, etc.

### Used Topics Tracking

When a blog is approved from a quick topic:
1. The exact topic is **permanently excluded** from future suggestions
2. The system generates a **related topic** with the same SEO keyword but different angle
   - Example: "materials of school ties" → "colours of school ties" → "logos on school ties"
3. Used topics are stored in `.tmp/vinuchi/used_topics.json`
4. System Reset clears used topics (all become available again)

### Quick Topics Behavior

- Topics **refresh on every app open** (not cached between sessions)
- Clicking a quick topic **populates the text box** (user can edit before generating)
- After clicking, that quick topic is **immediately replaced** with a fresh one
- Approved topics **never appear again** (until system reset)

---

## Reset System

Accessed via sidebar "Reset to Default":

**What it clears:**
- All generated blogs (drafts and approved)
- All user rules (banned words, style notes)
- All SEO keywords
- Learning log
- Usage limit (daily posts counter reset to 10)
- Used topics (all quick topics become available again)
- AI-generated topics pool

**What it keeps:**
- Scraped blogs (training data)
- Style analysis

---

## Troubleshooting

### "AttributeError: PersistentMemory object has no attribute..."
The app cached an old version. Kill and restart:
```bash
# macOS/Linux
pkill -f "streamlit run"
streamlit run app.py

# Windows - Use Task Manager to end Python processes, then restart
streamlit run app.py
```

### API calls not working
Check .env file has valid ANTHROPIC_API_KEY

### Usage limit reached
Either wait 12 hours or admin reset:
```bash
python usage_limiter.py reset
```

### Blogs too similar to each other
The similarity check was removed per user request (SEO allows duplicates). If you want to re-enable, uncomment the similarity checks in `_review_blog()`.

---

## Contact

If something breaks and you're reading this in 6 months:
1. Check REDEPLOY.md for fresh setup instructions
2. Check PROMPT_LOG.txt for all the prompts
3. The system self-documents - read the code comments

Built with the 3-layer architecture: Directives → Orchestration → Execution
