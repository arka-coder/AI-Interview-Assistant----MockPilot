"""
MockPilot AI — Resume API Routes
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
import os, sys, shutil, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.database.models import get_db, User, Resume
from backend.models.schemas import ResumeOut
from backend.auth.jwt_handler import get_current_user
from backend.services import resume_service
from backend.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/resume", tags=["resume"])
ALLOWED_EXTS = {".pdf", ".docx", ".doc", ".txt"}


@router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(file: UploadFile = File(...),
                        db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size_kb = os.path.getsize(file_path) / 1024
    if file_size_kb > settings.MAX_UPLOAD_SIZE_MB * 1024:
        os.remove(file_path)
        raise HTTPException(status_code=413, detail="File too large")

    # Extract & analyze
    raw_text = resume_service.extract_text(file_path)
    skills   = resume_service.extract_skills(raw_text)
    roles    = resume_service.detect_roles(raw_text)
    ats      = resume_service.ats_analysis(raw_text)

    resume = Resume(
        user_id=user.id,
        filename=file.filename,
        file_path=file_path,
        file_size_kb=round(file_size_kb, 1),
        raw_text=raw_text,
        extracted_skills=skills,
        detected_roles=roles,
        ats_score=ats["ats_score"],
        keyword_matches=ats["matched"],
        missing_keywords=ats["missing"],
        improvement_suggestions=ats["suggestions"],
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return ResumeOut.model_validate(resume)


@router.get("/list", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resumes = db.query(Resume).filter(Resume.user_id == user.id)\
                              .order_by(Resume.uploaded_at.desc()).all()
    return [ResumeOut.model_validate(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    r = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    return ResumeOut.model_validate(r)


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    r = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    if os.path.exists(r.file_path):
        os.remove(r.file_path)
    db.delete(r)
    db.commit()
