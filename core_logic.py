# core_logic.py
import os
import time
import tempfile
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

VOICES: dict[str, dict] = {
    "Jenny (Female · Warm)": {"name": "en-US-JennyNeural", "lang": "en-US"},
    "Aria (Female · Expressive)": {"name": "en-US-AriaNeural", "lang": "en-US"},
    "Emma (Female · Cheerful)": {"name": "en-US-EmmaNeural", "lang": "en-US"},
    "Guy (Male · Neutral)": {"name": "en-US-GuyNeural", "lang": "en-US"},
    "Davis (Male · Formal)": {"name": "en-US-DavisNeural", "lang": "en-US"},
    "Brian (Male · Deep)": {"name": "en-US-BrianNeural", "lang": "en-US"},
}

LANGUAGES: dict[str, str] = {
    "English (US)": "en-US", "English (UK)": "en-GB", "Spanish": "es-ES",
    "French": "fr-FR", "German": "de-DE", "Portuguese": "pt-BR", "Japanese": "ja-JP",
}

MAX_CHARS = 3000

def get_file_ext(mime: str) -> str:
    mapping = {
        "audio/wav": "wav", "audio/x-wav": "wav", "audio/mpeg": "mp3",
        "audio/mp3": "mp3", "audio/ogg": "ogg", "audio/flac": "flac",
        "audio/m4a": "m4a", "audio/mp4": "mp4", "audio/x-m4a": "m4a", "video/mp4": "mp4",
    }
    return mapping.get(mime, "wav")

def transcribe_audio(audio_path: str, language_code: str, key: str, region: str) -> dict:
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

        def on_stopped(evt): nonlocal done; done = True

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

        if errors: return {"success": False, "text": text, "error": "; ".join(errors)}
        if not text: return {"success": False, "text": "", "error": "No speech recognised."}
        return {"success": True, "text": text, "error": None}
    except Exception as e:
        return {"success": False, "text": "", "error": str(e)}

def synthesise_speech(text: str, voice_name: str, key: str, region: str) -> dict:
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
            return {"success": False, "text": "", "error": f"OCR failed: {result.status}"}
        
        all_text, all_words = [], []
        for page in result.analyze_result.read_results:
            for line in page.lines:
                all_text.append(line.text)
                for word in line.words:
                    all_words.append({"word": word.text, "confidence": word.confidence})
        
        extracted_text = "\n".join(all_text)
        avg_confidence = sum(w["confidence"] for w in all_words) / len(all_words) if all_words else 0
        
        return {"success": True, "text": extracted_text, "word_count": len(all_words), "confidence": avg_confidence, "error": None}
    except Exception as e:
        return {"success": False, "text": "", "error": str(e)}