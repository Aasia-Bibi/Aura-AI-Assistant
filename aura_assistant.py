import streamlit as st
from groq import Groq
from gtts import gTTS
import json
import os
import base64
import io
import uuid
from datetime import datetime, date

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Aura — AI Personal Assistant",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

REMINDERS_FILE = "reminders.json"
GROQ_MODEL = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# API KEY — Streamlit Secrets (no UI input box)
# ---------------------------------------------------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    # LOCAL TESTING FALLBACK ONLY — paste your key below for quick local runs,
    # then remove it again before pushing to GitHub. Never commit a real key.
    api_key = ""  # e.g. api_key = "gsk_...your_local_test_key_here"

groq_client = Groq(api_key=api_key) if api_key else None

# ---------------------------------------------------------------------------
# PREMIUM DARK / NEON TECH CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #1a0b2e 0%, #0d0618 35%, #050208 100%);
        background-attachment: fixed;
    }

    #MainMenu, footer, header {visibility: hidden;}

    [data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 320px !important;
    }

    .aura-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00f0ff 0%, #7b2ff7 50%, #f637ec 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    .aura-subtitle {
        color: #c5c5d8;
        font-size: 1.05rem;
        font-weight: 300;
        margin-top: -8px;
        margin-bottom: 25px;
        letter-spacing: 0.3px;
    }
    .aura-badge {
        display: inline-block;
        background: rgba(123, 47, 247, 0.15);
        border: 1px solid rgba(123, 47, 247, 0.4);
        color: #d4b8ff;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 14px;
    }

    .creator-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(168, 85, 247, 0.1);
        border: 1px solid rgba(0, 242, 254, 0.35);
        color: #d4d4e0;
        padding: 7px 18px;
        border-radius: 24px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 22px;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.12);
    }
    .creator-name {
        background: linear-gradient(90deg, #00f2fe 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
    }
    .page-footer {
        text-align: center;
        color: #a6adc8;
        font-size: 0.85rem;
        margin-top: 10px;
        padding: 14px 0;
    }
    .page-footer a {
        color: #00f2fe;
        text-decoration: none;
        font-weight: 600;
    }
    .page-footer a:hover {
        color: #a855f7;
    }

    .stButton>button {
        background: linear-gradient(90deg, #7b2ff7 0%, #00f0ff 100%);
        color: #050208;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 10px 18px;
        letter-spacing: 0.3px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 18px rgba(123, 47, 247, 0.35);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0, 240, 255, 0.45);
        color: #050208;
    }
    .stButton>button p {
        color: #050208 !important;
        font-weight: 700 !important;
    }
    .stDownloadButton>button {
        background: rgba(255,255,255,0.06);
        color: #00f0ff;
        border: 1px solid rgba(0, 240, 255, 0.4);
        border-radius: 10px;
        font-weight: 600;
    }
    .stDownloadButton>button p {
        color: #00f0ff !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255,255,255,0.03);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: #c5c5d8;
        font-weight: 600;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab"] p {
        color: inherit !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(123,47,247,0.35), rgba(0,240,255,0.2));
        color: #ffffff !important;
        box-shadow: 0 2px 12px rgba(123, 47, 247, 0.3);
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        background-color: #181825 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        caret-color: #00f0ff !important;
    }
    .stTextInput div[data-baseweb="input"],
    .stNumberInput div[data-baseweb="input"],
    .stTextArea div[data-baseweb="textarea"] {
        background-color: #181825 !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border: 1px solid rgba(0, 240, 255, 0.6) !important;
        box-shadow: 0 0 0 1px rgba(0, 240, 255, 0.35) !important;
        background-color: #1e1e2e !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stNumberInput input::placeholder {
        color: #a6adc8 !important;
        opacity: 1 !important;
    }
    .stNumberInput button {
        background-color: #1e1e2e !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
    }
    .stNumberInput button:hover {
        background-color: #292941 !important;
        border: 1px solid rgba(0, 240, 255, 0.5) !important;
    }
    .stNumberInput button svg {
        fill: #ffffff !important;
        color: #ffffff !important;
        opacity: 1 !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #181825 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    .stSelectbox div[data-baseweb="select"] * {
        color: #ffffff !important;
    }
    div[data-baseweb="popover"] ul[role="listbox"] {
        background-color: #181825 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
    }
    div[data-baseweb="popover"] ul[role="listbox"] li {
        color: #ffffff !important;
        background-color: #181825 !important;
    }
    div[data-baseweb="popover"] ul[role="listbox"] li:hover {
        background-color: #292941 !important;
        color: #00f0ff !important;
    }
    .stDateInput input {
        background-color: #181825 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    .stDateInput input::placeholder {
        color: #a6adc8 !important;
        opacity: 1 !important;
    }

    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label,
    label {
        color: #f5f5fa !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }
    .stTextInput label p,
    .stTextArea label p,
    .stNumberInput label p,
    .stSelectbox label p,
    .stDateInput label p {
        color: #f5f5fa !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #a6adc8 !important;
    }
    .stMarkdown p {
        color: #e4e4ef;
    }
    div[data-testid="stFormSubmitButton"] button p {
        color: #050208 !important;
        font-weight: 700 !important;
    }

    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 1.3rem;
        color: #ffffff;
        margin-top: 10px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(0,240,255,0.4), rgba(123,47,247,0.1), transparent);
        margin: 20px 0;
        border: none;
    }

    section[data-testid="stSidebar"] {
        background: rgba(10, 5, 20, 0.95);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] * {
        color: #e4e4ef;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    .sidebar-card {
        background: rgba(255, 255, 255, 0.06);
        border-left: 3px solid #00f0ff;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
    .sidebar-card-urgent {
        background: rgba(246, 55, 236, 0.10);
        border-left: 3px solid #f637ec;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
    .sidebar-card-title {
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .sidebar-card-meta {
        color: #c5c5d8;
        font-size: 0.8rem;
        margin-top: 3px;
    }
    .sidebar-tag {
        display: inline-block;
        background: rgba(0, 240, 255, 0.15);
        color: #7cf5ff;
        padding: 1px 8px;
        border-radius: 8px;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .sidebar-footer-text {
        margin-top: 10px;
        padding-top: 14px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.78rem;
        color: #a6adc8;
        text-align: center;
        line-height: 1.8;
    }
    .sidebar-footer-text a {
        color: #00f2fe;
        text-decoration: none;
        font-weight: 600;
    }
    .sidebar-footer-text a:hover {
        color: #a855f7;
    }

    .result-box {
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #00f0ff;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 10px;
        color: #f0f0f5;
    }
    .result-box strong, .result-box b {
        color: #ffffff;
    }

    div[data-testid="stAlert"] p {
        color: #f5f5fa !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# DATA LAYER: reminders.json
# ---------------------------------------------------------------------------
def load_reminders():
    if not os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(REMINDERS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        with open(REMINDERS_FILE, "w") as f:
            json.dump([], f)
        return []

def save_reminders(data):
    with open(REMINDERS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

def add_reminder(title, category, target_date, notes):
    data = load_reminders()
    new_item = {
        "id": str(uuid.uuid4()),
        "title": title,
        "category": category,
        "date": str(target_date),
        "notes": notes
    }
    data.append(new_item)
    save_reminders(data)

def delete_reminder(item_id):
    data = load_reminders()
    data = [d for d in data if d["id"] != item_id]
    save_reminders(data)

def days_remaining(date_str):
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (target - date.today()).days
    except ValueError:
        return None

# ---------------------------------------------------------------------------
# AI LAYER (Groq Cloud API)
# ---------------------------------------------------------------------------
def call_groq(prompt, system_prompt="You are Aura, a precise and helpful AI study assistant."):
    if not groq_client:
        return None, "⚠️ No API key found. Add GROQ_API_KEY to your Streamlit secrets."

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=2048,
        )
        return response.choices[0].message.content, None
    except Exception as e:
        error_text = str(e)
        if "429" in error_text or "rate limit" in error_text.lower():
            return None, "⚠️ Groq rate limit reached. Please wait a few seconds and try again."
        if "401" in error_text or "authentication" in error_text.lower():
            return None, "⚠️ Invalid Groq API key. Check your GROQ_API_KEY in secrets."
        return None, f"⚠️ Groq API error: {error_text}"

def summarize_to_bullets(text):
    prompt = f"""Summarize the following text into clean, concise bullet points.
Use a maximum of 8 bullet points. Each bullet must start with "- " and capture
one key idea only. Do not add any preamble or conclusion, only the bullets.

TEXT:
\"\"\"{text}\"\"\"
"""
    return call_groq(prompt)

def extract_difficult_words(text):
    prompt = f"""Read the following text and identify 5 to 10 difficult, advanced,
or uncommon vocabulary words from it. For each word, provide:
1. The word (bolded)
2. A simple, one-sentence meaning
3. The exact sentence from the text where it appears

Format strictly as a markdown list like this example:
- **Word** — meaning here. (Context: "...sentence from text...")

TEXT:
\"\"\"{text}\"\"\"
"""
    return call_groq(prompt)

def simplify_language(text):
    prompt = f"""Rewrite the following text using very simple, plain English.
Use short sentences. Avoid jargon and complex vocabulary. Keep the same
meaning and all key facts. Do not add any commentary, only output the
rewritten text.

TEXT:
\"\"\"{text}\"\"\"
"""
    return call_groq(prompt)

def generate_study_plan(exam_name, num_days, focus_areas):
    prompt = f"""Act as an expert exam preparation coach. Create a structured
{num_days}-day study schedule for the exam: "{exam_name}".
{"The student wants to focus especially on: " + focus_areas + "." if focus_areas else ""}

Format the output in clean markdown exactly like this:

### 📅 {num_days}-Day Study Plan for {exam_name}

**Day 1: [Topic Title]**
- Task 1
- Task 2
- Recommended time: X hours

(repeat for each day)

### 📚 Top Free Resources
List 6 to 8 real, well-known free resources (YouTube channels, Khan Academy
courses, free websites, official practice test sites) relevant specifically
to "{exam_name}". Format as a markdown bullet list with the resource name in
bold, and a one-line description of what it offers.

### 💡 Quick Tips
Give 3 short actionable exam-day tips.
"""
    return call_groq(prompt, system_prompt="You are Aura, an expert exam preparation coach who creates highly structured, realistic study plans.")

# ---------------------------------------------------------------------------
# VOICE LAYER (gTTS)
# ---------------------------------------------------------------------------
def text_to_speech_bytes(text):
    clean_text = text.replace("*", "").replace("#", "").replace("-", " ")
    if not clean_text.strip():
        return None
    tts = gTTS(text=clean_text, lang="en", slow=False)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()

def render_audio_player(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    html = f"""
    <audio controls autoplay style="width:100%; margin-top:10px; border-radius: 10px;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "last_output_text" not in st.session_state:
    st.session_state.last_output_text = ""
if "summary_result" not in st.session_state:
    st.session_state.summary_result = ""
if "words_result" not in st.session_state:
    st.session_state.words_result = ""
if "simplified_result" not in st.session_state:
    st.session_state.simplified_result = ""
if "study_plan_result" not in st.session_state:
    st.session_state.study_plan_result = ""

# ---------------------------------------------------------------------------
# SIDEBAR: OPERATIONAL CENTER
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛰️ Operational Center")
    st.caption("Live dashboard for deadlines & exams")

    if not api_key:
        st.warning("No GROQ_API_KEY found in secrets. AI features are disabled until you add one.", icon="⚠️")

    st.divider()

    st.markdown("#### 📊 Active Schedules Countdown")

    reminders = load_reminders()
    reminders_sorted = sorted(
        reminders,
        key=lambda r: r.get("date", "9999-99-99")
    )

    if not reminders_sorted:
        st.info("No reminders yet. Add one below to get started.")
    else:
        urgent_count = sum(
            1 for r in reminders_sorted
            if days_remaining(r["date"]) is not None and days_remaining(r["date"]) <= 7
        )
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Total Tracked", len(reminders_sorted))
        with m2:
            st.metric("Due Soon (≤7d)", urgent_count)

        st.write("")

        for item in reminders_sorted:
            d_left = days_remaining(item["date"])
            urgent = d_left is not None and d_left <= 7
            card_class = "sidebar-card-urgent" if urgent else "sidebar-card"

            days_text = ""
            if d_left is not None:
                if d_left < 0:
                    days_text = f"⏰ {abs(d_left)} days ago (overdue)"
                elif d_left == 0:
                    days_text = "🔥 Due TODAY"
                else:
                    days_text = f"📆 {d_left} days remaining"

            with st.container():
                st.markdown(
                    f"""<div class="{card_class}">
                    <span class="sidebar-tag">{item['category']}</span><br>
                    <span class="sidebar-card-title">{item['title']}</span>
                    <div class="sidebar-card-meta">{item['date']} • {days_text}</div>
                    <div class="sidebar-card-meta">{item.get('notes','')}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
                if st.button("🗑️ Remove", key=f"del_{item['id']}", use_container_width=True):
                    delete_reminder(item["id"])
                    st.rerun()

    st.divider()

    st.markdown("#### ➕ Register New Schedule")
    with st.form("add_reminder_form", clear_on_submit=True):
        r_title = st.text_input("Title", placeholder="e.g. MIT Application / Physics Final")
        r_category = st.selectbox("Category", ["University Application", "Exam Date", "Other"])
        r_date = st.date_input("Date", value=date.today())
        r_notes = st.text_area("Notes (optional)", height=60)
        submitted = st.form_submit_button("Save Reminder", use_container_width=True)
        if submitted:
            if r_title.strip():
                add_reminder(r_title.strip(), r_category, r_date, r_notes.strip())
                st.success(f"Saved: {r_title}")
                st.rerun()
            else:
                st.error("Please enter a title.")

    st.markdown(
        """<div class="sidebar-footer-text">
        Built with 💜 using Streamlit & Groq Cloud API<br>
        <a href="your-github-link-here" target="_blank">GitHub</a> | <a href="https://www.linkedin.com/in/aasia-bibi-8276502b8/" target="_blank">LinkedIn</a>
        </div>""",
        unsafe_allow_html=True
    )

# ---------------------------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------------------------
st.markdown('<div class="aura-badge">✨ AI-Powered · Runs Locally</div>', unsafe_allow_html=True)
st.markdown('<div class="aura-header">Aura</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="creator-badge">🚀 Developed by <span class="creator-name">Aasia Bibi</span> &nbsp;|&nbsp; Open-Source AI Portfolio Project</div>',
    unsafe_allow_html=True
)
st.markdown('<div class="aura-subtitle">A personal AI assistant for smarter studying — summarize, simplify, listen, and stay on track.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝  Text Intelligence", "🎯  Exam Prep Coach"])

# ---------------------------------------------------------------------------
# TAB 1: TEXT TOOLS + VOICE
# ---------------------------------------------------------------------------
with tab1:
    st.markdown('<div class="section-header">Paste Your Text</div>', unsafe_allow_html=True)
    input_text = st.text_area(
        "Text to process",
        height=220,
        placeholder="Paste an article, lecture notes, or any text you want summarized, explained, or simplified...",
        label_visibility="collapsed"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        summarize_btn = st.button("📋 Summarize to Bullets", use_container_width=True)
    with col2:
        words_btn = st.button("📖 Difficult Words", use_container_width=True)
    with col3:
        simplify_btn = st.button("🔤 Simplify Language", use_container_width=True)

    if summarize_btn:
        if not input_text.strip():
            st.warning("Please paste some text first.")
        else:
            with st.spinner("Summarizing..."):
                result, error = summarize_to_bullets(input_text)
                if error:
                    st.error(error)
                else:
                    st.session_state.summary_result = result
                    st.session_state.last_output_text = result

    if words_btn:
        if not input_text.strip():
            st.warning("Please paste some text first.")
        else:
            with st.spinner("Finding difficult words..."):
                result, error = extract_difficult_words(input_text)
                if error:
                    st.error(error)
                else:
                    st.session_state.words_result = result
                    st.session_state.last_output_text = result

    if simplify_btn:
        if not input_text.strip():
            st.warning("Please paste some text first.")
        else:
            with st.spinner("Simplifying..."):
                result, error = simplify_language(input_text)
                if error:
                    st.error(error)
                else:
                    st.session_state.simplified_result = result
                    st.session_state.last_output_text = result

    if st.session_state.summary_result:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📋 Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{st.session_state.summary_result}</div>', unsafe_allow_html=True)

    if st.session_state.words_result:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📖 Difficult Words</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{st.session_state.words_result}</div>', unsafe_allow_html=True)

    if st.session_state.simplified_result:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🔤 Simplified Version</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{st.session_state.simplified_result}</div>', unsafe_allow_html=True)

    if st.session_state.last_output_text:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🔊 Listen to the Result</div>', unsafe_allow_html=True)
        if st.button("🎙️ Generate Voice"):
            with st.spinner("Generating audio with gTTS..."):
                audio_bytes = text_to_speech_bytes(st.session_state.last_output_text)
                if audio_bytes:
                    render_audio_player(audio_bytes)
                    st.download_button(
                        "⬇️ Download MP3",
                        data=audio_bytes,
                        file_name="aura_speech.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.warning("Nothing to convert to speech yet.")

# ---------------------------------------------------------------------------
# TAB 2: EXAM PREP COACH
# ---------------------------------------------------------------------------
with tab2:
    st.markdown('<div class="section-header">🎯 Build Your Study Plan</div>', unsafe_allow_html=True)
    st.caption("Get a full schedule and curated free resources for any exam.")

    ecol1, ecol2 = st.columns([2, 1])
    with ecol1:
        exam_name = st.text_input("Exam Name", placeholder="e.g. SAT Math, IELTS, AP Biology, GATE CSE")
    with ecol2:
        num_days = st.number_input("Number of Days", min_value=1, max_value=30, value=7, step=1)

    focus_areas = st.text_input("Specific topics to focus on (optional)", placeholder="e.g. algebra, essay writing, organic chemistry")

    if st.button("🚀 Generate Study Plan", use_container_width=True):
        if not exam_name.strip():
            st.warning("Please enter an exam name.")
        else:
            with st.spinner(f"Building your {num_days}-day plan for {exam_name}..."):
                result, error = generate_study_plan(exam_name.strip(), int(num_days), focus_areas.strip())
                if error:
                    st.error(error)
                else:
                    st.session_state.study_plan_result = result

    if st.session_state.study_plan_result:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{st.session_state.study_plan_result}</div>', unsafe_allow_html=True)

        if st.button("🎙️ Listen to Study Plan Summary"):
            with st.spinner("Generating audio..."):
                audio_bytes = text_to_speech_bytes(st.session_state.study_plan_result)
                if audio_bytes:
                    render_audio_player(audio_bytes)

# ---------------------------------------------------------------------------
# PAGE FOOTER
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    """<div class="page-footer">
    ✨ Aura — Personal AI Assistant · Built with 💜 using Streamlit & Groq Cloud API<br>
    <a href="your-github-link-here" target="_blank">GitHub</a> | <a href="https://www.linkedin.com/in/aasia-bibi-8276502b8/" target="_blank">LinkedIn</a>
    </div>""",
    unsafe_allow_html=True
)