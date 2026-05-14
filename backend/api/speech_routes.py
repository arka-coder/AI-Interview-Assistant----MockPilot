"""
MockPilot AI — FastAPI Speech Route
"""
from fastapi import APIRouter, UploadFile, File, Depends
from backend.auth.jwt_handler import get_current_user
from backend.database.models import User
from backend.services.speech_service import transcribe_bytes

router = APIRouter(prefix="/api/speech", tags=["speech"])

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...),
                     user: User = Depends(get_current_user)):
    audio_bytes = await file.read()
    import os
    ext = os.path.splitext(file.filename)[1] or ".wav"
    result = transcribe_bytes(audio_bytes, ext)
    return result
