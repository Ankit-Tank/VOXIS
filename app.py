# app.py
import os
import tempfile
import json
import streamlit as st

# Import our custom modules
from core_logic import transcribe_audio, synthesise_speech, extract_ocr, get_file_ext, VOICES, LANGUAGES, MAX_CHARS
from ui_components import get_header_html, get_panel_html, get_info_box_html, get_result_html, get_confidence_box_html, get_footer_html

st.set_page_config(page_title="VOXIS · AI Voice Studio", page_icon="🎙", layout="wide", initial_sidebar_state="collapsed")

# Inject CSS File
def load_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css("style.css")
except FileNotFoundError:
    st.warning("style.css not found.")

@st.cache_resource(show_spinner=False)
def load_credentials() -> tuple[str, str, str, str]:
    try:
        return st.secrets["AZURE_SPEECH_KEY"], st.secrets["AZURE_SPEECH_REGION"], st.secrets["AZURE_VISION_ENDPOINT"], st.secrets["AZURE_VISION_KEY"]
    except KeyError as e:
        st.error(f"⚠️ Missing secret: `{e}`.")
        st.stop()

def main():
    AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AZURE_VISION_ENDPOINT, AZURE_VISION_KEY = load_credentials()

    st.markdown(get_header_html(), unsafe_allow_html=True)
    tab_stt, tab_tts, tab_ocr = st.tabs(["🎤  Voice → Text", "🔊  Text → Voice", "📸  Image → Text"])

    # TAB 1 — SPEECH TO TEXT
    with tab_stt:
        st.markdown(get_panel_html("01", "Speech Recognition", "Upload any audio recording and VOXIS will transcribe it..."), unsafe_allow_html=True)
        col_lang, col_upload = st.columns([1, 2], gap="medium")

        with col_lang:
            selected_lang_label = st.selectbox("Recognition Language", options=list(LANGUAGES.keys()), index=0, key="stt_lang")
            lang_code = LANGUAGES[selected_lang_label]
            st.markdown(get_info_box_html("Supported Formats", "WAV"), unsafe_allow_html=True)

        with col_upload:
            uploaded_file = st.file_uploader("Drop your audio file here", type=["wav"], key="stt_file", label_visibility="collapsed")
            if uploaded_file: st.audio(uploaded_file, format=uploaded_file.type)

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

                if outcome["success"]: st.session_state["stt_result"] = outcome["text"]
                else: st.error(f"❌ {outcome['error']}")

        if st.session_state.get("stt_result"):
            text = st.session_state["stt_result"]
            st.markdown(get_result_html(text, "Transcribed Output"), unsafe_allow_html=True)
            col1, col2 = st.columns(2, gap="small")
            with col1: st.download_button("⬇ Download as .txt", text, "voxis_transcript.txt", "text/plain", use_container_width=True)
            with col2:
                payload = json.dumps({"transcript": text, "language": selected_lang_label, "words": len(text.split()), "characters": len(text)}, indent=2)
                st.download_button("⬇ Download as .json", payload, "voxis_transcript.json", "application/json", use_container_width=True)

    # TAB 2 — TEXT TO SPEECH
    with tab_tts:
        st.markdown(get_panel_html("02", "Neural Text-to-Speech", "Type or paste your text and choose from premium Azure Neural voices..."), unsafe_allow_html=True)
        col_v, col_t = st.columns([1, 2], gap="medium")

        with col_v:
            selected_voice_label = st.selectbox("Neural Voice", options=list(VOICES.keys()), index=0, key="tts_voice")
            voice_name = VOICES[selected_voice_label]["name"]
            st.markdown(get_info_box_html("Selected Voice", f"<b>{selected_voice_label.split(' (')[0]}</b>"), unsafe_allow_html=True)

        with col_t:
            tts_text = st.text_area("Input Text", placeholder="Begin typing your text here…", height=200, max_chars=MAX_CHARS, key="tts_input")
            char_count = len(tts_text) if tts_text else 0
            cls = "danger" if char_count / MAX_CHARS > 0.9 else ""
            st.markdown(f'<div class="char-counter {cls}">{char_count:,} / {MAX_CHARS:,} characters</div>', unsafe_allow_html=True)

        if st.button("✦ Synthesise Speech", key="btn_synth", use_container_width=True):
            if not tts_text or not tts_text.strip():
                st.warning("Please enter some text to synthesise.")
            else:
                with st.spinner("Generating audio…"):
                    outcome = synthesise_speech(tts_text.strip(), voice_name, AZURE_SPEECH_KEY, AZURE_SPEECH_REGION)
                if outcome["success"]:
                    st.session_state["tts_audio"] = outcome["audio"]
                else:
                    st.error(f"❌ {outcome['error']}")

        if st.session_state.get("tts_audio"):
            st.markdown("<div style='margin:1.5rem 0;height:1px;background:var(--border);'></div>", unsafe_allow_html=True)
            st.audio(st.session_state["tts_audio"], format="audio/wav")
            st.download_button("⬇ Download WAV Audio", st.session_state["tts_audio"], "voxis_speech.wav", "audio/wav", use_container_width=True)

    # TAB 3 — OCR (IMAGE TO TEXT)
    with tab_ocr:
        st.markdown(get_panel_html("03", "Image OCR", "Upload an image and VOXIS will instantly extract all text..."), unsafe_allow_html=True)
        col_info, col_upload = st.columns([1, 2], gap="medium")

        with col_info:
            st.markdown(get_info_box_html("Supported Formats", "JPG · PNG · BMP · TIFF"), unsafe_allow_html=True)

        with col_upload:
            uploaded_image = st.file_uploader("Drop your image here", type=["jpg", "jpeg", "png", "bmp", "tiff"], key="ocr_file", label_visibility="collapsed")
            if uploaded_image: st.image(uploaded_image, use_container_width=True)

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
                else: st.error(f"❌ {outcome['error']}")

        if st.session_state.get("ocr_result"):
            text = st.session_state["ocr_result"]
            confidence = st.session_state.get("ocr_confidence", 0)
            
            st.markdown(get_result_html(text, "Extracted Text"), unsafe_allow_html=True)
            st.markdown(get_confidence_box_html(confidence), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2, gap="small")
            with col1: st.download_button("⬇ Download as .txt", text, "voxis_ocr.txt", "text/plain", use_container_width=True)
            with col2:
                payload = json.dumps({"extracted_text": text, "word_count": len(text.split()), "character_count": len(text), "confidence": float(confidence)}, indent=2)
                st.download_button("⬇ Download as .json", payload, "voxis_ocr.json", "application/json", use_container_width=True)

    st.markdown(get_footer_html(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()