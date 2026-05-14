"""
MockPilot AI — Interview Room
The core interview experience: setup → question → answer → feedback loop.
"""
import streamlit as st
import time
import json
import requests as req
from frontend.components.ui_components import (
    inject_css, section_header, ai_avatar, question_display,
    timer_display, mic_visualizer, thinking_loader
)
from frontend.api_client import (
    start_session, get_current_question, submit_answer,
    complete_session, list_resumes
)

BACKEND = "http://localhost:8000"

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
  background:linear-gradient(135deg,rgba(124,58,237,0.1),rgba(34,211,238,0.04));
  border:1px solid rgba(124,58,237,0.3);
  border-radius:24px;padding:2rem 2rem 1.5rem;
  position:relative;overflow:hidden;
  box-shadow:0 0 60px rgba(124,58,237,0.12);
}
.focus-question::before {
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,#7C3AED,#22D3EE,#7C3AED);
  background-size:200%;animation:shimmer 3s linear infinite;
}
.q-badge {
  display:inline-flex;align-items:center;gap:0.4rem;
  background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);
  border-radius:99px;padding:3px 12px;
  font-size:0.72rem;font-weight:700;color:#A855F7;
  letter-spacing:0.5px;margin-bottom:0.75rem;
}
.mode-badge {
  display:inline-flex;align-items:center;gap:0.4rem;
  background:rgba(34,211,238,0.1);border:1px solid rgba(34,211,238,0.25);
  border-radius:99px;padding:3px 12px;font-size:0.72rem;font-weight:600;color:#22D3EE;
}
.recruiter-card {
  background:linear-gradient(135deg,rgba(16,185,129,0.06),rgba(34,211,238,0.04));
  border:1px solid rgba(16,185,129,0.2);border-radius:20px;padding:1.3rem 1.5rem;
  margin-top:1rem;
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
  0%,100% { box-shadow: 0 0 0 0 rgba(168,85,247,0.4); }
  50%      { box-shadow: 0 0 0 6px rgba(168,85,247,0); }
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
  0%,100% { border-color: rgba(124,58,237,0.35); }
  50%      { border-color: rgba(34,211,238,0.45); }
}
@keyframes ctaPulse {
  0%,100% { box-shadow: 0 0 30px rgba(124,58,237,0.5), 0 8px 32px rgba(124,58,237,0.3); }
  50%      { box-shadow: 0 0 60px rgba(124,58,237,0.75), 0 16px 48px rgba(34,211,238,0.25), 0 0 0 4px rgba(168,85,247,0.15); }
}

.ai-hero-banner {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 2.4rem 2.5rem 2rem;
  margin-bottom: 2rem;
  background: linear-gradient(
    135deg,
    rgba(15, 5, 35, 0.95) 0%,
    rgba(10, 5, 28, 0.97) 35%,
    rgba(5, 18, 35, 0.96) 65%,
    rgba(10, 5, 28, 0.97) 100%
  );
  border: 1px solid rgba(124,58,237,0.35);
  animation: borderGlow 4s ease-in-out infinite;
  box-shadow:
    0 0 80px rgba(124,58,237,0.18),
    0 0 160px rgba(34,211,238,0.06),
    inset 0 1px 0 rgba(255,255,255,0.06),
    inset 0 -1px 0 rgba(0,0,0,0.3);
}

/* Animated gradient mesh background */
.ai-hero-banner::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(
    120deg,
    rgba(124,58,237,0.12) 0%,
    rgba(34,211,238,0.06) 30%,
    rgba(168,85,247,0.08) 60%,
    rgba(34,211,238,0.10) 100%
  );
  background-size: 300% 300%;
  animation: heroGradientShift 8s ease-in-out infinite;
  pointer-events: none;
}

/* Shimmer sweep */
.ai-hero-banner::after {
  content: '';
  position: absolute; top: 0; left: 0;
  width: 40%; height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255,255,255,0.03) 50%,
    transparent 100%
  );
  animation: heroShimmer 5s ease-in-out infinite;
  pointer-events: none;
}

/* Top accent line */
.hero-top-line {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent 0%, #7C3AED 30%, #22D3EE 60%, transparent 100%);
  background-size: 200%;
  animation: heroGradientShift 4s linear infinite;
}

/* Floating ambient particles */
.hero-particle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}
.hero-p1 {
  width: 140px; height: 140px; top: -30px; right: 80px;
  background: radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%);
  animation: particleFloat 7s ease-in-out infinite;
}
.hero-p2 {
  width: 100px; height: 100px; bottom: -20px; right: 20%;
  background: radial-gradient(circle, rgba(34,211,238,0.14) 0%, transparent 70%);
  animation: particleFloat 9s 1.5s ease-in-out infinite;
}
.hero-p3 {
  width: 80px; height: 80px; top: 30%; left: -20px;
  background: radial-gradient(circle, rgba(168,85,247,0.16) 0%, transparent 70%);
  animation: particleFloat 6s 3s ease-in-out infinite;
}
.hero-p4 {
  width: 60px; height: 60px; bottom: 15px; left: 35%;
  background: radial-gradient(circle, rgba(34,211,238,0.10) 0%, transparent 70%);
  animation: particleFloat 8s 0.5s ease-in-out infinite;
}

/* Badge */
.hero-top-badge {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: rgba(124,58,237,0.15);
  border: 1px solid rgba(168,85,247,0.35);
  border-radius: 99px;
  padding: 5px 16px;
  font-size: 0.72rem; font-weight: 700; color: #C084FC;
  letter-spacing: 0.8px; text-transform: uppercase;
  margin-bottom: 1rem;
  animation: heroBadgePulse 2.5s ease-in-out infinite;
  position: relative; z-index: 2;
}
.hero-badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #A855F7;
  box-shadow: 0 0 6px rgba(168,85,247,0.8);
}

/* Main title */
.hero-main-title {
  font-size: 2.4rem; font-weight: 900; line-height: 1.15;
  margin: 0 0 0.75rem;
  background: linear-gradient(135deg, #FFFFFF 0%, #E2D9F3 40%, #A855F7 70%, #22D3EE 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: heroTitleReveal 0.7s 0.1s ease-out both;
  position: relative; z-index: 2;
  text-shadow: none;
}

/* Subtitle */
.hero-subtitle {
  font-size: 1rem; color: #94A3B8; line-height: 1.7;
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
  background: rgba(124,58,237,0.2);
  border-color: rgba(168,85,247,0.5);
  color: #E2E8F0;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(124,58,237,0.25);
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

/* Preview card */
.preview-card {
  background: rgba(124,58,237,0.07);
  border: 1px solid rgba(124,58,237,0.2);
  border-radius: 14px;
  padding: 1rem 1.4rem;
  margin-bottom: 1.25rem;
  position: relative; overflow: hidden;
}
.preview-card::before {
  content:'';position:absolute;left:0;top:0;bottom:0;width:3px;
  background:linear-gradient(180deg,#7C3AED,#22D3EE);
  border-radius:3px 0 0 3px;
}

/* Enhanced CTA */
.launch-cta-wrapper {
  position: relative;
}
.launch-cta-wrapper .stButton > button {
  background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 50%, #4C1D95 100%) !important;
  font-size: 1.05rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.5px !important;
  padding: 0.85rem 2rem !important;
  border-radius: 16px !important;
  border: 1px solid rgba(168,85,247,0.5) !important;
  animation: ctaPulse 3s ease-in-out infinite !important;
  position: relative; overflow: hidden;
}
.launch-cta-wrapper .stButton > button:hover {
  transform: translateY(-4px) scale(1.02) !important;
  box-shadow: 0 0 80px rgba(124,58,237,0.8), 0 20px 60px rgba(124,58,237,0.4) !important;
  border-color: rgba(168,85,247,0.8) !important;
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
        <div class="preview-card">
          <p style="color:#A855F7;font-weight:700;font-size:0.78rem;text-transform:uppercase;
                    letter-spacing:0.5px;margin:0 0 0.5rem;">📋 Interview Preview</p>
          <p style="color:#E2E8F0;font-size:0.95rem;font-weight:600;margin:0 0 0.25rem;">
            {role}
          </p>
          <p style="color:#94A3B8;font-size:0.82rem;margin:0;">
            {exp} &nbsp;·&nbsp; {itype} &nbsp;·&nbsp; Up to {MAX_QUESTIONS} adaptive AI questions
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
          <p style="color:#A855F7;font-weight:700;font-size:0.85rem;margin:0 0 0.3rem;">
            🎙️ LIVE INTERVIEW
          </p>
          <p style="color:#F1F5F9;font-weight:600;font-size:0.95rem;margin:0;">{role}</p>
          <p style="color:#64748B;font-size:0.8rem;margin:2px 0 0;">{itype}</p>
          <hr style="border-color:rgba(255,255,255,0.08);margin:0.75rem 0;">
          <p style="color:#94A3B8;font-size:0.8rem;margin:0;">Question</p>
          <p style="font-size:1.8rem;font-weight:800;color:#A855F7;margin:0;">
            {q_num}<span style="font-size:1rem;color:#64748B;">/{MAX_QUESTIONS}</span>
          </p>
        </div>""", unsafe_allow_html=True)
        st.progress(q_num / MAX_QUESTIONS)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⏹  End Interview Early", use_container_width=True):
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
            st.error(f"❌ {q_data['error']}")
            return
        st.session_state["last_question"] = q_data

    q_data = st.session_state["last_question"]

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
                '<p style="color:#94A3B8;font-size:0.85rem;margin:0;font-weight:500;">'
                f'{"🎙️ Voice Mode active" if voice_mode else "📝 Your Answer"}</p>',
                unsafe_allow_html=True,
            )
        with c_toggle:
            if voice_mode:
                if st.button("⌨️ Switch to Text", key=f"switch_text_{q_num}",
                             use_container_width=True):
                    st.session_state["voice_mode"] = False
                    st.rerun()
            else:
                if st.button("🎙️ Use Voice", key=f"switch_voice_{q_num}",
                             use_container_width=True):
                    st.session_state["voice_mode"] = True
                    st.rerun()

        st.markdown("<br style='margin:0;'>", unsafe_allow_html=True)

        if voice_mode:
            # ── Voice mode: show voice UI directly, no tab click needed ──
            _render_voice_tab(session_id, q_data, q_num)
        else:
            # ── Text mode: original tabs ──────────────────────────────────
            answer_tab, voice_tab = st.tabs(["⌨️  Type Answer", "🎙️  Live Voice"])

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
                    if st.button("✅  Analyze Response", key=f"submit_{q_num}", use_container_width=True):
                        if not answer or len(answer.strip()) < 10:
                            st.warning("Please write a more detailed answer (at least 10 characters).")
                        else:
                            _submit_answer(session_id, q_data["id"], answer, "text")
                with col_skip:
                    if st.button("⏭ Skip Question", key=f"skip_{q_num}", use_container_width=True):
                        _submit_answer(session_id, q_data["id"], "I'll skip this question.", "text")

            with voice_tab:
                _render_voice_tab(session_id, q_data, q_num)

    else:
        # Show submitted state + feedback
        feedback = st.session_state.get("last_feedback", {})
        _show_inline_feedback(feedback)

        next_q = feedback.get("next_question")
        if next_q and q_num < MAX_QUESTIONS:
            if st.button("➡️  Next Question", key="next_q_btn", use_container_width=True):
                st.session_state.update({
                    "question_number":  q_num + 1,
                    "answer_submitted": False,
                    "last_question":    None,
                    "last_feedback":    None,
                    # voice_mode intentionally NOT reset — stays sticky
                })
                st.rerun()
        else:
            st.success("🎉 Interview complete!")
            if st.button("📊  View Full Results", key="view_results", use_container_width=True):
                st.session_state["interview_stage"] = "completed"
                st.rerun()


# ── Voice Tab ─────────────────────────────────────────────────────────────────

def _inject_question_tts(question_text: str, q_num: int):
    """Inject JS to read the question aloud via browser Speech Synthesis.
    Only fires once per question number."""
    safe_text = question_text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    st.components.v1.html(f"""
<script>
(function(){{
  const key = 'tts_q_{q_num}';
  if (sessionStorage.getItem(key)) return;
  sessionStorage.setItem(key, '1');
  const speak = () => {{
    if (!window.speechSynthesis) return;
    const u = new SpeechSynthesisUtterance("{safe_text}");
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
    .vc-panel{background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.2);
              border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:0.75rem;}
    .vc-step{display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem;}
    .vc-step-num{width:22px;height:22px;border-radius:50%;background:rgba(124,58,237,0.3);
                 color:#A855F7;font-size:0.72rem;font-weight:700;display:flex;
                 align-items:center;justify-content:center;flex-shrink:0;}
    .vc-step-txt{color:#94A3B8;font-size:0.82rem;}
    .vc-label{color:#22D3EE;font-size:0.78rem;font-weight:600;text-transform:uppercase;
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
        <span class="vc-step-txt">Click <strong style="color:#A855F7;">Transcribe my answer</strong> to convert speech to text</span>
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
            with st.spinner("🎤 Transcribing with Groq Whisper..."):
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
        <div style="color:#475569;font-size:0.82rem;text-align:center;
                    padding:0.6rem 0;border-top:1px solid rgba(255,255,255,0.05);margin-top:0.5rem;">
          🎙️ Record your answer above, then click <strong style="color:#A855F7;">Transcribe</strong>
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
    with st.spinner("🤖 AI is analyzing your answer..."):
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
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.1),rgba(34,211,238,0.05));
                border:1px solid rgba(124,58,237,0.25);border-radius:24px;
                padding:1.5rem;margin-bottom:1rem;position:relative;overflow:hidden;">
      <div style="position:absolute;top:0;left:0;right:0;height:3px;
                  background:linear-gradient(90deg,{color},{color}88);"></div>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <p style="color:#A855F7;font-size:0.72rem;font-weight:700;
                    letter-spacing:0.5px;margin:0 0 0.2rem;">AI ANALYSIS COMPLETE</p>
          <p style="color:#F1F5F9;font-weight:800;font-size:1.1rem;margin:0;">Response Evaluated ✅</p>
        </div>
        <div style="text-align:center;">
          <div style="font-size:2.8rem;font-weight:900;color:{color};line-height:1;">{score:.0f}</div>
          <div style="font-size:0.72rem;color:#64748B;">/100 · {grade}</div>
        </div>
      </div>
      <p style="color:#94A3B8;font-size:0.85rem;margin:0.9rem 0 0;line-height:1.65;">
        {feedback.get('ai_feedback','')[:320]}...
      </p>
    </div>""", unsafe_allow_html=True)

    # Recruiter Perspective scorecard
    conf  = feedback.get("confidence_score", score * 0.9)
    comm  = feedback.get("communication_score", score * 0.95)
    tech  = feedback.get("technical_score", score)
    rel   = feedback.get("relevance_score", score * 0.92)
    st.markdown(f"""
    <div class="recruiter-card">
      <p style="color:#10B981;font-size:0.72rem;font-weight:700;
                letter-spacing:0.5px;margin:0 0 0.9rem;">RECRUITER PERSPECTIVE</p>
      {''.join([
        f'<div style="margin-bottom:0.5rem;">'
        f'  <div style="display:flex;justify-content:space-between;">' 
        f'    <span style="color:#94A3B8;font-size:0.78rem;">{lbl}</span>'
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
    st.markdown("""
    <div class="fade-in-up" style="text-align:center;padding:2rem 0;">
      <div style="font-size:4rem;margin-bottom:1rem;">🏆</div>
      <h1 style="font-size:2.2rem;font-weight:800;
                 background:linear-gradient(135deg,#A855F7,#22D3EE);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 background-clip:text;margin:0;">Interview Complete!</h1>
      <p style="color:#64748B;margin:0.5rem 0 2rem;">
        Your detailed feedback is ready. Check the Feedback page for full analysis.
      </p>
    </div>""", unsafe_allow_html=True)

    # Quick summary of all feedback
    all_fb = st.session_state.get("all_feedback", [])
    if all_fb:
        scores = [f.get("overall_score", 0) for f in all_fb]
        avg    = sum(scores) / len(scores) if scores else 0
        color  = "#10B981" if avg >= 75 else "#F59E0B" if avg >= 50 else "#EF4444"
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;margin-bottom:1.5rem;">
          <p style="color:#94A3B8;font-size:0.85rem;margin:0 0 0.3rem;">Your Overall Score</p>
          <h2 style="font-size:4rem;font-weight:900;color:{color};margin:0;">{avg:.0f}</h2>
          <p style="color:#64748B;font-size:0.85rem;margin:0;">/100</p>
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊  Detailed Feedback", use_container_width=True):
            st.session_state["page"] = "feedback"
            st.rerun()
    with col2:
        if st.button("🔄  New Interview", use_container_width=True):
            st.session_state.update({
                "interview_stage": "setup",
                "session_id": None,
                "all_feedback": [],
                "last_question": None,
                "last_feedback": None,
                "answer_submitted": False,
            })
            st.rerun()
