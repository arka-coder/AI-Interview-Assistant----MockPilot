"""
MockPilot AI — Speech Recognition Service (Whisper)
"""
import os, sys, tempfile, re
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.config import get_settings
settings = get_settings()

_whisper_model = None

def _load_whisper():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            _whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        except ImportError:
            pass
    return _whisper_model

def transcribe_bytes(audio_bytes: bytes, ext: str = ".wav") -> dict:
    """Transcribe raw audio bytes. Returns {text, language, confidence}."""
    model = _load_whisper()
    if not model:
        return {"text": "", "language": "en", "confidence": 0.0, "error": "Whisper not installed"}
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    try:
        result = model.transcribe(tmp, fp16=False)
        return {"text": result["text"].strip(), "language": result.get("language", "en"), "confidence": 0.95}
    except Exception as e:
        return {"text": "", "language": "en", "confidence": 0.0, "error": str(e)}
    finally:
        os.unlink(tmp)

def transcribe_file(path: str) -> dict:
    """Transcribe an audio file."""
    model = _load_whisper()
    if not model:
        return {"text": "", "language": "en", "confidence": 0.0, "error": "Whisper not installed"}
    try:
        result = model.transcribe(path, fp16=False)
        return {"text": result["text"].strip(), "language": result.get("language", "en"), "confidence": 0.95}
    except Exception as e:
        return {"text": "", "language": "en", "confidence": 0.0, "error": str(e)}

FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "literally",
                "actually", "honestly", "right", "i mean", "kind of", "sort of"]

def count_fillers(text: str) -> dict:
    text_lower = text.lower()
    return {w: len(re.findall(r'\b' + re.escape(w) + r'\b', text_lower))
            for w in FILLER_WORDS if re.search(r'\b' + re.escape(w) + r'\b', text_lower)}
