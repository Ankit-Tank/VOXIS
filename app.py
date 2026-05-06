"""
VOXIS — AI Voice Studio
Azure Cognitive Services Speech SDK · Streamlit Cloud Ready
Credentials are loaded exclusively from st.secrets (never hardcoded)
"""

import os
import time
import tempfile
import base64
import streamlit as st
import azure.cognitiveservices.speech as speechsdk

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VOXIS · AI Voice Studio",
    page_icon="🎙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM CSS  — Obsidian Studio Aesthetic
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400&display=swap" rel="stylesheet">

<style>
/* ── GLOBAL RESET & BASE ─────────────────────────────── */
:root {
  --gold:        #C9A84C;
  --gold-light:  #E8C96A;
  --gold-dim:    #7A5F24;
  --obsidian:    #060608;
  --surface-1:   #0C0C10;
  --surface-2:   #131318;
  --surface-3:   #1A1A22;
  --surface-4:   #242430;
  --border:      rgba(201,168,76,0.18);
  --border-soft: rgba(201,168,76,0.08);
  --cream:       #EDE5D0;
  --cream-dim:   #A89878;
  --white:       #F7F2E8;
  --danger:      #C0444A;
  --success:     #4A9C6A;
  --font-display: 'Cormorant Garamond', Georgia, serif;
  --font-ui:      'Syne', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
  --radius-sm:    6px;
  --radius-md:    12px;
  --radius-lg:    20px;
  --shadow-gold:  0 0 40px rgba(201,168,76,0.12);
  --shadow-deep:  0 20px 60px rgba(0,0,0,0.8);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background: var(--obsidian) !important;
  font-family: var(--font-ui) !important;
  color: var(--cream) !important;
}

/* hide streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* scrollbar */
::-webkit-scrollbar { width: 4px; background: var(--obsidian); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 2px; }

/* main content area */
[data-testid="stMain"] .block-container {
  max-width: 960px !important;
  padding: 0 2rem 4rem !important;
  margin: 0 auto !important;
}

/* ── TYPOGRAPHY ──────────────────────────────────────── */
h1,h2,h3,h4 { font-family: var(--font-display) !important; }
p, span, label, div { font-family: var(--font-ui) !important; }

/* ── HEADER SECTION ──────────────────────────────────── */
.voxis-header {
  padding: 3.5rem 0 2rem;
  text-align: center;
  position: relative;
}
.voxis-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.35em;
  color: var(--gold);
  text-transform: uppercase;
  margin-bottom: 1rem;
  opacity: 0.9;
}
.voxis-wordmark {
  font-family: var(--font-display);
  font-size: clamp(4rem, 10vw, 7rem);
  font-weight: 300;
  letter-spacing: 0.2em;
  color: var(--white);
  line-height: 1;
  margin-bottom: 0.3rem;
  background: linear-gradient(135deg, #F7F2E8 0%, #C9A84C 50%, #F7F2E8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.voxis-tagline {
  font-family: var(--font-ui);
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.15em;
  color: var(--cream-dim);
  text-transform: uppercase;
  margin-bottom: 2rem;
}
.voxis-divider {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-dim), var(--gold), var(--gold-dim), transparent);
  margin: 0 auto 2.5rem;
  max-width: 400px;
}

/* waveform decorative bars */
.waveform-deco {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  margin: 1.2rem auto 0;
  height: 32px;
}
.waveform-deco span {
  display: inline-block;
  width: 3px;
  background: var(--gold);
  border-radius: 2px;
  animation: wave-idle 1.6s ease-in-out infinite;
  opacity: 0.7;
}
.waveform-deco span:nth-child(1)  { height: 8px;  animation-delay: 0s; }
.waveform-deco span:nth-child(2)  { height: 18px; animation-delay: 0.15s; }
.waveform-deco span:nth-child(3)  { height: 26px; animation-delay: 0.3s; }
.waveform-deco span:nth-child(4)  { height: 14px; animation-delay: 0.45s; }
.waveform-deco span:nth-child(5)  { height: 30px; animation-delay: 0.6s; }
.waveform-deco span:nth-child(6)  { height: 20px; animation-delay: 0.75s; }
.waveform-deco span:nth-child(7)  { height: 12px; animation-delay: 0.9s; }
.waveform-deco span:nth-child(8)  { height: 24px; animation-delay: 1.05s; }
.waveform-deco span:nth-child(9)  { height: 16px; animation-delay: 1.2s; }
.waveform-deco span:nth-child(10) { height: 8px;  animation-delay: 1.35s; }

@keyframes wave-idle {
  0%, 100% { transform: scaleY(1); opacity: 0.5; }
  50%       { transform: scaleY(1.6); opacity: 1; }
}

/* ── TAB SELECTOR ────────────────────────────────────── */
.mode-selector {
  display: flex;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 50px;
  padding: 5px;
  margin: 0 auto 2.5rem;
  width: fit-content;
  gap: 4px;
}
.mode-btn {
  padding: 0.55rem 1.8rem;
  border-radius: 50px;
  font-family: var(--font-ui);
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--cream-dim);
  background: transparent;
  border: none;
}
.mode-btn.active {
  background: linear-gradient(135deg, var(--gold-dim), var(--gold));
  color: var(--obsidian);
  box-shadow: 0 4px 20px rgba(201,168,76,0.35);
}

/* ── CARDS / PANELS ──────────────────────────────────── */
.panel {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2rem 2.2rem;
  margin-bottom: 1.2rem;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-deep);
  transition: border-color 0.3s ease;
}
.panel::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  opacity: 0.6;
}
.panel:hover { border-color: rgba(201,168,76,0.3); }

.panel-label {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  letter-spacing: 0.3em;
  color: var(--gold);
  text-transform: uppercase;
  margin-bottom: 1.2rem;
  opacity: 0.85;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.panel-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.panel-title {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 300;
  color: var(--white);
  margin-bottom: 0.5rem;
  letter-spacing: 0.02em;
}
.panel-desc {
  font-size: 0.82rem;
  color: var(--cream-dim);
  line-height: 1.6;
  margin-bottom: 1.5rem;
  font-weight: 400;
}

/* ── STREAMLIT WIDGET OVERRIDES ──────────────────────── */

/* file uploader */
[data-testid="stFileUploader"] {
  background: var(--surface-2) !important;
  border: 1px dashed var(--gold-dim) !important;
  border-radius: var(--radius-md) !important;
  padding: 1.5rem !important;
  transition: border-color 0.3s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--gold) !important;
  background: var(--surface-3) !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span {
  color: var(--cream-dim) !important;
  font-family: var(--font-ui) !important;
  font-size: 0.85rem !important;
}
[data-testid="stFileUploaderDropzoneInput"] + div { color: var(--gold) !important; }

/* selectbox */
[data-testid="stSelectbox"] label {
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--gold) !important;
}
[data-testid="stSelectbox"] > div > div {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--cream) !important;
  font-family: var(--font-ui) !important;
  font-size: 0.88rem !important;
}
[data-testid="stSelectbox"] > div > div:hover {
  border-color: var(--gold) !important;
}

/* text area */
[data-testid="stTextArea"] label {
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--gold) !important;
}
[data-testid="stTextArea"] textarea {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--cream) !important;
  font-family: var(--font-ui) !important;
  font-size: 0.92rem !important;
  line-height: 1.7 !important;
  resize: vertical !important;
  transition: border-color 0.3s ease !important;
}
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
  outline: none !important;
}

/* slider */
[data-testid="stSlider"] label {
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--gold) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
  background: var(--gold) !important;
}

/* buttons — primary */
[data-testid="stButton"] > button {
  background: linear-gradient(135deg, var(--gold-dim) 0%, var(--gold) 50%, var(--gold-dim) 100%) !important;
  color: var(--obsidian) !important;
  font-family: var(--font-ui) !important;
  font-weight: 700 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
  border: none !important;
  border-radius: 50px !important;
  padding: 0.75rem 2.5rem !important;
  width: 100% !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 24px rgba(201,168,76,0.3) !important;
}
[data-testid="stButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 32px rgba(201,168,76,0.5) !important;
}
[data-testid="stButton"] > button:active {
  transform: translateY(0) !important;
}

/* download button */
[data-testid="stDownloadButton"] > button {
  background: transparent !important;
  color: var(--gold) !important;
  font-family: var(--font-ui) !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
  border: 1px solid var(--gold-dim) !important;
  border-radius: 50px !important;
  padding: 0.7rem 2rem !important;
  width: 100% !important;
  transition: all 0.3s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: rgba(201,168,76,0.1) !important;
  border-color: var(--gold) !important;
  box-shadow: 0 4px 20px rgba(201,168,76,0.2) !important;
}

/* audio player */
[data-testid="stAudio"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  padding: 0.5rem !important;
}
[data-testid="stAudio"] audio {
  width: 100% !important;
  filter: invert(1) hue-rotate(180deg) brightness(0.9) !important;
}

/* alerts */
[data-testid="stAlert"] {
  background: var(--surface-2) !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid !important;
  font-family: var(--font-ui) !important;
  font-size: 0.85rem !important;
}
[data-testid="stAlert"][data-baseweb="notification"] {
  border-color: var(--border) !important;
}

/* success alert */
div[data-baseweb="notification"].st-emotion-cache-1xarl3l {
  background: rgba(74,156,106,0.12) !important;
  border-color: rgba(74,156,106,0.4) !important;
}

/* spinner */
[data-testid="stSpinner"] { color: var(--gold) !important; }
.stSpinner > div { border-color: var(--gold) transparent transparent !important; }

/* columns gap */
[data-testid="stHorizontalBlock"] { gap: 1rem !important; }

/* radio (for voice gender) */
[data-testid="stRadio"] label {
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--gold) !important;
}
[data-testid="stRadio"] div[data-baseweb="radio"] label {
  font-family: var(--font-ui) !important;
  font-size: 0.85rem !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  color: var(--cream) !important;
}

/* ── RESULT BOX ──────────────────────────────────────── */
.result-box {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.4rem 1.6rem;
  position: relative;
  margin-top: 1rem;
}
.result-box::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--gold-dim), var(--gold), var(--gold-dim));
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}
.result-label {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 0.8rem;
  opacity: 0.7;
}
.result-text {
  font-family: var(--font-ui);
  font-size: 1.05rem;
  line-height: 1.75;
  color: var(--white);
  white-space: pre-wrap;
  word-break: break-word;
}
.result-meta {
  margin-top: 0.8rem;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--cream-dim);
  opacity: 0.6;
  letter-spacing: 0.1em;
}

/* ── STAT CHIPS ──────────────────────────────────────── */
.stat-row {
  display: flex;
  gap: 0.7rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}
.stat-chip {
  background: var(--surface-3);
  border: 1px solid var(--border-soft);
  border-radius: 50px;
  padding: 0.3rem 0.9rem;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--cream-dim);
  letter-spacing: 0.12em;
}
.stat-chip b { color: var(--gold); font-weight: 500; }

/* ── VOICE CARD GRID ─────────────────────────────────── */
.voice-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.6rem;
  margin-top: 0.8rem;
}
.voice-card {
  background: var(--surface-2);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  padding: 0.7rem 1rem;
  cursor: pointer;
  transition: all 0.25s ease;
}
.voice-card:hover { border-color: var(--gold-dim); background: var(--surface-3); }
.voice-card.selected { border-color: var(--gold); background: rgba(201,168,76,0.07); }
.voice-name { font-size: 0.82rem; color: var(--cream); font-weight: 600; margin-bottom: 0.2rem; }
.voice-desc { font-size: 0.68rem; color: var(--cream-dim); font-family: var(--font-mono); }

/* ── CHAR COUNTER ────────────────────────────────────── */
.char-counter {
  text-align: right;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--cream-dim);
  margin-top: 0.3rem;
  opacity: 0.6;
  letter-spacing: 0.1em;
}
.char-counter.warn { color: var(--gold); opacity: 1; }
.char-counter.danger { color: var(--danger); opacity: 1; }

/* ── FOOTER ──────────────────────────────────────────── */
.voxis-footer {
  text-align: center;
  padding: 2rem 0 1rem;
  font-family: var(--font-mono);
  font-size: 0.62rem;
  letter-spacing: 0.2em;
  color: var(--cream-dim);
  opacity: 0.35;
  text-transform: uppercase;
}

/* ── SECTION SEPARATOR ───────────────────────────────── */
.section-sep {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0;
}
.section-sep::before, .section-sep::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.section-sep-text {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  color: var(--gold-dim);
  text-transform: uppercase;
}

/* ── MODE TABS (Streamlit native) ────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 50px !important;
  padding: 4px !important;
  gap: 0 !important;
  width: fit-content !important;
  margin: 0 auto 2rem !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 50px !important;
  font-family: var(--font-ui) !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--cream-dim) !important;
  padding: 0.5rem 1.8rem !important;
  transition: all 0.3s ease !important;
  border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  background: linear-gradient(135deg, var(--gold-dim), var(--gold)) !important;
  color: var(--obsidian) !important;
  box-shadow: 0 3px 16px rgba(201,168,76,0.35) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
  display: none !important;
}
[data-testid="stTabs"] [data-baseweb="tab-border"] {
  display: none !important;
}
[data-testid="stTabPanel"] {
  padding: 0 !important;
}

/* ── STATUS BADGE ────────────────────────────────────── */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(74,156,106,0.12);
  border: 1px solid rgba(74,156,106,0.3);
  border-radius: 50px;
  padding: 0.3rem 0.8rem;
  font-family: var(--font-mono);
  font-size: 0.62rem;
  letter-spacing: 0.15em;
  color: #6EC98A;
  text-transform: uppercase;
}
.status-dot {
  width: 6px; height: 6px;
  background: #6EC98A;
  border-radius: 50%;
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(0.8); }
}

/* fix stMarkdown rendering */
[data-testid="stMarkdownContainer"] { font-family: var(--font-ui) !important; }

/* number input */
[data-testid="stNumberInput"] label {
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--gold) !important;
}
[data-testid="stNumberInput"] input {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--cream) !important;
  font-family: var(--font-ui) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CREDENTIAL LOADING  (only from st.secrets — never hardcoded)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_credentials() -> tuple[str, str]:
    """Load Azure credentials from Streamlit secrets."""
    try:
        key    = st.secrets["AZURE_SPEECH_KEY"]
        region = st.secrets["AZURE_SPEECH_REGION"]
        return key, region
    except KeyError as e:
        st.error(
            f"⚠️  Missing secret: `{e}`.  "
            "Add your Azure credentials in **Settings → Secrets** on Streamlit Cloud "
            "or in `.streamlit/secrets.toml` locally."
        )
        st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# AZURE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

VOICES: dict[str, dict] = {
    "Jenny (Female · Warm)"    : {"name": "en-US-JennyNeural",    "lang": "en-US"},
    "Aria (Female · Expressive)": {"name": "en-US-AriaNeural",     "lang": "en-US"},
    "Emma (Female · Cheerful)" : {"name": "en-US-EmmaNeural",      "lang": "en-US"},
    "Guy (Male · Neutral)"     : {"name": "en-US-GuyNeural",       "lang": "en-US"},
    "Davis (Male · Formal)"    : {"name": "en-US-DavisNeural",     "lang": "en-US"},
    "Brian (Male · Deep)"      : {"name": "en-US-BrianNeural",     "lang": "en-US"},
    "Sonia (Female · British)" : {"name": "en-GB-SoniaNeural",     "lang": "en-GB"},
    "Ryan (Male · British)"    : {"name": "en-GB-RyanNeural",      "lang": "en-GB"},
}

LANGUAGES: dict[str, str] = {
    "English (US)"    : "en-US",
    "English (UK)"    : "en-GB",
    "English (India)" : "en-IN",
    "Hindi"           : "hi-IN",
    "Spanish"         : "es-ES",
    "French"          : "fr-FR",
    "German"          : "de-DE",
    "Portuguese"      : "pt-BR",
    "Japanese"        : "ja-JP",
    "Chinese (Mandarin)": "zh-CN",
}

MAX_CHARS = 3000


def transcribe_audio(audio_path: str, language_code: str,
                     key: str, region: str) -> dict:
    """
    Transcribe an audio file using Azure continuous recognition.
    Returns {'success': bool, 'text': str, 'error': str|None}
    """
    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.speech_recognition_language = language_code

    audio_cfg   = speechsdk.audio.AudioConfig(filename=audio_path)
    recognizer  = speechsdk.SpeechRecognizer(speech_config=config,
                                              audio_config=audio_cfg)

    results: list[str] = []
    errors:  list[str] = []
    done = False

    def on_recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            results.append(evt.result.text)

    def on_canceled(evt):
        nonlocal done
        details = evt.result.cancellation_details
        if details.reason == speechsdk.CancellationReason.Error:
            errors.append(details.error_details)
        done = True

    def on_stopped(evt):
        nonlocal done
        done = True

    recognizer.recognized.connect(on_recognized)
    recognizer.canceled.connect(on_canceled)
    recognizer.session_stopped.connect(on_stopped)

    recognizer.start_continuous_recognition()

    timeout_s, elapsed = 120, 0.0
    while not done and elapsed < timeout_s:
        time.sleep(0.1)
        elapsed += 0.1

    recognizer.stop_continuous_recognition()

    text = " ".join(results).strip()
    if errors:
        return {"success": False, "text": text,
                "error": "; ".join(errors)}
    if not text:
        return {"success": False, "text": "",
                "error": "No speech could be recognised in the audio."}
    return {"success": True, "text": text, "error": None}


def synthesise_speech(text: str, voice_name: str,
                      key: str, region: str) -> dict:
    """
    Synthesise speech from text.
    Returns {'success': bool, 'audio': bytes|None, 'error': str|None}
    """
    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.speech_synthesis_voice_name = voice_name

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()

    try:
        audio_cfg   = speechsdk.audio.AudioOutputConfig(filename=tmp.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=config,
                                                   audio_config=audio_cfg)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            with open(tmp.name, "rb") as fh:
                audio_bytes = fh.read()
            return {"success": True, "audio": audio_bytes, "error": None}

        cancel = result.cancellation_details
        return {"success": False, "audio": None,
                "error": f"Synthesis cancelled: {cancel.error_details}"}

    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def render_header():
    bars = "".join(["<span></span>"] * 10)
    st.markdown(f"""
    <div class="voxis-header">
      <div class="voxis-eyebrow">Azure Cognitive Services · AI Voice Studio</div>
      <div class="voxis-wordmark">VOXIS</div>
      <div class="voxis-tagline">Transform Voice &nbsp;·&nbsp; Transcribe Speech &nbsp;·&nbsp; Synthesise Sound</div>
      <div class="voxis-divider"></div>
      <div class="waveform-deco">{bars}</div>
    </div>
    """, unsafe_allow_html=True)


def render_result(text: str):
    word_count = len(text.split())
    char_count = len(text)
    st.markdown(f"""
    <div class="result-box">
      <div class="result-label">✦ Transcribed Output</div>
      <div class="result-text">{text}</div>
      <div class="stat-row">
        <div class="stat-chip"><b>{word_count}</b> words</div>
        <div class="stat-chip"><b>{char_count}</b> characters</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def get_file_ext(mime: str) -> str:
    mapping = {
        "audio/wav":  "wav",
        "audio/x-wav": "wav",
        "audio/mpeg": "mp3",
        "audio/mp3":  "mp3",
        "audio/ogg":  "ogg",
        "audio/flac": "flac",
        "audio/m4a":  "m4a",
        "audio/mp4":  "mp4",
        "audio/x-m4a": "m4a",
        "video/mp4":  "mp4",
    }
    return mapping.get(mime, "wav")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    AZURE_KEY, AZURE_REGION = load_credentials()

    render_header()

    # ── TABS ─────────────────────────────────────────────────────────────────
    tab_stt, tab_tts = st.tabs(["🎤  Voice → Text", "🔊  Text → Voice"])

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 1 — SPEECH TO TEXT
    # ═════════════════════════════════════════════════════════════════════════
    with tab_stt:
        st.markdown("""
        <div class="panel">
          <div class="panel-label">01 &nbsp; Upload Audio</div>
          <div class="panel-title">Speech Recognition</div>
          <div class="panel-desc">
            Upload any audio recording and VOXIS will transcribe it using
            Azure's neural speech recognition engine with support for
            10+ languages and continuous multi-sentence detection.
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_lang, col_upload = st.columns([1, 2], gap="medium")

        with col_lang:
            selected_lang_label = st.selectbox(
                "Recognition Language",
                options=list(LANGUAGES.keys()),
                index=0,
                key="stt_lang"
            )
            lang_code = LANGUAGES[selected_lang_label]

            st.markdown("""
            <div style="
              background:var(--surface-2);
              border:1px solid var(--border-soft);
              border-radius:var(--radius-md);
              padding:1rem 1.2rem;
              margin-top:0.8rem;
            ">
              <div style="font-family:var(--font-mono);font-size:0.6rem;
                          letter-spacing:0.25em;color:var(--gold);
                          text-transform:uppercase;margin-bottom:0.6rem;">
                Supported Formats
              </div>
              <div style="font-size:0.78rem;color:var(--cream-dim);line-height:1.8;">
                WAV · MP3 · OGG · FLAC · M4A<br>
                <span style="opacity:0.5;font-size:0.68rem;font-family:var(--font-mono);">
                  Max recommended: 25 MB
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with col_upload:
            uploaded_file = st.file_uploader(
                "Drop your audio file here",
                type=["wav", "mp3", "ogg", "flac", "m4a", "mp4"],
                key="stt_file",
                label_visibility="collapsed",
            )
            if uploaded_file:
                st.audio(uploaded_file, format=uploaded_file.type)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        transcribe_btn = st.button(
            "✦ Transcribe Audio", key="btn_transcribe", use_container_width=True
        )

        # ── Process transcription ─────────────────────────────────────────
        if transcribe_btn:
            if not uploaded_file:
                st.warning("Please upload an audio file first.")
            else:
                ext = get_file_ext(uploaded_file.type)
                with tempfile.NamedTemporaryFile(
                    suffix=f".{ext}", delete=False
                ) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                with st.spinner("Transcribing…  this may take a moment"):
                    outcome = transcribe_audio(
                        tmp_path, lang_code, AZURE_KEY, AZURE_REGION
                    )

                os.unlink(tmp_path)

                if outcome["success"]:
                    st.session_state["stt_result"] = outcome["text"]
                else:
                    st.error(f"Transcription failed: {outcome['error']}")
                    if outcome.get("text"):
                        st.session_state["stt_result"] = outcome["text"]

        # ── Show cached result ────────────────────────────────────────────
        if st.session_state.get("stt_result"):
            text = st.session_state["stt_result"]
            render_result(text)

            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

            col_copy, col_dl = st.columns(2, gap="small")
            with col_copy:
                st.download_button(
                    "⬇  Download as .txt",
                    data=text,
                    file_name="voxis_transcript.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col_dl:
                import json
                payload = json.dumps({
                    "transcript": text,
                    "language": selected_lang_label,
                    "words": len(text.split()),
                    "characters": len(text),
                }, indent=2)
                st.download_button(
                    "⬇  Download as .json",
                    data=payload,
                    file_name="voxis_transcript.json",
                    mime="application/json",
                    use_container_width=True,
                )

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 2 — TEXT TO SPEECH
    # ═════════════════════════════════════════════════════════════════════════
    with tab_tts:
        st.markdown("""
        <div class="panel">
          <div class="panel-label">02 &nbsp; Synthesise Voice</div>
          <div class="panel-title">Neural Text-to-Speech</div>
          <div class="panel-desc">
            Type or paste your text and choose from 8 premium Azure Neural voices.
            Download the generated audio as a studio-quality WAV file.
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_v, col_t = st.columns([1, 2], gap="medium")

        with col_v:
            selected_voice_label = st.selectbox(
                "Neural Voice",
                options=list(VOICES.keys()),
                index=0,
                key="tts_voice"
            )
            voice_name = VOICES[selected_voice_label]["name"]

            st.markdown(f"""
            <div style="
              background:var(--surface-2);
              border:1px solid var(--border);
              border-radius:var(--radius-md);
              padding:1rem 1.2rem;
              margin-top:0.8rem;
            ">
              <div style="font-family:var(--font-mono);font-size:0.6rem;
                          letter-spacing:0.25em;color:var(--gold);
                          text-transform:uppercase;margin-bottom:0.5rem;">
                Selected Voice
              </div>
              <div style="font-size:0.9rem;color:var(--white);
                          font-weight:600;margin-bottom:0.2rem;">
                {selected_voice_label.split(" (")[0]}
              </div>
              <div style="font-family:var(--font-mono);font-size:0.65rem;
                          color:var(--cream-dim);">
                {voice_name}
              </div>
            </div>
            """, unsafe_allow_html=True)

        with col_t:
            tts_text = st.text_area(
                "Input Text",
                placeholder="Begin typing your text here…",
                height=200,
                max_chars=MAX_CHARS,
                key="tts_input",
            )

            char_count = len(tts_text) if tts_text else 0
            pct = char_count / MAX_CHARS
            cls = "danger" if pct > 0.9 else ("warn" if pct > 0.7 else "")
            st.markdown(
                f'<div class="char-counter {cls}">'
                f'{char_count:,} / {MAX_CHARS:,} characters</div>',
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        synth_btn = st.button(
            "✦ Synthesise Speech", key="btn_synth", use_container_width=True
        )

        # ── Process synthesis ─────────────────────────────────────────────
        if synth_btn:
            if not tts_text or not tts_text.strip():
                st.warning("Please enter some text to synthesise.")
            else:
                with st.spinner("Generating audio…"):
                    outcome = synthesise_speech(
                        tts_text.strip(), voice_name, AZURE_KEY, AZURE_REGION
                    )

                if outcome["success"]:
                    st.session_state["tts_audio"] = outcome["audio"]
                    st.session_state["tts_voice_used"] = selected_voice_label
                else:
                    st.error(f"Synthesis failed: {outcome['error']}")

        # ── Show cached audio ─────────────────────────────────────────────
        if st.session_state.get("tts_audio"):
            audio_bytes = st.session_state["tts_audio"]
            voice_used  = st.session_state.get("tts_voice_used", "")

            st.markdown("""
            <div class="section-sep">
              <div class="section-sep-text">Generated Audio</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        margin-bottom:0.8rem;">
              <div class="status-badge">
                <div class="status-dot"></div>
                Ready to play
              </div>
              <div style="font-family:var(--font-mono);font-size:0.65rem;
                          color:var(--cream-dim);">
                {voice_used}
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.audio(audio_bytes, format="audio/wav")

            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

            st.download_button(
                "⬇  Download WAV Audio",
                data=audio_bytes,
                file_name="voxis_speech.wav",
                mime="audio/wav",
                use_container_width=True,
            )

    # ── FOOTER ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="voxis-footer">
      VOXIS · Powered by Azure Cognitive Services · Built with Streamlit
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
