"""
MockPilot AI — Premium Performance Analytics Page
Based on stitch_mockpilot_premium_design_system/mockpilot_performance_analytics
"""
import streamlit as st
from components.ui_components import (
    inject_css, score_card, radar_chart, bar_chart, list_card, info_card,
    html_escape
)
from api_client import get_history


FEEDBACK_CSS = """
<style>
/* Neural orb animation */
.neural-orb-wrap {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, transparent, #22C55E, #5DE6FF, transparent);
  animation: neuralRotate 4s linear infinite;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}
.neural-orb-wrap::before {
  content: '';
  position: absolute;
  inset: 4px;
  background: #12121f;
  border-radius: 50%;
}
/* Glass panels */
.analytics-panel {
  background: rgba(255,255,255,0.035);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 24px;
  padding: 1.5rem;
}
/* Transcript messages */
.transcript-block {
  background: rgba(41,41,55,0.5);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px 16px 16px 4px;
  padding: 1rem 1.2rem;
  max-width: 92%;
  margin-bottom: 0.75rem;
}
.ai-suggestion-block {
  background: rgba(255,255,255,0.035);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 0.9rem 1.1rem;
  margin-left: 1.5rem;
  margin-bottom: 1.5rem;
  position: relative;
}
.ai-suggestion-block::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 16px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(34,197,94,0.3), rgba(93,230,255,0.1));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
/* Learning path cards */
.learn-card {
  background: rgba(255,255,255,0.035);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 24px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  height: 100%;
}
.learn-card:hover {
  border-color: rgba(210,187,255,0.3);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(34,197,94,0.18);
}
/* Score progress bars */
.score-row { margin-bottom: 1.2rem; }
.score-row-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 0.4rem;
}
</style>
"""

VOICE_BARS = "".join([
    f'<div class="stitch-wave-bar" style="animation-delay:{d}s;"></div>'
    for d in [0.1, 0.3, 0.2, 0.4, 0.1]
])


def render():
    inject_css()
    st.markdown(FEEDBACK_CSS, unsafe_allow_html=True)

    # ── Source: live session or historical ────────────────────────────────────
    all_fb = st.session_state.get("all_feedback", [])

    if not all_fb:
        history = get_history()
        if not history:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.07);
                        border-radius:24px;text-align:center;padding:3rem;">
              <p style="font-size:2.5rem;margin:0 0 0.75rem;">📊</p>
              <h3 style="font-family:'Outfit',sans-serif;color:#FFFFFF;margin:0 0 0.5rem;">
                No feedback available yet
              </h3>
              <p style="color:#64748B;margin:0;">
                Complete an interview to see your AI performance analytics.
              </p>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀  Start Interview", use_container_width=True):
                st.session_state["page"] = "interview"
                st.rerun()
            return

        session_labels = [
            f"{s['role']} — {s['interview_type']} ({s.get('started_at','')[:10]}) | Score: {s.get('overall_score') or 0:.0f}"
            for s in history
        ]
        # Session selector with glass styling
        st.markdown("""
        <div style="margin-bottom:1.5rem;">
          <p class="label-caps" style="margin-bottom:0.5rem;">SELECT SESSION TO REVIEW</p>
        </div>
        """, unsafe_allow_html=True)
        chosen = st.selectbox("", session_labels, label_visibility="collapsed")
        chosen_session = history[session_labels.index(chosen)]
        _render_session_analytics(chosen_session)
        return

    _render_live_analytics(all_fb)


def _score_bar(label, value, color):
    st.markdown(f"""
    <div style="margin-bottom:1.25rem;">
      <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:0.45rem;">
        <span style="font-family:'Inter',sans-serif;font-size:0.92rem;font-weight:600;
                     color:#e3e0f3;">{label}</span>
        <span style="font-family:'Outfit',sans-serif;font-size:1rem;font-weight:700;
                     color:{color};">{value:.0f}%</span>
      </div>
      <div class="stitch-score-track">
        <div class="stitch-score-fill" style="width:{value:.0f}%;background:{color};
             box-shadow:0 0 8px {color}60;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def _render_live_analytics(all_fb: list):
    def avg(key):
        vals = [f.get(key, 0) for f in all_fb if f.get(key) is not None]
        return round(sum(vals) / len(vals), 1) if vals else 0.0

    overall       = avg("overall_score")
    confidence    = avg("confidence_score")
    communication = avg("communication_score")
    technical     = avg("technical_score")
    grammar       = avg("grammar_score")
    relevance     = avg("relevance_score")

    if overall < 50:
        perf_label = "Beginner"
        sub_text = "Building foundational interview skills."
    elif overall < 65:
        perf_label = "Developing"
        sub_text = "Making progress. Focus on structuring your answers."
    elif overall < 80:
        perf_label = "Competent"
        sub_text = "Solid performance. Refine your narrative and delivery."
    elif overall < 90:
        perf_label = "Proficient"
        sub_text = "Strong interview. Minor optimizations will make you top-tier."
    else:
        perf_label = "Expert"
        sub_text = "Outstanding performance. You're ready for the real thing."

    score_color = "#10B981" if overall >= 75 else "#F59E0B" if overall >= 50 else "#EF4444"

    # ── HEADER SUMMARY CARD ───────────────────────────────────────────────────
    st.markdown(f"""
    <div class="analytics-panel fade-in neural-glow" style="display:flex;align-items:center;
         justify-content:space-between;flex-wrap:wrap;gap:1.5rem;margin-bottom:1.5rem;">
      <div style="display:flex;align-items:center;gap:1.5rem;">
        <div class="neural-orb-wrap">
          <span style="position:relative;z-index:1;font-family:'Outfit',sans-serif;
                       font-size:2rem;font-weight:800;color:#d2bbff;">{overall:.0f}</span>
        </div>
        <div>
          <p class="label-caps" style="color:#ccc3d8;margin:0 0 6px;">OVERALL SCORE</p>
          <h2 style="font-family:'Outfit',sans-serif;font-size:1.875rem;font-weight:700;
                     color:#FFFFFF;margin:0 0 8px;letter-spacing:-0.01em;">{perf_label}</h2>
          <p style="color:#ccc3d8;font-size:0.9rem;max-width:440px;margin:0;line-height:1.6;">
            {sub_text}
          </p>
        </div>
      </div>
      <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
        <div class="analytics-panel" style="padding:0.75rem 1.25rem;text-align:center;min-width:120px;">
          <p class="label-caps" style="color:#5de6ff;margin:0 0 4px;">QUESTIONS</p>
          <p style="font-family:'Outfit',sans-serif;font-size:1.375rem;font-weight:700;
                    color:#e3e0f3;margin:0;">{len(all_fb)}</p>
        </div>
        <div class="analytics-panel" style="padding:0.75rem 1.25rem;text-align:center;min-width:120px;">
          <p class="label-caps" style="color:#d2bbff;margin:0 0 4px;">TOP SCORE</p>
          <p style="font-family:'Outfit',sans-serif;font-size:1.375rem;font-weight:700;
                    color:#e3e0f3;margin:0;">{max((f.get('overall_score') or 0) for f in all_fb):.0f}</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CORE SCORES + TRANSCRIPT ──────────────────────────────────────────────
    col_scores, col_transcript = st.columns([5, 8], gap="medium")

    with col_scores:
        st.markdown("""
        <div class="analytics-panel fade-in" style="margin-bottom:1rem;animation-delay:0.1s;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem;">
            <p class="label-caps" style="margin:0;">CORE SCORES</p>
            <span style="font-size:1.2rem;">📊</span>
          </div>
        """, unsafe_allow_html=True)
        _score_bar("Confidence", confidence, "#d2bbff")
        _score_bar("Communication", communication, "#5de6ff")
        _score_bar("Technical Accuracy", technical, "#ddb7ff")
        _score_bar("Grammar", grammar, "#10B981")
        _score_bar("Relevance", relevance, "#F59E0B")
        st.markdown("</div>", unsafe_allow_html=True)

        # Behavioral analysis
        st.markdown(f"""
        <div class="neural-card" style="padding:1.2rem;margin-top:0.75rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
            <p class="label-caps" style="margin:0;">BEHAVIORAL ANALYSIS</p>
            <div>{VOICE_BARS}</div>
          </div>
          <p style="color:#ccc3d8;font-size:0.85rem;line-height:1.65;margin:0 0 0.75rem;">
            Your responses demonstrated strong structure. We noticed some filler words
            during complex technical explanations — aim for deliberate pauses.
          </p>
          <div style="display:flex;align-items:center;gap:0.75rem;
                      background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.07);
                      border-radius:12px;padding:0.75rem 1rem;">
            <span style="font-size:1.1rem;">⚠️</span>
            <span style="font-size:0.83rem;color:#e3e0f3;">
              Tip: Slow down when explaining complex architectures.
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_transcript:
        st.markdown("""
        <div class="analytics-panel fade-in" style="min-height:400px;animation-delay:0.2s;">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      margin-bottom:1.5rem;padding-bottom:1rem;
                      border-bottom:1px solid rgba(255,255,255,0.07);">
            <p class="label-caps" style="margin:0;">INTERVIEW TRANSCRIPT & AI FEEDBACK</p>
          </div>
        """, unsafe_allow_html=True)

        for i, fb in enumerate(all_fb[:3]):
            q_score = fb.get("overall_score", 0)
            q_color = "#10B981" if q_score >= 75 else "#F59E0B" if q_score >= 50 else "#EF4444"
            user_answer = fb.get("user_answer", fb.get("answer", "Your response..."))
            ai_feedback = fb.get("ai_feedback", "Great response! Continue building on this approach.")

            st.markdown(f"""
            <div style="display:flex;gap:1rem;margin-bottom:0.5rem;">
              <div style="width:40px;font-family:'Space Grotesk',sans-serif;font-size:0.7rem;
                          font-weight:700;color:rgba(204,195,216,0.5);padding-top:4px;flex-shrink:0;">
                Q{i+1}
              </div>
              <div style="flex:1;">
                <div class="transcript-block">
                  <p style="font-family:'Space Grotesk',sans-serif;font-size:0.65rem;
                             font-weight:700;letter-spacing:0.05em;color:#ccc3d8;margin:0 0 6px;
                             text-transform:uppercase;">CANDIDATE (YOU)</p>
                  <p style="font-size:0.88rem;color:#e3e0f3;margin:0;line-height:1.65;">
                    "{html_escape(user_answer[:200])}{'...' if len(user_answer) > 200 else ''}"
                  </p>
                </div>
                <div class="ai-suggestion-block">
                  <div style="display:flex;align-items:flex-start;gap:0.75rem;">
                    <div style="width:32px;height:32px;border-radius:50%;
                                background:rgba(210,187,255,0.15);border:1px solid rgba(210,187,255,0.3);
                                display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                      <span style="font-size:0.85rem;">✨</span>
                    </div>
                    <div>
                      <p style="font-family:'Space Grotesk',sans-serif;font-size:0.65rem;
                                 font-weight:700;letter-spacing:0.05em;color:#d2bbff;margin:0 0 4px;
                                 text-transform:uppercase;">AI SUGGESTION</p>
                      <p style="font-size:0.85rem;color:#e3e0f3;margin:0;line-height:1.65;">
                        {html_escape(ai_feedback[:200])}{'...' if len(ai_feedback) > 200 else ''}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if len(all_fb) > 3:
            st.markdown(f"""
            <p style="color:#ccc3d8;font-size:0.85rem;text-align:center;
                      margin-top:0.5rem;padding-top:0.75rem;
                      border-top:1px solid rgba(255,255,255,0.07);">
              +{len(all_fb)-3} more question(s) — expand below
            </p>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DETAILED Q&A ─────────────────────────────────────────────────────────
    st.markdown("""
    <p class="mp-section-title">Question-by-Question Analysis</p>
    """, unsafe_allow_html=True)

    for i, fb in enumerate(all_fb):
        q_score = fb.get("overall_score", 0)
        q_color = "#10B981" if q_score >= 75 else "#F59E0B" if q_score >= 50 else "#EF4444"
        with st.expander(f"Question {i+1} — Score: {q_score:.0f}/100", expanded=(i == 0)):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"""
                <div style="background:rgba(34,197,94,0.08);border-left:3px solid #22C55E;
                            border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.9rem;">
                  <p style="color:#d2bbff;font-family:'Space Grotesk',sans-serif;font-size:0.7rem;
                             font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin:0 0 6px;">
                    AI FEEDBACK
                  </p>
                  <p style="color:#ccc3d8;font-size:0.88rem;margin:0;line-height:1.7;">
                    {html_escape(fb.get('ai_feedback','No feedback available.'))}
                  </p>
                </div>
                <div style="background:rgba(93,230,255,0.05);border-left:3px solid #5de6ff;
                            border-radius:10px;padding:0.9rem 1.1rem;">
                  <p style="color:#5de6ff;font-family:'Space Grotesk',sans-serif;font-size:0.7rem;
                             font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin:0 0 6px;">
                    💡 IDEAL ANSWER
                  </p>
                  <p style="color:#ccc3d8;font-size:0.85rem;margin:0;line-height:1.7;">
                    {html_escape(fb.get('ideal_answer','Not available.'))}
                  </p>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                strengths    = fb.get("strengths", [])
                improvements = fb.get("improvements", [])
                fillers      = fb.get("filler_words", {})
                if strengths:
                    list_card("Strengths", strengths[:3], "✅", "#10B981")
                if improvements:
                    st.markdown("<br>", unsafe_allow_html=True)
                    list_card("Improve", improvements[:3], "⚡", "#F59E0B")
                if fillers:
                    st.markdown("<br>", unsafe_allow_html=True)
                    filler_list = [f'"{w}" × {c}' for w, c in fillers.items()]
                    list_card("Filler Words", filler_list, "🔴", "#EF4444")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHARTS ───────────────────────────────────────────────────────────────
    col_radar, col_bar = st.columns(2, gap="medium")
    with col_radar:
        st.markdown('<p class="mp-section-title">Skill Radar</p>', unsafe_allow_html=True)
        cats = ["Confidence", "Communication", "Technical", "Grammar", "Relevance"]
        vals = [confidence, communication, technical, grammar, relevance]
        radar_chart(cats, vals)
    with col_bar:
        st.markdown('<p class="mp-section-title">Per-Question Scores</p>', unsafe_allow_html=True)
        q_labels = [f"Q{i+1}" for i in range(len(all_fb))]
        q_scores = [f.get("overall_score", 0) for f in all_fb]
        bar_chart(q_labels, q_scores)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SUGGESTED LEARNING PATH ───────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
      <h3 style="font-family:'Outfit',sans-serif;font-size:1.375rem;font-weight:700;
                 color:#FFFFFF;margin:0;">Suggested Learning Path</h3>
      <div style="flex:1;height:1px;background:rgba(255,255,255,0.07);"></div>
    </div>
    """, unsafe_allow_html=True)

    lp1, lp2, lp3 = st.columns(3, gap="medium")
    learning_paths = [
        (lp1, "#d2bbff", "rgba(210,187,255,0.1)", "🏛️",
         "Distributed Systems Mastery",
         "Focused module on caching, load balancing, and data consistency for high-scale apps.",
         "2h 15m"),
        (lp2, "#5de6ff", "rgba(93,230,255,0.1)", "🎤",
         "The STAR Storytelling Framework",
         "Learn to structure behavioral answers that highlight your impact and metrics.",
         "45m"),
        (lp3, "#ddb7ff", "rgba(221,183,255,0.1)", "📊",
         "Advanced Algorithm Patterns",
         "Deep dive into dynamic programming and complex graph traversals.",
         "3h 30m"),
    ]
    for col, color, bg, icon, title, desc, duration in learning_paths:
        with col:
            st.markdown(f"""
            <div class="learn-card">
              <div class="learn-card-icon" style="background:{bg};border:1px solid {color}30;">
                {icon}
              </div>
              <h4 style="font-family:'Outfit',sans-serif;font-size:1rem;font-weight:700;
                         color:#e3e0f3;margin:0 0 0.5rem;">{title}</h4>
              <p style="color:#ccc3d8;font-size:0.83rem;line-height:1.65;margin:0 0 1rem;">{desc}</p>
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.07);
                             border-radius:9999px;padding:3px 14px;
                             font-family:'Space Grotesk',sans-serif;
                             font-size:0.68rem;font-weight:700;letter-spacing:0.05em;">{duration}</span>
                <span style="color:{color};font-size:1.2rem;transition:transform 0.3s;">→</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ACTIONS ───────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        if st.button("🔄  Practice Again", use_container_width=True):
            st.session_state.update({
                "interview_stage": "setup",
                "all_feedback": [],
                "last_question": None,
                "last_feedback": None,
            })
            st.session_state["page"] = "interview"
            st.rerun()
    with col_b:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("📊  Go to Dashboard", use_container_width=True):
            st.session_state["page"] = "dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def _render_session_analytics(session: dict):
    """Render feedback for a historical session."""
    overall = session.get("overall_score") or 0
    score_color = "#10B981" if overall >= 75 else "#F59E0B" if overall >= 50 else "#EF4444"
    if overall < 50:
        perf_label = "Beginner"
    elif overall < 65:
        perf_label = "Developing"
    elif overall < 80:
        perf_label = "Competent"
    elif overall < 90:
        perf_label = "Proficient"
    else:
        perf_label = "Expert"

    st.markdown(f"""
    <div class="analytics-panel fade-in neural-glow" style="display:flex;align-items:center;
         justify-content:space-between;flex-wrap:wrap;gap:1.5rem;margin-bottom:1.5rem;">
      <div style="display:flex;align-items:center;gap:1.5rem;">
        <div class="neural-orb-wrap">
          <span style="position:relative;z-index:1;font-family:'Outfit',sans-serif;
                       font-size:2rem;font-weight:800;color:#d2bbff;">{overall:.0f}</span>
        </div>
        <div>
          <p class="label-caps" style="color:#ccc3d8;margin:0 0 6px;">OVERALL SCORE</p>
          <h2 style="font-family:'Outfit',sans-serif;font-size:1.875rem;font-weight:700;
                     color:#FFFFFF;margin:0 0 8px;">{perf_label}</h2>
          <p style="color:#ccc3d8;font-size:0.88rem;margin:0;">
            {html_escape(session.get('role','—'))} · {html_escape(session.get('interview_type','—'))} · {html_escape(session.get('experience_level','—'))}
          </p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_scores, col_info = st.columns([1, 1.5], gap="medium")

    with col_scores:
        st.markdown('<div class="analytics-panel">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem;">
          <p class="label-caps" style="margin:0;">CORE SCORES</p>
          <span>📊</span>
        </div>
        """, unsafe_allow_html=True)
        score_map = [
            ("Confidence",    session.get("confidence_score") or 0,    "#d2bbff"),
            ("Communication", session.get("communication_score") or 0, "#5de6ff"),
            ("Technical",     session.get("technical_score") or 0,     "#ddb7ff"),
            ("Grammar",       session.get("grammar_score") or 0,       "#10B981"),
        ]
        for label, val, color in score_map:
            _score_bar(label, val, color)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        if session.get("ai_summary"):
            st.markdown(f"""
            <div class="analytics-panel" style="margin-bottom:1rem;">
              <p class="label-caps" style="color:#d2bbff;margin:0 0 0.75rem;">AI SUMMARY</p>
              <p style="color:#ccc3d8;font-size:0.9rem;line-height:1.7;margin:0;">
                {html_escape(session['ai_summary'])}
              </p>
            </div>
            """, unsafe_allow_html=True)

        sw1, sw2 = st.columns(2, gap="small")
        with sw1:
            if session.get("strengths"):
                list_card("Strengths", session["strengths"][:4], "✅", "#10B981")
        with sw2:
            if session.get("weaknesses"):
                list_card("Key Improvements", session["weaknesses"][:4], "⚡", "#F59E0B")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        if st.button("🔄  Practice Again", use_container_width=True, key="hist_retry"):
            st.session_state["interview_stage"] = "setup"
            st.session_state["page"] = "interview"
            st.rerun()
    with col_b:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("📊  Go to Dashboard", use_container_width=True, key="hist_dash"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
