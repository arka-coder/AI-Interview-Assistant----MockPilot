"""
MockPilot AI — Premium Dashboard
Futuristic AI-first analytics experience.
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from frontend.components.ui_components import (
    inject_css, radar_chart, line_chart
)
from frontend.api_client import get_analytics, get_history, clear_all_sessions


# ── Premium CSS ───────────────────────────────────────────────────────────────
DASH_CSS = """
<style>
/* Animated background grid */
.dash-bg-grid {
  position:fixed;top:0;left:0;width:100%;height:100%;
  background-image:
    linear-gradient(rgba(124,58,237,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124,58,237,0.03) 1px, transparent 1px);
  background-size:50px 50px;
  pointer-events:none;z-index:0;
}
/* Metric cards */
.mp-metric {
  background:rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:20px;padding:1.4rem 1.2rem;
  position:relative;overflow:hidden;
  transition:all 0.35s cubic-bezier(0.4,0,0.2,1);
  cursor:default;
}
.mp-metric::before {
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#7C3AED,#22D3EE);
  transform:scaleX(0);transform-origin:left;
  transition:transform 0.4s ease;
}
.mp-metric:hover { transform:translateY(-6px);border-color:rgba(168,85,247,0.4);
  box-shadow:0 20px 60px rgba(124,58,237,0.25); }
.mp-metric:hover::before { transform:scaleX(1); }
.mp-metric-icon { font-size:1.8rem;margin-bottom:0.6rem; }
.mp-metric-val {
  font-size:2.4rem;font-weight:900;line-height:1;
  background:linear-gradient(135deg,#F1F5F9,#A855F7);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}
.mp-metric-label { color:#64748B;font-size:0.78rem;font-weight:600;
  text-transform:uppercase;letter-spacing:0.8px;margin-top:0.3rem; }
.mp-metric-trend { font-size:0.72rem;font-weight:600;margin-top:0.4rem; }

/* AI Assistant card */
.ai-assistant {
  background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(34,211,238,0.08));
  border:1px solid rgba(124,58,237,0.3);border-radius:24px;
  padding:1.5rem;position:relative;overflow:hidden;
}
.ai-assistant::after {
  content:'';position:absolute;top:-40%;right:-20%;
  width:200px;height:200px;border-radius:50%;
  background:radial-gradient(circle,rgba(168,85,247,0.15),transparent 70%);
  pointer-events:none;
}
.ai-pulse {
  display:inline-block;width:10px;height:10px;border-radius:50%;
  background:#A855F7;margin-right:6px;
  animation:aiPulse 2s ease-in-out infinite;
}
@keyframes aiPulse {
  0%,100%{box-shadow:0 0 0 0 rgba(168,85,247,0.7);}
  50%{box-shadow:0 0 0 8px rgba(168,85,247,0);}
}

/* Insight cards */
.insight-card {
  background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
  border-radius:16px;padding:1rem 1.2rem;margin-bottom:0.75rem;
  display:flex;align-items:flex-start;gap:0.75rem;
  transition:all 0.3s ease;
}
.insight-card:hover { border-color:rgba(34,211,238,0.3);
  background:rgba(34,211,238,0.04);transform:translateX(4px); }

/* Practice recommendation cards */
.rec-card {
  background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
  border-radius:16px;padding:1.1rem 1.2rem;
  transition:all 0.3s ease;
}
.rec-card:hover { border-color:rgba(168,85,247,0.4);
  background:rgba(124,58,237,0.07);transform:translateY(-3px);
  box-shadow:0 12px 40px rgba(124,58,237,0.2); }

/* Make rec-card Streamlit buttons look like inline links */
.rec-btn button {
  background:transparent !important;
  border:none !important;
  box-shadow:none !important;
  padding:0 !important;
  font-size:0.72rem !important;
  font-weight:600 !important;
  height:auto !important;
  min-height:0 !important;
  line-height:1.4 !important;
  text-align:left !important;
  width:auto !important;
}
.rec-btn button:hover { background:transparent !important; opacity:0.8; }
.rec-btn-purple button { color:#A855F7 !important; }
.rec-btn-cyan   button { color:#22D3EE !important; }
.rec-btn-green  button { color:#10B981 !important; }

/* Session row */
.sess-row {
  background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
  border-radius:14px;padding:0.9rem 1.2rem;margin-bottom:0.5rem;
  transition:all 0.25s ease;
}
.sess-row:hover { background:rgba(124,58,237,0.06);
  border-color:rgba(124,58,237,0.2); }

/* Section titles */
.mp-section-title {
  font-size:0.72rem;font-weight:700;color:#64748B;
  text-transform:uppercase;letter-spacing:1.2px;
  margin:0 0 1rem;display:flex;align-items:center;gap:0.4rem;
}
.mp-section-title::after {
  content:'';flex:1;height:1px;
  background:linear-gradient(90deg,rgba(124,58,237,0.3),transparent);
}

/* Streak dots */
.streak-dot {
  display:inline-block;width:12px;height:12px;border-radius:3px;
  margin:2px;transition:transform 0.2s;
}
.streak-dot:hover { transform:scale(1.3); }
</style>
"""


def _metric_card(icon, label, value, trend_text="", trend_up=True):
    color = "#10B981" if trend_up else "#EF4444"
    arrow = "↑" if trend_up else "↓"
    trend_html = f'<div class="mp-metric-trend" style="color:{color}">{arrow} {trend_text}</div>' if trend_text else ""
    st.markdown(f"""
    <div class="mp-metric">
      <div class="mp-metric-icon">{icon}</div>
      <div class="mp-metric-val">{value}</div>
      <div class="mp-metric-label">{label}</div>
      {trend_html}
    </div>""", unsafe_allow_html=True)


def _section(label, icon=""):
    st.markdown(f'<p class="mp-section-title"><span>{icon}</span>{label}</p>',
                unsafe_allow_html=True)


def render():
    inject_css()
    st.markdown(DASH_CSS, unsafe_allow_html=True)
    st.markdown('<div class="dash-bg-grid"></div>', unsafe_allow_html=True)

    # ── Load data ─────────────────────────────────────────────────
    with st.spinner(""):
        analytics = get_analytics()
        history   = get_history()

    total    = analytics.get("total_sessions", 0)
    avg_sc   = analytics.get("avg_overall_score", 0)
    avg_conf = analytics.get("avg_confidence_score", 0)
    avg_comm = analytics.get("avg_communication_score", 0)
    avg_tech = analytics.get("avg_technical_score", 0)

    # ── Header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="fade-in" style="display:flex;justify-content:space-between;
         align-items:flex-start;margin-bottom:2.5rem;">
      <div>
        <div style="display:inline-flex;align-items:center;gap:0.5rem;
             background:rgba(124,58,237,0.12);border:1px solid rgba(124,58,237,0.25);
             border-radius:99px;padding:4px 14px;margin-bottom:0.75rem;">
          <span style="width:6px;height:6px;border-radius:50%;background:#A855F7;
                       animation:aiPulse 2s infinite;display:inline-block;"></span>
          <span style="color:#A855F7;font-size:0.75rem;font-weight:600;letter-spacing:0.5px;">
            LIVE DASHBOARD
          </span>
        </div>
        <h1 style="font-size:2.4rem;font-weight:900;margin:0;line-height:1.1;
                   background:linear-gradient(135deg,#F1F5F9 40%,#A855F7 80%,#22D3EE);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   background-clip:text;">MockPilot AI</h1>
        <p style="color:#475569;font-size:0.9rem;margin:4px 0 0;">
          Welcome to MockPilot AI 🚀 &nbsp;·&nbsp;
          <span style="color:#A855F7;">{total} session{'s' if total!=1 else ''} completed</span>
        </p>
      </div>
      <div style="text-align:right;">
        <p style="color:#475569;font-size:0.72rem;margin:0;text-transform:uppercase;letter-spacing:0.5px;">Today</p>
        <p style="color:#F1F5F9;font-size:1rem;font-weight:700;margin:2px 0 0;">
          {datetime.now().strftime('%b %d, %Y')}
        </p>
        <p style="color:#64748B;font-size:0.75rem;margin:2px 0 0;">
          {datetime.now().strftime('%A')}
        </p>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Metric Cards ──────────────────────────────────────────────
    _section("Performance Overview", "📊")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: _metric_card("🎯", "Total Sessions", str(total))
    with c2: _metric_card("⭐", "Avg Score",      f"{avg_sc:.0f}", "pts")
    with c3: _metric_card("💪", "Confidence",     f"{avg_conf:.0f}", "pts")
    with c4: _metric_card("🗣️", "Communication",  f"{avg_comm:.0f}", "pts")
    with c5: _metric_card("⚡", "Technical",      f"{avg_tech:.0f}", "pts")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── AI Assistant + Insights ────────────────────────────────────
    col_ai, col_ins = st.columns([1, 1.2])

    with col_ai:
        _section("AI Assistant", "🤖")
        st.markdown(f"""
        <div class="ai-assistant">
          <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem;">
            <div style="width:42px;height:42px;border-radius:50%;
                        background:linear-gradient(135deg,#7C3AED,#22D3EE);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.2rem;flex-shrink:0;
                        box-shadow:0 0 20px rgba(124,58,237,0.4);">🤖</div>
            <div>
              <p style="color:#F1F5F9;font-weight:700;margin:0;font-size:0.92rem;">MockPilot AI</p>
              <p style="margin:0;font-size:0.72rem;">
                <span class="ai-pulse"></span>
                <span style="color:#10B981;font-size:0.7rem;">Online · Ready</span>
              </p>
            </div>
          </div>
          <p style="color:#CBD5E1;font-size:0.9rem;margin:0 0 1rem;line-height:1.6;">
            {"Ready for your next interview? Let's sharpen your skills!" if total == 0
             else f"Great work on {total} session{'s' if total!=1 else ''}! Keep the momentum going."}
          </p>
          <div style="background:rgba(124,58,237,0.12);border:1px solid rgba(124,58,237,0.2);
                      border-radius:12px;padding:0.7rem 1rem;margin-bottom:0.75rem;">
            <p style="color:#A855F7;font-size:0.75rem;font-weight:600;margin:0 0 0.2rem;">
              💡 Tip of the day
            </p>
            <p style="color:#94A3B8;font-size:0.82rem;margin:0;">
              Structure behavioral answers using the STAR method for 30% higher scores.
            </p>
          </div>
          <div style="background:rgba(34,211,238,0.08);border:1px solid rgba(34,211,238,0.2);
                      border-radius:12px;padding:0.7rem 1rem;">
            <p style="color:#22D3EE;font-size:0.75rem;font-weight:600;margin:0 0 0.2rem;">
              🎙️ Voice Mode Available
            </p>
            <p style="color:#94A3B8;font-size:0.82rem;margin:0;">
              Answer questions with your mic for a real interview feel.
            </p>
          </div>
        </div>""", unsafe_allow_html=True)

    with col_ins:
        _section("AI Insights", "✨")
        insights = [
            ("🧠", "#A855F7", "Keep practicing", "Complete your first interview to unlock personalized AI insights." if total == 0 else f"Your average score of {avg_sc:.0f} puts you in the top performers range."),
            ("📈", "#22D3EE", "Progress Tracking", "Consistency is key — regular practice sessions lead to measurable improvement."),
            ("⚡", "#10B981", "Strength Detected", f"Technical skills scoring {avg_tech:.0f} — focus on behavioral for a balanced profile." if avg_tech > 0 else "Complete interviews to discover your strongest skill areas."),
        ]
        for icon, color, title, text in insights:
            st.markdown(f"""
            <div class="insight-card">
              <div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;
                          background:{color}18;border:1px solid {color}33;
                          display:flex;align-items:center;justify-content:center;font-size:1rem;">
                {icon}
              </div>
              <div>
                <p style="color:#F1F5F9;font-weight:600;font-size:0.85rem;margin:0 0 0.2rem;">{title}</p>
                <p style="color:#64748B;font-size:0.8rem;margin:0;line-height:1.5;">{text}</p>
              </div>
            </div>""", unsafe_allow_html=True)

        # Quick start button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀  Start New Interview", key="dash_start_btn", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ────────────────────────────────────────────────
    col_chart, col_radar = st.columns([1.4, 1])

    with col_chart:
        _section("Score Trend", "📈")
        score_hist = analytics.get("score_history", [])
        if score_hist:
            dates  = [h.get("date", "") for h in score_hist]
            scores = [h.get("score", 0) for h in score_hist]
            line_chart(dates, scores, "Overall Score Over Time")
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                        border-radius:20px;padding:2.5rem;text-align:center;">
              <p style="font-size:2.5rem;margin:0 0 0.5rem;">📈</p>
              <p style="color:#475569;font-size:0.85rem;margin:0;">
                Complete interviews to see your score trend
              </p>
            </div>""", unsafe_allow_html=True)

    with col_radar:
        _section("Skill Radar", "🎯")
        skill_scores = analytics.get("skill_scores", {})
        if skill_scores:
            radar_chart(list(skill_scores.keys()), list(skill_scores.values()))
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                        border-radius:20px;padding:2.5rem;text-align:center;">
              <p style="font-size:2.5rem;margin:0 0 0.5rem;">🕸️</p>
              <p style="color:#475569;font-size:0.85rem;margin:0;">Skill radar unlocks after first session</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Practice Recommendations ───────────────────────────────────
    _section("Recommended Practice", "🏋️")
    recs = [
        ("🗣️", "#A855F7", "purple", "Behavioral (STAR)",
         "Master the Situation-Task-Action-Result framework", "behavioral"),
        ("⚙️", "#22D3EE", "cyan",   "System Design",
         "Practice high-level architecture & scalability",   "technical"),
        ("💼", "#10B981", "green",  "HR & Culture Fit",
         "Align your story with company values",              "hr"),
    ]
    rc1, rc2, rc3 = st.columns(3)
    for col, (icon, color, btn_cls, title, desc, itype) in zip([rc1, rc2, rc3], recs):
        with col:
            # Visual card body (no click needed on the div itself)
            st.markdown(f"""
            <div class="rec-card">
              <div style="width:40px;height:40px;border-radius:12px;
                          background:{color}18;border:1px solid {color}33;
                          display:flex;align-items:center;justify-content:center;
                          font-size:1.2rem;margin-bottom:0.7rem;">{icon}</div>
              <p style="color:#F1F5F9;font-weight:700;font-size:0.88rem;margin:0 0 0.3rem;">{title}</p>
              <p style="color:#64748B;font-size:0.78rem;margin:0 0 0.5rem;line-height:1.4;">{desc}</p>
            </div>""", unsafe_allow_html=True)
            # Real clickable button styled as a link
            st.markdown(f'<div class="rec-btn rec-btn-{btn_cls}">', unsafe_allow_html=True)
            if st.button(f"Start practicing →", key=f"rec_{itype}", use_container_width=False):
                st.session_state["interview_type_preset"] = itype
                st.session_state["page"] = "interview"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Strengths & Weaknesses ────────────────────────────────────
    col_s, col_w = st.columns(2)
    with col_s:
        _section("Strong Areas", "✅")
        strong = analytics.get("strong_areas", [])
        if strong:
            for item in strong:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.6rem;
                            background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);
                            border-radius:12px;padding:0.55rem 1rem;margin-bottom:0.45rem;
                            transition:all 0.2s;">
                  <span style="color:#10B981;font-size:0.9rem;">✅</span>
                  <span style="color:#CBD5E1;font-size:0.85rem;">{item}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.05);border:1px dashed rgba(16,185,129,0.2);
                        border-radius:12px;padding:1.2rem;text-align:center;">
              <p style="color:#475569;font-size:0.83rem;margin:0;">
                Complete interviews to identify your strengths
              </p>
            </div>""", unsafe_allow_html=True)

    with col_w:
        _section("Areas to Improve", "⚠️")
        weak = analytics.get("weak_areas", [])
        if weak:
            for item in weak:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.6rem;
                            background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);
                            border-radius:12px;padding:0.55rem 1rem;margin-bottom:0.45rem;">
                  <span style="color:#EF4444;font-size:0.9rem;">⚠️</span>
                  <span style="color:#CBD5E1;font-size:0.85rem;">{item}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.05);border:1px dashed rgba(16,185,129,0.2);
                        border-radius:12px;padding:1.2rem;text-align:center;">
              <p style="color:#10B981;font-size:0.83rem;margin:0;">🎉 No major weak areas identified!</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Clear All Sessions ────────────────────────────────────────
    with st.expander("⚠️  Danger Zone", expanded=False):
        st.markdown("""
        <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);
                    border-radius:16px;padding:1rem 1.2rem;">
          <p style="color:#EF4444;font-weight:700;font-size:0.88rem;margin:0 0 0.3rem;">
            🗑️ Clear All Sessions
          </p>
          <p style="color:#64748B;font-size:0.8rem;margin:0;">
            Permanently deletes all interview sessions, answers, and analytics.
            This action cannot be undone.
          </p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        confirm = st.checkbox(
            "I understand this will permanently delete all my data",
            key="confirm_clear"
        )
        if confirm:
            if st.button("🗑️  Confirm — Delete Everything", key="clear_all_btn",
                         use_container_width=True):
                with st.spinner("Clearing all sessions..."):
                    result = clear_all_sessions()
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    deleted = result.get("deleted", 0)
                    st.success(f"✅ {deleted} session(s) deleted. Dashboard will refresh.")
                    # Reset local session state
                    st.session_state.pop("confirm_clear", None)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent Sessions ───────────────────────────────────────────
    _section("Recent Sessions", "🕐")
    if history:
        for session in history[:8]:
            score = session.get("overall_score") or 0
            sc_color = "#10B981" if score >= 75 else "#F59E0B" if score >= 50 else "#EF4444"
            st_color  = "#10B981" if session.get("status") == "completed" else "#F59E0B"
            started = session.get("started_at", "")
            if started:
                try:
                    started = datetime.fromisoformat(started.replace("Z","")).strftime("%b %d")
                except Exception:
                    pass

            col_a, col_b, col_c, col_d, col_e = st.columns([2.5, 1.2, 0.8, 1, 0.7])
            with col_a:
                st.markdown(f"""
                <div style="padding:6px 0;">
                  <p style="color:#F1F5F9;font-weight:600;margin:0;font-size:0.9rem;">
                    {session.get('role','—')}
                  </p>
                  <p style="color:#64748B;font-size:0.75rem;margin:2px 0 0;">
                    {session.get('interview_type','—')} · {session.get('experience_level','—')}
                  </p>
                </div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"<p style='color:#64748B;font-size:0.8rem;margin:0;padding-top:10px;'>{started}</p>", unsafe_allow_html=True)
            with col_c:
                st.markdown(f"<p style='color:{sc_color};font-weight:800;font-size:1.1rem;margin:0;padding-top:6px;'>{score:.0f}</p>", unsafe_allow_html=True)
            with col_d:
                st.markdown(f"""
                <span style="background:{st_color}18;color:{st_color};border-radius:99px;
                             padding:3px 12px;font-size:0.72rem;font-weight:600;">
                  {session.get('status','—').title()}
                </span>""", unsafe_allow_html=True)
            with col_e:
                if st.button("View", key=f"view_{session['id']}", use_container_width=True):
                    st.session_state["view_session_id"] = session["id"]
                    st.session_state["page"] = "feedback"
                    st.rerun()
            st.markdown("<hr style='margin:0.3rem 0;border-color:rgba(255,255,255,0.04);'>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(124,58,237,0.08),rgba(34,211,238,0.04));
                    border:1px solid rgba(124,58,237,0.2);border-radius:24px;
                    padding:3rem;text-align:center;">
          <p style="font-size:3rem;margin:0 0 0.75rem;">🎯</p>
          <h3 style="color:#F1F5F9;font-weight:800;margin:0 0 0.5rem;">No interviews yet</h3>
          <p style="color:#64748B;margin:0 0 1.5rem;">
            Start your first AI mock interview to see your analytics here.
          </p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀  Start Your First Interview", use_container_width=True, key="dash_first_btn"):
            st.session_state["page"] = "interview"
            st.rerun()
