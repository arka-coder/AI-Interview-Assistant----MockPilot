"""
MockPilot AI — Interview Session API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid, sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.database.models import get_db, InterviewSession, Question, User, UserAnalytics
from backend.models.schemas import SessionCreate, SessionOut, AnswerSubmit, FeedbackOut, QuestionOut
from backend.auth.jwt_handler import get_current_user
from backend.services import ai_service

router = APIRouter(prefix="/api/interview", tags=["interview"])
MAX_QUESTIONS = 10


@router.post("/start", response_model=SessionOut, status_code=201)
def start_session(payload: SessionCreate,
                  db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    """Create a new interview session and generate the first question."""
    session = InterviewSession(
        user_id=payload.user_id if hasattr(payload, 'user_id') else user.id,
        session_uuid=str(uuid.uuid4()),
        role=payload.role,
        experience_level=payload.experience_level,
        interview_type=payload.interview_type,
        status="active",
    )
    # Override user_id from token
    session.user_id = user.id
    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate first question
    first_q = ai_service.generate_first_question(
        role=payload.role,
        experience_level=payload.experience_level,
        interview_type=payload.interview_type,
    )
    q = Question(session_id=session.id, question_number=1, question_text=first_q)
    db.add(q)
    db.commit()

    return SessionOut.model_validate(session)


@router.get("/{session_id}/current-question", response_model=QuestionOut)
def get_current_question(session_id: int,
                         db: Session = Depends(get_db),
                         user: User = Depends(get_current_user)):
    """Get the latest unanswered question for a session."""
    session = _get_session(session_id, user.id, db)
    q = (db.query(Question)
           .filter(Question.session_id == session_id, Question.answer_text == None)
           .order_by(Question.question_number)
           .first())
    if not q:
        raise HTTPException(status_code=404, detail="No pending question")
    return QuestionOut.model_validate(q)


@router.post("/answer", response_model=FeedbackOut)
def submit_answer(payload: AnswerSubmit,
                  db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    """Submit an answer, evaluate it, and generate the next question."""
    session = _get_session(payload.session_id, user.id, db)
    q = db.query(Question).filter(Question.id == payload.question_id,
                                   Question.session_id == payload.session_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    # Evaluate answer
    feedback = ai_service.evaluate_answer(
        question=q.question_text,
        answer=payload.answer_text,
        role=session.role,
        experience_level=session.experience_level,
        interview_type=session.interview_type,
    )

    # Persist answer & scores
    q.answer_text        = payload.answer_text
    q.answer_method      = payload.answer_method
    q.overall_score      = feedback.get("overall_score", 0)
    q.confidence_score   = feedback.get("confidence_score", 0)
    q.communication_score= feedback.get("communication_score", 0)
    q.technical_score    = feedback.get("technical_score", 0)
    q.grammar_score      = feedback.get("grammar_score", 0)
    q.relevance_score    = feedback.get("relevance_score", 0)
    q.ai_feedback        = feedback.get("ai_feedback", "")
    q.ideal_answer       = feedback.get("ideal_answer", "")
    q.filler_words       = feedback.get("filler_words", {})
    q.strengths          = feedback.get("strengths", [])
    q.improvements       = feedback.get("improvements", [])
    q.answered_at        = datetime.utcnow()
    db.commit()

    # Determine next question
    answered_count = db.query(Question).filter(
        Question.session_id == payload.session_id,
        Question.answer_text != None
    ).count()

    next_q_text = None
    if answered_count < MAX_QUESTIONS:
        history = [{"question": row.question_text, "answer": row.answer_text}
                   for row in db.query(Question)
                                .filter(Question.session_id == payload.session_id,
                                        Question.answer_text != None)
                                .order_by(Question.question_number).all()]
        next_q_text = ai_service.generate_follow_up(
            role=session.role, experience_level=session.experience_level,
            interview_type=session.interview_type,
            history=history, question_number=answered_count + 1
        )
        nq = Question(session_id=session.id, question_number=answered_count + 1,
                      question_text=next_q_text)
        db.add(nq)
        db.commit()
    else:
        # Complete the session
        _complete_session(session, db)

    return FeedbackOut(
        question_id=q.id, next_question=next_q_text,
        overall_score=q.overall_score, confidence_score=q.confidence_score,
        communication_score=q.communication_score, technical_score=q.technical_score,
        grammar_score=q.grammar_score, relevance_score=q.relevance_score,
        ai_feedback=q.ai_feedback, ideal_answer=q.ideal_answer,
        strengths=q.strengths or [], improvements=q.improvements or [],
        filler_words=q.filler_words or {}
    )


@router.post("/{session_id}/complete", response_model=SessionOut)
def complete_session(session_id: int,
                     db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    session = _get_session(session_id, user.id, db)
    _complete_session(session, db)
    return SessionOut.model_validate(session)


@router.get("/history", response_model=list[SessionOut])
def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = (db.query(InterviewSession)
                  .filter(InterviewSession.user_id == user.id)
                  .order_by(InterviewSession.started_at.desc())
                  .limit(20).all())
    return [SessionOut.model_validate(s) for s in sessions]


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    return SessionOut.model_validate(_get_session(session_id, user.id, db))


@router.delete("/all")
def clear_all_sessions(db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    """Delete every session + question for this user and reset analytics."""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user.id
    ).all()
    for s in sessions:
        db.query(Question).filter(Question.session_id == s.id).delete()
        db.delete(s)

    # Reset analytics
    analytics = db.query(UserAnalytics).filter(
        UserAnalytics.user_id == user.id
    ).first()
    if analytics:
        db.delete(analytics)

    db.commit()
    return {"message": "All sessions cleared", "deleted": len(sessions)}


# ── Helpers ──────────────────────────────────────────────────────

def _get_session(session_id: int, user_id: int, db: Session) -> InterviewSession:
    s = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user_id
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s

def _complete_session(session: InterviewSession, db: Session):
    """Calculate aggregate scores and mark session complete."""
    qs = db.query(Question).filter(
        Question.session_id == session.id,
        Question.answer_text != None
    ).all()
    if qs:
        session.overall_score       = round(sum(q.overall_score or 0 for q in qs) / len(qs), 1)
        session.confidence_score    = round(sum(q.confidence_score or 0 for q in qs) / len(qs), 1)
        session.communication_score = round(sum(q.communication_score or 0 for q in qs) / len(qs), 1)
        session.technical_score     = round(sum(q.technical_score or 0 for q in qs) / len(qs), 1)
        session.grammar_score       = round(sum(q.grammar_score or 0 for q in qs) / len(qs), 1)
    session.status       = "completed"
    session.completed_at = datetime.utcnow()
    if session.started_at:
        diff = (session.completed_at - session.started_at).total_seconds()
        session.duration_minutes = round(diff / 60, 1)
    db.commit()
