# Lead Scraper & Cold Email Sender

An AI-orchestrated system for scraping leads and managing cold email campaigns using a 3-layer architecture.

## Architecture

This system uses a 3-layer architecture that separates concerns for maximum reliability:

### Layer 1: Directives (`directives/`)
SOPs written in Markdown that define:
- Goals and objectives
- Required inputs
- Tools/scripts to use
- Expected outputs
- Edge cases and error handling

### Layer 2: Orchestration (AI Agent)
The AI agent reads directives, makes decisions, calls execution tools, handles errors, and continuously improves the system.

### Layer 3: Execution (`execution/`)
Deterministic Python scripts that:
- Handle API calls
- Process data
- Manage file operations
- Interact with databases
- Perform reliable, testable operations

## Directory Structure

```
.
├── directives/          # SOPs in Markdown
├── execution/           # Python scripts
├── .tmp/               # Temporary/intermediate files (gitignored)
├── .env                # Environment variables (gitignored)
├── credentials.json    # Google OAuth (gitignored)
├── token.json         # Google OAuth token (gitignored)
└── Claude.md          # Agent instructions
```

## Setup

1. **Copy environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Add your API keys to `.env`:**
   - Google API credentials
   - Apollo API key (for lead scraping)
   - Instantly API key (for email campaigns)
   - Any other service credentials

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google OAuth:**
   - Place your `credentials.json` in the root directory
   - First run will generate `token.json`

## Usage

The AI agent orchestrates the system by:
1. Reading directives from `directives/`
2. Executing scripts from `execution/`
3. Storing intermediate data in `.tmp/`
4. Delivering final outputs to cloud services (Google Sheets, Slides, etc.)

## Key Principles

- **Deliverables** go to cloud services (Google Sheets, Slides)
- **Intermediates** stay in `.tmp/` and can be regenerated
- **Self-annealing**: When errors occur, fix the script, update the directive, and the system gets stronger
- **Bias toward action**: Build and execute automatically unless there's risk or ambiguity

## Operating Guidelines

See [Claude.md](Claude.md) for complete agent instructions and operating principles.
