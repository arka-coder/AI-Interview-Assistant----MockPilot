"""
MockPilot AI — Live Voice Chat Route
POST /api/voice/transcribe-only  → transcribe audio bytes → return transcript
POST /api/voice/chat             → transcribe + AI response
"""
import os, sys, json
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.auth.jwt_handler import get_current_user
from backend.database.models import User
from backend.services.voice_service import transcribe_audio_groq, generate_voice_response

router = APIRouter(prefix="/api/voice", tags=["voice"])


def _ext_from_upload(upload: UploadFile) -> str:
    """Best-effort extension from uploaded file's filename/content-type."""
    if upload.filename:
        ext = os.path.splitext(upload.filename)[1].lower()
        if ext:
            return ext
    ct = (upload.content_type or "").lower()
    if "webm" in ct:    return ".webm"
    if "ogg"  in ct:    return ".ogg"
    if "mp4"  in ct:    return ".mp4"
    if "mpeg" in ct:    return ".mp3"
    if "wav"  in ct:    return ".wav"
    if "flac" in ct:    return ".flac"
    if "opus" in ct:    return ".opus"
    return ".webm"      # safest default


@router.post("/transcribe-only")
async def transcribe_only(
    audio: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """
    Transcribe audio to text using Groq Whisper.
    Returns {transcript, error}.
    """
    raw = await audio.read()
    hint = _ext_from_upload(audio)

    transcript, error = transcribe_audio_groq(raw, hint)

    if error:
        # Return 200 with error field so frontend can display the message
        return JSONResponse({"transcript": "", "error": error}, status_code=200)

    return JSONResponse({"transcript": transcript, "error": None})


@router.post("/chat")
async def voice_chat(
    audio: UploadFile = File(...),
    session_id: str = Form(default=""),
    role: str = Form(default="Software Engineer"),
    interview_type: str = Form(default="Technical"),
    experience_level: str = Form(default="mid"),
    question_context: str = Form(default=""),
    conversation_history: str = Form(default="[]"),
    user: User = Depends(get_current_user),
):
    """Transcribe + generate AI response for live voice chat."""
    raw = await audio.read()
    hint = _ext_from_upload(audio)

    transcript, error = transcribe_audio_groq(raw, hint)
    if error:
        return JSONResponse({"transcript": "", "ai_response": "", "tts_text": "", "error": error})

    try:
        history = json.loads(conversation_history)
    except Exception:
        history = []

    ai_response = generate_voice_response(
        transcript=transcript,
        role=role,
        interview_type=interview_type,
        experience_level=experience_level,
        question_context=question_context,
        history=history,
    )

    return JSONResponse({
        "transcript": transcript,
        "ai_response": ai_response,
        "tts_text": ai_response,
        "error": None,
    })
