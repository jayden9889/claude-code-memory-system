#!/usr/bin/env python3
"""
Vinuchi Blog Writer - Branded UI
A secure, easy-to-use interface for generating blog posts.

SECURITY ARCHITECTURE:
======================
This is a Streamlit application (server-side Python framework).
- ALL API calls (Anthropic, etc.) are made from the Python server process
- The browser receives only rendered HTML/CSS/JS - never API keys
- Secrets stored in .env (local) or st.secrets (Streamlit Cloud)
- The frontend (browser) NEVER makes direct calls to api.anthropic.com
- Password protection prevents unauthorized access

DEPLOYMENT:
===========
Local: Uses .env file for secrets
Streamlit Cloud: Uses st.secrets (configured in app settings)
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST (for local development)
load_dotenv()


def get_secret(key: str, default: str = None) -> str:
    """
    Get a secret from either Streamlit Cloud secrets or local .env file.
    Streamlit Cloud takes priority over .env for deployed apps.
    """
    # Try Streamlit Cloud secrets first (for deployed app)
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    # Fall back to environment variable (for local development)
    return os.getenv(key, default)


def check_password() -> bool:
    """
    Show a password login form and return True if the correct password is entered.
    Password is stored in APP_PASSWORD secret/env variable.
    """
    # Check if already authenticated this session
    if st.session_state.get("authenticated", False):
        return True

    # Get the password from secrets
    correct_password = get_secret("APP_PASSWORD")

    # If no password is set, skip authentication (for development)
    if not correct_password:
        return True

    # Show login form
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            border-radius: 10px;
            text-align: center;
        }
        .login-title { color: white; font-size: 1.8rem; margin-bottom: 1rem; }
        .login-subtitle { color: #a0aec0; font-size: 0.9rem; margin-bottom: 1.5rem; }
    </style>
    <div class="login-container">
        <div class="login-title">Vinuchi Blog Writer</div>
        <div class="login-subtitle">Please enter your password to continue</div>
    </div>
    """, unsafe_allow_html=True)

    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        password = st.text_input(
            "Password",
            type="password",
            key="password_input",
            placeholder="Enter password..."
        )

        if st.button("Login", use_container_width=True, type="primary"):
            if password == correct_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

        st.markdown("")
        st.caption("Contact your administrator if you've forgotten your password.")

    return False

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="Vinuchi Blog Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import after streamlit setup
from persistent_memory import get_memory

# Validate critical environment variables on startup
def _validate_environment():
    """Ensure required API keys are configured."""
    missing = []
    if not get_secret("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    return missing


# ============ PASSWORD PROTECTION (DISABLED) ============
# Password protection has been disabled - app is publicly accessible
# To re-enable, uncomment the lines below and set APP_PASSWORD in secrets
# if not check_password():
#     st.stop()

# Validate environment on startup
_missing_env = _validate_environment()
if _missing_env:
    st.error(f"Missing required environment variables: {', '.join(_missing_env)}")
    st.info("Please configure these in your .env file or Streamlit Cloud secrets")
    st.stop()

# Custom CSS
st.markdown("""
<style>
    /* Brand colors */
    .main-header {
        background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
    }
    .main-header h1 { color: white; margin: 0; font-size: 2rem; }
    .main-header p { color: #a0aec0; margin: 0.5rem 0 0 0; }

    /* Rule badges */
    .rule-badge {
        display: inline-block;
        background: #e53e3e;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    .rule-badge-green { background: #38a169; }
    .rule-badge-blue { background: #3182ce; }
    .rule-badge-purple { background: #805ad5; }
    .rule-badge-gold { background: #d69e2e; }

    /* Cross buttons - matching colors */
    .del-btn-red button { background: #e53e3e !important; color: white !important; border: none !important; }
    .del-btn-green button { background: #38a169 !important; color: white !important; border: none !important; }
    .del-btn-blue button { background: #3182ce !important; color: white !important; border: none !important; }
    .del-btn-purple button { background: #805ad5 !important; color: white !important; border: none !important; }

    /* Rule tag buttons - styled by data attribute */
    .rule-btn-red button[kind="secondary"] {
        background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.8rem !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
    }
    .rule-btn-red button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #9b2c2c 0%, #742a2a 100%) !important;
    }
    .rule-btn-green button[kind="secondary"] {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.8rem !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
    }
    .rule-btn-green button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #c53030 0%, #9b2c2c 100%) !important;
    }
    .rule-btn-blue button[kind="secondary"] {
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.8rem !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
    }
    .rule-btn-blue button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #c53030 0%, #9b2c2c 100%) !important;
    }
    .rule-btn-purple button[kind="secondary"] {
        background: linear-gradient(135deg, #805ad5 0%, #6b46c1 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.8rem !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
    }
    .rule-btn-purple button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #c53030 0%, #9b2c2c 100%) !important;
    }
    .rule-btn-gold button[kind="secondary"] {
        background: linear-gradient(135deg, #d69e2e 0%, #b7791f 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.8rem !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
    }
    .rule-btn-gold button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #c53030 0%, #9b2c2c 100%) !important;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hide Streamlit header toolbar only */
    [data-testid="stToolbar"] {display: none !important;}

    /* Hide sidebar collapse button - sidebar should always be visible */
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebarCollapseButton"] {display: none !important;}
    button[aria-label="Collapse sidebar"] {display: none !important;}
    button[aria-label="Expand sidebar"] {display: none !important;}

    /* Force sidebar to always be visible and expanded */
    [data-testid="stSidebar"] {
        transform: none !important;
        visibility: visible !important;
        width: 21rem !important;
        min-width: 21rem !important;
        margin-left: 0 !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: none !important;
        width: 21rem !important;
        min-width: 21rem !important;
        margin-left: 0 !important;
    }


    /* Hide "Press Enter to apply" hint on text inputs */
    .stTextInput div[data-testid="InputInstructions"] { display: none !important; }

    /* Change text area and input focus color from red to green */
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: #38a169 !important;
        box-shadow: 0 0 0 1px #38a169 !important;
    }
    div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="input"]:focus-within {
        border-color: #38a169 !important;
        box-shadow: 0 0 0 1px #38a169 !important;
    }

    /* Hide Streamlit's built-in copy/fullscreen buttons only */
    button[data-testid="StyledFullScreenButton"] { display: none !important; }

    /* ALL primary buttons - friendly green (not scary red) */
    button[kind="primary"],
    .stButton button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%) !important;
        border-color: #38a169 !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover,
    .stButton button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #2f855a 0%, #276749 100%) !important;
        border-color: #2f855a !important;
    }

    /* Generate button wrapper (legacy - now redundant but kept for specificity) */
    .generate-btn-green button[kind="primary"] {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%) !important;
        border-color: #38a169 !important;
    }

    /* Prevent button text from wrapping (except quick topics) */
    .stButton button {
        white-space: nowrap !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] > div {
        background: #1a202c;
    }

    /* Blog display area */
    .blog-content {
        background: #2d3748;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 0.5rem;
    }

    /* Approved blog cards */
    .blog-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border: 1px solid #4a5568;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .blog-card:hover {
        border-color: #63b3ed;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .blog-card-title {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    .blog-card-preview {
        color: #a0aec0;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    .blog-card-meta {
        color: #718096;
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }
    /* Style the Open buttons as card footers */
    .blog-card-btn button {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%) !important;
        border: 1px solid #4a5568 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        color: #a0aec0 !important;
        margin-top: -8px !important;
        transition: all 0.2s ease !important;
    }
    .blog-card-btn button:hover {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%) !important;
        border-color: #38a169 !important;
        color: white !important;
    }

    /* Tweaker section styling */
    .tweaker-section {
        background: #2d3748;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Align iframe (copy button) with Streamlit buttons */
    iframe {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Make all buttons have consistent styling */
    [data-testid="stButton"] button {
        padding: 11px 16px !important;
        border-radius: 8px !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)


def load_quick_topics():
    """Load smart, varied topics relevant to Vinuchi's industry."""
    from topic_generator import get_quick_topics
    return get_quick_topics(4)


def init_session_state():
    """Initialize session state variables."""
    if 'memory' not in st.session_state:
        st.session_state.memory = get_memory()
    if 'generated_blog' not in st.session_state:
        st.session_state.generated_blog = None
    if 'topic_input' not in st.session_state:
        st.session_state.topic_input = ""
    if 'quick_topics' not in st.session_state:
        st.session_state.quick_topics = load_quick_topics()
    if 'is_generating' not in st.session_state:
        st.session_state.is_generating = False
    if 'generation_topic' not in st.session_state:
        st.session_state.generation_topic = None
    if 'viewing_blog_id' not in st.session_state:
        st.session_state.viewing_blog_id = None
    if 'show_topic_warning' not in st.session_state:
        st.session_state.show_topic_warning = False
    if 'seo_to_delete' not in st.session_state:
        st.session_state.seo_to_delete = None
    if 'rule_to_delete' not in st.session_state:
        st.session_state.rule_to_delete = None  # Tuple: (rule_type, rule_value)
    if 'editing_blog' not in st.session_state:
        st.session_state.editing_blog = False
    if 'confirm_cancel_edit' not in st.session_state:
        st.session_state.confirm_cancel_edit = False
    if 'pending_quick_topic' not in st.session_state:
        st.session_state.pending_quick_topic = None
    if 'quick_topic_source' not in st.session_state:
        st.session_state.quick_topic_source = None  # Tracks if current blog came from a quick topic
    if 'copy_blog_trigger' not in st.session_state:
        st.session_state.copy_blog_trigger = False
    if 'clear_topic_next_render' not in st.session_state:
        st.session_state.clear_topic_next_render = False
    if 'sidebar_visible' not in st.session_state:
        st.session_state.sidebar_visible = True




def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>Vinuchi Blog Writer</h1>
        <p>AI-powered blog generation matching your exact style</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with rules and settings."""
    from usage_limiter import get_usage_stats

    memory = st.session_state.memory

    with st.sidebar:
        # Usage limit indicator (Financial Kill Switch)
        usage = get_usage_stats()
        remaining = usage['remaining']
        limit = usage['limit']

        if remaining <= 0:
            st.error(f"Daily Limit Reached: 0/{limit} posts")
        elif remaining <= 3:
            st.warning(f"Daily Posts Remaining: {remaining}/{limit}")
        else:
            st.success(f"Daily Posts Remaining: {remaining}/{limit}")

        # Stats
        stats = memory.get_learning_stats()
        # Count actual active rules (not historical learning log)
        active_rules_count = (
            stats['banned_words_count'] +
            stats['required_elements_count'] +
            stats['style_notes_count'] +
            stats['formatting_rules_count'] +
            len(memory.get_seo_keyword_list())
        )
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Blogs", stats['blogs_generated'])
        with col2:
            st.metric("Rules", active_rules_count)

        st.markdown("---")

        # ============ SEO KEYWORDS SECTION (MOST IMPORTANT) ============
        st.markdown("### 🎯 SEO Keywords")
        st.caption("Add keywords to use in all future blogs")

        seo_keyword = st.text_input(
            "New SEO Keyword",
            placeholder="e.g., custom corporate ties, school scarves...",
            key="seo_keyword_input",
            label_visibility="collapsed"
        )

        if st.button("+ Add SEO Keyword", key="add_seo_btn", use_container_width=True, type="primary"):
            if seo_keyword:
                memory.add_seo_keyword(seo_keyword)
                st.success(f"Added: {seo_keyword}")
                st.rerun()

        # Show current SEO keywords as styled tags with delete
        seo_keywords = memory.get_seo_keyword_list()

        # Check if we're showing a confirmation dialog
        if st.session_state.seo_to_delete:
            kw_to_delete = st.session_state.seo_to_delete
            st.warning(f"Remove **'{kw_to_delete}'** from SEO keywords?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✓ Yes, Remove", key="confirm_seo_yes", use_container_width=True, type="primary"):
                    memory.remove_seo_keyword(kw_to_delete)
                    st.session_state.seo_to_delete = None
                    st.rerun()
            with col_no:
                if st.button("✗ Cancel", key="confirm_seo_no", use_container_width=True):
                    st.session_state.seo_to_delete = None
                    st.rerun()
        elif seo_keywords:
            st.caption("Active Keywords:")
            st.caption("_Click to remove_")
            for idx, kw in enumerate(seo_keywords):
                display = kw[:20] + "..." if len(kw) > 20 else kw
                st.markdown('<div class="rule-btn-gold">', unsafe_allow_html=True)
                if st.button(f"🏷️ {display}", key=f"del_seo_{idx}", use_container_width=True, help=f"Click to remove: {kw}"):
                    st.session_state.seo_to_delete = kw
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.caption("No SEO keywords yet - add some!")

        st.markdown("---")

        # Add rules section
        st.markdown("### Add Rule")

        rule_type = st.selectbox(
            "Type",
            options=["banned_word", "required_element", "style_note", "formatting_rule"],
            format_func=lambda x: {
                "banned_word": "🚫 Ban Word",
                "required_element": "✓ Require",
                "style_note": "📝 Style",
                "formatting_rule": "📐 Format"
            }.get(x, x),
            label_visibility="collapsed"
        )

        rule_value = st.text_input(
            "Value",
            placeholder={
                "banned_word": "Word to never use...",
                "required_element": "Must include...",
                "style_note": "Style preference...",
                "formatting_rule": "Formatting rule..."
            }.get(rule_type, ""),
            label_visibility="collapsed"
        )

        if st.button("Save Rule", key="save_rule_btn", use_container_width=True, type="primary"):
            if rule_value:
                if rule_type == "banned_word":
                    memory.add_banned_word(rule_value, "")
                elif rule_type == "required_element":
                    memory.add_required_element(rule_value, "")
                elif rule_type == "style_note":
                    memory.add_style_note(rule_value)
                else:
                    memory.add_formatting_rule(rule_value)
                st.success("Saved!")
                st.rerun()

        st.markdown("---")

        # Show current rules
        st.markdown("### Active Rules")

        prefs = memory.get_all_preferences()

        # Handle rule deletion confirmation dialog
        if st.session_state.rule_to_delete:
            rule_type_del, rule_value_del = st.session_state.rule_to_delete
            st.warning(f"Remove **'{rule_value_del[:30]}{'...' if len(rule_value_del) > 30 else ''}'**?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✓ Yes, Remove", key="confirm_rule_yes", use_container_width=True, type="primary"):
                    if rule_type_del == "banned":
                        memory.remove_banned_word(rule_value_del)
                    elif rule_type_del == "required":
                        memory.remove_required_element(rule_value_del)
                    elif rule_type_del == "style":
                        memory.remove_style_note(rule_value_del)
                    elif rule_type_del == "format":
                        memory.remove_formatting_rule(rule_value_del)
                    st.session_state.rule_to_delete = None
                    st.rerun()
            with col_no:
                if st.button("✗ Cancel", key="confirm_rule_no", use_container_width=True):
                    st.session_state.rule_to_delete = None
                    st.rerun()
        else:
            # Show all rules as clickable buttons (same UX as SEO keywords)
            has_any_rules = any([prefs['banned_words'], prefs['required_elements'], prefs['style_notes'], prefs['formatting_rules']])

            if has_any_rules:
                st.caption("_Click to remove_")

            # Banned words (red)
            if prefs['banned_words']:
                st.caption("🚫 Banned:")
                for idx, word in enumerate(prefs['banned_words']):
                    display = word[:20] + "..." if len(word) > 20 else word
                    st.markdown('<div class="rule-btn-red">', unsafe_allow_html=True)
                    if st.button(f"🚫 {display}", key=f"del_ban_{idx}", use_container_width=True, help=f"Click to remove: {word}"):
                        st.session_state.rule_to_delete = ("banned", word)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # Required elements (green)
            if prefs['required_elements']:
                st.caption("✓ Required:")
                for idx, elem in enumerate(prefs['required_elements']):
                    display = elem[:20] + "..." if len(elem) > 20 else elem
                    st.markdown('<div class="rule-btn-green">', unsafe_allow_html=True)
                    if st.button(f"✓ {display}", key=f"del_req_{idx}", use_container_width=True, help=f"Click to remove: {elem}"):
                        st.session_state.rule_to_delete = ("required", elem)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # Style notes (blue)
            if prefs['style_notes']:
                st.caption("📝 Style:")
                for idx, note in enumerate(prefs['style_notes']):
                    display = note[:20] + "..." if len(note) > 20 else note
                    st.markdown('<div class="rule-btn-blue">', unsafe_allow_html=True)
                    if st.button(f"📝 {display}", key=f"del_style_{idx}", use_container_width=True, help=f"Click to remove: {note}"):
                        st.session_state.rule_to_delete = ("style", note)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # Formatting rules (purple)
            if prefs['formatting_rules']:
                st.caption("📐 Format:")
                for idx, rule in enumerate(prefs['formatting_rules']):
                    display = rule[:20] + "..." if len(rule) > 20 else rule
                    st.markdown('<div class="rule-btn-purple">', unsafe_allow_html=True)
                    if st.button(f"📐 {display}", key=f"del_fmt_{idx}", use_container_width=True, help=f"Click to remove: {rule}"):
                        st.session_state.rule_to_delete = ("format", rule)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            if not has_any_rules:
                st.caption("No rules yet")

        # Reset section
        st.markdown("---")
        with st.expander("Reset to Default", expanded=False):
            st.warning("This will delete ALL generated blogs and rules!")
            st.caption("Type CONFIRM below to enable the reset button")

            confirm_text = st.text_input(
                "Type CONFIRM to proceed",
                key="reset_confirm_input",
                label_visibility="collapsed",
                placeholder="Type CONFIRM here..."
            )

            reset_enabled = confirm_text.strip().upper() == "CONFIRM"

            if st.button(
                "🔄 RESET EVERYTHING",
                type="primary",
                use_container_width=True,
                disabled=not reset_enabled
            ):
                reset_system()
                st.success("System reset complete!")
                # Clear the confirm textbox
                if "reset_confirm_input" in st.session_state:
                    del st.session_state["reset_confirm_input"]
                st.rerun()


def reset_system():
    """Reset all memory - admin only."""
    from usage_limiter import admin_reset
    from topic_generator import clear_used_topics

    memory = st.session_state.memory

    # Reset preferences (clears all user-added rules and SEO keywords)
    memory.preferences = {
        "banned_words": [],
        "required_elements": [],
        "style_notes": [],
        "keywords_to_include": [],
        "topics_to_avoid": [],
        "formatting_rules": [],
        "custom_rules": [],
        "seo_keywords": []
    }

    # Reset generated blogs
    memory.generated_blogs = []
    memory.learning_log = []
    memory.content_hashes = []

    # Save
    memory._save_all()

    # Reset usage limit (daily posts counter)
    admin_reset()

    # Clear used topics (allows all quick topics to appear again)
    clear_used_topics()

    # Clear session
    st.session_state.generated_blog = None
    st.session_state.is_generating = False
    st.session_state.generation_topic = None
    st.session_state.quick_topic_source = None

    # Refresh quick topics with fresh set
    st.session_state.quick_topics = load_quick_topics()


def generate_blog(topic: str):
    """Generate a blog post with user-friendly error messages."""
    try:
        from generate_blog import VinuchiBlogGenerator, UsageLimitExceeded
        generator = VinuchiBlogGenerator()
        result = generator.generate(topic, save=True)
        return result
    except UsageLimitExceeded as e:
        # Daily limit reached - clear message
        st.warning(f"⏸️ Daily limit reached. Please try again later.")
        return None
    except ImportError:
        # Missing package
        st.error("⚠️ Setup issue: A required component is missing. Please contact support.")
        return None
    except ConnectionError:
        # Network issues
        st.error("🌐 Connection lost. Please check your internet and try again.")
        return None
    except TimeoutError:
        # Request took too long
        st.error("⏱️ Taking too long. The AI service might be busy. Please try again in a moment.")
        return None
    except Exception as e:
        # Generic error - translate common technical messages
        error_str = str(e).lower()
        if "api" in error_str or "key" in error_str or "authentication" in error_str:
            st.error("🔑 Connection to AI service failed. Please contact support.")
        elif "rate" in error_str or "limit" in error_str:
            st.error("⏸️ Too many requests. Please wait a moment and try again.")
        elif "timeout" in error_str or "timed out" in error_str:
            st.error("⏱️ Request took too long. Please try again.")
        elif "network" in error_str or "connection" in error_str or "internet" in error_str:
            st.error("🌐 Connection lost. Please check your internet and try again.")
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            st.error("🔧 The AI service is temporarily unavailable. Please try again in a few minutes.")
        else:
            st.error("❌ Something went wrong. Please try again or contact support if this keeps happening.")
        # Log the actual error for debugging (won't show to user)
        import traceback
        traceback.print_exc()
        return None


def do_generation(topic: str):
    """Handle blog generation with proper state management."""
    st.session_state.is_generating = True
    st.session_state.generation_topic = topic

    result = generate_blog(topic)

    st.session_state.is_generating = False
    st.session_state.generation_topic = None

    if result:
        st.session_state.generated_blog = result
        st.session_state.topic_input = ""
        return True
    return False


def render_main_content():
    """Render the main content area."""
    memory = st.session_state.memory

    # Safety: Reset is_generating if it's been stuck (no active spinner)
    # This prevents the UI from getting permanently disabled
    if st.session_state.is_generating and st.session_state.generation_topic is None:
        st.session_state.is_generating = False

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Generate Blog")

        # If currently generating, show locked UI and do the generation
        if st.session_state.is_generating and st.session_state.generation_topic:
            # Show topic being generated
            topic_display = st.session_state.generation_topic[:50]
            if len(st.session_state.generation_topic) > 50:
                topic_display += "..."

            # Loading state container
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
                        padding: 1.5rem; border-radius: 10px; border-left: 4px solid #38a169;
                        margin-bottom: 1rem;">
                <p style="color: #a0aec0; margin: 0 0 0.5rem 0; font-size: 0.9rem;">Creating your blog about:</p>
                <p style="color: #e2e8f0; margin: 0; font-weight: 600;">{topic_display}</p>
            </div>
            """, unsafe_allow_html=True)

            # Animated spinner with friendly message
            with st.spinner("✨ Writing your blog... This usually takes 10-20 seconds"):
                topic_to_generate = st.session_state.generation_topic
                success = do_generation(topic_to_generate)

            if success:
                st.rerun()
            # Error is already shown by generate_blog() function

        else:
            # Handle state changes BEFORE widgets render (Streamlit requirement)
            # 1. Clear topic if flagged (after successful generation)
            if st.session_state.get('clear_topic_next_render'):
                st.session_state.topic_text_area = ""
                st.session_state.clear_topic_next_render = False

            # 2. Set quick topic if pending
            if st.session_state.pending_quick_topic:
                st.session_state.topic_text_area = st.session_state.pending_quick_topic
                st.session_state.pending_quick_topic = None

            # Text area for topic input (no form - forms have state issues with quick topics)
            topic = st.text_area(
                "Topic",
                placeholder="What should the blog be about?",
                height=80,
                label_visibility="collapsed",
                key="topic_text_area"
            )

            # Generate button
            st.markdown('<div class="generate-btn-green">', unsafe_allow_html=True)
            generate_clicked = st.button(
                "✨ Generate Blog",
                use_container_width=True,
                type="primary"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            if generate_clicked:
                actual_topic = topic.strip()

                if actual_topic:
                    # Check usage limit FIRST before locking UI
                    from usage_limiter import check_limit
                    allowed, remaining, limit_msg = check_limit()

                    if not allowed:
                        # Show limit error but DON'T lock UI - user can keep trying
                        st.warning(f"🚫 {limit_msg}")
                    else:
                        # If user typed their own topic (not from quick topics), clear the source tracker
                        if not st.session_state.pending_quick_topic:
                            st.session_state.quick_topic_source = None

                        # Valid topic and under limit - store it and lock UI
                        st.session_state.generation_topic = actual_topic
                        st.session_state.is_generating = True
                        st.session_state.show_topic_warning = False
                        st.session_state.clear_topic_next_render = True  # Flag to clear on next render
                        st.rerun()  # Rerun to show locked state and start generation
                else:
                    st.session_state.show_topic_warning = True

            # Show warning if no topic entered
            if st.session_state.show_topic_warning:
                st.warning("Please enter a topic first.")

        # Quick Topics section
        st.markdown("##### Quick Topics")
        st.caption("Click to add to topic box")

        suggestions = st.session_state.quick_topics

        for i, sug in enumerate(suggestions):
            # Truncate display text for clean buttons (keep full topic for click)
            display_text = sug if len(sug) <= 50 else sug[:47] + "..."
            clicked = st.button(display_text, key=f"quick_{i}", use_container_width=True, disabled=st.session_state.is_generating)
            if clicked:
                # Set pending topic (will be applied before form renders on next rerun)
                st.session_state.pending_quick_topic = sug
                st.session_state.show_topic_warning = False

                # Track that this blog came from a quick topic (for permanent exclusion if approved)
                st.session_state.quick_topic_source = sug

                # Replace this topic with a fresh one (so user doesn't accidentally reuse it)
                from topic_generator import get_single_fresh_topic
                fresh_topic = get_single_fresh_topic(exclude_topics=st.session_state.quick_topics)
                st.session_state.quick_topics[i] = fresh_topic

                st.rerun()

        # Refresh quick topics button
        if st.button("🔄 New Topics", use_container_width=True):
            from topic_generator import refresh_topics
            st.session_state.quick_topics = refresh_topics(4)
            st.rerun()

    with col2:
        st.markdown("### Generated Blog")

        blog = st.session_state.generated_blog

        if blog:
            # Title (read-only)
            st.markdown(f"**Title:** {blog.get('title', 'Untitled')}")

            # Content display - editable, use dynamic key to prevent caching issues
            content_version = st.session_state.get('content_version', 0)
            content_key = f"blog_content_display_{content_version}"
            edited_content = st.text_area(
                "Content",
                value=blog.get('content', ''),
                height=350,
                key=content_key,
                label_visibility="collapsed"
            )

            # Calculate word count from ACTUAL content in text area (live count)
            current_word_count = len(edited_content.split()) if edited_content else 0

            # Word count indicator - shows live count as user types
            if current_word_count <= 500:
                st.success(f"✓ {current_word_count} words")
            elif current_word_count <= 515:
                st.warning(f"⚠ {current_word_count} words (slightly over)")
            else:
                st.error(f"✗ {current_word_count} words (over limit)")

            # Show any validation issues from generation
            validation = blog.get('validation', {})
            if validation.get('issues'):
                for issue in validation['issues']:
                    st.error(issue)
            if validation.get('warnings'):
                for warning in validation['warnings']:
                    st.warning(warning)

            # Track if user has made manual edits (different from original)
            if edited_content != blog.get('content', ''):
                # Update the blog in session state with user's edits
                st.session_state.generated_blog['content'] = edited_content
                st.session_state.generated_blog['word_count'] = current_word_count

            # ============ TWEAKER SECTION ============
            st.markdown("---")
            st.markdown("##### ✏️ Tweak This Blog Using AI")
            st.caption("Make a specific change without regenerating the whole blog")

            tweak_col1, tweak_col2 = st.columns([3, 1])

            with tweak_col1:
                tweak_instruction = st.text_input(
                    "Tweak instruction",
                    placeholder="e.g., 'Replace Alumni with Graduates' or 'Make intro shorter'",
                    key="tweak_input",
                    label_visibility="collapsed"
                )

            with tweak_col2:
                tweak_clicked = st.button("🔧 Apply", use_container_width=True, disabled=not tweak_instruction)

            if tweak_clicked and tweak_instruction:
                with st.spinner("Applying tweak..."):
                    from generate_blog import VinuchiBlogGenerator
                    generator = VinuchiBlogGenerator()
                    result = generator.tweak_blog(
                        title=blog.get('title', ''),
                        content=blog.get('content', ''),
                        tweak_instruction=tweak_instruction
                    )

                    if result.get('success'):
                        # Update the current blog in session state
                        st.session_state.generated_blog['title'] = result['title']
                        st.session_state.generated_blog['content'] = result['content']
                        st.session_state.generated_blog['word_count'] = result['word_count']
                        # Increment version to force text_area refresh
                        st.session_state.content_version = st.session_state.get('content_version', 0) + 1
                        st.success("✓ Tweak applied!")
                        st.rerun()
                    else:
                        st.error(f"Tweak failed: {result.get('error', 'Unknown error')}")

            st.markdown("---")

            # Action buttons
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if st.button("🔄 Regenerate", use_container_width=True):
                    original_topic = blog.get('topic_requested', '')
                    if original_topic:
                        with st.spinner("Regenerating..."):
                            if do_generation(original_topic):
                                st.rerun()

            with col_b:
                if st.button("✓ Approve", use_container_width=True, type="primary"):
                    blog_id = blog.get('blog_id')
                    if blog_id:
                        # Save any manual edits the user made before approving
                        memory.update_blog_content(
                            blog_id,
                            blog.get('title', ''),
                            blog.get('content', '')
                        )
                        memory.update_blog_status(blog_id, "approved")

                        # If this blog was generated from a quick topic, mark it as permanently used
                        # AND generate a related topic with the same SEO concept but different angle
                        if st.session_state.quick_topic_source:
                            from topic_generator import save_used_topic
                            used_topic = st.session_state.quick_topic_source
                            save_used_topic(used_topic)

                            # Generate a related topic (same SEO keyword, different angle)
                            # e.g., "materials of school ties" → "colours of school ties"
                            try:
                                from ai_topic_generator import generate_related_topic, mark_ai_topic_used
                                related_topic = generate_related_topic(used_topic)
                                if related_topic:
                                    # Add the related topic to the AI topics pool
                                    from ai_topic_generator import _load_ai_topics, _save_ai_topics
                                    data = _load_ai_topics()
                                    topics_list = data.get("topics", [])
                                    if related_topic not in topics_list:
                                        topics_list.append(related_topic)
                                        data["topics"] = topics_list[-30:]  # Keep recent 30
                                        _save_ai_topics(data)
                            except Exception as e:
                                # Silently fail - related topic generation is a nice-to-have
                                pass

                            st.session_state.quick_topic_source = None

                        st.session_state.generated_blog = None  # Clear current
                        st.balloons()
                        st.success("Blog approved! See it in Approved Blogs below.")
                        st.rerun()

            with col_c:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.generated_blog = None
                    st.rerun()

            # Show topic that was requested
            st.caption(f"Topic: {blog.get('topic_requested', 'N/A')}")

        else:
            # No blog generated yet
            st.markdown("""
            <div style="text-align: center; padding: 3rem 1rem; color: #718096; background: #2d3748; border-radius: 8px;">
                <p style="font-size: 3rem; margin-bottom: 1rem;">✍️</p>
                <p style="font-size: 1.1rem;">No blog generated yet</p>
                <p style="font-size: 0.9rem; color: #a0aec0;">Enter a topic or click a Quick Topic to start</p>
            </div>
            """, unsafe_allow_html=True)


def format_blog_for_copy(title: str, content: str) -> str:
    """
    Format blog exactly as it appears on vinuchi.co.za website.
    Title in CAPS, followed by content paragraphs.
    """
    # Ensure title is uppercase
    formatted_title = title.upper()

    # Clean up content - ensure proper paragraph spacing
    paragraphs = content.strip().split('\n')
    cleaned_paragraphs = [p.strip() for p in paragraphs if p.strip()]
    formatted_content = '\n\n'.join(cleaned_paragraphs)

    return f"{formatted_title}\n\n{formatted_content}"


def render_blog_viewer():
    """Render the full blog viewer when a blog is selected."""
    if not st.session_state.viewing_blog_id:
        return

    memory = st.session_state.memory
    blog = memory.get_blog_by_id(st.session_state.viewing_blog_id)

    if not blog:
        st.session_state.viewing_blog_id = None
        return

    st.markdown("---")

    # Back button (disabled during edit mode)
    if st.session_state.editing_blog:
        st.button("← Back to list", key="back_to_list", disabled=True)
    else:
        if st.button("← Back to list", key="back_to_list"):
            st.session_state.viewing_blog_id = None
            st.session_state.editing_blog = False
            st.session_state.confirm_cancel_edit = False
            st.rerun()

    # Word count and date inline
    created = blog.get('created_at', '')[:10]
    st.caption(f"📝 {blog.get('word_count', 0)} words • 📅 {created}")

    # Check if we're in edit mode
    if st.session_state.editing_blog:
        # Cancel confirmation dialog
        if st.session_state.confirm_cancel_edit:
            st.warning("Are you sure you want to cancel your changes?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, Cancel", key="confirm_cancel_yes", use_container_width=True, type="primary"):
                    st.session_state.editing_blog = False
                    st.session_state.confirm_cancel_edit = False
                    # Clear the widget keys
                    if 'edit_title_input' in st.session_state:
                        del st.session_state.edit_title_input
                    if 'edit_content_input' in st.session_state:
                        del st.session_state.edit_content_input
                    st.rerun()
            with col_no:
                if st.button("No, Keep Editing", key="confirm_cancel_no", use_container_width=True):
                    st.session_state.confirm_cancel_edit = False
                    st.rerun()
        else:
            # Edit mode UI
            st.markdown("#### ✏️ Edit Blog")

            # Editable title - key manages state, initialized when entering edit mode
            edit_title = st.text_input(
                "Title",
                key="edit_title_input"
            )

            # Editable content - key manages state, initialized when entering edit mode
            edit_content = st.text_area(
                "Content",
                height=400,
                key="edit_content_input"
            )

            # Word count for edited content
            new_word_count = len(edit_content.split()) if edit_content else 0
            if new_word_count <= 500:
                st.success(f"✓ {new_word_count} words")
            elif new_word_count <= 515:
                st.warning(f"⚠ {new_word_count} words (slightly over)")
            else:
                st.error(f"✗ {new_word_count} words (over limit)")

            # Confirm/Cancel buttons
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("✓ Save Changes", key="save_edit", use_container_width=True, type="primary"):
                    # Get values from the widget keys (Streamlit manages these)
                    final_title = st.session_state.get('edit_title_input', blog['title'])
                    final_content = st.session_state.get('edit_content_input', blog['content'])

                    # Save the changes
                    memory.update_blog_content(
                        st.session_state.viewing_blog_id,
                        final_title,
                        final_content
                    )
                    st.session_state.editing_blog = False
                    # Clear the widget keys
                    if 'edit_title_input' in st.session_state:
                        del st.session_state.edit_title_input
                    if 'edit_content_input' in st.session_state:
                        del st.session_state.edit_content_input
                    st.success("Changes saved!")
                    st.rerun()
            with col_cancel:
                if st.button("✗ Cancel", key="cancel_edit", use_container_width=True):
                    st.session_state.confirm_cancel_edit = True
                    st.rerun()
    else:
        # View mode - show blog content
        # Format paragraphs properly - split by double newlines, wrap in <p> tags
        paragraphs = [p.strip() for p in blog['content'].split('\n\n') if p.strip()]
        formatted_content = ''.join(f'<p style="margin: 0 0 1em 0;">{p}</p>' for p in paragraphs)

        st.markdown(f"""
        <div style="background: #1a202c; padding: 2rem; border-radius: 8px; border-left: 4px solid #38a169;">
            <h2 style="color: #e2e8f0; margin-top: 0; text-transform: uppercase;">{blog['title']}</h2>
            <div style="color: #e2e8f0; line-height: 1.6; margin-top: 1rem;">{formatted_content}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # Copy and Edit buttons side by side (both native Streamlit buttons)
        col_copy, col_edit = st.columns(2)

        with col_copy:
            if st.button("📋 Copy Blog", key="copy_blog_btn", use_container_width=True):
                st.session_state.copy_blog_trigger = True
                st.rerun()

        with col_edit:
            if st.button("✏️ Edit Blog", key="edit_blog_btn", use_container_width=True):
                st.session_state.editing_blog = True
                # Initialize the widget keys directly (Streamlit manages state via keys)
                st.session_state.edit_title_input = blog['title']
                st.session_state.edit_content_input = blog['content']
                st.rerun()

        # Handle copy action with hidden auto-executing script
        if st.session_state.get('copy_blog_trigger'):
            formatted_blog = format_blog_for_copy(blog['title'], blog['content'])
            escaped_blog = formatted_blog.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            import streamlit.components.v1 as components
            components.html(f"""
            <script>
                const text = `{escaped_blog}`;
                navigator.clipboard.writeText(text).then(() => {{
                    window.parent.postMessage({{type: 'clipboard', status: 'success'}}, '*');
                }}).catch(err => {{
                    window.parent.postMessage({{type: 'clipboard', status: 'error'}}, '*');
                }});
            </script>
            """, height=0)
            st.session_state.copy_blog_trigger = False
            st.success("✓ Copied to clipboard!")


def render_approved_blogs():
    """Render the approved blogs section with clickable cards."""
    memory = st.session_state.memory
    approved_blogs = memory.get_approved_blogs()

    st.markdown("---")
    st.markdown("### ✅ Approved Blogs")

    if not approved_blogs:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #718096; background: #2d3748; border-radius: 8px;">
            <p style="font-size: 1.5rem; margin-bottom: 0.5rem;">📚</p>
            <p>No approved blogs yet</p>
            <p style="font-size: 0.85rem; color: #a0aec0;">Approve a generated blog to see it here</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.caption(f"{len(approved_blogs)} approved blog{'s' if len(approved_blogs) != 1 else ''}")

    # Display blogs in a grid (2 columns)
    cols = st.columns(2)

    for idx, blog in enumerate(approved_blogs):
        col = cols[idx % 2]

        with col:
            # Create preview (first ~100 chars)
            content = blog.get('content', '')
            preview = content[:150]
            if len(content) > 150:
                last_period = preview.rfind('.')
                if last_period > 50:
                    preview = preview[:last_period + 1]
                else:
                    preview = preview[:147] + "..."

            created = blog.get('created_at', '')[:10]
            word_count = blog.get('word_count', 0)
            title_display = blog['title'][:55] + '...' if len(blog['title']) > 55 else blog['title']

            # Card header (visual only)
            st.markdown(f"""
            <div class="blog-card">
                <div style="color: #718096; font-size: 0.7rem; margin-bottom: 0.4rem;">{created}</div>
                <div class="blog-card-title">{title_display.upper()}</div>
                <div class="blog-card-preview">{preview}</div>
                <div class="blog-card-meta">{word_count} words</div>
            </div>
            """, unsafe_allow_html=True)

            # Visible, styled button to open the blog
            st.markdown('<div class="blog-card-btn">', unsafe_allow_html=True)
            if st.button("📖 Open Blog", key=f"view_{blog['id']}", use_container_width=True):
                st.session_state.viewing_blog_id = blog['id']
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main application."""
    init_session_state()
    render_header()
    render_sidebar()
    render_main_content()

    # Show blog viewer if a blog is selected, otherwise show approved blogs list
    if st.session_state.viewing_blog_id:
        render_blog_viewer()
    else:
        render_approved_blogs()


if __name__ == "__main__":
    main()
