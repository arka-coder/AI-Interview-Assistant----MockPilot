"""
MockPilot AI — Groq AI Service
Question generation, adaptive follow-ups, and answer evaluation.
"""
import os, sys, re, json
from groq import Groq
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.config import get_settings

settings = get_settings()
client = Groq(api_key=settings.GROQ_API_KEY)

# ── System Prompts ───────────────────────────────────────────────

INTERVIEWER_PROMPT = """You are an elite AI interviewer at a top-tier tech company with 20+ years of expertise.

Your style:
- Professional, precise, and engaging
- Ask exactly ONE question at a time
- Build contextually on previous answers for follow-ups
- Calibrate difficulty to the experience level
- Never repeat questions asked previously
- No preamble — output ONLY the question text

Interview type guidelines:
- HR: Culture fit, motivation, values, career goals, team dynamics
- Technical: Algorithms, system design, domain-specific knowledge, code logic
- Behavioral: STAR-method situations, leadership, conflict, impact
- Business Development: Market strategy, client handling, revenue, negotiation
- Data Science: Statistics, ML modeling, feature engineering, business insights
- System Design: Distributed systems, scalability, trade-offs, architecture"""

EVALUATOR_PROMPT = """You are a senior interview coach with 20+ years evaluating candidates at FAANG companies.

Analyze the interview answer and return ONLY a valid JSON object in this exact format:
{
  "overall_score": <integer 0-100>,
  "confidence_score": <integer 0-100>,
  "communication_score": <integer 0-100>,
  "technical_score": <integer 0-100>,
  "grammar_score": <integer 0-100>,
  "relevance_score": <integer 0-100>,
  "ai_feedback": "<2-3 paragraph detailed feedback>",
  "ideal_answer": "<what an exemplary answer looks like>",
  "strengths": ["<specific strength 1>", "<specific strength 2>", "<specific strength 3>"],
  "improvements": ["<actionable improvement 1>", "<actionable improvement 2>", "<actionable improvement 3>"],
  "filler_words": {"um": 0, "uh": 0, "like": 0, "basically": 0}
}

Scoring guide: 90-100 Exceptional | 75-89 Strong | 60-74 Adequate | 40-59 Weak | 0-39 Poor
Be direct, specific, and constructive. No generic feedback."""


# ── Question Generation ──────────────────────────────────────────

def generate_first_question(role: str, experience_level: str, interview_type: str,
                             resume_context: Optional[str] = None) -> str:
    """Generate the opening question for an interview."""
    context = f"\n\nResume context (use this to personalize):\n{resume_context[:800]}" if resume_context else ""
    prompt = (f"Generate the opening interview question for:\n"
              f"Role: {role} | Level: {experience_level} | Type: {interview_type}{context}\n\n"
              f"Output ONLY the question.")
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "system", "content": INTERVIEWER_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=0.7, max_tokens=300
    )
    return resp.choices[0].message.content.strip()


def generate_follow_up(role: str, experience_level: str, interview_type: str,
                       history: List[dict], question_number: int) -> str:
    """Generate a contextual follow-up based on the conversation so far."""
    history_text = "\n".join([
        f"Q{i+1}: {h['question']}\nA{i+1}: {h['answer']}" for i, h in enumerate(history)
    ])
    prompt = (f"Continue the interview. This is question #{question_number}.\n"
              f"Role: {role} | Level: {experience_level} | Type: {interview_type}\n\n"
              f"Conversation so far:\n{history_text}\n\n"
              f"Ask the next most relevant question. Output ONLY the question.")
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "system", "content": INTERVIEWER_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=0.7, max_tokens=300
    )
    return resp.choices[0].message.content.strip()


# ── Answer Evaluation ────────────────────────────────────────────

def evaluate_answer(question: str, answer: str, role: str,
                    experience_level: str, interview_type: str) -> dict:
    """Evaluate a candidate answer and return structured JSON feedback."""
    if not answer or len(answer.strip()) < 5:
        return _empty_feedback()

    prompt = (f"Evaluate this answer:\n\n"
              f"Role: {role} | Level: {experience_level} | Type: {interview_type}\n\n"
              f"QUESTION: {question}\n\nANSWER: {answer}\n\n"
              f"Return evaluation as the exact JSON format specified.")
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "system", "content": EVALUATOR_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=0.3, max_tokens=1500
    )
    raw = resp.choices[0].message.content.strip()
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(match.group()) if match else json.loads(raw)
    except Exception:
        return _fallback_feedback(raw)


def _empty_feedback() -> dict:
    return {"overall_score": 0, "confidence_score": 0, "communication_score": 0,
            "technical_score": 0, "grammar_score": 0, "relevance_score": 0,
            "ai_feedback": "No answer provided. Please submit your response.",
            "ideal_answer": "Provide a structured, detailed answer using the STAR method where applicable.",
            "strengths": [], "improvements": ["Submit a complete answer"], "filler_words": {}}

def _fallback_feedback(raw: str) -> dict:
    return {"overall_score": 50, "confidence_score": 50, "communication_score": 50,
            "technical_score": 50, "grammar_score": 50, "relevance_score": 50,
            "ai_feedback": raw[:500], "ideal_answer": "See feedback above.",
            "strengths": ["Answer submitted"], "improvements": ["Add more specifics"], "filler_words": {}}


# ── Interview Summary ────────────────────────────────────────────

def generate_summary(role: str, interview_type: str, all_feedback: list) -> dict:
    """Generate a holistic end-of-interview summary."""
    feedback_text = "\n".join([
        f"Q{i+1}: Score={f.get('overall_score', 0):.0f} — {f.get('ai_feedback', '')[:150]}"
        for i, f in enumerate(all_feedback)
    ])
    prompt = (f"Summarize the complete interview:\nRole: {role} | Type: {interview_type}\n\n"
              f"Per-question performance:\n{feedback_text}\n\n"
              f"Return JSON:\n"
              f'{{"overall_summary":"<2-3 paragraphs>","top_strengths":["s1","s2","s3"],'
              f'"key_weaknesses":["w1","w2","w3"],"action_plan":["a1","a2","a3","a4"],'
              f'"readiness":"<Not Ready|Almost Ready|Ready|Highly Ready>"}}')
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "system", "content": "You are a senior interview coach giving holistic assessment."},
                  {"role": "user", "content": prompt}],
        temperature=0.4, max_tokens=1000
    )
    raw = resp.choices[0].message.content.strip()
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(match.group()) if match else {"overall_summary": raw}
    except Exception:
        return {"overall_summary": raw}


# ── Resume-based Questions ───────────────────────────────────────

def generate_resume_questions(resume_text: str, role: str, interview_type: str, count: int = 8) -> List[str]:
    """Generate personalized questions from a resume."""
    prompt = (f"Generate {count} targeted {interview_type} interview questions for a {role} role "
              f"based on this resume:\n\n{resume_text[:2000]}\n\n"
              f"Output ONLY a JSON array: [\"q1\", \"q2\", ...]")
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "system", "content": "Expert interviewer creating personalized resume-based questions."},
                  {"role": "user", "content": prompt}],
        temperature=0.6, max_tokens=800
    )
    raw = resp.choices[0].message.content.strip()
    try:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        return json.loads(match.group()) if match else []
    except Exception:
        return []
