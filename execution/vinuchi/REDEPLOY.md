# Vinuchi Blog Writer - Redeployment Guide

**Purpose:** Step-by-step instructions to set up this system from scratch on a new server.

**Estimated Time:** 30-45 minutes

**Last Updated:** January 16, 2026

> **MAINTENANCE NOTE:** This file MUST be updated whenever dependencies, setup steps,
> or environment variables change. Also update: README.md and PROMPT_LOG.txt.

---

## Current Live Deployment

The app is currently live at:
- **URL:** https://jayden9889-claude-code-memory-system-executionvinuchiapp-kbttv1.streamlit.app/
- **GitHub Repo:** https://github.com/jayden9889/claude-code-memory-system
- **Main File Path:** `execution/vinuchi/app.py`
- **Hosting:** Streamlit Cloud (free tier)
- **Auto-Deploy:** Yes - pushes to `main` branch auto-deploy in ~1-2 minutes

### To Update the Live App
```bash
git add .
git commit -m "Your change description"
git push origin main
# Wait 1-2 minutes, then refresh the app URL
```

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
python-dotenv==1.0.0        # Load .env files
anthropic>=0.39.0           # Claude API
streamlit>=1.40.0           # Web UI framework
st-copy-to-clipboard>=0.1.0 # Clipboard copy functionality
requests==2.31.0            # HTTP requests
beautifulsoup4==4.12.3      # Web scraping
```

---

## Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# macOS/Linux
touch .env

# Windows (PowerShell)
New-Item .env -ItemType File

# Windows (Command Prompt)
type nul > .env
```

Add these variables (replace with your actual values):

```env
# REQUIRED - Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx

# PASSWORD PROTECTION (optional but recommended)
# Leave empty or remove to disable password login
APP_PASSWORD=your-secure-password

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
# macOS/Linux
mkdir -p .tmp/vinuchi

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path .tmp\vinuchi

# Windows (Command Prompt)
mkdir .tmp\vinuchi
```

If restoring from backup, copy these files:
```
.tmp/vinuchi/
├── scraped_blogs.json         # Original Vinuchi blogs (CRITICAL)
├── deep_style_analysis.json   # Style patterns extracted
├── persistent_memory.json     # Rules and preferences
├── usage_tracking.json        # API usage (can be empty)
├── ai_generated_topics.json   # AI-generated trending topics (optional - regenerates)
└── used_topics.json           # Used topics tracking (optional - regenerates)
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

1. **Check the UI loads** - You should see "Vinuchi Blog Writer" login screen
2. **Enter password** - If APP_PASSWORD is set, enter it to access the app
3. **Try generating a blog** - Enter any topic, click Generate
4. **Check SEO keywords section** - Should be visible in sidebar
5. **Check usage counter** - Should show "X/10 posts remaining"

If any step fails, check:
- Is ANTHROPIC_API_KEY set correctly in .env?
- Are all Python packages installed?
- Do the .tmp/vinuchi/*.json files exist?

---

## Streamlit Cloud Deployment (RECOMMENDED)

**This is the recommended way to deploy the app for remote users.**

Streamlit Cloud is a free hosting service that:
- Runs your app 24/7 on the internet
- Auto-deploys when you push changes to GitHub
- Handles all server infrastructure for you

### Prerequisites

1. A GitHub account (free)
2. Your code pushed to a GitHub repository
3. An Anthropic API key

### Step 1: Push to GitHub

The code is already hosted on GitHub:
- **Repo:** https://github.com/jayden9889/claude-code-memory-system

If setting up fresh, push your code to GitHub:

```bash
# Initialize git (if not done)
git init

# Add files (excluding sensitive data)
git add .

# Commit
git commit -m "Initial commit"

# Add remote (use the existing repo or create your own)
git remote add origin https://github.com/jayden9889/claude-code-memory-system.git

# Push
git push -u origin main
```

**IMPORTANT:** Make sure `.env` is in your `.gitignore` file! API keys should NEVER be in GitHub.

### Step 2: Connect to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set the main file path: `execution/vinuchi/app.py`
6. Click "Deploy"

### Step 3: Configure Secrets

After deploying, you need to add your API keys:

1. In Streamlit Cloud, click on your app
2. Click **Settings** (gear icon) → **Secrets**
3. Add your secrets in TOML format:

```toml
# REQUIRED
ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"

# PASSWORD PROTECTION (recommended)
APP_PASSWORD = "your-secure-password"
```

4. Click "Save"
5. The app will restart with the new secrets

### Step 4: Share the URL

Your app is now live! Share the URL with your client:
- URL format: `https://your-app-name.streamlit.app`

The client will see a login screen and need to enter the password you set.

### Updating the App

To push updates to your client's version:

1. Make changes in your code locally
2. Run these commands:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. Streamlit Cloud automatically redeploys within ~1-2 minutes
4. Your client sees the updates by refreshing their browser

### Important Notes

- **Free tier limits:** 1GB of memory, apps may sleep after 7 days of inactivity
- **Data persistence:** `.tmp/` files are temporary on Streamlit Cloud - they reset when the app restarts
- **For persistent data:** Use Supabase or another cloud database (see main README)
- **Custom domain:** Available on paid plans

---

## Step 7: Optional - Run as Background Service (Local)

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

### Windows (Task Scheduler)

1. Open **Task Scheduler** (search for it in Start menu)
2. Click **Create Basic Task**
3. Name: "Vinuchi Blog Writer"
4. Trigger: **When the computer starts**
5. Action: **Start a program**
6. Program: `C:\path\to\python.exe` (or `streamlit.exe` if in PATH)
7. Arguments: `-m streamlit run app.py`
8. Start in: `C:\path\to\execution\vinuchi`
9. Finish

Or create a simple batch file `start-vinuchi.bat`:
```batch
@echo off
cd /d "C:\path\to\execution\vinuchi"
streamlit run app.py
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
# macOS/Linux
pkill -f "streamlit run"
streamlit run app.py

# Windows (PowerShell)
Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"} | Stop-Process
streamlit run app.py

# Windows - Alternative: Use Task Manager to end Python/Streamlit processes
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
- `ai_generated_topics.json` - AI generates fresh topics daily
- `used_topics.json` - Tracks approved topics (cleared on reset anyway)
- Any `__pycache__` folders

### Backup Command

```bash
# macOS/Linux
tar -czvf vinuchi-backup-$(date +%Y%m%d).tar.gz \
    .env \
    .tmp/vinuchi/ \
    execution/vinuchi/ \
    directives/vinuchi_blog_writer.md

# Windows (PowerShell) - Windows 10+ has tar built-in
$date = Get-Date -Format "yyyyMMdd"
tar -czvf "vinuchi-backup-$date.tar.gz" .env .tmp\vinuchi\ execution\vinuchi\ directives\vinuchi_blog_writer.md

# Windows - Alternative: Just copy the folders to a backup location
# Right-click → Copy the .env, .tmp\vinuchi\, execution\vinuchi\ folders
```

---

## Quick Reference

| Task | macOS/Linux | Windows |
|------|-------------|---------|
| Start the app | `streamlit run app.py` | `streamlit run app.py` |
| Check usage | `python usage_limiter.py status` | `python usage_limiter.py status` |
| Reset usage limit | `python usage_limiter.py reset` | `python usage_limiter.py reset` |
| Kill the app | `pkill -f "streamlit run"` | Use Task Manager or `taskkill /IM python.exe /F` |
| Re-scrape blogs | `python scrape_all_blogs.py` | `python scrape_all_blogs.py` |
| Re-analyze style | `python analyze_style.py` | `python analyze_style.py` |

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
