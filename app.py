"""
VOXIS — AI Voice Studio + OCR
Azure Cognitive Services Speech SDK + Computer Vision
Credentials are loaded exclusively from st.secrets (never hardcoded)
"""

import os
import time
import tempfile
import json
import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

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
  resize: vertical !important;
}

/* buttons */
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

/* download button */
[data-testid="stDownloadButton"] > button {
  background: transparent !important;
  color: var(--gold) !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
  border: 1px solid var(--gold-dim) !important;
  border-radius: 50px !important;
  padding: 0.7rem 2rem !important;
  width: 100% !important;
  transition: all 0.3s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: rgba(201,168,76,0.1) !important;
  border-color: var(--gold) !important;
}

/* audio player */
[data-testid="stAudio"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  padding: 0.5rem !important;
}

/* image display */
[data-testid="stImage"] {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  overflow: hidden !important;
}

/* alerts */
[data-testid="stAlert"] {
  background: var(--surface-2) !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid !important;
  font-family: var(--font-ui) !important;
}

/* spinner */
[data-testid="stSpinner"] { color: var(--gold) !important; }

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
}
.result-text {
  font-family: var(--font-ui);
  font-size: 1.05rem;
  line-height: 1.75;
  color: var(--white);
  white-space: pre-wrap;
  word-break: break-word;
}

/* stat chips */
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
}
.stat-chip b { color: var(--gold); font-weight: 500; }

/* char counter */
.char-counter {
  text-align: right;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--cream-dim);
  margin-top: 0.3rem;
}

/* ── FOOTER ──────────────────────────────────────────── */
.voxis-footer {
  text-align: center;
  padding: 2rem 0 1rem;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  margin-top: 2rem;
  line-height: 1.9;

  background: linear-gradient(
      90deg,
      #C9A84C 0%,
      #F7E7A1 50%,
      #C9A84C 100%
  );

  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;

  text-shadow:
      0 0 10px rgba(201,168,76,0.35),
      0 0 20px rgba(201,168,76,0.15);

  border-top: 1px solid rgba(201,168,76,0.15);
}

/* ── MODE TABS ────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 50px !important;
  padding: 4px !important;
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
}
[data-testid="stTabs"] [aria-selected="true"] {
  background: linear-gradient(135deg, var(--gold-dim), var(--gold)) !important;
  color: var(--obsidian) !important;
  box-shadow: 0 3px 16px rgba(201,168,76,0.35) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* status badge */
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
  50% { opacity: 0.5; transform: scale(0.8); }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CREDENTIAL LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_credentials() -> tuple[str, str, str, str]:
    """Load Azure credentials from Streamlit secrets."""
    try:
        speech_key = st.secrets["AZURE_SPEECH_KEY"]
        speech_region = st.secrets["AZURE_SPEECH_REGION"]
        vision_endpoint = st.secrets["AZURE_VISION_ENDPOINT"]
        vision_key = st.secrets["AZURE_VISION_KEY"]
        return speech_key, speech_region, vision_endpoint, vision_key
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
    "Jenny (Female · Warm)": {"name": "en-US-JennyNeural", "lang": "en-US"},
    "Aria (Female · Expressive)": {"name": "en-US-AriaNeural", "lang": "en-US"},
    "Emma (Female · Cheerful)": {"name": "en-US-EmmaNeural", "lang": "en-US"},
    "Guy (Male · Neutral)": {"name": "en-US-GuyNeural", "lang": "en-US"},
    "Davis (Male · Formal)": {"name": "en-US-DavisNeural", "lang": "en-US"},
    "Brian (Male · Deep)": {"name": "en-US-BrianNeural", "lang": "en-US"},
}

LANGUAGES: dict[str, str] = {
    "English (US)": "en-US",
    "English (UK)": "en-GB",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Portuguese": "pt-BR",
    "Japanese": "ja-JP",
}

MAX_CHARS = 3000


def transcribe_audio(audio_path: str, language_code: str, key: str, region: str) -> dict:
    """Transcribe audio using Azure Speech SDK."""
    try:
        config = speechsdk.SpeechConfig(subscription=key, region=region)
        config.speech_recognition_language = language_code

        audio_cfg = speechsdk.audio.AudioConfig(filename=audio_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config=config, audio_config=audio_cfg)

        results, errors = [], []
        done = False

        def on_recognized(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                results.append(evt.result.text)

        def on_canceled(evt):
            nonlocal done
            if evt.result.cancellation_details.reason == speechsdk.CancellationReason.Error:
                errors.append(evt.result.cancellation_details.error_details)
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
            return {"success": False, "text": text, "error": "; ".join(errors)}
        if not text:
            return {"success": False, "text": "", "error": "No speech recognised."}
        return {"success": True, "text": text, "error": None}
    except Exception as e:
        return {"success": False, "text": "", "error": str(e)}


def synthesise_speech(text: str, voice_name: str, key: str, region: str) -> dict:
    """Synthesise speech from text."""
    try:
        config = speechsdk.SpeechConfig(subscription=key, region=region)
        config.speech_synthesis_voice_name = voice_name

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()

        audio_cfg = speechsdk.audio.AudioOutputConfig(filename=tmp.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio_cfg)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            with open(tmp.name, "rb") as fh:
                audio_bytes = fh.read()
            os.unlink(tmp.name)
            return {"success": True, "audio": audio_bytes, "error": None}

        os.unlink(tmp.name)
        return {"success": False, "audio": None, "error": str(result.cancellation_details.error_details)}
    except Exception as e:
        return {"success": False, "audio": None, "error": str(e)}


def extract_ocr(image_path: str, endpoint: str, key: str) -> dict:
    """Extract text from image using Azure Computer Vision OCR."""
    try:
        client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
        
        with open(image_path, "rb") as img:
            response = client.read_in_stream(img, raw=True)
        
        operation_id = response.headers["Operation-Location"].split("/")[-1]
        elapsed = 0
        
        while elapsed < 30:
            result = client.get_read_result(operation_id)
            if result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            time.sleep(1)
            elapsed += 1
        
        if result.status != OperationStatusCodes.succeeded:
            return {"success": False, "text": "", "error": f"OCR failed with status: {result.status}"}
        
        all_text = []
        all_words = []
        
        for page in result.analyze_result.read_results:
            for line in page.lines:
                all_text.append(line.text)
                for word in line.words:
                    all_words.append({"word": word.text, "confidence": word.confidence})
        
        extracted_text = "\n".join(all_text)
        avg_confidence = sum(w["confidence"] for w in all_words) / len(all_words) if all_words else 0
        
        return {
            "success": True,
            "text": extracted_text,
            "word_count": len(all_words),
            "confidence": avg_confidence,
            "error": None,
        }
    except Exception as e:
        return {"success": False, "text": "", "error": str(e)}


def render_header():
    """Render app header."""
    bars = "".join(["<span></span>"] * 10)
    st.markdown(f"""
    <div class="voxis-header">
      <div class="voxis-eyebrow">Azure Cognitive Services · AI Voice Studio</div>
      <div class="voxis-wordmark">VOXIS</div>
      <div class="voxis-tagline">Transform Voice · Transcribe Speech · Synthesise Sound · Extract Text</div>
      <div class="voxis-divider"></div>
      <div class="waveform-deco">{bars}</div>
    </div>
    """, unsafe_allow_html=True)


def render_result(text: str, label: str = "Extracted Output"):
    """Render result box."""
    word_count = len(text.split())
    char_count = len(text)
    st.markdown(f"""
    <div class="result-box">
      <div class="result-label">✦ {label}</div>
      <div class="result-text">{text}</div>
      <div class="stat-row">
        <div class="stat-chip"><b>{word_count}</b> words</div>
        <div class="stat-chip"><b>{char_count}</b> characters</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def get_file_ext(mime: str) -> str:
    """Get file extension from MIME type."""
    mapping = {
        "audio/wav": "wav", "audio/x-wav": "wav", "audio/mpeg": "mp3",
        "audio/mp3": "mp3", "audio/ogg": "ogg", "audio/flac": "flac",
        "audio/m4a": "m4a", "audio/mp4": "mp4", "audio/x-m4a": "m4a",
        "video/mp4": "mp4",
    }
    return mapping.get(mime, "wav")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AZURE_VISION_ENDPOINT, AZURE_VISION_KEY = load_credentials()

    render_header()

    # Tabs
    tab_stt, tab_tts, tab_ocr = st.tabs(["🎤  Voice → Text", "🔊  Text → Voice", "📸  Image → Text"])

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
            <div style="background:var(--surface-2);border:1px solid var(--border-soft);
                        border-radius:var(--radius-md);padding:1rem 1.2rem;margin-top:0.8rem;">
              <div style="font-family:var(--font-mono);font-size:0.6rem;
                          letter-spacing:0.25em;color:var(--gold);text-transform:uppercase;">
                Supported Formats
              </div>
              <div style="font-size:0.78rem;color:var(--cream-dim);margin-top:0.6rem;">
                WAV · MP3 · OGG · FLAC · M4A
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

        if st.button("✦ Transcribe Audio", key="btn_transcribe", use_container_width=True):
            if not uploaded_file:
                st.warning("Please upload an audio file first.")
            else:
                ext = get_file_ext(uploaded_file.type)
                with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                with st.spinner("Transcribing…"):
                    outcome = transcribe_audio(tmp_path, lang_code, AZURE_SPEECH_KEY, AZURE_SPEECH_REGION)

                os.unlink(tmp_path)

                if outcome["success"]:
                    st.session_state["stt_result"] = outcome["text"]
                else:
                    st.error(f"❌ {outcome['error']}")

        if st.session_state.get("stt_result"):
            text = st.session_state["stt_result"]
            render_result(text, "Transcribed Output")
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

            col1, col2 = st.columns(2, gap="small")
            with col1:
                st.download_button(
                    "⬇  Download as .txt",
                    data=text,
                    file_name="voxis_transcript.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col2:
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
            Type or paste your text and choose from premium Azure Neural voices.
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
            <div style="background:var(--surface-2);border:1px solid var(--border);
                        border-radius:var(--radius-md);padding:1rem 1.2rem;margin-top:0.8rem;">
              <div style="font-family:var(--font-mono);font-size:0.6rem;
                          letter-spacing:0.25em;color:var(--gold);text-transform:uppercase;">
                Selected Voice
              </div>
              <div style="font-size:0.9rem;color:var(--white);font-weight:600;margin-top:0.5rem;">
                {selected_voice_label.split(" (")[0]}
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
                f'<div class="char-counter {cls}">{char_count:,} / {MAX_CHARS:,} characters</div>',
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        if st.button("✦ Synthesise Speech", key="btn_synth", use_container_width=True):
            if not tts_text or not tts_text.strip():
                st.warning("Please enter some text to synthesise.")
            else:
                with st.spinner("Generating audio…"):
                    outcome = synthesise_speech(tts_text.strip(), voice_name, AZURE_SPEECH_KEY, AZURE_SPEECH_REGION)

                if outcome["success"]:
                    st.session_state["tts_audio"] = outcome["audio"]
                    st.session_state["tts_voice_used"] = selected_voice_label
                else:
                    st.error(f"❌ {outcome['error']}")

        if st.session_state.get("tts_audio"):
            st.markdown("<div style='margin:1.5rem 0;height:1px;background:var(--border);'></div>", unsafe_allow_html=True)
            st.audio(st.session_state["tts_audio"], format="audio/wav")
            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
            st.download_button(
                "⬇  Download WAV Audio",
                data=st.session_state["tts_audio"],
                file_name="voxis_speech.wav",
                mime="audio/wav",
                use_container_width=True,
            )

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 3 — OCR (IMAGE TO TEXT)
    # ═════════════════════════════════════════════════════════════════════════
    with tab_ocr:
        st.markdown("""
        <div class="panel">
          <div class="panel-label">03 &nbsp; Extract Text</div>
          <div class="panel-title">Image OCR</div>
          <div class="panel-desc">
            Upload an image and VOXIS will instantly extract all text using
            Azure Computer Vision OCR with support for 100+ languages and
            precise character recognition.
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_info, col_upload = st.columns([1, 2], gap="medium")

        with col_info:
            st.markdown("""
            <div style="background:var(--surface-2);border:1px solid var(--border-soft);
                        border-radius:var(--radius-md);padding:1rem 1.2rem;margin-top:0rem;">
              <div style="font-family:var(--font-mono);font-size:0.6rem;
                          letter-spacing:0.25em;color:var(--gold);text-transform:uppercase;">
                Supported Formats
              </div>
              <div style="font-size:0.78rem;color:var(--cream-dim);margin-top:0.6rem;line-height:1.8;">
                JPG · PNG · BMP · PDF · TIFF
              </div>
            </div>
            """, unsafe_allow_html=True)

        with col_upload:
            uploaded_image = st.file_uploader(
                "Drop your image here",
                type=["jpg", "jpeg", "png", "bmp", "tiff"],
                key="ocr_file",
                label_visibility="collapsed",
            )
            if uploaded_image:
                st.image(uploaded_image, use_container_width=True)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        if st.button("✦ Extract Text", key="btn_ocr", use_container_width=True):
            if not uploaded_image:
                st.warning("Please upload an image first.")
            else:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    tmp.write(uploaded_image.read())
                    tmp_path = tmp.name

                with st.spinner("Extracting text…"):
                    outcome = extract_ocr(tmp_path, AZURE_VISION_ENDPOINT, AZURE_VISION_KEY)

                os.unlink(tmp_path)

                if outcome["success"]:
                    st.session_state["ocr_result"] = outcome["text"]
                    st.session_state["ocr_confidence"] = outcome["confidence"]
                else:
                    st.error(f"❌ {outcome['error']}")

        if st.session_state.get("ocr_result"):
            text = st.session_state["ocr_result"]
            confidence = st.session_state.get("ocr_confidence", 0)
            
            render_result(text, "Extracted Text")
            
            st.markdown(f"""
            <div style="margin-top:1rem;padding:0.8rem;background:var(--surface-3);
                        border:1px solid var(--border-soft);border-radius:var(--radius-md);">
              <div style="font-family:var(--font-mono);font-size:0.62rem;
                          letter-spacing:0.15em;color:var(--gold);text-transform:uppercase;">
                Recognition Confidence
              </div>
              <div style="font-size:1.1rem;color:var(--white);font-weight:600;margin-top:0.4rem;">
                {confidence:.1%}
              </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

            col1, col2 = st.columns(2, gap="small")
            with col1:
                st.download_button(
                    "⬇  Download as .txt",
                    data=text,
                    file_name="voxis_ocr.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col2:
                payload = json.dumps({
                    "extracted_text": text,
                    "word_count": len(text.split()),
                    "character_count": len(text),
                    "confidence": float(confidence),
                }, indent=2)
                st.download_button(
                    "⬇  Download as .json",
                    data=payload,
                    file_name="voxis_ocr.json",
                    mime="application/json",
                    use_container_width=True,
                )

    # ── FOOTER ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="voxis-footer">
      VOXIS · Powered by Azure Cognitive Services · Built with Streamlit<br>
      Made by Ankit Tank
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()