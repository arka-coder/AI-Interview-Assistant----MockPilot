"""
MockPilot AI — Voice Service
Groq Whisper API transcription + conversational AI for voice interviews.
"""
import os, sys, tempfile, re
from typing import Optional, List
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.config import get_settings

settings = get_settings()
client = Groq(api_key=settings.GROQ_API_KEY)

# Groq Whisper supported extensions
GROQ_ALLOWED = {".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a",
                ".ogg", ".opus", ".wav", ".webm"}


def _detect_ext(audio_bytes: bytes, hint_ext: str = ".webm") -> str:
    """
    Detect real audio format from magic bytes.
    Falls back to hint_ext, then .webm.
    """
    if len(audio_bytes) < 4:
        return ".webm"

    sig = audio_bytes[:12]

    # WebM / MKV — starts with 0x1A 0x45 0xDF 0xA3
    if sig[:4] == b'\x1a\x45\xdf\xa3':
        return ".webm"

    # OGG — starts with OggS
    if sig[:4] == b'OggS':
        return ".ogg"

    # MP3 — ID3 tag or 0xFF 0xFB/0xFA/0xF3
    if sig[:3] == b'ID3' or sig[0] == 0xFF and sig[1] in (0xFB, 0xFA, 0xF3, 0xE3):
        return ".mp3"

    # WAV — RIFF....WAVE
    if sig[:4] == b'RIFF' and sig[8:12] == b'WAVE':
        return ".wav"

    # FLAC
    if sig[:4] == b'fLaC':
        return ".flac"

    # MP4 / M4A — ftyp box at offset 4
    if sig[4:8] in (b'ftyp', b'moov', b'mdat'):
        return ".mp4"

    # Use hint if it's a known type
    clean = hint_ext if hint_ext.startswith(".") else f".{hint_ext}"
    if clean in GROQ_ALLOWED:
        return clean

    return ".webm"  # safest default — Groq handles it well


def transcribe_audio_groq(audio_bytes: bytes, hint_ext: str = ".webm") -> tuple[str, str]:
    """
    Transcribe audio bytes using Groq's hosted Whisper large-v3-turbo.
    Returns (transcript, error_message). On success error_message is "".
    """
    if not audio_bytes or len(audio_bytes) < 500:
        return "", "Audio is too short or empty. Please record for at least 1 second."

    ext = _detect_ext(audio_bytes, hint_ext)
    print(f"[VoiceService] Audio size={len(audio_bytes)}B  detected_ext={ext}  hint={hint_ext}")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=(os.path.basename(tmp_path), audio_file, f"audio/{ext.lstrip('.')}"),
                response_format="text",
                language="en",
            )
        text = transcription if isinstance(transcription, str) else str(transcription)
        text = text.strip()
        if not text:
            return "", "Transcription came back empty. Speak clearly and try again."
        print(f"[VoiceService] Transcript: {text[:80]}")
        return text, ""
    except Exception as e:
        err = str(e)
        print(f"[VoiceService] Groq Whisper error: {err}")
        return "", f"Transcription failed: {err[:120]}"
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


# ── AI Voice Conversation ─────────────────────────────────────────────────────

VOICE_INTERVIEWER_PROMPT = """You are an expert AI interviewer conducting a live voice interview.
Your responses must be:
- Concise (2-4 sentences MAX) — this is a spoken conversation
- Natural and conversational — no bullet points, no markdown, no lists
- Professional but warm — like a senior interviewer on a real call
- Acknowledge the candidate's answer briefly, then ask the next question
- Keep responses under 80 words for smooth TTS playback
- Never use special characters, asterisks, or formatting symbols"""


def generate_voice_response(
    transcript: str,
    role: str = "Software Engineer",
    interview_type: str = "Technical",
    experience_level: str = "mid",
    question_context: str = "",
    history: List[dict] = None,
) -> str:
    """Generate a natural spoken AI response. Optimized for TTS."""
    if history is None:
        history = []

    context_parts = []
    if question_context:
        context_parts.append(f"Current question: {question_context}")
    for turn in history[-4:]:
        context_parts.append(f"Candidate said: {turn.get('candidate', '')}")
        if turn.get('ai'):
            context_parts.append(f"You replied: {turn.get('ai', '')}")

    context = "\n".join(context_parts)
    user_message = (
        f"Interview context: {role} | {experience_level} level | {interview_type}\n"
        f"{context}\n\nCandidate just said: \"{transcript}\"\n\n"
        f"Respond naturally (spoken word, max 80 words). "
        f"Acknowledge briefly, then ask the next relevant question."
    )

    try:
        resp = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": VOICE_INTERVIEWER_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=150,
        )
        raw = resp.choices[0].message.content.strip()
        return re.sub(r'[*_`#\[\]{}|]', '', raw).strip()
    except Exception as e:
        print(f"[VoiceService] AI response error: {e}")
        return "I see. Could you elaborate a bit more on that?"
