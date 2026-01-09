"""
Writing Assistant - Web Application
A friendly AI-powered tool for improving your writing.
Free to use with Google Gemini AI.
"""

import streamlit as st
import re
import os
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Writing Assistant",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container padding */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
    }

    /* Card styling */
    .stExpander {
        background-color: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1a73e8;
    }

    /* Text area styling */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        font-size: 1rem;
        line-height: 1.6;
    }

    .stTextArea textarea:focus {
        border-color: #1a73e8;
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
    }

    /* Button styling */
    .stButton > button {
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #202124;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #1a73e8;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #e0e0e0, transparent);
    }

    /* Issue card */
    .issue-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e8eaed;
    }

    .category-badge {
        background: #e8f0fe;
        color: #1a73e8;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.75rem;
    }

    .issue-title {
        font-weight: 600;
        color: #202124;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }

    .text-box {
        padding: 1rem 1.25rem;
        border-radius: 8px;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0.5rem 0;
    }

    .original-box {
        background: #fef7e0;
        border-left: 4px solid #f9ab00;
    }

    .revised-box {
        background: #e6f4ea;
        border-left: 4px solid #34a853;
    }

    .placeholder-box {
        background: #f1f3f4;
        border-left: 4px solid #9aa0a6;
        color: #5f6368;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Gemini
def get_gemini_model():
    """Get configured Gemini model."""
    api_key = os.environ.get("GOOGLE_API_KEY") or st.session_state.get("api_key")
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    return None


def get_ai_suggestion(issue_type: str, original: str) -> str:
    """Get AI-powered suggestion for a specific issue."""
    model = get_gemini_model()
    if not model:
        return None

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
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return None


def get_full_analysis(text: str) -> str:
    """Get comprehensive AI analysis of the text."""
    model = get_gemini_model()
    if not model:
        return None

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
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


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
<div style="text-align: center; padding: 2rem 0 1rem 0;">
    <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem; color: #202124;">✍️ Writing Assistant</h1>
    <p style="font-size: 1.1rem; color: #5f6368;">Free AI-powered suggestions to improve your writing</p>
</div>
""", unsafe_allow_html=True)

# API Key in sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    api_key_input = st.text_input(
        "Google API Key",
        type="password",
        placeholder="AIza...",
        help="Get a free key from Google AI Studio"
    )

    if api_key_input:
        st.session_state["api_key"] = api_key_input
        st.success("✓ API key saved!")

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
st.markdown('<p class="section-header">📄 Enter Your Text</p>', unsafe_allow_html=True)

input_method = st.radio(
    "Choose input:",
    ["✏️ Paste text", "📁 Upload file"],
    horizontal=True,
    label_visibility="collapsed"
)

text = ""

if "✏️" in input_method:
    text = st.text_area(
        "Your text",
        height=220,
        placeholder="Paste or type your text here...\n\nFor best results, enter at least a few sentences.",
        label_visibility="collapsed"
    )
else:
    uploaded = st.file_uploader("Upload", type=['txt', 'md'], label_visibility="collapsed")
    if uploaded:
        text = uploaded.read().decode('utf-8')
        st.info(f"📄 Loaded {len(text.split())} words")

# Options row
st.markdown("")
col1, col2 = st.columns([1, 3])

with col1:
    use_ai = st.toggle(
        "🤖 AI Suggestions",
        value=has_api,
        disabled=not has_api,
        help="Enable AI-powered rewrites"
    )

with col2:
    if not has_api:
        st.caption("💡 Add your free Google API key in the sidebar to enable AI suggestions")

# Analyze button
st.markdown("")
if st.button("🔍 Analyze My Writing", type="primary", use_container_width=True):

    if not text.strip():
        st.warning("Please enter some text to analyze.")
    else:
        st.markdown("---")

        # Run analysis
        with st.spinner("Analyzing..."):
            results = analyze_text(text)

        # Scores section
        st.markdown('<p class="section-header">📊 Scores</p>', unsafe_allow_html=True)

        cols = st.columns(5)
        score_names = ['Overall', 'Clarity', 'Style', 'Conciseness', 'Tone']
        score_keys = ['overall', 'clarity', 'style', 'conciseness', 'tone']

        for col, name, key in zip(cols, score_names, score_keys):
            with col:
                st.metric(name, f"{results['scores'][key]}/10")

        # Stats
        st.markdown("")
        st.markdown(
            f"📝 **{results['stats']['words']}** words · "
            f"**{results['stats']['sentences']}** sentences · "
            f"**{results['stats']['avg_length']}** avg words/sentence"
        )

        # Overall message
        emoji, message = get_overall_message(results['scores']['overall'])
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.25rem 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
            <p style="color: white; font-size: 1.2rem; margin: 0; font-weight: 500;">
                {emoji} {message}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Suggestions
        if results['issues']:
            st.markdown("---")
            st.markdown('<p class="section-header">💡 Suggestions</p>', unsafe_allow_html=True)
            st.markdown(f"Found **{len(results['issues'])}** areas to improve:")

            for i, issue in enumerate(results['issues']):
                st.markdown(f"""
                <div class="issue-card">
                    <span class="category-badge">{issue['category']}</span>
                    <div class="issue-title">{issue['issue']}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**📝 Original**")
                    st.markdown(f"""
                    <div class="text-box original-box">{issue['original']}</div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("**✨ Suggested**")

                    suggestion = issue.get('fallback')

                    if use_ai:
                        with st.spinner("AI thinking..."):
                            ai_suggestion = get_ai_suggestion(issue['type'], issue['original'])
                            if ai_suggestion:
                                suggestion = ai_suggestion

                    if suggestion:
                        st.markdown(f"""
                        <div class="text-box revised-box">{suggestion}</div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="text-box placeholder-box">
                            Enable AI suggestions for a personalized rewrite
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("")

        else:
            st.success("🎉 Great job! No major issues found.")

        # Full AI Analysis
        if use_ai and has_api:
            st.markdown("---")
            st.markdown('<p class="section-header">🤖 AI Writing Coach</p>', unsafe_allow_html=True)

            with st.spinner("Getting personalized feedback..."):
                ai_feedback = get_full_analysis(text)

            if ai_feedback:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 1.5rem;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e8eaed;
                            line-height: 1.8; white-space: pre-wrap;">
{ai_feedback}
                </div>
                """, unsafe_allow_html=True)

        # Footer message
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; color: #5f6368;">
            <p style="font-size: 1.1rem;">✨ Good writing is rewriting. Keep improving!</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #9aa0a6; font-size: 0.9rem;">
    Writing Assistant · Powered by Google Gemini AI · Free to use
</div>
""", unsafe_allow_html=True)
