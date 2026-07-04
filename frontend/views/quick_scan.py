"""
MockPilot AI — Quick Readiness Scan (3-Step Flow)
2-minute interview readiness assessment.
"""
import streamlit as st
import requests as req
import time
from frontend.components.ui_components import inject_css, html_escape
from frontend.api_client import start_quick_scan, complete_quick_scan, upload_resume, BACKEND


# ── Local resume text extraction (no backend dependency) ─────────────────────
def _extract_text_local(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from PDF, DOCX, or TXT without importing backend modules."""
    ext = filename.lower().split('.')[-1]
    try:
        if ext == 'pdf':
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=file_bytes, filetype='pdf')
                return '\n'.join(page.get_text() for page in doc)
            except ImportError:
                try:
                    import pdfplumber
                    import io
                    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                        return '\n'.join(p.extract_text() or '' for p in pdf.pages)
                except ImportError:
                    pass
        elif ext == 'docx':
            try:
                from docx import Document
                import io
                doc = Document(io.BytesIO(file_bytes))
                return '\n'.join(p.text for p in doc.paragraphs)
            except ImportError:
                pass
        elif ext == 'txt':
            return file_bytes.decode('utf-8', errors='ignore')
    except Exception:
        pass
    return ''


def _analyze_resume_via_api(file_bytes: bytes, filename: str, token: str) -> dict:
    """Upload resume to backend for ATS analysis; returns {ats_score, skills, missing}."""
    try:
        r = req.post(
            f"{BACKEND}/api/resume/upload",
            files={"file": (filename, file_bytes, "application/octet-stream")},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        if r.ok:
            data = r.json()
            return {
                "ats_score": data.get("ats_score", 0),
                "skills": data.get("skills", {}),
                "missing": data.get("missing_keywords", []),
            }
    except Exception:
        pass
    return {"ats_score": 0, "skills": {}, "missing": []}

SCAN_CSS = """
<style>
/* All scan-specific styles now live in main.css as stitch-* classes.
   Keeping this for minimal local overrides. */
.upload-zone {
  border:2px dashed rgba(22,163,74,0.35);border-radius:20px;
  padding:2.5rem;text-align:center;
  background:rgba(34,197,94,0.04);
  transition:all 0.3s;cursor:pointer;
}
.upload-zone:hover {
  border-color:rgba(22,163,74,0.7);
  background:rgba(34,197,94,0.08);
}
.ats-ring-wrap {
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:0.5rem;
}
.skill-badge {
  display:inline-flex;align-items:center;
  background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);
  border-radius:99px;padding:3px 14px;font-size:0.72rem;color:#d2bbff;
  font-family:'Space Grotesk',sans-serif;font-weight:700;margin:3px;
  letter-spacing:0.03em;
}
.skill-badge.cyan {
  background:rgba(93,230,255,0.1);border-color:rgba(93,230,255,0.3);color:#5de6ff;
}
.mode-tab {
  display:inline-flex;align-items:center;gap:0.4rem;padding:6px 18px;
  border-radius:99px;font-size:0.82rem;font-weight:600;cursor:pointer;
  transition:all 0.2s;border:1px solid rgba(255,255,255,0.1);color:#64748B;
}
.mode-tab.active {
  background:rgba(34,197,94,0.2);border-color:rgba(22,163,74,0.5);color:#d2bbff;
}
</style>
"""

ROLES = [
    "Data Scientist", "Software Engineer", "Business Analyst",
    "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "ML Engineer", "Data Engineer", "Product Manager",
    "DevOps Engineer", "Cloud Architect", "AI Engineer",
]
LEVELS = ["Entry (0–1 yr)", "Junior (1–3 yrs)", "Mid (3–5 yrs)", "Senior (5–8 yrs)", "Lead (8+ yrs)"]
TYPES  = [
    "Technical",
    "Behavioral / HR",
    "System Design",
    "Project Discussion",
    "Problem Solving",
    "Rapid Fire",
    "Case Study",
    "Mixed Interview",
]


# ── ATS ring SVG ─────────────────────────────────────────────────────────────
def _ats_ring(score: float) -> str:
    r = 54
    circ = 2 * 3.14159 * r
    offset = circ * (1 - score / 100)
    color = "#10B981" if score >= 70 else "#F59E0B" if score >= 45 else "#EF4444"
    label = "Strong" if score >= 70 else "Average" if score >= 45 else "Weak"
    return f"""
    <div class="ats-ring-wrap">
      <svg width="130" height="130" viewBox="0 0 130 130">
        <circle cx="65" cy="65" r="{r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
        <circle cx="65" cy="65" r="{r}" fill="none" stroke="{color}" stroke-width="10"
                stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"
                stroke-linecap="round" transform="rotate(-90 65 65)"
                style="transition:stroke-dashoffset 1.2s ease;filter:drop-shadow(0 0 8px {color}88);"/>
        <text x="65" y="60" text-anchor="middle" fill="{color}" font-size="22" font-weight="900"
              font-family="Outfit,Inter,sans-serif">{score:.0f}</text>
        <text x="65" y="78" text-anchor="middle" fill="#64748B" font-size="11"
              font-family="Outfit,Inter,sans-serif">ATS Score</text>
      </svg>
      <span style="color:{color};font-size:0.78rem;font-weight:700;letter-spacing:0.5px;">{label}</span>
    </div>"""


def render():
    inject_css()
    st.markdown(SCAN_CSS, unsafe_allow_html=True)

    # ── Init state
    for k, v in {
        "scan_step": 1,
        "scan_resume_text": "",
        "scan_ats": 0,
        "scan_skills": {},
        "scan_missing": [],
        "scan_role": "Data Scientist",
        "scan_level": "Mid (3–5 yrs)",
        "scan_type": "Technical",
        "scan_session": None,
        "scan_q1": None,
        "scan_q2": None,
        "scan_q1_ans": "",
        "scan_q2_ans": "",
        "scan_q1_method": "text",
        "scan_q2_method": "text",
        "scan_report": None,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    step = st.session_state["scan_step"]

    # ── Header
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 0.5rem;">
      <div style="display:inline-flex;align-items:center;gap:0.5rem;
           background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);
           border-radius:99px;padding:4px 18px;margin-bottom:1rem;">
        <span style="width:7px;height:7px;border-radius:50%;background:#16A34A;
                     animation:aiPulse 2s infinite;display:inline-block;"></span>
        <span style="color:#16A34A;font-size:0.75rem;font-weight:700;letter-spacing:0.5px;">
          ⚡ QUICK READINESS SCAN — UNDER 2 MINUTES
        </span>
      </div>
      <h1 style="font-size:2.2rem;font-weight:900;margin:0 0 0.4rem;
                 background:linear-gradient(135deg,#FFFFFF 30%,#16A34A 65%,#4ADE80);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
        Know Your Interview Readiness
      </h1>
      <p style="color:#64748B;font-size:0.95rem;margin:0;">
        Resume analysis · 2 targeted questions · AI readiness score
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Step bar
    steps_info = [
        ("1", "Resume Upload", step > 1),
        ("2", "Role Selection", step > 2),
        ("3", "Quick Interview", step > 3),
    ]
    bar_html = '<div class="stitch-step-bar">'
    for num, label, done in steps_info:
        cur = (int(num) == step)
        cls = "done" if done else ("active" if cur else "")
        icon = "✓" if done else num
        bar_html += f'<div class="stitch-step {cls}">{icon} &nbsp;{label}</div>'
    bar_html += "</div>"
    st.markdown(bar_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # STEP 1: Resume Upload
    # ─────────────────────────────────────────────
    if step == 1:
        st.markdown('<p style="color:#B5B5B5;font-size:0.9rem;margin-bottom:1rem;">Upload your resume for ATS analysis and personalized questions (optional but recommended).</p>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Drop your resume here (PDF / DOCX / TXT)",
            type=["pdf", "docx", "txt"],
            key="scan_upload",
            label_visibility="collapsed",
        )
        st.markdown("""
        <div class="upload-zone">
          <div style="font-size:2.5rem;margin-bottom:0.5rem;">📄</div>
          <p style="color:#16A34A;font-weight:700;margin:0 0 0.3rem;">Drag & drop your resume</p>
          <p style="color:#64748B;font-size:0.82rem;margin:0;">PDF, DOCX, or TXT · Max 10MB</p>
        </div>""", unsafe_allow_html=True)

        if uploaded:
            with st.spinner("Analyzing your resume…"):
                file_bytes = uploaded.read()
                token = st.session_state.get("token", "")
                # Try backend API for full analysis
                api_result = _analyze_resume_via_api(file_bytes, uploaded.name, token)
                if api_result["ats_score"] > 0:
                    raw_text = _extract_text_local(file_bytes, uploaded.name)
                    skills = api_result["skills"]
                    ats = {"ats_score": api_result["ats_score"], "missing": api_result["missing"]}
                else:
                    # Fallback: local text extraction only, no ATS score
                    raw_text = _extract_text_local(file_bytes, uploaded.name)
                    skills = {}
                    ats = {"ats_score": 0, "missing": []}

            st.session_state["scan_resume_text"] = raw_text
            st.session_state["scan_ats"]         = ats.get("ats_score", 0)
            st.session_state["scan_skills"]      = skills
            st.session_state["scan_missing"]     = ats.get("missing", [])

            # Show ATS results
            col_ring, col_info = st.columns([1, 2])
            with col_ring:
                st.markdown(_ats_ring(ats.get("ats_score", 0)), unsafe_allow_html=True)
            with col_info:
                st.markdown('<p style="color:#FFFFFF;font-weight:700;margin:0 0 0.5rem;">Detected Skills</p>', unsafe_allow_html=True)
                badges_html = ""
                for cat, kws in skills.items():
                    for kw in kws[:4]:
                        badges_html += f'<span class="skill-badge">{html_escape(kw)}</span>'
                if not badges_html:
                    badges_html = '<span style="color:#777777;font-size:0.83rem;">No skills detected — try a more detailed resume.</span>'
                st.markdown(badges_html, unsafe_allow_html=True)

                if ats.get("missing"):
                    st.markdown('<p style="color:#F59E0B;font-size:0.78rem;margin:0.6rem 0 0.3rem;font-weight:600;">Missing ATS Keywords</p>', unsafe_allow_html=True)
                    miss_html = "".join(f'<span class="skill-badge cyan">{html_escape(k)}</span>' for k in ats["missing"][:5])
                    st.markdown(miss_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("Continue without resume →", key="skip_resume", use_container_width=True):
                st.session_state["scan_step"] = 2
                st.rerun()
        with c3:
            if uploaded and st.button("✅  Proceed with Resume →", key="proceed_resume", use_container_width=True):
                st.session_state["scan_step"] = 2
                st.rerun()

    # ─────────────────────────────────────────────
    # STEP 2: Role Selection
    # ─────────────────────────────────────────────
    elif step == 2:
        st.markdown('<p style="color:#B5B5B5;font-size:0.9rem;margin-bottom:1.5rem;">Select the role you are targeting. This personalizes both questions to your specific career goal.</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            role = st.selectbox("Target Role", ROLES, key="role_sel",
                                index=ROLES.index(st.session_state["scan_role"]) if st.session_state["scan_role"] in ROLES else 0)
        with col2:
            level = st.selectbox("Experience Level", LEVELS, key="level_sel",
                                 index=LEVELS.index(st.session_state["scan_level"]) if st.session_state["scan_level"] in LEVELS else 2)
        with col3:
            itype = st.selectbox("Interview Type", TYPES, key="type_sel",
                                 index=TYPES.index(st.session_state["scan_type"]) if st.session_state["scan_type"] in TYPES else 0)

        # Dynamic description based on chosen type
        type_desc = {
            "Technical":         "2 technical questions — one conceptual, one applied/practical — tailored to your role.",
            "Behavioral / HR":   "2 STAR-method behavioral/HR questions — one on collaboration, one on challenges & achievements.",
            "System Design":     "2 system design questions — one architecture overview, one component deep-dive — for your role.",
            "Project Discussion":"2 project-focused questions — one on a past project's impact, one on technical decisions made.",
            "Problem Solving":   "2 analytical problem-solving questions — one logical puzzle, one real-world scenario for your role.",
            "Rapid Fire":        "2 rapid-fire questions — quick, concise answers expected. Tests breadth and clarity under pressure.",
            "Case Study":        "2 case study questions — one business/technical case analysis, one on your recommended solution.",
            "Mixed Interview":   "2 mixed questions — one technical/domain-specific, one behavioral/situational for full-spectrum coverage.",
        }.get(itype, "2 AI-generated questions tailored to your role and interview type.")
        st.markdown(f"""
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);
                    border-radius:16px;padding:1rem 1.5rem;margin-top:1rem;">
          <p style="color:#16A34A;font-weight:700;font-size:0.88rem;margin:0 0 0.4rem;">What happens next?</p>
          <p style="color:#64748B;font-size:0.82rem;margin:0;line-height:1.6;">
            AI will generate {type_desc}
            Answer by <strong style="color:#B5B5B5;">typing or voice</strong>. Evaluation takes ~30 seconds.
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("← Back", key="back_step2", use_container_width=True):
                st.session_state["scan_step"] = 1
                st.rerun()
        with c3:
            if st.button("🚀  Generate My Questions →", key="gen_questions", use_container_width=True):
                st.session_state["scan_role"]  = role
                st.session_state["scan_level"] = level
                st.session_state["scan_type"]  = itype
                with st.spinner("Generating personalized questions…"):
                    result = start_quick_scan(
                        role=role,
                        experience_level=level,
                        interview_type=itype,
                        resume_text=st.session_state.get("scan_resume_text", ""),
                    )
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state["scan_session"] = result["session_id"]
                    st.session_state["scan_q1"]      = result["question1"]
                    st.session_state["scan_q2"]      = result["question2"]
                    st.session_state["scan_step"]    = 3
                    st.rerun()

    # ─────────────────────────────────────────────
    # STEP 3: Quick 2-Question Interview
    # ─────────────────────────────────────────────
    elif step == 3:
        q1 = st.session_state.get("scan_q1", {})
        q2 = st.session_state.get("scan_q2", {})
        scan_type = st.session_state.get("scan_type", "Technical")
        token = st.session_state.get("token", "")

        # Badge colors by type
        badge_color = "#16A34A" if scan_type == "Technical" else "#4ADE80"
        badge_bg    = "rgba(22,163,74,0.18)" if scan_type == "Technical" else "rgba(74,222,128,0.12)"

        st.markdown(f"""
        <div style="background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.2);
                    border-radius:12px;padding:0.7rem 1.2rem;margin-bottom:1.5rem;
                    display:flex;align-items:center;gap:0.6rem;">
          <span style="font-size:1.1rem;">🎯</span>
          <span style="color:#B5B5B5;font-size:0.85rem;">
            <strong style="color:#16A34A;">{html_escape(st.session_state['scan_role'])}</strong> ·
            {html_escape(st.session_state['scan_level'])} · {html_escape(scan_type)}
          </span>
          <span style="margin-left:auto;color:#64748B;font-size:0.75rem;">2 questions · ~90 seconds</span>
        </div>""", unsafe_allow_html=True)

        # ── Question 1 ─────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="stitch-q-card">
          <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span style="background:{badge_bg};color:{badge_color};border-radius:99px;
                         padding:2px 14px;font-size:0.72rem;font-weight:700;
                         font-family:'Space Grotesk',sans-serif;letter-spacing:0.05em;">
              Q1 — {html_escape(scan_type)}
            </span>
          </div>
          <p style="color:#e3e0f3;font-size:1.05rem;font-weight:500;margin:0;line-height:1.65;">
            {html_escape(q1.get('text', ''))}
          </p>
        </div>""", unsafe_allow_html=True)

        tab_text1, tab_voice1 = st.tabs(["⌨️  Type Answer", "🎙️  Voice Answer"])

        with tab_text1:
            q1_typed = st.text_area(
                "Q1 text answer", key="q1_text_input",
                placeholder="Type your answer here... Be concise but complete. 3–5 sentences recommended.",
                height=120, label_visibility="collapsed",
            )
            if q1_typed.strip():
                st.session_state["scan_q1_ans"]    = q1_typed
                st.session_state["scan_q1_method"] = "text"

        with tab_voice1:
            audio1 = st.audio_input("🎤 Record your answer to Q1", key="q1_voice_rec")
            if audio1 is not None:
                c_t1, c_r1 = st.columns([2, 1])
                with c_t1:
                    if st.button("🔊 Transcribe Q1 Answer", key="q1_transcribe", use_container_width=True, type="primary"):
                        with st.spinner("Transcribing your response…"):
                            try:
                                audio1.seek(0)
                                ab1 = audio1.read()
                                if len(ab1) < 500:
                                    st.warning("Recording too short — please speak for at least 2 seconds.")
                                else:
                                    r1 = req.post(
                                        f"{BACKEND}/api/voice/transcribe-only",
                                        files={"audio": ("rec.webm", ab1, "audio/webm")},
                                        headers={"Authorization": f"Bearer {token}"},
                                        timeout=40,
                                    )
                                    if r1.ok:
                                        t1 = r1.json().get("transcript", "")
                                        if t1:
                                            st.session_state["scan_q1_voice_text"] = t1
                                            st.session_state["scan_q1_ans"]        = t1
                                            st.session_state["scan_q1_method"]     = "voice"
                                            st.success("✅ Transcribed! Review and edit below.")
                                        else:
                                            st.warning("Couldn't catch that — try re-recording.")
                                    else:
                                        st.error(f"Backend error: {r1.status_code}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                with c_r1:
                    if st.button("🔄 Re-record", key="q1_redo", use_container_width=True):
                        st.session_state.pop("scan_q1_voice_text", None)
                        st.session_state["scan_q1_ans"] = ""
                        st.rerun()

            saved_q1_voice = st.session_state.get("scan_q1_voice_text", "")
            if saved_q1_voice:
                edited_q1 = st.text_area(
                    "Transcribed Q1 (edit if needed)", value=saved_q1_voice,
                    height=110, key="q1_voice_edit", label_visibility="collapsed",
                )
                st.session_state["scan_q1_ans"]    = edited_q1
                st.session_state["scan_q1_method"] = "voice"
            elif audio1 is None:
                st.markdown('<p style="color:#777777;font-size:0.8rem;text-align:center;padding:0.5rem 0;">Record above then click Transcribe</p>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Question 2 ─────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="stitch-q-card secondary">
          <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span style="background:{badge_bg};color:{badge_color};border-radius:99px;
                         padding:2px 14px;font-size:0.72rem;font-weight:700;
                         font-family:'Space Grotesk',sans-serif;letter-spacing:0.05em;">
              Q2 — {html_escape(scan_type)}
            </span>
          </div>
          <p style="color:#e3e0f3;font-size:1.05rem;font-weight:500;margin:0;line-height:1.65;">
            {html_escape(q2.get('text', ''))}
          </p>
        </div>""", unsafe_allow_html=True)

        tab_text2, tab_voice2 = st.tabs(["⌨️  Type Answer", "🎙️  Voice Answer"])

        with tab_text2:
            q2_typed = st.text_area(
                "Q2 text answer", key="q2_text_input",
                placeholder="Type your answer here... Show depth and clarity.",
                height=120, label_visibility="collapsed",
            )
            if q2_typed.strip():
                st.session_state["scan_q2_ans"]    = q2_typed
                st.session_state["scan_q2_method"] = "text"

        with tab_voice2:
            audio2 = st.audio_input("🎤 Record your answer to Q2", key="q2_voice_rec")
            if audio2 is not None:
                c_t2, c_r2 = st.columns([2, 1])
                with c_t2:
                    if st.button("🔊 Transcribe Q2 Answer", key="q2_transcribe", use_container_width=True, type="primary"):
                        with st.spinner("Transcribing your response…"):
                            try:
                                audio2.seek(0)
                                ab2 = audio2.read()
                                if len(ab2) < 500:
                                    st.warning("Recording too short — please speak for at least 2 seconds.")
                                else:
                                    r2 = req.post(
                                        f"{BACKEND}/api/voice/transcribe-only",
                                        files={"audio": ("rec.webm", ab2, "audio/webm")},
                                        headers={"Authorization": f"Bearer {token}"},
                                        timeout=40,
                                    )
                                    if r2.ok:
                                        t2 = r2.json().get("transcript", "")
                                        if t2:
                                            st.session_state["scan_q2_voice_text"] = t2
                                            st.session_state["scan_q2_ans"]        = t2
                                            st.session_state["scan_q2_method"]     = "voice"
                                            st.success("✅ Transcribed! Review and edit below.")
                                        else:
                                            st.warning("Couldn't catch that — try re-recording.")
                                    else:
                                        st.error(f"Backend error: {r2.status_code}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                with c_r2:
                    if st.button("🔄 Re-record", key="q2_redo", use_container_width=True):
                        st.session_state.pop("scan_q2_voice_text", None)
                        st.session_state["scan_q2_ans"] = ""
                        st.rerun()

            saved_q2_voice = st.session_state.get("scan_q2_voice_text", "")
            if saved_q2_voice:
                edited_q2 = st.text_area(
                    "Transcribed Q2 (edit if needed)", value=saved_q2_voice,
                    height=110, key="q2_voice_edit", label_visibility="collapsed",
                )
                st.session_state["scan_q2_ans"]    = edited_q2
                st.session_state["scan_q2_method"] = "voice"
            elif audio2 is None:
                st.markdown('<p style="color:#777777;font-size:0.8rem;text-align:center;padding:0.5rem 0;">Record above then click Transcribe</p>', unsafe_allow_html=True)

        # ── Submit ──────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("← Back", key="back_step3", use_container_width=True):
                st.session_state["scan_step"] = 2
                st.rerun()
        with c3:
            if st.button("⚡  Analyze My Readiness →", key="submit_scan", use_container_width=True):
                final_q1 = st.session_state.get("scan_q1_ans", "").strip()
                final_q2 = st.session_state.get("scan_q2_ans", "").strip()
                if not final_q1 or not final_q2:
                    st.warning("⚠️ Please answer both questions (type or voice) before submitting.")
                else:
                    with st.spinner("Building your readiness report…"):
                        report = complete_quick_scan(
                            session_id=st.session_state["scan_session"],
                            q1_id=q1["id"],
                            q1_answer=final_q1,
                            q1_method=st.session_state.get("scan_q1_method", "text"),
                            q2_id=q2["id"],
                            q2_answer=final_q2,
                            q2_method=st.session_state.get("scan_q2_method", "text"),
                            ats_score=st.session_state.get("scan_ats", 0),
                            resume_skills=st.session_state.get("scan_skills", {}),
                            missing_keywords=st.session_state.get("scan_missing", []),
                        )
                    if "error" in report:
                        st.error(f"❌ {report['error']}")
                    else:
                        st.session_state["scan_report"] = report
                        st.session_state["page"] = "readiness_report"
                        st.rerun()
