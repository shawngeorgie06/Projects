"""
Writing Assistant - Web Application
A friendly AI-powered tool for improving your writing.
Free to use with Google Gemini AI.
"""

import streamlit as st
import re
import os
from google import genai

# Page configuration
st.set_page_config(
    page_title="Writing Assistant",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS — Editorial / Literary Magazine Aesthetic
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
    :root {
        --ink: #1a1a1a;
        --ink-light: #3d3529;
        --parchment: #faf8f4;
        --parchment-deep: #f3efe8;
        --warm-gray: #8a8070;
        --accent-rust: #b85c38;
        --accent-rust-light: #d4845a;
        --accent-forest: #4a6741;
        --accent-forest-light: #e8f0e5;
        --accent-gold: #c4973b;
        --accent-gold-light: #fdf6e8;
        --rule: #d5cfc5;
        --serif: 'Playfair Display', 'Georgia', serif;
        --body: 'Source Serif 4', 'Georgia', serif;
        --mono: 'JetBrains Mono', monospace;
    }

    /* === Global overrides === */
    .main {
        background: var(--parchment) !important;
    }
    .main .block-container {
        padding: 2.5rem 3rem 4rem 3rem;
        max-width: 820px;
    }
    .stApp {
        background: var(--parchment) !important;
    }
    .stApp > header {
        background: transparent !important;
    }

    /* Subtle paper grain overlay */
    .main::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.025'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
    }

    /* === Typography === */
    h1, h2, h3 {
        font-family: var(--serif) !important;
        color: var(--ink) !important;
    }
    p, li, label, .stMarkdown, span, div {
        font-family: var(--body) !important;
        color: var(--ink-light) !important;
    }

    /* === Metrics — editorial stat cards === */
    [data-testid="stMetricValue"] {
        font-family: var(--serif) !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
        letter-spacing: -0.02em;
    }
    [data-testid="stMetricLabel"] {
        font-family: var(--mono) !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--warm-gray) !important;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: center;
    }

    /* === Text area — manuscript feel === */
    .stTextArea textarea {
        border-radius: 2px !important;
        border: 1px solid var(--rule) !important;
        font-family: var(--body) !important;
        font-size: 1.05rem !important;
        line-height: 1.85 !important;
        background: #fff !important;
        color: var(--ink) !important;
        padding: 1.25rem 1.5rem !important;
        transition: border-color 0.2s ease;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent-rust) !important;
        box-shadow: 0 0 0 1px var(--accent-rust-light) !important;
    }
    .stTextArea textarea::placeholder {
        color: var(--warm-gray) !important;
        font-style: italic !important;
    }

    /* === Buttons === */
    .stButton > button {
        border-radius: 2px !important;
        padding: 0.7rem 2rem !important;
        font-family: var(--mono) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        background: var(--ink) !important;
        color: var(--parchment) !important;
        border: none !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        background: var(--accent-rust) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(184, 92, 56, 0.25) !important;
    }
    .stButton > button:active {
        transform: translateY(0px);
    }

    /* === Section headers — editorial rules === */
    .section-header {
        font-family: var(--serif) !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        color: var(--ink) !important;
        margin: 2.5rem 0 1rem 0;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid var(--ink);
        letter-spacing: -0.01em;
    }

    /* === Hide Streamlit chrome === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* === Issue cards — manuscript note style === */
    .issue-card {
        background: #fff;
        border-radius: 0;
        padding: 1.1rem 1.4rem;
        margin: 1.2rem 0 0.5rem 0;
        border: 1px solid var(--rule);
        border-left: 3px solid var(--accent-rust);
        position: relative;
    }
    .issue-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(to right, var(--accent-rust), transparent);
    }

    .category-badge {
        background: transparent;
        color: var(--accent-rust);
        padding: 0.15rem 0;
        border-radius: 0;
        font-family: var(--mono) !important;
        font-size: 0.65rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        display: inline-block;
        margin-bottom: 0.35rem;
    }

    .issue-title {
        font-family: var(--body) !important;
        font-weight: 600;
        color: var(--ink) !important;
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
        line-height: 1.4;
    }

    /* === Text comparison boxes === */
    .text-box {
        padding: 1rem 1.2rem;
        border-radius: 0;
        font-family: var(--body) !important;
        font-size: 0.92rem;
        line-height: 1.7;
        margin: 0.5rem 0;
        color: var(--ink) !important;
    }

    .original-box {
        background: var(--accent-gold-light);
        border-left: 3px solid var(--accent-gold);
        color: var(--ink-light) !important;
    }

    .revised-box {
        background: var(--accent-forest-light);
        border-left: 3px solid var(--accent-forest);
        color: var(--ink-light) !important;
    }

    .placeholder-box {
        background: var(--parchment-deep);
        border-left: 3px solid var(--rule);
        color: var(--warm-gray) !important;
        font-style: italic;
    }

    /* === Overall message box === */
    .message-box {
        background: #fff;
        padding: 1.2rem 1.5rem;
        border-radius: 0;
        border: 1px solid var(--rule);
        margin: 1.2rem 0;
        position: relative;
    }
    .message-box p {
        color: var(--ink) !important;
        font-family: var(--body) !important;
    }

    /* === AI feedback box === */
    .ai-feedback {
        background: #fff;
        border-radius: 0;
        padding: 1.5rem 1.75rem;
        border: 1px solid var(--rule);
        line-height: 1.8;
        color: var(--ink-light) !important;
        font-family: var(--body) !important;
        font-size: 0.95rem;
        position: relative;
    }
    .ai-feedback::before {
        content: '';
        position: absolute;
        top: -1px;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(to right, var(--accent-rust), var(--accent-gold), transparent);
    }

    /* === Sidebar === */
    [data-testid="stSidebar"] {
        background: var(--parchment-deep) !important;
        border-right: 1px solid var(--rule) !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--ink-light) !important;
    }

    /* === Toggle === */
    .stToggle label span {
        font-family: var(--body) !important;
        color: var(--ink-light) !important;
    }

    /* === Radio buttons === */
    .stRadio label {
        font-family: var(--body) !important;
        color: var(--ink-light) !important;
    }

    /* === Dividers === */
    hr {
        border: none !important;
        border-top: 1px solid var(--rule) !important;
        margin: 1.5rem 0 !important;
    }

    /* === Scrollbar styling === */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--parchment-deep);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--rule);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--warm-gray);
    }

    /* === Score cards container === */
    .score-card {
        text-align: center;
        padding: 1rem 0.5rem;
        border: 1px solid var(--rule);
        background: #fff;
        position: relative;
    }
    .score-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 40%;
        height: 2px;
        background: var(--accent-rust);
    }
    .score-val {
        font-family: var(--serif);
        font-size: 2rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.2;
    }
    .score-label {
        font-family: var(--mono);
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--warm-gray);
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Gemini
def get_client():
    """Get configured Gemini client."""
    api_key = os.environ.get("GOOGLE_API_KEY") or st.session_state.get("api_key", "")
    if api_key:
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            st.error(f"API Error: {e}")
            return None
    return None


def test_api_connection():
    """Test if API key works."""
    client = get_client()
    if client:
        try:
            # List models to verify API key works
            models = list(client.models.list())
            return len(models) > 0
        except Exception as e:
            st.error(f"Test failed: {e}")
            return False
    return False


def get_available_model(client):
    """Find an available model for text generation."""
    try:
        for model in client.models.list():
            model_name = model.name if hasattr(model, 'name') else str(model)
            # Look for gemini models that support generation
            if 'gemini' in model_name.lower() and 'flash' in model_name.lower():
                return model_name.replace('models/', '')
        # Fallback to any gemini model
        for model in client.models.list():
            model_name = model.name if hasattr(model, 'name') else str(model)
            if 'gemini' in model_name.lower():
                return model_name.replace('models/', '')
    except:
        pass
    return "gemini-1.5-flash-latest"  # Default fallback


def get_ai_suggestion(issue_type: str, original: str) -> tuple[str, str]:
    """Get AI-powered suggestion for a specific issue. Returns (suggestion, error)."""
    client = get_client()
    if not client:
        return None, "No API key configured"

    prompts = {
        "passive_voice": f"Rewrite this sentence in active voice. Return ONLY the rewritten sentence:\n\n{original}",
        "long_sentence": f"Break this into 2-3 shorter, clearer sentences. Return ONLY the rewritten text:\n\n{original}",
        "wordy": f"Make this more concise. Return ONLY the rewritten sentence:\n\n{original}",
        "complex_words": f"Simplify using everyday words. Return ONLY the rewritten sentence:\n\n{original}",
        "weak_words": f"Remove filler words and strengthen this. Return ONLY the rewritten sentence:\n\n{original}",
        "hedging": f"Make this more confident and direct. Return ONLY the rewritten sentence:\n\n{original}",
        "general": f"Improve clarity and impact. Return ONLY the rewritten sentence:\n\n{original}",
    }

    prompt = prompts.get(issue_type, prompts["general"])

    try:
        model_name = get_available_model(client)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text.strip(), None
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return None, "Rate limit - wait 15 seconds"
        return None, f"AI error: {error_msg[:100]}"


def get_full_analysis(text: str) -> tuple[str, str]:
    """Get comprehensive AI analysis. Returns (analysis, error)."""
    client = get_client()
    if not client:
        return None, "No API key configured"

    prompt = f"""You are a helpful writing coach. Analyze this text and provide friendly, actionable feedback.

For each issue you find:
1. Quote the problematic text
2. Explain briefly why it could be improved
3. Provide a specific rewritten version

Focus on: clarity, conciseness, tone, and impact. Be encouraging!

TEXT:
{text}

Provide your feedback in a clear, organized format."""

    try:
        model_name = get_available_model(client)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text.strip(), None
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return None, "Rate limit exceeded. Please wait 15-30 seconds and try again."
        return None, f"Error: {error_msg}"


# Helper functions
def get_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def get_words(text: str) -> list[str]:
    return re.findall(r'\b[a-zA-Z]+\b', text.lower())


def get_overall_message(score: int) -> tuple[str, str]:
    if score >= 8:
        return "🌟", "Excellent work! Your writing is clear and polished."
    elif score >= 6:
        return "👍", "Good foundation! A few tweaks will make it even better."
    elif score >= 4:
        return "💪", "You're on the right track! Check the suggestions below."
    else:
        return "🌱", "Let's improve this together! See the suggestions below."


# Analysis patterns
WORDY_PHRASES = {
    'in order to': 'to', 'due to the fact that': 'because',
    'at this point in time': 'now', 'in the event that': 'if',
    'for the purpose of': 'to', 'at the present time': 'now',
    'in the near future': 'soon', 'has the ability to': 'can',
    'is able to': 'can', 'a large number of': 'many',
    'the majority of': 'most', 'in close proximity to': 'near',
    'take into consideration': 'consider', 'make a decision': 'decide',
}

COMPLEX_WORDS = {
    'utilize': 'use', 'implement': 'start', 'facilitate': 'help',
    'leverage': 'use', 'optimize': 'improve', 'methodology': 'method',
    'functionality': 'feature', 'subsequently': 'then',
    'approximately': 'about', 'commence': 'begin', 'terminate': 'end',
    'endeavor': 'try', 'sufficient': 'enough', 'numerous': 'many',
}

WEAK_WORDS = ['very', 'really', 'quite', 'rather', 'somewhat',
              'basically', 'actually', 'literally', 'just']

HEDGING_WORDS = ['maybe', 'perhaps', 'possibly', 'might', 'could be',
                 'seems like', 'sort of', 'kind of', 'I think', 'I believe']


def analyze_text(text: str) -> dict:
    """Analyze text for issues."""
    sentences = get_sentences(text)
    words = get_words(text)
    issues = []

    # Passive voice
    for sentence in sentences:
        if re.search(r'\b(is|are|was|were|been|being)\s+\w+ed\b', sentence, re.IGNORECASE):
            issues.append({
                'type': 'passive_voice',
                'category': 'Clarity',
                'issue': 'Passive voice detected',
                'original': sentence,
            })
            if len(issues) >= 2:
                break

    # Long sentences
    for sentence in sentences:
        word_count = len(get_words(sentence))
        if word_count > 30:
            issues.append({
                'type': 'long_sentence',
                'category': 'Clarity',
                'issue': f'Long sentence ({word_count} words)',
                'original': sentence,
            })

    # Wordy phrases
    for phrase, replacement in WORDY_PHRASES.items():
        for sentence in sentences:
            if phrase.lower() in sentence.lower():
                issues.append({
                    'type': 'wordy',
                    'category': 'Conciseness',
                    'issue': f'Wordy: "{phrase}" → "{replacement}"',
                    'original': sentence,
                    'fallback': re.sub(re.escape(phrase), replacement, sentence, flags=re.IGNORECASE)
                })
                break

    # Complex words
    found_complex = set()
    for sentence in sentences:
        for word, simple in COMPLEX_WORDS.items():
            if word in sentence.lower() and word not in found_complex:
                issues.append({
                    'type': 'complex_words',
                    'category': 'Style',
                    'issue': f'Complex: "{word}" → "{simple}"',
                    'original': sentence,
                    'fallback': re.sub(r'\b' + word + r'\b', simple, sentence, flags=re.IGNORECASE)
                })
                found_complex.add(word)
                break

    # Weak words
    weak_found = [w for w in words if w in WEAK_WORDS]
    if len(weak_found) > 2:
        for sentence in sentences:
            if any(w in sentence.lower() for w in WEAK_WORDS):
                issues.append({
                    'type': 'weak_words',
                    'category': 'Style',
                    'issue': 'Contains filler words',
                    'original': sentence,
                })
                break

    # Hedging
    for hedge in HEDGING_WORDS:
        for sentence in sentences:
            if hedge.lower() in sentence.lower():
                issues.append({
                    'type': 'hedging',
                    'category': 'Tone',
                    'issue': f'Hedging: "{hedge}"',
                    'original': sentence,
                })
                break
        if any(i['type'] == 'hedging' for i in issues):
            break

    # Calculate scores
    clarity_issues = len([i for i in issues if i['category'] == 'Clarity'])
    style_issues = len([i for i in issues if i['category'] == 'Style'])
    conciseness_issues = len([i for i in issues if i['category'] == 'Conciseness'])
    tone_issues = len([i for i in issues if i['category'] == 'Tone'])

    scores = {
        'clarity': max(5, 10 - clarity_issues * 2),
        'style': max(5, 10 - style_issues * 2),
        'conciseness': max(5, 10 - conciseness_issues * 2),
        'tone': max(5, 10 - tone_issues * 2),
    }
    scores['overall'] = round(sum(scores.values()) / 4)

    return {
        'issues': issues[:8],
        'scores': scores,
        'stats': {
            'words': len(words),
            'sentences': len(sentences),
            'avg_length': round(len(words) / max(len(sentences), 1), 1)
        }
    }


# ============== MAIN APP ==============

# Header
st.markdown("""
<div style="text-align: center; padding: 3rem 0 1.5rem 0;">
    <p style="font-family: var(--mono); font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.25em; color: var(--accent-rust); margin-bottom: 0.75rem;">AI-Powered</p>
    <h1 style="font-family: var(--serif); font-size: 3.2rem; margin-bottom: 0.4rem; color: var(--ink); font-weight: 700; letter-spacing: -0.02em; line-height: 1.1;">Writing<br>Assistant</h1>
    <div style="width: 50px; height: 2px; background: var(--ink); margin: 1rem auto;"></div>
    <p style="font-family: var(--body); font-size: 1rem; color: var(--warm-gray); font-style: italic;">Refine your prose with intelligent suggestions</p>
</div>
""", unsafe_allow_html=True)

# API Key in sidebar
with st.sidebar:
    st.markdown("### Settings")
    st.markdown("---")

    # Initialize session state
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""

    api_key_input = st.text_input(
        "Google API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="AIza...",
        help="Get a free key from Google AI Studio"
    )

    if api_key_input:
        st.session_state.api_key = api_key_input
        # Test the connection
        if st.button("Test API Key"):
            with st.spinner("Testing..."):
                if test_api_connection():
                    st.success("✅ API key works!")
                else:
                    st.error("❌ Invalid API key")

    if st.session_state.api_key:
        st.caption("✓ API key saved")

    st.markdown("---")
    st.markdown("""
    **Get your FREE API key:**
    1. Go to [aistudio.google.com](https://aistudio.google.com/apikey)
    2. Click "Create API Key"
    3. Copy and paste it here

    *Free tier: 15 requests/min*
    """)

# Check API availability
has_api = bool(os.environ.get("GOOGLE_API_KEY") or st.session_state.get("api_key"))

st.markdown("---")

# Input section
st.markdown('<p class="section-header">Your Text</p>', unsafe_allow_html=True)

input_method = st.radio(
    "Choose input:",
    ["Paste text", "Upload file"],
    horizontal=True,
    label_visibility="collapsed"
)

text = ""

if "Paste" in input_method:
    text = st.text_area(
        "Your text",
        height=220,
        placeholder="Begin typing or paste your text here...\n\nA few sentences will yield the richest feedback.",
        label_visibility="collapsed"
    )
else:
    uploaded = st.file_uploader("Upload", type=['txt', 'md'], label_visibility="collapsed")
    if uploaded:
        text = uploaded.read().decode('utf-8')
        st.info(f"Loaded {len(text.split())} words")

# Options row
st.markdown("")
col1, col2 = st.columns([1, 3])

with col1:
    use_ai = st.toggle(
        "AI Suggestions",
        value=has_api,
        disabled=not has_api,
        help="Enable AI-powered rewrites"
    )

with col2:
    if not has_api:
        st.caption("Add your free Google API key in the sidebar to enable AI suggestions")

# Analyze button
st.markdown("")
if st.button("ANALYZE MY WRITING", type="primary", use_container_width=True):

    if not text.strip():
        st.warning("Please enter some text to analyze.")
    else:
        st.markdown("---")

        # Run analysis
        with st.spinner("Analyzing..."):
            results = analyze_text(text)

        # Scores section
        st.markdown('<p class="section-header">Assessment</p>', unsafe_allow_html=True)

        score_names = ['Overall', 'Clarity', 'Style', 'Conciseness', 'Tone']
        score_keys = ['overall', 'clarity', 'style', 'conciseness', 'tone']

        scores_html = '<div style="display: flex; gap: 0; margin: 1rem 0;">'
        for name, key in zip(score_names, score_keys):
            val = results['scores'][key]
            scores_html += f'''
            <div class="score-card" style="flex: 1;">
                <div class="score-val">{val}</div>
                <div class="score-label">{name}</div>
            </div>'''
        scores_html += '</div>'
        st.markdown(scores_html, unsafe_allow_html=True)

        # Stats
        st.markdown("")
        st.markdown(
            f"<p style='color: var(--warm-gray); font-family: var(--mono); font-size: 0.75rem; letter-spacing: 0.05em;'>"
            f"<strong>{results['stats']['words']}</strong> words &middot; "
            f"<strong>{results['stats']['sentences']}</strong> sentences &middot; "
            f"<strong>{results['stats']['avg_length']}</strong> avg words/sentence</p>",
            unsafe_allow_html=True
        )

        # Overall message
        emoji, message = get_overall_message(results['scores']['overall'])
        st.markdown(f"""
        <div class="message-box">
            <p style="color: var(--ink); font-size: 1.05rem; margin: 0; font-family: var(--body); font-style: italic;">
                {emoji} {message}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Suggestions
        if results['issues']:
            st.markdown("---")
            st.markdown('<p class="section-header">Suggestions</p>', unsafe_allow_html=True)
            st.markdown(f"<p style='color: var(--warm-gray); font-style: italic;'>{len(results['issues'])} areas identified for revision</p>", unsafe_allow_html=True)

            for i, issue in enumerate(results['issues']):
                st.markdown(f"""
                <div class="issue-card">
                    <span class="category-badge">{issue['category']}</span>
                    <div class="issue-title">{issue['issue']}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Original**")
                    st.markdown(f"""
                    <div class="text-box original-box">{issue['original']}</div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("**Revised**")

                    suggestion = issue.get('fallback')
                    ai_error = None

                    if use_ai:
                        with st.spinner("AI thinking..."):
                            ai_suggestion, ai_error = get_ai_suggestion(issue['type'], issue['original'])
                            if ai_suggestion:
                                suggestion = ai_suggestion

                    if suggestion:
                        st.markdown(f"""
                        <div class="text-box revised-box">{suggestion}</div>
                        """, unsafe_allow_html=True)
                        if ai_error and use_ai:
                            st.caption(f"⚠️ {ai_error} (showing fallback)")
                    else:
                        msg = ai_error if ai_error else "Enable AI suggestions for a personalized rewrite"
                        st.markdown(f"""
                        <div class="text-box placeholder-box">{msg}</div>
                        """, unsafe_allow_html=True)

                st.markdown("")

        else:
            st.success("Excellent — no major issues found.")

        # Full AI Analysis
        if use_ai and has_api:
            st.markdown("---")
            st.markdown('<p class="section-header">AI Writing Coach</p>', unsafe_allow_html=True)

            with st.spinner("Getting personalized feedback..."):
                ai_feedback, ai_error = get_full_analysis(text)

            if ai_feedback:
                st.markdown(f"""
                <div class="ai-feedback" style="white-space: pre-wrap;">
{ai_feedback}
                </div>
                """, unsafe_allow_html=True)
            elif ai_error:
                st.warning(f"⚠️ {ai_error}")

        # Footer message
        st.markdown("---")
        st.markdown("""
        <p style="text-align: center; color: var(--warm-gray); font-size: 0.95rem; padding: 1rem 0; font-family: var(--body); font-style: italic;">
            Good writing is rewriting. Keep refining.
        </p>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem 0 2rem 0;">
    <p style="font-family: var(--mono); font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.2em; color: var(--warm-gray);">
        Writing Assistant &middot; Powered by Google Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)
