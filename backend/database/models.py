"""
MockPilot AI — Database Models (SQLAlchemy ORM)
Modular design: SQLite → PostgreSQL with one config change.
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, ForeignKey, Text, Boolean, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Models ──────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id             = Column(Integer, primary_key=True, index=True)
    email          = Column(String(255), unique=True, index=True, nullable=False)
    username       = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password= Column(String(255), nullable=False)
    full_name      = Column(String(200))
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=datetime.utcnow)

    sessions  = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    resumes   = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("UserAnalytics", back_populates="user", uselist=False)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_uuid     = Column(String(36), unique=True, index=True)
    role             = Column(String(200), nullable=False)
    experience_level = Column(String(50), nullable=False)
    interview_type   = Column(String(100), nullable=False)
    status           = Column(String(20), default="active")   # active|completed|abandoned
    overall_score    = Column(Float)
    confidence_score = Column(Float)
    communication_score = Column(Float)
    technical_score  = Column(Float)
    grammar_score    = Column(Float)
    started_at       = Column(DateTime, default=datetime.utcnow)
    completed_at     = Column(DateTime)
    duration_minutes = Column(Float)
    ai_summary       = Column(Text)
    strengths        = Column(JSON)
    weaknesses       = Column(JSON)
    improvement_tips = Column(JSON)

    user      = relationship("User", back_populates="sessions")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    id               = Column(Integer, primary_key=True, index=True)
    session_id       = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_number  = Column(Integer, nullable=False)
    question_text    = Column(Text, nullable=False)
    question_type    = Column(String(50), default="open")
    answer_text      = Column(Text)
    answer_method    = Column(String(20), default="text")  # text|voice
    confidence_score = Column(Float)
    communication_score = Column(Float)
    technical_score  = Column(Float)
    grammar_score    = Column(Float)
    relevance_score  = Column(Float)
    overall_score    = Column(Float)
    ai_feedback      = Column(Text)
    ideal_answer     = Column(Text)
    filler_words     = Column(JSON)
    strengths        = Column(JSON)
    improvements     = Column(JSON)
    answered_at      = Column(DateTime)

    session = relationship("InterviewSession", back_populates="questions")


class Resume(Base):
    __tablename__ = "resumes"
    id                    = Column(Integer, primary_key=True, index=True)
    user_id               = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename              = Column(String(500), nullable=False)
    file_path             = Column(String(1000), nullable=False)
    file_size_kb          = Column(Float)
    raw_text              = Column(Text)
    extracted_skills      = Column(JSON)
    detected_roles        = Column(JSON)
    ats_score             = Column(Float)
    keyword_matches       = Column(JSON)
    missing_keywords      = Column(JSON)
    improvement_suggestions = Column(JSON)
    uploaded_at           = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class UserAnalytics(Base):
    __tablename__ = "user_analytics"
    id                    = Column(Integer, primary_key=True, index=True)
    user_id               = Column(Integer, ForeignKey("users.id"), unique=True)
    total_sessions        = Column(Integer, default=0)
    total_questions       = Column(Integer, default=0)
    avg_overall_score     = Column(Float, default=0.0)
    avg_confidence_score  = Column(Float, default=0.0)
    avg_communication_score = Column(Float, default=0.0)
    avg_technical_score   = Column(Float, default=0.0)
    avg_grammar_score     = Column(Float, default=0.0)
    skill_scores          = Column(JSON)
    score_history         = Column(JSON)   # [{date, score}, ...]
    weak_areas            = Column(JSON)
    strong_areas          = Column(JSON)
    last_updated          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="analytics")


def init_db():
    Base.metadata.create_all(bind=engine)
    print("[OK] MockPilot DB initialized.")
