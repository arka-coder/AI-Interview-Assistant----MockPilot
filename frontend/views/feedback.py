"""
MockPilot AI — AI Feedback Page
Comprehensive feedback with score rings, radar chart, strengths/weaknesses, ideal answer.
"""
import streamlit as st
from frontend.components.ui_components import (
    inject_css, section_header, score_card, radar_chart,
    bar_chart, list_card, info_card
)
from frontend.api_client import get_history
import requests


def render():
    inject_css()

    st.markdown("""
    <div class="fade-in-up" style="margin-bottom:2rem;">
      <h1 style="font-size:2rem;font-weight:800;
                 background:linear-gradient(135deg,#A855F7,#22D3EE);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 background-clip:text;margin:0;">AI Feedback Report</h1>
      <p style="color:#64748B;font-size:0.9rem;margin:4px 0 0;">
        Detailed analysis of your interview performance
      </p>
    </div>""", unsafe_allow_html=True)

    # Source: in-memory from interview room OR from session history
    all_fb = st.session_state.get("all_feedback", [])

    if not all_fb:
        # Try to load from selected session
        history = get_history()
        if not history:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:3rem;">
              <p style="font-size:2.5rem;">📊</p>
              <h3 style="color:#F1F5F9;">No feedback available yet</h3>
              <p style="color:#64748B;">Complete an interview to see your AI feedback report.</p>
            </div>""", unsafe_allow_html=True)
            if st.button("🚀  Start Interview", use_container_width=True):
                st.session_state["page"] = "interview"
                st.rerun()
            return

        # Session picker
        session_labels = [
            f"{s['role']} — {s['interview_type']} ({s.get('started_at','')[:10]}) | Score: {s.get('overall_score') or 0:.0f}"
            for s in history
        ]
        chosen = st.selectbox("📂 Select a session to review:", session_labels)
        chosen_session = history[session_labels.index(chosen)]
        _render_session_feedback(chosen_session)
        return

    # Use live session feedback
    _render_live_feedback(all_fb)


def _render_live_feedback(all_fb: list):
    """Render feedback from live session data in session_state."""
    if not all_fb:
        return

    # ── Aggregate scores ─────────────────────────────────────────
    def avg(key):
        vals = [f.get(key, 0) for f in all_fb if f.get(key) is not None]
        return round(sum(vals) / len(vals), 1) if vals else 0.0

    overall       = avg("overall_score")
    confidence    = avg("confidence_score")
    communication = avg("communication_score")
    technical     = avg("technical_score")
    grammar       = avg("grammar_score")
    relevance     = avg("relevance_score")

    score_color = "#10B981" if overall >= 75 else "#F59E0B" if overall >= 50 else "#EF4444"

    # ── Hero score ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;padding:2rem;margin-bottom:1.5rem;
                border:1px solid {score_color}44;background:rgba(0,0,0,0.2);">
      <p style="color:#94A3B8;font-size:0.85rem;margin:0 0 0.3rem;text-transform:uppercase;letter-spacing:1px;">
        Overall Performance Score
      </p>
      <h1 style="font-size:5rem;font-weight:900;color:{score_color};margin:0;line-height:1;">
        {overall:.0f}
      </h1>
      <p style="color:#64748B;font-size:0.85rem;margin:0.3rem 0 0;">/100</p>
    </div>""", unsafe_allow_html=True)

    # ── Score rings ───────────────────────────────────────────────
    section_header("Score Breakdown", "🎯")
    ring_cols = st.columns(5)
    ring_data = [
        ("Confidence",    confidence,    "#7C3AED"),
        ("Communication", communication, "#A855F7"),
        ("Technical",     technical,     "#22D3EE"),
        ("Grammar",       grammar,       "#10B981"),
        ("Relevance",     relevance,     "#F59E0B"),
    ]
    for col, (label, val, color) in zip(ring_cols, ring_data):
        with col:
            score_card(label, val, color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Radar chart ───────────────────────────────────────────────
    col_radar, col_bar = st.columns(2)
    with col_radar:
        section_header("Skill Radar", "🕸️")
        cats = ["Confidence", "Communication", "Technical", "Grammar", "Relevance"]
        vals = [confidence, communication, technical, grammar, relevance]
        radar_chart(cats, vals)

    with col_bar:
        section_header("Per-Question Scores", "📊")
        q_labels = [f"Q{i+1}" for i in range(len(all_fb))]
        q_scores = [f.get("overall_score", 0) for f in all_fb]
        bar_chart(q_labels, q_scores)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Per-question breakdown ────────────────────────────────────
    section_header("Question-by-Question Analysis", "📋")
    for i, fb in enumerate(all_fb):
        q_score = fb.get("overall_score", 0)
        q_color = "#10B981" if q_score >= 75 else "#F59E0B" if q_score >= 50 else "#EF4444"

        with st.expander(f"Question {i+1} — Score: {q_score:.0f}/100", expanded=(i == 0)):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"""
                <div style="background:rgba(124,58,237,0.08);border-radius:10px;
                            padding:0.8rem 1rem;margin-bottom:0.8rem;">
                  <p style="color:#A855F7;font-size:0.78rem;font-weight:600;margin:0 0 0.3rem;">
                    AI FEEDBACK
                  </p>
                  <p style="color:#CBD5E1;font-size:0.88rem;margin:0;line-height:1.65;">
                    {fb.get('ai_feedback', 'No feedback available.')}
                  </p>
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:rgba(34,211,238,0.06);border-left:3px solid #22D3EE;
                            border-radius:10px;padding:0.8rem 1rem;">
                  <p style="color:#22D3EE;font-size:0.78rem;font-weight:600;margin:0 0 0.3rem;">
                    💡 IDEAL ANSWER
                  </p>
                  <p style="color:#CBD5E1;font-size:0.85rem;margin:0;line-height:1.65;">
                    {fb.get('ideal_answer', 'Not available.')}
                  </p>
                </div>""", unsafe_allow_html=True)

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

    # ── Actions ───────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
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
        if st.button("📊  Go to Dashboard", use_container_width=True):
            st.session_state["page"] = "dashboard"
            st.rerun()


def _render_session_feedback(session: dict):
    """Render feedback for a historical session."""
    overall = session.get("overall_score") or 0
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;padding:1.5rem;margin-bottom:1.5rem;">
      <p style="color:#94A3B8;font-size:0.85rem;margin:0;">
        {session.get('role')} · {session.get('interview_type')} · {session.get('experience_level')}
      </p>
      <h2 style="font-size:3.5rem;font-weight:900;
                 color:{'#10B981' if overall>=75 else '#F59E0B' if overall>=50 else '#EF4444'};
                 margin:0.3rem 0 0;">{overall:.0f}<span style="font-size:1rem;color:#64748B;">/100</span></h2>
    </div>""", unsafe_allow_html=True)

    section_header("Score Breakdown", "🎯")
    ring_cols = st.columns(4)
    for col, (label, key, color) in zip(ring_cols, [
        ("Confidence", "confidence_score", "#7C3AED"),
        ("Communication", "communication_score", "#A855F7"),
        ("Technical", "technical_score", "#22D3EE"),
        ("Grammar", "grammar_score", "#10B981"),
    ]):
        with col:
            score_card(label, session.get(key) or 0, color)

    if session.get("ai_summary"):
        st.markdown("<br>", unsafe_allow_html=True)
        info_card("AI Summary", session["ai_summary"], "🤖", "#7C3AED")

    col_s, col_w = st.columns(2)
    with col_s:
        if session.get("strengths"):
            list_card("Strengths", session["strengths"], "✅", "#10B981")
    with col_w:
        if session.get("weaknesses"):
            list_card("Key Improvements", session["weaknesses"], "⚡", "#F59E0B")
