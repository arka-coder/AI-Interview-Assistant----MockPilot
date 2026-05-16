"""
MockPilot AI — Frontend API Client (Fixed)
"""
import requests
import streamlit as st
import os
from typing import Optional

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")


def _headers(json_content: bool = True) -> dict:
    token = st.session_state.get("token", "")
    h = {"Authorization": f"Bearer {token}"}
    if json_content:
        h["Content-Type"] = "application/json"
    return h


def _handle(r: requests.Response, fallback=None):
    """Centralised response handler — auto-clears session on 401."""
    if r.status_code == 401:
        had_token = bool(st.session_state.get("token"))
        # Clear session
        st.session_state["token"] = None
        st.session_state["user"] = None
        st.session_state["page"] = "landing"
        if had_token:
            # Real expiry — user was logged in before
            st.error("⚠️ Session expired. Please refresh the page.")
        else:
            # Backend was unreachable during auto-login (Render cold start)
            st.warning("⏳ Backend is starting up — please wait ~30 seconds and refresh.")
        st.stop()
    if r.ok:
        return r.json()
    try:
        detail = r.json().get("detail", r.text)
    except Exception:
        detail = r.text
    return {"error": str(detail)} if fallback is None else fallback


# ── Auth ──────────────────────────────────────────────────────────────────────

def signup(email: str, username: str, password: str, full_name: str = "") -> dict:
    r = requests.post(f"{BACKEND}/api/auth/signup",
                      json={"email": email, "username": username,
                            "password": password, "full_name": full_name}, timeout=15)
    if r.ok:
        return r.json()
    try:
        return {"error": r.json().get("detail", "Signup failed")}
    except Exception:
        return {"error": "Signup failed"}


def login(email: str, password: str) -> dict:
    r = requests.post(f"{BACKEND}/api/auth/login",
                      json={"email": email, "password": password}, timeout=15)
    if r.ok:
        return r.json()
    try:
        return {"error": r.json().get("detail", "Login failed")}
    except Exception:
        return {"error": "Login failed"}


# ── Interview ─────────────────────────────────────────────────────────────────

def start_session(role: str, experience_level: str, interview_type: str,
                  resume_id: Optional[int] = None) -> dict:
    payload = {"role": role, "experience_level": experience_level,
               "interview_type": interview_type}
    if resume_id:
        payload["resume_id"] = resume_id
    r = requests.post(f"{BACKEND}/api/interview/start",
                      json=payload, headers=_headers(), timeout=30)
    return _handle(r)


def get_current_question(session_id: int) -> dict:
    r = requests.get(f"{BACKEND}/api/interview/{session_id}/current-question",
                     headers=_headers(), timeout=15)
    return _handle(r)


def submit_answer(session_id: int, question_id: int, answer: str,
                  method: str = "text") -> dict:
    r = requests.post(f"{BACKEND}/api/interview/answer",
                      json={"session_id": session_id, "question_id": question_id,
                            "answer_text": answer, "answer_method": method},
                      headers=_headers(), timeout=60)
    return _handle(r)


def complete_session(session_id: int) -> dict:
    r = requests.post(f"{BACKEND}/api/interview/{session_id}/complete",
                      headers=_headers(), timeout=15)
    return _handle(r, fallback={})


def get_history() -> list:
    r = requests.get(f"{BACKEND}/api/interview/history",
                     headers=_headers(), timeout=15)
    if r.status_code == 401:
        return []
    return r.json() if r.ok else []


def clear_all_sessions() -> dict:
    """Delete all sessions and reset analytics for the current user."""
    r = requests.delete(f"{BACKEND}/api/interview/all",
                        headers=_headers(), timeout=15)
    return _handle(r, fallback={"error": "Failed to clear sessions"})


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_analytics() -> dict:
    r = requests.get(f"{BACKEND}/api/analytics/me",
                     headers=_headers(), timeout=15)
    if r.status_code == 401:
        return {}
    return r.json() if r.ok else {}


# ── Resume ────────────────────────────────────────────────────────────────────

def upload_resume(file_bytes: bytes, filename: str) -> dict:
    token = st.session_state.get("token", "")
    files = {"file": (filename, file_bytes, "application/octet-stream")}
    r = requests.post(f"{BACKEND}/api/resume/upload",
                      files=files,
                      headers={"Authorization": f"Bearer {token}"},
                      timeout=30)
    return _handle(r)


def list_resumes() -> list:
    token = st.session_state.get("token", "")
    if not token:
        return []
    r = requests.get(f"{BACKEND}/api/resume/list",
                     headers={"Authorization": f"Bearer {token}"}, timeout=10)
    if not r.ok:
        return []
    return r.json()


def delete_resume(resume_id: int) -> dict:
    """Permanently delete a resume by ID."""
    r = requests.delete(f"{BACKEND}/api/resume/{resume_id}",
                        headers=_headers(json_content=False), timeout=10)
    if r.status_code == 204:
        return {"ok": True}
    return _handle(r, fallback={"error": "Failed to delete resume"})


# ── Quick Scan ────────────────────────────────────────────────────────────────

def start_quick_scan(role: str, experience_level: str, interview_type: str,
                     resume_text: str = "") -> dict:
    """Start a 2-question quick readiness scan session."""
    payload = {
        "role": role,
        "experience_level": experience_level,
        "interview_type": interview_type,
        "resume_text": resume_text[:600] if resume_text else "",
    }
    r = requests.post(f"{BACKEND}/api/quick-scan/start",
                      json=payload, headers=_headers(), timeout=30)
    return _handle(r)


def complete_quick_scan(session_id: int, q1_id: int, q1_answer: str, q1_method: str,
                        q2_id: int, q2_answer: str, q2_method: str,
                        ats_score: float = 0, resume_skills: dict = None,
                        missing_keywords: list = None) -> dict:
    """Submit both answers and receive the full readiness report."""
    payload = {
        "session_id": session_id,
        "q1_id": q1_id,
        "q1_answer": q1_answer,
        "q1_method": q1_method,
        "q2_id": q2_id,
        "q2_answer": q2_answer,
        "q2_method": q2_method,
        "ats_score": ats_score,
        "resume_skills": resume_skills or {},
        "missing_keywords": missing_keywords or [],
    }
    r = requests.post(f"{BACKEND}/api/quick-scan/complete",
                      json=payload, headers=_headers(), timeout=90)
    return _handle(r)


# ── Health ────────────────────────────────────────────────────────────────────

def check_backend() -> bool:
    try:
        r = requests.get(f"{BACKEND}/health", timeout=3)
        return r.ok
    except Exception:
        return False
