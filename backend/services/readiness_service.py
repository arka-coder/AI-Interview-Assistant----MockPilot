"""
MockPilot AI — Interview Readiness Service
Composite scoring, AI hiring insights, and 7-day improvement roadmap.
"""
import re, json, sys, os
from groq import Groq
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.config import get_settings

settings = get_settings()
client = Groq(api_key=settings.GROQ_API_KEY)


# ── Readiness Level Labels ───────────────────────────────────────────────────

def get_readiness_level(score: float) -> dict:
    if score >= 81:
        return {"label": "Industry Ready", "color": "#10B981", "emoji": "🏆"}
    elif score >= 66:
        return {"label": "Interview Ready", "color": "#A855F7", "emoji": "✅"}
    elif score >= 41:
        return {"label": "Developing", "color": "#F59E0B", "emoji": "📈"}
    else:
        return {"label": "Beginner", "color": "#EF4444", "emoji": "🌱"}


# ── Composite Score Calculation ──────────────────────────────────────────────

def calculate_readiness_score(
    ats_score: float = 0,
    communication_score: float = 0,
    technical_score: float = 0,
    confidence_score: float = 0,
    grammar_score: float = 0,
    relevance_score: float = 0,
    portfolio_score: float = 0,
) -> dict:
    """
    Weighted composite score:
    - ATS / Resume: 20%
    - Communication: 25%
    - Technical:     25%
    - Confidence:    15%
    - Grammar:       10%
    - Relevance:      5%
    """
    weights = {
        "ats": 0.20,
        "communication": 0.25,
        "technical": 0.25,
        "confidence": 0.15,
        "grammar": 0.10,
        "relevance": 0.05,
    }
    overall = (
        ats_score          * weights["ats"]
        + communication_score * weights["communication"]
        + technical_score     * weights["technical"]
        + confidence_score    * weights["confidence"]
        + grammar_score       * weights["grammar"]
        + relevance_score     * weights["relevance"]
    )
    overall = round(min(100.0, max(0.0, overall)), 1)

    breakdown = {
        "overall": overall,
        "resume_strength": round(ats_score, 1),
        "communication": round(communication_score, 1),
        "technical_readiness": round(technical_score, 1),
        "confidence": round(confidence_score, 1),
        "ats_compatibility": round(ats_score, 1),
        "grammar": round(grammar_score, 1),
        "portfolio_strength": round(portfolio_score, 1),
    }
    level = get_readiness_level(overall)
    breakdown.update(level)
    return breakdown


# ── AI Hiring Insights ───────────────────────────────────────────────────────

INSIGHTS_PROMPT = """You are a senior hiring manager at a top-tier tech firm with 15+ years recruiting for FAANG and elite startups.
Analyze the candidate profile and return ONLY valid JSON in this exact format:
{
  "strong_signals": ["<specific strength with context>", "<specific strength>", "<specific strength>"],
  "hiring_risks": ["<specific risk with business impact>", "<specific risk>", "<specific risk>"],
  "recruiter_impression": "<1 precise, realistic recruiter verdict sentence — e.g. shortlisted, needs improvement, etc.>",
  "shortlist_probability": "<Low|Medium|High|Very High>"
}
Rules:
- Be brutally honest and specific — avoid generic phrases like 'shows potential'
- Strong signals: name concrete skills, behaviors, or indicators visible in the data
- Hiring risks: name specific gaps with business/interview impact (e.g., 'no quantified achievements weakens impact stories')
- Recruiter impression: write as if emailing a hiring team — direct, specific, professional
- Examples of good signals: 'Communication aligns with senior IC expectations for Data Science roles', 'Technical depth adequate for ML Engineer screening round'
- Examples of good risks: 'Answers lacked measurable business impact and STAR structure', 'ATS score reduced by absence of deployment/MLOps keywords'"""


def generate_hiring_insights(
    role: str,
    experience_level: str,
    interview_type: str,
    scores: dict,
    resume_skills: dict = None,
    missing_keywords: list = None,
) -> dict:
    """Generate AI recruiter perspective on a candidate."""
    skill_summary = ""
    if resume_skills:
        flat = [kw for kws in resume_skills.values() for kw in kws]
        skill_summary = f"Detected skills: {', '.join(flat[:15])}"
    missing_kw = f"Missing keywords: {', '.join((missing_keywords or [])[:6])}" if missing_keywords else ""

    prompt = (
        f"Role: {role} | Level: {experience_level} | Type: {interview_type}\n\n"
        f"Readiness Score: {scores.get('overall', 0):.0f}/100\n"
        f"Communication: {scores.get('communication', 0):.0f} | "
        f"Technical: {scores.get('technical_readiness', 0):.0f} | "
        f"Confidence: {scores.get('confidence', 0):.0f} | "
        f"ATS: {scores.get('ats_compatibility', 0):.0f}\n"
        f"{skill_summary}\n{missing_kw}\n\n"
        f"Generate concise recruiter insights as JSON."
    )
    try:
        resp = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": INSIGHTS_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.4,
            max_tokens=500,
        )
        raw = resp.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(match.group()) if match else _default_insights(scores)
    except Exception:
        return _default_insights(scores)


def _default_insights(scores: dict) -> dict:
    overall = scores.get("overall", 50)
    if overall >= 75:
        signals = ["Strong communication clarity", "Solid technical foundation", "Well-structured responses"]
        risks = ["Could add more quantified achievements", "Expand project descriptions", "Practice edge case handling"]
        impression = "Likely shortlisted for initial technical screening."
        prob = "High"
    elif overall >= 50:
        signals = ["Shows potential in core areas", "Demonstrates awareness of role requirements", "Good grammar and structure"]
        risks = ["Technical depth needs improvement", "Confidence could be stronger", "Resume keywords incomplete"]
        impression = "May pass initial screen but needs stronger technical answers."
        prob = "Medium"
    else:
        signals = ["Willingness to learn detected", "Basic communication present", "Role awareness shown"]
        risks = ["Technical knowledge gaps identified", "Low confidence signals", "Resume ATS compatibility low"]
        impression = "Needs significant preparation before applying."
        prob = "Low"
    return {
        "strong_signals": signals,
        "hiring_risks": risks,
        "recruiter_impression": impression,
        "shortlist_probability": prob,
    }


# ── 7-Day Improvement Roadmap ────────────────────────────────────────────────

ROADMAP_PROMPT = """You are a senior career coach who has helped 500+ candidates land offers at top companies.
Generate a hyper-specific, prioritized 7-day interview prep roadmap.
Return ONLY a valid JSON array of exactly 7 items:
[
  {"day": 1, "focus": "<concise topic e.g. 'Resume Impact Bullets'>", "task": "<very specific action e.g. 'Rewrite 3 bullet points using X metric Y result Z context format'>", "duration": "<realistic time e.g. '40 min'>", "priority": "<High|Medium|Low>"},
  ...
]
Rules:
- Day 1-2: highest-priority quick wins (resume fixes, intro polish)
- Day 3-5: core technical/behavioral skill work tailored to the role
- Day 6: full mock interview practice
- Day 7: final review of weakest areas
- Tasks must be SPECIFIC actions, not vague goals. Bad: 'Practice interviews'. Good: 'Record a 90-second answer to Tell Me About Yourself and review for filler words'
- Vary duration realistically: 20–60 min per day
- Assign High priority to days 1,2,6 unless other weaknesses are critical"""


def generate_roadmap(
    role: str,
    interview_type: str,
    scores: dict,
    weak_areas: list = None,
    missing_keywords: list = None,
) -> list:
    """Generate a personalized 7-day improvement plan."""
    weakness_text = ""
    if weak_areas:
        weakness_text = f"Weak areas: {', '.join(weak_areas)}"
    missing_text = f"Missing resume keywords: {', '.join((missing_keywords or [])[:5])}" if missing_keywords else ""

    prompt = (
        f"Candidate Profile:\n"
        f"Role: {role} | Interview Type: {interview_type}\n"
        f"Readiness: {scores.get('overall', 0):.0f}/100\n"
        f"Communication: {scores.get('communication', 0):.0f} | "
        f"Technical: {scores.get('technical_readiness', 0):.0f} | "
        f"Confidence: {scores.get('confidence', 0):.0f} | "
        f"ATS Score: {scores.get('ats_compatibility', 0):.0f}\n"
        f"{weakness_text}\n{missing_text}\n\n"
        f"Create a focused 7-day roadmap to maximize readiness for {role} {interview_type} interview."
    )
    try:
        resp = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": ROADMAP_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.5,
            max_tokens=800,
        )
        raw = resp.choices[0].message.content.strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        return json.loads(match.group()) if match else _default_roadmap(role, scores)
    except Exception:
        return _default_roadmap(role, scores)


def _default_roadmap(role: str, scores: dict) -> list:
    return [
        {"day": 1, "focus": "Resume Polish", "task": "Add 3 quantified achievements and fix ATS keywords", "duration": "45 min", "priority": "High"},
        {"day": 2, "focus": "HR Introduction", "task": "Write and rehearse a 90-second 'Tell me about yourself'", "duration": "30 min", "priority": "High"},
        {"day": 3, "focus": "Technical Concepts", "task": f"Review 5 core concepts for {role} role", "duration": "60 min", "priority": "High"},
        {"day": 4, "focus": "Speaking Pace", "task": "Record voice answers and review filler word count", "duration": "30 min", "priority": "Medium"},
        {"day": 5, "focus": "Behavioral Stories", "task": "Prepare 3 STAR-method behavioral answers", "duration": "45 min", "priority": "Medium"},
        {"day": 6, "focus": "Mock Practice", "task": "Complete a full 10-question mock interview on MockPilot", "duration": "30 min", "priority": "High"},
        {"day": 7, "focus": "Final Review", "task": "Review all feedback, polish top 3 weak areas", "duration": "30 min", "priority": "Medium"},
    ]
