#!/bin/bash
# Vinuchi Blog Writer Launcher
# Run this script to start the blog writer UI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=================================="
echo "  Vinuchi Blog Writer"
echo "=================================="
echo ""

# Check if style profile exists
if [ ! -f "$PROJECT_DIR/.tmp/vinuchi/style_profile.json" ]; then
    echo "⚠️  Style profile not found. Running analysis..."
    python3 "$SCRIPT_DIR/analyze_style.py"
fi

# Check for Anthropic API key
if ! grep -q "ANTHROPIC_API_KEY=sk-" "$PROJECT_DIR/.env" 2>/dev/null; then
    echo ""
    echo "⚠️  ANTHROPIC_API_KEY not set in .env"
    echo "   Add your API key to $PROJECT_DIR/.env"
    echo ""
fi

echo "Starting Blog Writer UI..."
echo "Open http://localhost:8501 in your browser"
echo ""

# Run Streamlit
cd "$SCRIPT_DIR"
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
