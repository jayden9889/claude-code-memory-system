# Vinuchi Blog Writer - Redeployment Guide

**Purpose:** Step-by-step instructions to set up this system from scratch on a new server.

**Estimated Time:** 30-45 minutes

> **MAINTENANCE NOTE:** This file MUST be updated whenever dependencies, setup steps,
> or environment variables change. Also update: README.md and PROMPT_LOG.txt.

---

## Prerequisites

You will need:
- [ ] Python 3.9 or higher
- [ ] A computer running macOS, Linux, or Windows
- [ ] An Anthropic API key (for Claude)
- [ ] The codebase files (from backup or git)

---

## Step 1: Get the Code

If you have a git repository:
```bash
git clone <your-repo-url>
cd "Lead scraper : cold email sender"
```

If you're restoring from backup, copy the entire folder to your new server.

---

## Step 2: Set Up Python Environment

### Option A: Using System Python (Simple)

```bash
# Install dependencies
pip install -r requirements.txt
```

### Option B: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies List (requirements.txt)

These are the key packages needed:
```
python-dotenv==1.0.0      # Load .env files
anthropic>=0.39.0         # Claude API
streamlit>=1.40.0         # Web UI framework
requests==2.31.0          # HTTP requests
beautifulsoup4==4.12.3    # Web scraping
```

---

## Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create the file
touch .env
```

Add these variables (replace with your actual values):

```env
# REQUIRED - Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx

# OPTIONAL - Only if using Supabase for cloud storage
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhxxxxxxxxxx
SUPABASE_ANON_KEY=eyJhxxxxxxxxxx

# OPTIONAL - Only if using other services
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
INSTANTLY_API_KEY=your-instantly-key
```

### How to Get an Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new key
5. Copy and paste into .env file

**IMPORTANT:** Never commit .env to git. It should be in .gitignore.

---

## Step 4: Set Up Data Directory

The system needs a `.tmp/vinuchi/` folder for data storage:

```bash
# Create the directory
mkdir -p .tmp/vinuchi
```

If restoring from backup, copy these files:
```
.tmp/vinuchi/
├── scraped_blogs.json         # Original Vinuchi blogs (CRITICAL)
├── deep_style_analysis.json   # Style patterns extracted
├── persistent_memory.json     # Rules and preferences
└── usage_tracking.json        # API usage (can be empty)
```

**If you don't have scraped_blogs.json**, you'll need to re-scrape:
```bash
cd execution/vinuchi
python scrape_all_blogs.py
python analyze_style.py
```

---

## Step 5: Run the Application

```bash
# Navigate to the vinuchi folder
cd execution/vinuchi

# Start Streamlit
streamlit run app.py
```

The app will start and display:
```
Local URL: http://localhost:8501
Network URL: http://your-ip:8501
```

Open http://localhost:8501 in your browser.

---

## Step 6: Verify Everything Works

1. **Check the UI loads** - You should see "Vinuchi Blog Writer" header
2. **Try generating a blog** - Enter any topic, click Generate
3. **Check SEO keywords section** - Should be visible in sidebar
4. **Check usage counter** - Should show "X/10 posts remaining"

If any step fails, check:
- Is ANTHROPIC_API_KEY set correctly in .env?
- Are all Python packages installed?
- Do the .tmp/vinuchi/*.json files exist?

---

## Step 7: Optional - Run as Background Service

### macOS (launchd)

Create `~/Library/LaunchAgents/com.vinuchi.blogwriter.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vinuchi.blogwriter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/streamlit</string>
        <string>run</string>
        <string>/path/to/execution/vinuchi/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.vinuchi.blogwriter.plist
```

### Linux (systemd)

Create `/etc/systemd/system/vinuchi-blog.service`:

```ini
[Unit]
Description=Vinuchi Blog Writer
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/execution/vinuchi
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/streamlit run app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vinuchi-blog
sudo systemctl start vinuchi-blog
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'anthropic'"
**Solution:** Run `pip install anthropic`

### Problem: "Error: ANTHROPIC_API_KEY not set"
**Solution:** Check your .env file exists and has the key

### Problem: "FileNotFoundError: .tmp/vinuchi/scraped_blogs.json"
**Solution:** Either restore from backup or re-scrape:
```bash
python scrape_all_blogs.py
python analyze_style.py
```

### Problem: "Usage limit exceeded"
**Solution:** Wait 12 hours or reset:
```bash
python usage_limiter.py reset
```

### Problem: App crashes on start
**Solution:** Kill any existing instances and restart:
```bash
pkill -f "streamlit run"
streamlit run app.py
```

### Problem: Changes not appearing after code edit
**Solution:** Streamlit should hot-reload, but if not:
```bash
# Press Ctrl+C to stop, then restart
streamlit run app.py
```

---

## Backup Strategy

### What to Back Up (CRITICAL)

1. **`.env`** - Your API keys
2. **`.tmp/vinuchi/scraped_blogs.json`** - Training data (235+ blogs)
3. **`.tmp/vinuchi/deep_style_analysis.json`** - Style patterns
4. **`.tmp/vinuchi/persistent_memory.json`** - User rules and preferences
5. **The entire `execution/vinuchi/` folder** - All code

### What Can Be Regenerated

- `usage_tracking.json` - Just tracks API calls
- Any `__pycache__` folders

### Backup Command

```bash
# Create dated backup
tar -czvf vinuchi-backup-$(date +%Y%m%d).tar.gz \
    .env \
    .tmp/vinuchi/ \
    execution/vinuchi/ \
    directives/vinuchi_blog_writer.md
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start the app | `streamlit run app.py` |
| Check usage | `python usage_limiter.py status` |
| Reset usage limit | `python usage_limiter.py reset` |
| Kill the app | `pkill -f "streamlit run"` |
| Re-scrape blogs | `python scrape_all_blogs.py` |
| Re-analyze style | `python analyze_style.py` |

---

## File Locations Quick Reference

| File | Purpose |
|------|---------|
| `execution/vinuchi/app.py` | Main UI application |
| `execution/vinuchi/generate_blog.py` | Blog generation logic |
| `execution/vinuchi/persistent_memory.py` | Data storage |
| `.tmp/vinuchi/scraped_blogs.json` | Training data |
| `.tmp/vinuchi/persistent_memory.json` | User preferences |
| `.env` | API keys |
| `directives/vinuchi_blog_writer.md` | System documentation |

---

## Support

If this guide doesn't solve your problem:

1. Check `README.md` for architecture overview
2. Check `PROMPT_LOG.txt` for all AI prompts
3. Read the code comments - they're detailed
4. The code is the documentation

Good luck!
