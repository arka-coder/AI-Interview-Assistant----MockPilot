"""
MockPilot AI — Interview Room
The core interview experience: setup → question → answer → feedback loop.
"""
import streamlit as st
import time
import json
import requests as req
import os
from components.ui_components import (
    inject_css, section_header, ai_avatar, question_display,
    timer_display, mic_visualizer, thinking_loader, html_escape
)
from api_client import (
    start_session, get_current_question, submit_answer,
    complete_session, list_resumes
)

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

ROLES = [
    "Software Engineer", "Data Scientist", "Product Manager", "ML Engineer",
    "DevOps Engineer", "Backend Developer", "Frontend Developer", "Full Stack Developer",
    "Data Analyst", "Business Analyst", "Cloud Architect", "AI Engineer",
    "Data Engineer", "System Architect", "Mobile Developer", "QA Engineer",
]
INTERVIEW_TYPES = [
    "HR / Cultural Fit", "Technical", "Behavioral (STAR)",
    "Business Development", "Data Science", "System Design"
]
EXPERIENCE_LEVELS = ["Junior (0-2 yrs)", "Mid-Level (2-5 yrs)", "Senior (5-10 yrs)", "Lead / Principal (10+ yrs)"]
LEVEL_MAP = {"Junior (0-2 yrs)": "junior", "Mid-Level (2-5 yrs)": "mid",
             "Senior (5-10 yrs)": "senior", "Lead / Principal (10+ yrs)": "lead"}
MAX_QUESTIONS = 10

ROOM_CSS = """
<style>
.focus-question {
  background:#111311;
  border:1px solid rgba(255,255,255,0.08);
  border-radius:18px;padding:2rem 2rem 1.75rem;
  position:relative;overflow:hidden;
  box-shadow:0 0 0 1px rgba(34,197,94,0.14), 0 8px 30px rgba(0,0,0,0.35);
}
.focus-question::before {
  content:'';position:absolute;top:0;left:0;bottom:0;width:3px;
  background:#22C55E;border-radius:0 3px 3px 0;
}
.q-badge {
  display:inline-flex;align-items:center;gap:0.4rem;
  background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);
  border-radius:99px;padding:3px 12px;
  font-size:0.7rem;font-weight:700;color:#16A34A;
  letter-spacing:0.05em;margin-bottom:0.75rem;text-transform:uppercase;
}
.mode-badge {
  display:inline-flex;align-items:center;gap:0.4rem;
  background:rgba(22,163,74,0.08);border:1px solid rgba(22,163,74,0.2);
  border-radius:99px;padding:3px 12px;font-size:0.7rem;font-weight:700;color:#86EFAC;
}
.recruiter-card {
  background:linear-gradient(135deg,rgba(16,185,129,0.05),rgba(22,163,74,0.03));
  border:1px solid rgba(16,185,129,0.18);border-radius:20px;padding:1.3rem 1.5rem;
  margin-top:1rem;
}
.recruiter-bar {
  height:3px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;margin-top:4px;
}
.recruiter-bar-fill {
  height:100%;background:linear-gradient(90deg,#22C55E,#16A34A);border-radius:99px;transition:width 1.2s ease;
}

/* ── AI Hero Banner ──────────────────────────────────────────────── */
@keyframes heroGradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes particleFloat {
  0%,100% { transform: translateY(0px) translateX(0px) scale(1); opacity:0.4; }
  33%      { transform: translateY(-18px) translateX(8px) scale(1.1); opacity:0.7; }
  66%      { transform: translateY(-8px) translateX(-6px) scale(0.95); opacity:0.5; }
}
@keyframes heroShimmer {
  0%   { transform: translateX(-100%) skewX(-12deg); }
  100% { transform: translateX(300%) skewX(-12deg); }
}
@keyframes heroBadgePulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(22,163,74,0.4); }
  50%      { box-shadow: 0 0 0 6px rgba(22,163,74,0); }
}
@keyframes heroTitleReveal {
  from { opacity:0; transform: translateY(20px); }
  to   { opacity:1; transform: translateY(0); }
}
@keyframes pillFadeIn {
  from { opacity:0; transform: translateY(12px) scale(0.92); }
  to   { opacity:1; transform: translateY(0) scale(1); }
}
@keyframes borderGlow {
  0%,100% { border-color: rgba(34,197,94,0.35); }
  50%      { border-color: rgba(74,222,128,0.45); }
}
@keyframes ctaPulse {
  0%,100% { box-shadow: 0 6px 20px rgba(34,197,94,0.14); }
  50%      { box-shadow: 0 10px 30px rgba(34,197,94,0.22); }
}

.ai-hero-banner {
  position: relative;
  overflow: hidden;
  border-radius: 22px;
  padding: 2.5rem 2.5rem 2.25rem;
  margin-bottom: 2rem;
  background: #111311;
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 8px 30px rgba(0,0,0,0.35);
}

/* Single restrained emerald wash — no animated mesh */
.ai-hero-banner::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 60% 80% at 100% 0%, rgba(34,197,94,0.06), transparent 60%);
  pointer-events: none;
}
.ai-hero-banner::after { content: none; }

/* Top accent line — static, subtle */
.hero-top-line {
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34,197,94,0.5), transparent);
}

/* Ambient particles removed for a calm, executive surface */
.hero-particle, .hero-p1, .hero-p2, .hero-p3, .hero-p4 { display: none !important; }

/* Badge */
.hero-top-badge {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: rgba(34,197,94,0.15);
  border: 1px solid rgba(22,163,74,0.35);
  border-radius: 99px;
  padding: 5px 16px;
  font-size: 0.72rem; font-weight: 700; color: #4ADE80;
  letter-spacing: 0.8px; text-transform: uppercase;
  margin-bottom: 1rem;
  animation: heroBadgePulse 2.5s ease-in-out infinite;
  position: relative; z-index: 2;
}
.hero-badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #16A34A;
  box-shadow: 0 0 6px rgba(22,163,74,0.35);
}

/* Main title */
.hero-main-title {
  font-size: 2.5rem; font-weight: 800; line-height: 1.1;
  letter-spacing: -0.035em;
  margin: 0 0 0.75rem;
  color: #FFFFFF;
  animation: heroTitleReveal 0.6s 0.05s ease-out both;
  position: relative; z-index: 2;
}

/* Subtitle */
.hero-subtitle {
  font-size: 1rem; color: #B5B5B5; line-height: 1.7;
  margin: 0 0 1.5rem; max-width: 600px;
  animation: heroTitleReveal 0.7s 0.25s ease-out both;
  position: relative; z-index: 2;
}

/* Feature pills */
.hero-pills {
  display: flex; flex-wrap: wrap; gap: 0.6rem;
  position: relative; z-index: 2;
}
.hero-pill {
  display: inline-flex; align-items: center; gap: 0.4rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px;
  padding: 6px 16px;
  font-size: 0.78rem; font-weight: 600; color: #CBD5E1;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  cursor: default;
}
.hero-pill:hover {
  background: rgba(34,197,94,0.2);
  border-color: rgba(22,163,74,0.5);
  color: #E2E8F0;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(34,197,94,0.25);
}
.hero-pill.p1 { animation: pillFadeIn 0.5s 0.35s ease-out both; }
.hero-pill.p2 { animation: pillFadeIn 0.5s 0.45s ease-out both; }
.hero-pill.p3 { animation: pillFadeIn 0.5s 0.55s ease-out both; }
.hero-pill.p4 { animation: pillFadeIn 0.5s 0.65s ease-out both; }
.hero-pill.p5 { animation: pillFadeIn 0.5s 0.75s ease-out both; }

/* Setup form container */
.setup-form-card {
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 20px;
  padding: 1.6rem 1.8rem 1.4rem;
  margin-bottom: 1.25rem;
  backdrop-filter: blur(12px);
  position: relative;
}
.setup-form-card::before {
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent);
}

/* Enhanced CTA */
.launch-cta-wrapper {
  position: relative;
}
.launch-cta-wrapper .stButton > button {
  background: #22C55E !important;
  color: #052e13 !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.01em !important;
  min-height: 48px !important;
  padding: 0.8rem 2rem !important;
  border-radius: 14px !important;
  border: none !important;
  animation: ctaPulse 3s ease-in-out infinite !important;
  position: relative; overflow: hidden;
}
.launch-cta-wrapper .stButton > button:hover {
  transform: translateY(-1px) !important;
  background: #16A34A !important;
  box-shadow: 0 10px 30px rgba(34,197,94,0.22) !important;
}
</style>
"""


def render():
    inject_css()
    st.markdown(ROOM_CSS, unsafe_allow_html=True)
    # Route sub-views
    stage = st.session_state.get("interview_stage", "setup")
    if stage == "setup":
        _render_setup()
    elif stage == "active":
        _render_active()
    elif stage == "completed":
        _render_completed()


# ── Setup Screen ──────────────────────────────────────────────────────────────

def _render_setup():
    # ── Premium AI Hero Banner ────────────────────────────────────────
    st.markdown("""
    <div class="ai-hero-banner fade-in-up">
      <!-- Gradient accent top line -->
      <div class="hero-top-line"></div>

      <!-- Floating ambient glow particles -->
      <div class="hero-particle hero-p1"></div>
      <div class="hero-particle hero-p2"></div>
      <div class="hero-particle hero-p3"></div>
      <div class="hero-particle hero-p4"></div>

      <!-- Top badge -->
      <div style="position:relative;z-index:2;">
        <div class="hero-top-badge">
          <div class="hero-badge-dot"></div>
          ⚡ Advanced AI Interview Experience
        </div>
      </div>

      <!-- Main title -->
      <h1 class="hero-main-title">🎤 Full AI Mock Interview</h1>

      <!-- Subheadline -->
      <p class="hero-subtitle">
        Adaptive AI interviewer with contextual follow-ups, live voice mode, and real-time scoring.
      </p>

      <!-- Feature pills -->
      <div class="hero-pills">
        <div class="hero-pill p1">⚡ Adaptive Questions</div>
        <div class="hero-pill p2">🎙 Voice AI</div>
        <div class="hero-pill p3">📊 Deep Analytics</div>
        <div class="hero-pill p4">🧠 Context-Aware Follow-Ups</div>
        <div class="hero-pill p5">🚀 Real-Time Evaluation</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Interview Setup Form ──────────────────────────────────────────
    # Resolve preset from Recommended Practice cards on the dashboard
    _PRESET_MAP = {
        "behavioral": "Behavioral (STAR)",
        "technical":  "Technical",
        "hr":         "HR / Cultural Fit",
    }
    preset_key = st.session_state.pop("interview_type_preset", None)
    preset_label = _PRESET_MAP.get(preset_key)
    type_default_idx = INTERVIEW_TYPES.index(preset_label) if preset_label in INTERVIEW_TYPES else 0

    _, col, _ = st.columns([0.5, 3, 0.5])
    with col:
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("🎯 Target Role", ROLES, key="setup_role")
            exp  = st.selectbox("📊 Experience Level", EXPERIENCE_LEVELS, key="setup_exp")
        with col2:
            itype = st.selectbox("🧩 Interview Type", INTERVIEW_TYPES,
                                 index=type_default_idx, key="setup_type")
            resumes = list_resumes()
            resume_options = ["None (general interview)"] + [
                f"📄 {r['filename'][:40]}" for r in resumes
            ]
            resume_choice = st.selectbox("📋 Use Resume (optional)", resume_options, key="setup_resume")

        # Interview preview card
        st.markdown(f"""
        <div class="interview-preview-box">
          <p style="color:#16A34A;font-weight:700;font-size:0.78rem;text-transform:uppercase;
                    letter-spacing:0.5px;margin:0 0 0.5rem;">📋 Interview Preview</p>
          <p style="color:#E2E8F0;font-size:0.95rem;font-weight:600;margin:0 0 0.25rem;">
            {html_escape(role)}
          </p>
          <p style="color:#B5B5B5;font-size:0.82rem;margin:0;">
            {html_escape(exp)} &nbsp;·&nbsp; {html_escape(itype)} &nbsp;·&nbsp; Up to {MAX_QUESTIONS} adaptive AI questions
          </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀  Launch Interview Session", key="start_btn", use_container_width=True):
            resume_id = None
            if resume_choice != "None (general interview)":
                idx = resume_options.index(resume_choice) - 1
                resume_id = resumes[idx]["id"] if idx >= 0 else None

            with st.spinner("Preparing your AI interviewer..."):
                result = start_session(
                    role=role,
                    experience_level=LEVEL_MAP.get(exp, "mid"),
                    interview_type=itype.split(" /")[0],
                    resume_id=resume_id,
                )
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.session_state.update({
                    "session_id":       result["id"],
                    "session_role":     role,
                    "session_type":     itype,
                    "session_exp":      exp,
                    "question_number":  1,
                    "all_feedback":     [],
                    "interview_stage":  "active",
                    "answer_submitted": False,
                    "last_feedback":    None,
                    "last_question":    None,
                })
                st.rerun()



# ── Active Interview ──────────────────────────────────────────────────────────

def _render_active():
    session_id  = st.session_state.get("session_id")
    q_num       = st.session_state.get("question_number", 1)
    role        = st.session_state.get("session_role", "")
    itype       = st.session_state.get("session_type", "")

    # Sidebar status
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem 0;">
          <p style="color:#16A34A;font-weight:700;font-size:0.85rem;margin:0 0 0.3rem;">
            LIVE INTERVIEW
          </p>
          <p style="color:#FFFFFF;font-weight:600;font-size:0.95rem;margin:0;">{role}</p>
          <p style="color:#777777;font-size:0.8rem;margin:2px 0 0;">{itype}</p>
          <hr style="border-color:rgba(255,255,255,0.08);margin:0.75rem 0;">
          <p style="color:#B5B5B5;font-size:0.8rem;margin:0;">Question</p>
          <p style="font-size:1.8rem;font-weight:800;color:#16A34A;margin:0;">
            {q_num}<span style="font-size:1rem;color:#777777;">/{MAX_QUESTIONS}</span>
          </p>
        </div>""", unsafe_allow_html=True)
        st.progress(q_num / MAX_QUESTIONS)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(":material/stop_circle: End interview early", use_container_width=True):
            with st.spinner("Finishing up..."):
                complete_session(session_id)
            st.session_state["interview_stage"] = "completed"
            st.rerun()

    # Load current question
    if not st.session_state.get("last_question"):
        with st.spinner(""):
            thinking_loader("AI Interviewer is preparing your question...")
            time.sleep(0.5)
            q_data = get_current_question(session_id)
        if "error" in q_data:
            st.error(q_data["error"])
            return
        st.session_state["last_question"] = q_data

    q_data = st.session_state["last_question"]

    # ── Question meta bar: progress · difficulty · category · est. time ──
    exp = st.session_state.get("session_exp", "")
    _diff = ("Foundational" if "Junior" in exp else "Advanced" if "Senior" in exp
             else "Expert" if "Lead" in exp else "Intermediate")
    _cat = (itype.split(" /")[0] if itype else "General")
    _ICON = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#86EFAC" '
             'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
             'style="flex-shrink:0;">{p}</svg>')
    _p_layers = '<path d="M2 20h.01"/><path d="M7 20v-4"/><path d="M12 20v-8"/><path d="M17 20V8"/>'
    _p_gauge  = '<path d="M12 2v4"/><path d="M12 18v4"/><circle cx="12" cy="12" r="4"/>'
    _p_tag    = '<path d="M12.5 2H20v7.5L9.5 20 2 12.5z"/><circle cx="7" cy="7" r="1"/>'
    _p_clock  = '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'
    def _mchip(icon, label, value):
        return (f'<div style="display:flex;align-items:center;gap:8px;">'
                f'{icon}'
                f'<div style="line-height:1.15;"><div style="font-family:Inter,sans-serif;font-size:0.6rem;'
                f'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#777777;">{label}</div>'
                f'<div style="font-family:Inter,sans-serif;font-size:0.82rem;font-weight:600;color:#FFFFFF;">{value}</div>'
                f'</div></div>')
    _sep = '<div style="width:1px;height:26px;background:rgba(255,255,255,0.08);"></div>'
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1.25rem;flex-wrap:wrap;'
        'background:#111311;border:1px solid rgba(255,255,255,0.08);border-radius:14px;'
        'padding:0.85rem 1.25rem;margin-bottom:1rem;box-shadow:0 8px 30px rgba(0,0,0,0.35);">'
        + _mchip(_ICON.format(p=_p_layers), "Progress", f"Question {q_num} of {MAX_QUESTIONS}")
        + _sep + _mchip(_ICON.format(p=_p_gauge), "Difficulty", _diff)
        + _sep + _mchip(_ICON.format(p=_p_tag), "Category", _cat)
        + _sep + _mchip(_ICON.format(p=_p_clock), "Est. time", "~2 min")
        + '</div>', unsafe_allow_html=True)

    # Layout
    col_avatar, col_main = st.columns([1, 4])
    with col_avatar:
        ai_avatar(thinking=False)

    with col_main:
        question_display(q_data["question_text"], q_num, MAX_QUESTIONS)

    st.markdown("<br>", unsafe_allow_html=True)

    # Inject browser TTS to read question aloud
    _inject_question_tts(q_data["question_text"], q_num)

    # Answer area
    if not st.session_state.get("answer_submitted"):

        voice_mode = st.session_state.get("voice_mode", False)

        # ── Mode toggle bar ───────────────────────────────────────
        c_label, c_toggle = st.columns([3, 1])
        with c_label:
            st.markdown(
                '<p style="color:#B5B5B5;font-size:0.85rem;margin:0;font-weight:500;">'
                f'{"Voice mode active" if voice_mode else "Your answer"}</p>',
                unsafe_allow_html=True,
            )
        with c_toggle:
            if voice_mode:
                if st.button(":material/keyboard: Switch to text", key=f"switch_text_{q_num}",
                             use_container_width=True):
                    st.session_state["voice_mode"] = False
                    st.rerun()
            else:
                if st.button(":material/mic: Use voice", key=f"switch_voice_{q_num}",
                             use_container_width=True):
                    st.session_state["voice_mode"] = True
                    st.rerun()

        st.markdown("<br style='margin:0;'>", unsafe_allow_html=True)

        if voice_mode:
            # ── Voice mode: show voice UI directly, no tab click needed ──
            _render_voice_tab(session_id, q_data, q_num)
        else:
            # ── Text mode: original tabs ──────────────────────────────────
            answer_tab, voice_tab = st.tabs([":material/keyboard: Type answer", ":material/mic: Live voice"])

            with answer_tab:
                answer = st.text_area(
                    "Write your answer here...",
                    height=160,
                    key=f"answer_text_{q_num}",
                    label_visibility="collapsed",
                    placeholder="Type your detailed answer here. Be specific, use examples, and structure your response clearly...",
                )
                col_sub, col_skip = st.columns([3, 1])
                with col_sub:
                    if st.button(":material/auto_awesome: Analyze response", key=f"submit_{q_num}", use_container_width=True):
                        if not answer or len(answer.strip()) < 10:
                            st.warning("Please write a more detailed answer (at least 10 characters).")
                        else:
                            _submit_answer(session_id, q_data["id"], answer, "text")
                with col_skip:
                    if st.button(":material/skip_next: Skip", key=f"skip_{q_num}", use_container_width=True):
                        _submit_answer(session_id, q_data["id"], "I'll skip this question.", "text")

            with voice_tab:
                _render_voice_tab(session_id, q_data, q_num)

    else:
        # Show submitted state + feedback
        feedback = st.session_state.get("last_feedback", {})
        _show_inline_feedback(feedback)

        next_q = feedback.get("next_question")
        if next_q and q_num < MAX_QUESTIONS:
            if st.button(":material/arrow_forward: Next question", key="next_q_btn", use_container_width=True):
                st.session_state.update({
                    "question_number":  q_num + 1,
                    "answer_submitted": False,
                    "last_question":    None,
                    "last_feedback":    None,
                    # voice_mode intentionally NOT reset — stays sticky
                })
                st.rerun()
        else:
            st.success("Interview complete!")
            if st.button(":material/assessment: View full results", key="view_results", use_container_width=True):
                st.session_state["interview_stage"] = "completed"
                st.rerun()


# ── Voice Tab ─────────────────────────────────────────────────────────────────

def _inject_question_tts(question_text: str, q_num: int):
    """Inject JS to read the question aloud via browser Speech Synthesis.
    Only fires once per question number."""
    safe_text = json.dumps(str(question_text).replace("\n", " "))
    st.components.v1.html(f"""
<script>
(function(){{
  const key = 'tts_q_{q_num}';
  if (sessionStorage.getItem(key)) return;
  sessionStorage.setItem(key, '1');
  const speak = () => {{
    if (!window.speechSynthesis) return;
    const u = new SpeechSynthesisUtterance({safe_text});
    const voices = window.speechSynthesis.getVoices();
    const v = voices.find(x => x.lang.startsWith('en') && x.name.includes('Google'))
           || voices.find(x => x.lang.startsWith('en'));
    if (v) u.voice = v;
    u.rate = 0.92; u.pitch = 1.0;
    window.speechSynthesis.speak(u);
  }};
  if (window.speechSynthesis.getVoices().length) speak();
  else window.speechSynthesis.onvoiceschanged = speak;
}})();
</script>""", height=0)


def _render_voice_tab(session_id: int, q_data: dict, q_num: int):
    """Live voice tab: record → transcribe → review → submit."""
    token = st.session_state.get("token", "")
    transcript_key = f"voice_transcript_{q_num}"
    audio_key      = f"voice_rec_{q_num}"

    st.markdown("""
    <style>
    .vc-panel{background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.2);
              border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:0.75rem;}
    .vc-step{display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem;}
    .vc-step-num{width:22px;height:22px;border-radius:50%;background:rgba(34,197,94,0.3);
                 color:#16A34A;font-size:0.72rem;font-weight:700;display:flex;
                 align-items:center;justify-content:center;flex-shrink:0;}
    .vc-step-txt{color:#B5B5B5;font-size:0.82rem;}
    .vc-label{color:#4ADE80;font-size:0.78rem;font-weight:600;text-transform:uppercase;
              letter-spacing:0.5px;margin:0.9rem 0 0.35rem;}
    </style>
    """, unsafe_allow_html=True)

    # ── Step guide ────────────────────────────────────────────────
    st.markdown("""
    <div class="vc-panel">
      <p style="color:#E2E8F0;font-weight:700;font-size:0.95rem;margin:0 0 0.75rem;">
        🎙️ How to answer with voice
      </p>
      <div class="vc-step">
        <div class="vc-step-num">1</div>
        <span class="vc-step-txt">Click <strong style="color:#E2E8F0;">Start recording</strong> below and speak your answer</span>
      </div>
      <div class="vc-step">
        <div class="vc-step-num">2</div>
        <span class="vc-step-txt">Click <strong style="color:#E2E8F0;">Stop</strong> when done</span>
      </div>
      <div class="vc-step">
        <div class="vc-step-num">3</div>
        <span class="vc-step-txt">Click <strong style="color:#16A34A;">Transcribe my answer</strong> to convert speech to text</span>
      </div>
      <div class="vc-step">
        <div class="vc-step-num">4</div>
        <span class="vc-step-txt">Review the transcript, edit if needed, then <strong style="color:#10B981;">Submit</strong></span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Step 1 & 2 — Record ───────────────────────────────────────
    audio_value = st.audio_input("🎤 Record your answer", key=audio_key)

    # ── Step 3 — Transcribe button (only when audio exists) ───────
    if audio_value is not None:
        col_t, col_r = st.columns([2, 1])
        with col_t:
            transcribe_clicked = st.button(
                "🔊 Transcribe my answer",
                key=f"transcribe_btn_{q_num}",
                use_container_width=True,
                type="primary",
            )
        with col_r:
            if st.button("🔄 Re-record", key=f"voice_redo_{q_num}", use_container_width=True):
                st.session_state.pop(transcript_key, None)
                st.rerun()

        if transcribe_clicked:
            with st.spinner("Transcribing your response…"):
                try:
                    # seek(0) is critical — BytesIO cursor may be non-zero
                    audio_value.seek(0)
                    audio_bytes = audio_value.read()

                    if len(audio_bytes) < 500:
                        st.warning("⚠️ Recording too short — please speak for at least 2 seconds.")
                    else:
                        headers = {"Authorization": f"Bearer {token}"}
                        # Send as .webm — st.audio_input() always outputs webm in browsers
                        files = {"audio": ("recording.webm", audio_bytes, "audio/webm")}
                        r = req.post(
                            f"{BACKEND}/api/voice/transcribe-only",
                            files=files, headers=headers, timeout=40,
                        )
                        if r.ok:
                            data = r.json()
                            err  = data.get("error")
                            transcript = data.get("transcript", "")
                            if transcript:
                                st.session_state[transcript_key] = transcript
                                st.success("✅ Transcribed! Review below and hit Submit.")
                            elif err:
                                st.warning(f"⚠️ {err}")
                            else:
                                st.warning("⚠️ Couldn't catch that — please speak more clearly and re-record.")
                        else:
                            try:
                                detail = r.json().get("detail", r.text[:200])
                            except Exception:
                                detail = r.text[:200]
                            st.error(f"Backend error ({r.status_code}): {detail}")
                except Exception as e:
                    st.error(f"Could not reach backend: {e}")

    else:
        st.markdown("""
        <div style="color:#777777;font-size:0.82rem;text-align:center;
                    padding:0.6rem 0;border-top:1px solid rgba(255,255,255,0.05);margin-top:0.5rem;">
          🎙️ Record your answer above, then click <strong style="color:#16A34A;">Transcribe</strong>
        </div>""", unsafe_allow_html=True)

    # ── Step 4 — Review & Submit ──────────────────────────────────
    saved = st.session_state.get(transcript_key, "")
    if saved:
        st.markdown('<p class="vc-label">📝 Your transcribed answer (edit if needed)</p>',
                    unsafe_allow_html=True)
        edited = st.text_area(
            "Transcript",
            value=saved,
            height=140,
            key=f"voice_edit_{q_num}",
            label_visibility="collapsed",
            placeholder="Your transcribed answer appears here...",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_sub, col_skip = st.columns([3, 1])
        with col_sub:
            if st.button(
                "✅  Submit Voice Answer",
                key=f"voice_submit_{q_num}",
                use_container_width=True,
                type="primary",
            ):
                if len(edited.strip()) < 5:
                    st.warning("Answer seems too short — please re-record.")
                else:
                    _submit_answer(session_id, q_data["id"], edited, "voice")
        with col_skip:
            if st.button("⏭ Skip", key=f"voice_skip_{q_num}", use_container_width=True):
                _submit_answer(session_id, q_data["id"], "I'll skip this question.", "voice")




def _submit_answer(session_id, question_id, answer, method):
    with st.spinner("Evaluating your answer…"):
        result = submit_answer(session_id, question_id, answer, method)
    if "error" in result:
        st.error(f"❌ {result['error']}")
    else:
        fb = st.session_state.get("all_feedback", [])
        fb.append(result)
        st.session_state.update({
            "answer_submitted": True,
            "last_feedback":    result,
            "all_feedback":     fb,
        })
        # If this was a voice answer, keep voice_mode sticky
        if method == "voice":
            st.session_state["voice_mode"] = True
        if not result.get("next_question"):
            complete_session(session_id)
            st.session_state["interview_stage"] = "completed"
        st.rerun()


def _show_inline_feedback(feedback: dict):
    score = feedback.get("overall_score", 0)
    color = "#10B981" if score >= 75 else "#F59E0B" if score >= 50 else "#EF4444"
    grade = "Excellent" if score >= 85 else "Good" if score >= 70 else "Needs Work" if score >= 50 else "Below Par"

    # Main score card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(22,163,74,0.04));
                border:1px solid rgba(34,197,94,0.22);border-radius:24px;
                padding:1.5rem;margin-bottom:1rem;position:relative;overflow:hidden;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;
                  background:linear-gradient(90deg,transparent,{color},transparent);"></div>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <p style="color:#16A34A;font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                    text-transform:uppercase;margin:0 0 0.3rem;">AI Analysis Complete</p>
          <p style="color:#FFFFFF;font-weight:700;font-size:1rem;margin:0;">Response Evaluated ✓</p>
        </div>
        <div style="text-align:center;">
          <div style="font-family:'Outfit',sans-serif;font-size:2.8rem;font-weight:900;
                      color:{color};line-height:1;letter-spacing:-0.04em;">{score:.0f}</div>
          <div style="font-size:0.68rem;color:#777777;font-family:'Inter',sans-serif;">/100 · {grade}</div>
        </div>
      </div>
      <p style="color:#B5B5B5;font-size:0.85rem;margin:0.85rem 0 0;line-height:1.7;
                font-family:'Inter',sans-serif;">
        {html_escape(feedback.get('ai_feedback','')[:320])}...
      </p>
    </div>""", unsafe_allow_html=True)

    # Recruiter Perspective scorecard
    conf  = feedback.get("confidence_score", score * 0.9)
    comm  = feedback.get("communication_score", score * 0.95)
    tech  = feedback.get("technical_score", score)
    rel   = feedback.get("relevance_score", score * 0.92)
    st.markdown(f"""
    <div class="recruiter-card">
      <p style="color:#10B981;font-size:0.68rem;font-weight:700;
                letter-spacing:0.08em;text-transform:uppercase;margin:0 0 0.85rem;">Recruiter Perspective</p>
      {''.join([
        f'<div style="margin-bottom:0.55rem;">'
        f'  <div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
        f'    <span style="color:#B5B5B5;font-size:0.78rem;font-family:Inter,sans-serif;">{lbl}</span>'
        f'    <span style="color:{"#10B981" if v>=70 else "#F59E0B"};font-size:0.78rem;font-weight:700;">{v:.0f}</span>'
        f'  </div>'
        f'  <div class="recruiter-bar">'
        f'    <div class="recruiter-bar-fill" style="width:{min(v,100):.0f}%"></div>'
        f'  </div></div>'
        for lbl, v in [("Confidence",conf),("Communication",comm),("Technical Depth",tech),("Relevance",rel)]
      ])}
    </div>""", unsafe_allow_html=True)


# ── Completed Screen ──────────────────────────────────────────────────────────


def _render_completed():
    all_fb = st.session_state.get("all_feedback", [])
    scores = [f.get("overall_score", 0) for f in all_fb]
    avg    = sum(scores) / len(scores) if scores else 0
    color  = "#10B981" if avg >= 75 else "#F59E0B" if avg >= 50 else "#EF4444"
    grade  = "Outstanding" if avg >= 90 else "Proficient" if avg >= 80 else "Competent" if avg >= 65 else "Developing" if avg >= 50 else "Beginner"

    st.markdown(f"""
    <div class="fade-in-up" style="text-align:center;padding:2.5rem 1rem 1.5rem;">
      <div style="width:72px;height:72px;margin:0 auto 1.25rem;border-radius:20px;background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.25);display:flex;align-items:center;justify-content:center;"><svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg></div>
      <p style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
                text-transform:uppercase;color:#22C55E;margin:0 0 0.5rem;">Interview Complete</p>
      <h1 style="font-family:'Outfit',sans-serif;font-size:2.75rem;font-weight:800;margin:0 0 0.5rem;
                 color:#FFFFFF;letter-spacing:-0.04em;">You did great.</h1>
      <p style="color:#777777;margin:0 0 2rem;font-size:0.9rem;font-family:'Inter',sans-serif;">
        Your comprehensive performance report is ready.
      </p>
    </div>""", unsafe_allow_html=True)

    if all_fb:
        _, card_col, _ = st.columns([1, 2, 1])
        with card_col:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(22,163,74,0.05));
                        border:1px solid rgba(34,197,94,0.2);border-radius:24px;
                        padding:2rem;text-align:center;margin-bottom:1.5rem;position:relative;overflow:hidden;">
              <div style="position:absolute;top:0;left:0;right:0;height:2px;
                          background:linear-gradient(90deg,transparent,{color},transparent);"></div>
              <p style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.1em;color:#777777;margin:0 0 0.5rem;">Final Score</p>
              <div style="font-family:'Outfit',sans-serif;font-size:4.5rem;font-weight:900;
                          color:{color};line-height:1;letter-spacing:-0.04em;margin-bottom:0.25rem;">{avg:.0f}</div>
              <div style="font-family:'Inter',sans-serif;font-size:0.72rem;font-weight:700;
                          text-transform:uppercase;letter-spacing:0.08em;color:#777777;">/100 · {grade}</div>
              <div style="margin-top:1rem;display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;">
                {''.join([f"<div style='text-align:center;'><div style='font-family:Outfit,sans-serif;font-size:1.1rem;font-weight:800;color:#86EFAC;'>Q{i+1}</div><div style='font-size:0.65rem;color:#777777;font-family:Inter,sans-serif;'>{s:.0f}pts</div></div>" for i, s in enumerate(scores[:6])])}
              </div>
            </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(":material/assessment: View detailed report", use_container_width=True):
            st.session_state["page"] = "feedback"
            st.rerun()
    with col2:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button(":material/refresh: Practice again", use_container_width=True):
            st.session_state.update({
                "interview_stage": "setup",
                "session_id": None,
                "all_feedback": [],
                "last_question": None,
                "last_feedback": None,
                "answer_submitted": False,
            })
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
