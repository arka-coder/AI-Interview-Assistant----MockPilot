"""
MockPilot AI — Quick Scan API Routes
2-minute readiness assessment: resume + 2 targeted questions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid, sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.database.models import get_db, InterviewSession, Question, User
from backend.auth.jwt_handler import get_current_user
from backend.services import ai_service
from backend.services.readiness_service import (
    calculate_readiness_score,
    generate_hiring_insights,
    generate_roadmap,
)

router = APIRouter(prefix="/api/quick-scan", tags=["quick-scan"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class QuickScanStart(BaseModel):
    role: str
    experience_level: str
    interview_type: str
    resume_text: Optional[str] = None


class QuickScanAnswer(BaseModel):
    session_id: int
    q1_id: int
    q1_answer: str
    q1_method: str = "text"
    q2_id: int
    q2_answer: str
    q2_method: str = "text"
    # Resume data passed from frontend
    ats_score: Optional[float] = 0
    resume_skills: Optional[dict] = None
    missing_keywords: Optional[List[str]] = None


# ── AI Question Generator ─────────────────────────────────────────────────────

# Type-specific system instructions for generating both questions
_TYPE_INSTRUCTIONS = {
    "Technical": (
        "You are a senior technical interviewer. "
        "Generate exactly 2 distinct, role-specific technical interview questions for a {role} ({level}) candidate. "
        "Q1: A foundational conceptual question testing core technical knowledge relevant to {role}. "
        "Q2: A practical/applied question — a coding scenario, system design micro-task, or debugging problem relevant to {role}. "
        "Both must be technical in nature. Do NOT include communication or HR questions."
    ),
    "Behavioral / HR": (
        "You are an experienced behavioral/HR interviewer using the STAR method. "
        "Generate exactly 2 distinct behavioral or HR interview questions for a {role} ({level}) candidate. "
        "Q1: A leadership or collaboration scenario question (e.g. conflict resolution, cross-team work, mentorship). "
        "Q2: A challenge, growth, or achievement question (e.g. tight deadline, failure recovery, measurable impact). "
        "Both must be behavioral or cultural-fit style. Do NOT include technical coding questions."
    ),
    "System Design": (
        "You are a staff-level systems architect conducting a system design interview. "
        "Generate exactly 2 system design interview questions for a {role} ({level}) candidate. "
        "Q1: A high-level architecture question (e.g. design a scalable service, distributed system, or platform feature). "
        "Q2: A component deep-dive question (e.g. database schema design, API design, caching strategy, or load balancing). "
        "Both must require the candidate to think about scale, trade-offs, and real-world constraints."
    ),
    "Project Discussion": (
        "You are a senior engineering manager conducting a project-focused interview. "
        "Generate exactly 2 project discussion questions for a {role} ({level}) candidate. "
        "Q1: Ask the candidate to walk through their most impactful or recent project — focusing on their specific role, decisions made, and outcomes. "
        "Q2: Ask about a specific technical or process challenge they faced in a project and how they resolved it. "
        "Both should prompt detailed storytelling about real experience."
    ),
    "Problem Solving": (
        "You are an analytical interviewer assessing problem-solving and logical thinking. "
        "Generate exactly 2 problem-solving interview questions for a {role} ({level}) candidate. "
        "Q1: A logical or estimation problem (e.g. a Fermi estimate, algorithmic thinking question, or data-driven decision scenario). "
        "Q2: A real-world scenario problem relevant to {role} that requires a structured analytical approach. "
        "Both should test structured thinking, not memorised answers."
    ),
    "Rapid Fire": (
        "You are a fast-paced interviewer running a rapid-fire round. "
        "Generate exactly 2 rapid-fire interview questions for a {role} ({level}) candidate. "
        "Q1: A quick conceptual/definition question that should be answered in 1-2 sentences max (e.g. 'What is X?', 'Difference between A and B?'). "
        "Q2: A short situational or opinion question that tests clarity and decisiveness (e.g. 'Which would you choose between X and Y, and why in one sentence?'). "
        "Both should be brief and expect sharp, confident answers. No long explanations needed."
    ),
    "Case Study": (
        "You are a case study interviewer at a top consulting or product firm. "
        "Generate exactly 2 case study interview questions for a {role} ({level}) candidate. "
        "Q1: Present a business or product problem as a mini-case (e.g. 'A {role} team is seeing X problem — how would you diagnose and solve it?'). "
        "Q2: Ask for a recommendation or decision based on a given constraint or data scenario relevant to {role}. "
        "Both should require structured analysis, frameworks, and a clear recommendation."
    ),
    "Mixed Interview": (
        "You are a comprehensive interviewer covering multiple dimensions in one session. "
        "Generate exactly 2 questions for a {role} ({level}) candidate that cover different interview dimensions. "
        "Q1: A technical or domain-specific question that tests hard skills relevant to {role}. "
        "Q2: A behavioral or situational question that tests soft skills, mindset, or cultural fit. "
        "The two questions must complement each other — together covering both technical competence and interpersonal effectiveness."
    ),
}

_FALLBACKS = {
    "Technical": [
        "Explain a core technical concept relevant to your {role} work and how you've applied it in practice.",
        "Walk me through how you would debug a production issue in a {role} environment. What steps do you take?",
    ],
    "Behavioral / HR": [
        "Tell me about a time you had to collaborate with a difficult team member to deliver a project. What was your approach?",
        "Describe a situation where you had to meet a tight deadline. How did you prioritize and what was the outcome?",
    ],
    "System Design": [
        "How would you design a scalable notification system that handles millions of users?",
        "Walk me through the database schema you would design for a {role}-related application and explain your key decisions.",
    ],
    "Project Discussion": [
        "Walk me through your most impactful project — what was your role, what decisions did you make, and what was the outcome?",
        "Describe a significant technical challenge you faced in a project and how you resolved it.",
    ],
    "Problem Solving": [
        "Estimate how many {role}-related API calls a mid-sized startup would make per day. Walk me through your reasoning.",
        "You're given a dataset with anomalies in user behavior. How would you approach identifying and resolving the issue?",
    ],
    "Rapid Fire": [
        "In one sentence: what is the difference between synchronous and asynchronous programming?",
        "Would you choose SQL or NoSQL for a user activity feed? Give your answer in two sentences.",
    ],
    "Case Study": [
        "A {role} team notices a 30% drop in user engagement over two weeks. How would you investigate and what would your first steps be?",
        "You're asked to prioritize three features with equal business impact but different technical complexity. How do you decide?",
    ],
    "Mixed Interview": [
        "Explain a core technical skill that makes you effective as a {role}.",
        "Tell me about a time you had to influence a decision you disagreed with. What did you do?",
    ],
}


def _generate_questions_ai(
    role: str, interview_type: str, level: str, resume_text: Optional[str]
) -> tuple[str, str]:
    """
    Use AI to generate 2 interview questions that are both faithful to the
    chosen interview_type. Returns (q1_text, q2_text).
    """
    system_tmpl = _TYPE_INSTRUCTIONS.get(interview_type, _TYPE_INSTRUCTIONS["Technical"])
    system_msg  = system_tmpl.format(role=role, level=level)

    resume_hint = ""
    if resume_text:
        resume_hint = f"\nResume snippet (personalise where relevant): {resume_text[:350]}"

    user_msg = (
        f"Role: {role} | Level: {level} | Interview Type: {interview_type}{resume_hint}\n\n"
        "Return your response as valid JSON only, exactly in this format:\n"
        '{"q1": "<question 1 text>", "q2": "<question 2 text>"}\n'
        "No markdown, no extra text."
    )

    try:
        resp = ai_service.client.chat.completions.create(
            model=ai_service.settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0.75,
            max_tokens=300,
        )
        import json, re
        raw = resp.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            q1 = data.get("q1", "").strip()
            q2 = data.get("q2", "").strip()
            if q1 and q2:
                return q1, q2
    except Exception:
        pass

    # Fallback
    fb = _FALLBACKS.get(interview_type, _FALLBACKS["Technical"])
    return fb[0].format(role=role), fb[1].format(role=role)


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/start", status_code=201)
def start_quick_scan(
    payload: QuickScanStart,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Creates a quick-scan session (max 2 questions), AI-generates both questions
    faithful to the chosen interview_type.
    Returns: session_id, question1, question2
    """
    # Create session
    session = InterviewSession(
        user_id=user.id,
        session_uuid=str(uuid.uuid4()),
        role=payload.role,
        experience_level=payload.experience_level,
        interview_type=f"QuickScan:{payload.interview_type}",
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate both questions via AI, both faithful to interview_type
    q1_text, q2_text = _generate_questions_ai(
        role=payload.role,
        interview_type=payload.interview_type,
        level=payload.experience_level,
        resume_text=payload.resume_text,
    )

    # Q1
    q1 = Question(session_id=session.id, question_number=1, question_text=q1_text,
                  question_type=payload.interview_type.lower())
    db.add(q1)

    # Q2
    q2 = Question(session_id=session.id, question_number=2, question_text=q2_text,
                  question_type=payload.interview_type.lower())
    db.add(q2)

    db.commit()
    db.refresh(q1)
    db.refresh(q2)

    type_label = payload.interview_type
    return {
        "session_id": session.id,
        "session_uuid": session.session_uuid,
        "question1": {"id": q1.id, "text": q1.question_text, "type": f"{type_label} — Q1"},
        "question2": {"id": q2.id, "text": q2.question_text, "type": f"{type_label} — Q2"},
    }


@router.post("/complete")
def complete_quick_scan(
    payload: QuickScanAnswer,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Evaluate both answers, calculate readiness score, generate insights + roadmap.
    Returns: full readiness report
    """
    # Verify session ownership
    session = db.query(InterviewSession).filter(
        InterviewSession.id == payload.session_id,
        InterviewSession.user_id == user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Quick scan session not found")

    # ── Evaluate Q1 (Communication focus)
    q1 = db.query(Question).filter(
        Question.id == payload.q1_id,
        Question.session_id == payload.session_id,
    ).first()
    if not q1:
        raise HTTPException(status_code=404, detail="Question 1 not found")

    interview_type_clean = session.interview_type.replace("QuickScan:", "")
    fb1 = ai_service.evaluate_answer(
        question=q1.question_text,
        answer=payload.q1_answer,
        role=session.role,
        experience_level=session.experience_level,
        interview_type=interview_type_clean,
    )
    q1.answer_text         = payload.q1_answer
    q1.answer_method       = payload.q1_method
    q1.overall_score       = fb1.get("overall_score", 0)
    q1.confidence_score    = fb1.get("confidence_score", 0)
    q1.communication_score = fb1.get("communication_score", 0)
    q1.technical_score     = fb1.get("technical_score", 0)
    q1.grammar_score       = fb1.get("grammar_score", 0)
    q1.relevance_score     = fb1.get("relevance_score", 0)
    q1.ai_feedback         = fb1.get("ai_feedback", "")
    q1.ideal_answer        = fb1.get("ideal_answer", "")
    q1.strengths           = fb1.get("strengths", [])
    q1.improvements        = fb1.get("improvements", [])
    q1.filler_words        = fb1.get("filler_words", {})

    # ── Evaluate Q2 (Technical focus)
    q2 = db.query(Question).filter(
        Question.id == payload.q2_id,
        Question.session_id == payload.session_id,
    ).first()
    if not q2:
        raise HTTPException(status_code=404, detail="Question 2 not found")

    fb2 = ai_service.evaluate_answer(
        question=q2.question_text,
        answer=payload.q2_answer,
        role=session.role,
        experience_level=session.experience_level,
        interview_type=interview_type_clean,
    )
    q2.answer_text         = payload.q2_answer
    q2.answer_method       = payload.q2_method
    q2.overall_score       = fb2.get("overall_score", 0)
    q2.confidence_score    = fb2.get("confidence_score", 0)
    q2.communication_score = fb2.get("communication_score", 0)
    q2.technical_score     = fb2.get("technical_score", 0)
    q2.grammar_score       = fb2.get("grammar_score", 0)
    q2.relevance_score     = fb2.get("relevance_score", 0)
    q2.ai_feedback         = fb2.get("ai_feedback", "")
    q2.ideal_answer        = fb2.get("ideal_answer", "")
    q2.strengths           = fb2.get("strengths", [])
    q2.improvements        = fb2.get("improvements", [])
    q2.filler_words        = fb2.get("filler_words", {})

    db.commit()

    # ── Build averaged communication / technical scores
    avg_communication = (fb1.get("communication_score", 0) + fb2.get("communication_score", 0)) / 2
    avg_technical     = (fb1.get("technical_score", 0)     + fb2.get("technical_score", 0))     / 2
    avg_confidence    = (fb1.get("confidence_score", 0)    + fb2.get("confidence_score", 0))    / 2
    avg_grammar       = (fb1.get("grammar_score", 0)       + fb2.get("grammar_score", 0))       / 2
    avg_relevance     = (fb1.get("relevance_score", 0)     + fb2.get("relevance_score", 0))     / 2
    ats_score         = payload.ats_score or 0

    # ── Composite readiness score
    scores = calculate_readiness_score(
        ats_score=ats_score,
        communication_score=avg_communication,
        technical_score=avg_technical,
        confidence_score=avg_confidence,
        grammar_score=avg_grammar,
        relevance_score=avg_relevance,
    )

    # ── Mark session complete
    session.overall_score       = scores["overall"]
    session.confidence_score    = avg_confidence
    session.communication_score = avg_communication
    session.technical_score     = avg_technical
    session.grammar_score       = avg_grammar
    session.status              = "completed"
    db.commit()

    # ── Determine weak areas
    score_map = {
        "Communication": avg_communication,
        "Technical Knowledge": avg_technical,
        "Confidence": avg_confidence,
        "Grammar & Clarity": avg_grammar,
        "ATS Compatibility": ats_score,
    }
    weak_areas   = [k for k, v in score_map.items() if v < 65]
    strong_areas = [k for k, v in score_map.items() if v >= 75]

    # ── AI Insights
    insights = generate_hiring_insights(
        role=session.role,
        experience_level=session.experience_level,
        interview_type=interview_type_clean,
        scores=scores,
        resume_skills=payload.resume_skills,
        missing_keywords=payload.missing_keywords,
    )

    # ── 7-Day Roadmap
    roadmap = generate_roadmap(
        role=session.role,
        interview_type=interview_type_clean,
        scores=scores,
        weak_areas=weak_areas,
        missing_keywords=payload.missing_keywords,
    )

    return {
        "session_id": session.id,
        "readiness": scores,
        "question1": {
            "text": q1.question_text,
            "answer": q1.answer_text,
            "feedback": fb1,
        },
        "question2": {
            "text": q2.question_text,
            "answer": q2.answer_text,
            "feedback": fb2,
        },
        "insights": insights,
        "roadmap": roadmap,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
    }
