"""
MockPilot AI — Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Auth ────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Interview ────────────────────────────────────────────────────
class SessionCreate(BaseModel):
    role: str
    experience_level: str
    interview_type: str
    resume_id: Optional[int] = None

class SessionOut(BaseModel):
    id: int
    session_uuid: str
    role: str
    experience_level: str
    interview_type: str
    status: str
    overall_score: Optional[float]
    confidence_score: Optional[float]
    communication_score: Optional[float]
    technical_score: Optional[float]
    grammar_score: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_minutes: Optional[float]
    ai_summary: Optional[str]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    class Config: from_attributes = True

class AnswerSubmit(BaseModel):
    session_id: int
    question_id: int
    answer_text: str
    answer_method: str = "text"

class QuestionOut(BaseModel):
    id: int
    question_number: int
    question_text: str
    question_type: str
    answer_text: Optional[str]
    overall_score: Optional[float]
    confidence_score: Optional[float]
    communication_score: Optional[float]
    technical_score: Optional[float]
    grammar_score: Optional[float]
    ai_feedback: Optional[str]
    ideal_answer: Optional[str]
    filler_words: Optional[Dict[str, int]]
    strengths: Optional[List[str]]
    improvements: Optional[List[str]]
    class Config: from_attributes = True

class FeedbackOut(BaseModel):
    question_id: int
    overall_score: float
    confidence_score: float
    communication_score: float
    technical_score: float
    grammar_score: float
    relevance_score: float
    ai_feedback: str
    ideal_answer: str
    strengths: List[str]
    improvements: List[str]
    filler_words: Dict[str, int]
    next_question: Optional[str] = None


# ── Resume ───────────────────────────────────────────────────────
class ResumeOut(BaseModel):
    id: int
    filename: str
    ats_score: Optional[float]
    extracted_skills: Optional[Any]
    detected_roles: Optional[List[str]]
    keyword_matches: Optional[List[str]]
    missing_keywords: Optional[List[str]]
    improvement_suggestions: Optional[List[str]]
    uploaded_at: datetime
    class Config: from_attributes = True


# ── Analytics ────────────────────────────────────────────────────
class AnalyticsOut(BaseModel):
    total_sessions: int
    total_questions: int
    avg_overall_score: float
    avg_confidence_score: float
    avg_communication_score: float
    avg_technical_score: float
    avg_grammar_score: float
    skill_scores: Optional[Dict[str, float]]
    score_history: Optional[List[Dict[str, Any]]]
    weak_areas: Optional[List[str]]
    strong_areas: Optional[List[str]]
    class Config: from_attributes = True
