"""
MockPilot AI — Resume Analysis Service
"""
import os, sys, re
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

SKILLS_DB = {
    "Languages":    ["python","java","javascript","typescript","c++","c#","go","rust","kotlin","swift","scala","r","ruby","php"],
    "Web":          ["react","angular","vue","next.js","node.js","express","django","flask","fastapi","html","css","tailwind","graphql"],
    "Data & AI":    ["pandas","numpy","scikit-learn","tensorflow","pytorch","keras","spark","hadoop","tableau","power bi","langchain","huggingface","openai","llm","rag"],
    "Cloud/DevOps": ["aws","azure","gcp","docker","kubernetes","terraform","ci/cd","jenkins","ansible","linux","bash"],
    "Databases":    ["sql","postgresql","mysql","mongodb","redis","elasticsearch","cassandra","dynamodb","sqlite","oracle"],
    "Soft Skills":  ["leadership","communication","agile","scrum","project management","teamwork","problem solving","analytical","collaboration"],
}

ATS_KEYWORDS = ["experience","skills","education","projects","achievements","certifications",
                "leadership","managed","developed","implemented","designed","analyzed",
                "optimized","team","results","impact","metrics","delivered"]

ROLE_PATTERNS = [
    "software engineer","data scientist","product manager","ml engineer","devops engineer",
    "backend developer","frontend developer","full stack developer","data analyst",
    "business analyst","cloud architect","ai engineer","data engineer","research scientist",
    "system architect","mobile developer","security engineer","qa engineer"
]

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: parts.append(t)
            return "\n".join(parts)
        except Exception:
            pass
        try:
            import fitz
            doc = fitz.open(file_path)
            text = "\n".join(p.get_text() for p in doc)
            doc.close()
            return text
        except Exception as e:
            return f"Error: {e}"
    elif ext in [".docx", ".doc"]:
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            return f"Error: {e}"
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return "Unsupported format."

def extract_skills(text: str) -> dict:
    tl = text.lower()
    return {cat: [kw for kw in kws if kw in tl] for cat, kws in SKILLS_DB.items()
            if any(kw in tl for kw in kws)}

def detect_roles(text: str) -> List[str]:
    tl = text.lower()
    return [r for r in ROLE_PATTERNS if r in tl]

def ats_analysis(text: str) -> dict:
    tl = text.lower()
    matched   = [k for k in ATS_KEYWORDS if k in tl]
    missing   = [k for k in ATS_KEYWORDS if k not in tl]
    base_score = (len(matched) / len(ATS_KEYWORDS)) * 70
    # Structure bonus
    for w in ["summary","experience","education","skills","projects"]:
        if w in tl: base_score += 3
    score = min(100.0, base_score)
    suggestions = []
    if len(text) < 400:     suggestions.append("Resume too short — expand experience sections.")
    if "github" not in tl:  suggestions.append("Add GitHub/portfolio link for visibility.")
    if "quantif" not in tl and not any(c.isdigit() for c in text[:500]):
        suggestions.append("Quantify achievements with numbers (e.g., 'improved performance by 40%').")
    if missing[:5]:         suggestions.append(f"Include keywords: {', '.join(missing[:5])}.")
    return {"ats_score": round(score, 1), "matched": matched, "missing": missing[:8], "suggestions": suggestions}
