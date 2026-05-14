"""
MockPilot AI — FastAPI Application Entry Point
Run with: uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.config import get_settings
from backend.database.models import init_db
from backend.api import auth_routes, interview_routes, resume_routes, analytics_routes, speech_routes, voice_routes, quick_scan_routes

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    yield


app = FastAPI(
    title="MockPilot AI",
    description="Your AI Interview Co-Pilot — Backend API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────
app.include_router(auth_routes.router)
app.include_router(interview_routes.router)
app.include_router(resume_routes.router)
app.include_router(analytics_routes.router)
app.include_router(speech_routes.router)
app.include_router(voice_routes.router)
app.include_router(quick_scan_routes.router)


@app.get("/", tags=["health"])
def root():
    return {"app": "MockPilot AI", "version": settings.APP_VERSION, "status": "running"}

@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
