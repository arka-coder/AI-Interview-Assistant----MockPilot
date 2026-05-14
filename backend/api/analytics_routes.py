"""
MockPilot AI — Analytics API Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.database.models import get_db, User, InterviewSession, Question, UserAnalytics
from backend.models.schemas import AnalyticsOut
from backend.auth.jwt_handler import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/me", response_model=AnalyticsOut)
def get_my_analytics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user.id,
        InterviewSession.status == "completed"
    ).order_by(InterviewSession.started_at).all()

    if not sessions:
        return AnalyticsOut(
            total_sessions=0, total_questions=0,
            avg_overall_score=0, avg_confidence_score=0,
            avg_communication_score=0, avg_technical_score=0,
            avg_grammar_score=0, skill_scores=None,
            score_history=[], weak_areas=[], strong_areas=[]
        )

    total_q = sum(
        db.query(Question).filter(Question.session_id == s.id,
                                   Question.answer_text != None).count()
        for s in sessions
    )

    def avg(attr):
        vals = [getattr(s, attr) for s in sessions if getattr(s, attr) is not None]
        return round(sum(vals) / len(vals), 1) if vals else 0.0

    score_history = [
        {"date": s.completed_at.strftime("%Y-%m-%d") if s.completed_at else "",
         "score": s.overall_score or 0,
         "role": s.role,
         "type": s.interview_type}
        for s in sessions
    ]

    skill_map = {
        "Confidence":    avg("confidence_score"),
        "Communication": avg("communication_score"),
        "Technical":     avg("technical_score"),
        "Grammar":       avg("grammar_score"),
        "Overall":       avg("overall_score"),
    }

    sorted_skills = sorted(skill_map.items(), key=lambda x: x[1])
    weak   = [k for k, v in sorted_skills if v < 60]
    strong = [k for k, v in sorted_skills if v >= 75]

    return AnalyticsOut(
        total_sessions=len(sessions),
        total_questions=total_q,
        avg_overall_score=avg("overall_score"),
        avg_confidence_score=avg("confidence_score"),
        avg_communication_score=avg("communication_score"),
        avg_technical_score=avg("technical_score"),
        avg_grammar_score=avg("grammar_score"),
        skill_scores=skill_map,
        score_history=score_history,
        weak_areas=weak or ["No weak areas identified yet"],
        strong_areas=strong or ["Complete more interviews to identify strengths"],
    )
