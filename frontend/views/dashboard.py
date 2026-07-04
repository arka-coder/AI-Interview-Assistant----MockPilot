"""
MockPilot AI — Premium Dashboard
Executive SaaS dashboard — Linear · Stripe aesthetic
"""
import streamlit as st
from datetime import datetime
from frontend.components.ui_components import (
    inject_css, radar_chart, line_chart
)
from frontend.api_client import get_analytics, get_history, clear_all_sessions


DASH_CSS = """
<style>
/* Dashboard waveform */
.dash-waveform { display:flex;align-items:flex-end;gap:3px;height:28px; }
.dash-wave-bar {
  width: 4px; border-radius: 99px;
  background: linear-gradient(to top, #16A34A, #86EFAC);
  animation: voicePulse 1.2s ease-in-out infinite;
}

/* Hero header section */
.dash-hero {
  position: relative;
  padding: 2rem 0 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  margin-bottom: 2rem;
}

/* KPI card enhanced */
.kpi-enhanced {
  background: #181B18;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  padding: 1.4rem 1.25rem;
  position: relative;
  overflow: hidden;
  transition: all 0.22s cubic-bezier(0.4,0,0.2,1);
  cursor: default;
}
.kpi-enhanced::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34,197,94,0.6), transparent);
  opacity: 0;
  transition: opacity 0.22s ease;
}
.kpi-enhanced:hover {
  transform: translateY(-2px);
  border-color: rgba(255,255,255,0.10);
  box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}
.kpi-enhanced:hover::before { opacity: 1; }
.kpi-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; margin-bottom: 0.85rem;
  flex-shrink: 0;
}
.kpi-num {
  font-family: 'Outfit', sans-serif;
  font-size: 2rem; font-weight: 800;
  letter-spacing: -0.04em; line-height: 1;
  background: linear-gradient(135deg, #FFFFFF, #86EFAC);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  margin-bottom: 4px;
}
.kpi-lbl {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.07em;
  color: #777777;
}
.kpi-trend {
  display: inline-flex; align-items: center; gap: 3px;
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem; font-weight: 700;
  border-radius: 99px; padding: 2px 8px; margin-top: 6px;
}
.kpi-trend.up   { background: rgba(16,185,129,0.1); color: #10B981; }
.kpi-trend.down { background: rgba(239,68,68,0.1);  color: #EF4444; }
.kpi-trend.neutral { background: rgba(113,113,122,0.12); color: #777777; }

/* CTA Banner */
.cta-banner-v2 {
  background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(24,24,27,0.9));
  border: 1px solid rgba(34,197,94,0.18);
  border-left: 3px solid #22C55E;
  border-radius: 20px;
  padding: 1.75rem 2rem;
  display: flex; align-items: center;
  justify-content: space-between; gap: 2rem;
  position: relative; overflow: hidden;
  box-shadow: 0 0 40px rgba(34,197,94,0.08);
}
.cta-banner-v2::after {
  content: ''; position: absolute; right: 0; top: 0;
  width: 40%; height: 100%;
  background: radial-gradient(ellipse at right center, rgba(34,197,94,0.07), transparent);
  pointer-events: none;
}

/* Sessions table */
.sess-table-row {
  display: grid; align-items: center;
  grid-template-columns: 2.5fr 1fr 0.7fr 0.9fr 0.6fr;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  transition: all 0.18s ease;
  border: 1px solid transparent;
}
.sess-table-row:hover {
  background: rgba(255,255,255,0.03);
  border-color: rgba(255,255,255,0.06);
}
.sess-table-header {
  display: grid;
  grid-template-columns: 2.5fr 1fr 0.7fr 0.9fr 0.6fr;
  gap: 1rem;
  padding: 0.5rem 1rem;
  margin-bottom: 0.25rem;
}
</style>
"""

WAVEFORM = "".join([
    f'<div class="dash-wave-bar" style="height:10px;animation-delay:{d}s;"></div>'
    for d in [0.1, 0.3, 0.2, 0.4, 0.15, 0.5]
])


# ── Lucide inline-SVG icon helper (one consistent icon set, no emojis) ──────────
_LU_PATHS = {
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "target":   '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "star":     '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "zap":      '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "message":  '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "cpu":      '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>',
    "trending": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "clock":    '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "sparkles": '<path d="M12 3l1.9 5.7 5.7 1.9-5.7 1.9L12 18l-1.9-5.5L4.4 10.6 10.1 8.7z"/>',
    "bot":      '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2M20 14h2M15 13v2M9 13v2"/>',
    "gauge":    '<path d="M12 14 8 8"/><circle cx="12" cy="12" r="9"/>',
}
def _lu(name, color="#86EFAC", size=18, sw=2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round">{_LU_PATHS.get(name, "")}</svg>')


def _section(label, icon=""):
    st.markdown(
        f'<p class="mp-section-title" style="display:flex;align-items:center;gap:8px;">'
        f'<span style="display:inline-flex;align-items:center;">{icon}</span>{label}</p>',
        unsafe_allow_html=True
    )


def _kpi(icon, label, value, trend="", trend_up=True, icon_bg="rgba(34,197,94,0.12)", icon_color="#86EFAC"):
    trend_class = "up" if trend_up else "down"
    arrow = "↑" if trend_up else "↓"
    trend_html = (
        f'<div class="kpi-trend {trend_class}">{arrow} {trend}</div>'
    ) if trend else '<div class="kpi-trend neutral">— No data</div>'

    st.markdown(f"""
    <div class="kpi-enhanced">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;">
        <div class="kpi-icon" style="background:{icon_bg};color:{icon_color};">{icon}</div>
      </div>
      <div class="kpi-num">{value}</div>
      <div class="kpi-lbl">{label}</div>
      {trend_html}
    </div>""", unsafe_allow_html=True)


def render():
    inject_css()
    st.markdown(DASH_CSS, unsafe_allow_html=True)

    # Load data
    with st.spinner(""):
        analytics = get_analytics()
        history   = get_history()

    total    = analytics.get("total_sessions", 0)
    avg_sc   = analytics.get("avg_overall_score", 0)
    avg_conf = analytics.get("avg_confidence_score", 0)
    avg_comm = analytics.get("avg_communication_score", 0)
    avg_tech = analytics.get("avg_technical_score", 0)

    # ── HEADER ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="dash-hero fade-in">
      <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:1rem;">
        <div>
          <p style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;color:#22C55E;margin:0 0 8px;">
            Member Dashboard
          </p>
          <h1 style="font-family:'Outfit',sans-serif;font-size:2.25rem;font-weight:800;
                     margin:0 0 6px;color:#FFFFFF;letter-spacing:-0.04em;">Welcome back.</h1>
          <p style="color:#777777;margin:0;font-size:0.9rem;font-family:'Inter',sans-serif;">
            {f'You have completed <strong style="color:#86EFAC;">{total} session{"s" if total!=1 else ""}</strong>. Keep the momentum going!'
             if total > 0 else 'Start your first AI mock interview to see your analytics here.'}
          </p>
        </div>
        <div style="display:flex;align-items:center;gap:0.6rem;
                    background:rgba(24,24,27,0.8);border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px;padding:0.6rem 1rem;">
          <div style="width:30px;height:30px;border-radius:9px;
                      background:var(--primary);
                      display:flex;align-items:center;justify-content:center;">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#052e13" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2M20 14h2M15 13v2M9 13v2"/></svg></div>
          <div>
            <p style="font-family:'Inter',sans-serif;font-size:0.78rem;font-weight:600;
                      color:#FFFFFF;margin:0;line-height:1;">MockPilot User</p>
            <p style="font-family:'Inter',sans-serif;font-size:0.65rem;color:#777777;margin:2px 0 0;">
              Guest Account
            </p>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA BANNER ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="cta-banner-v2 fade-in-up">
      <div style="flex:1;position:relative;z-index:1;">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.65rem;">
          <div class="dash-waveform">{WAVEFORM}</div>
          <span style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                       letter-spacing:0.1em;text-transform:uppercase;color:#86EFAC;">AI Analyst Active</span>
        </div>
        <h2 style="font-family:'Outfit',sans-serif;font-size:1.4rem;font-weight:700;
                   color:#FFFFFF;margin:0 0 0.4rem;letter-spacing:-0.02em;">Master your next interview.</h2>
        <p style="color:#B5B5B5;font-size:0.875rem;max-width:500px;margin:0;line-height:1.7;
                  font-family:'Inter',sans-serif;">
          Launch a high-fidelity mock session with our neural-voice assistant.
          Real-time feedback on tone, structure, and technical precision.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    _, cta_btn_col, _ = st.columns([1, 1.5, 1])
    with cta_btn_col:
        if st.button(":material/play_arrow: Start new mock interview", key="dash_start_btn", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── METRICS ROW ───────────────────────────────────────────────────────────
    _section("Performance Overview", _lu("activity","#86EFAC",16))
    m1, m2, m3, m4, m5 = st.columns(5, gap="small")
    with m1: _kpi(_lu("target","#86EFAC"), "Total Sessions", str(total), "", True,
                  "rgba(34,197,94,0.12)", "#86EFAC")
    with m2: _kpi(_lu("star","#FCD34D"), "Avg Score", f"{avg_sc:.0f}", "+12% this week", True,
                  "rgba(245,158,11,0.1)", "#FCD34D")
    with m3: _kpi(_lu("zap","#6EE7B7"), "Confidence", f"{avg_conf:.0f}", f"{avg_conf:.0f} pts", avg_conf >= 60,
                  "rgba(16,185,129,0.1)", "#6EE7B7")
    with m4: _kpi(_lu("message","#86EFAC"), "Communication", f"{avg_comm:.0f}", f"{avg_comm:.0f} pts", avg_comm >= 60,
                  "rgba(22,163,74,0.1)", "#86EFAC")
    with m5: _kpi(_lu("cpu","#16A34A"), "Technical", f"{avg_tech:.0f}", f"{avg_tech:.0f} pts", avg_tech >= 60,
                  "rgba(22,163,74,0.1)", "#16A34A")

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── SESSIONS + PERFORMANCE TRENDS ─────────────────────────────────────────
    col_sessions, col_chart = st.columns([5, 8], gap="medium")

    with col_sessions:
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
          <p class="mp-section-title" style="margin:0;">Recent Sessions</p>
        </div>
        """, unsafe_allow_html=True)

        if history:
            for session in history[:4]:
                score = session.get("overall_score") or 0
                sc_color = "#10B981" if score >= 75 else "#F59E0B" if score >= 50 else "#EF4444"
                role = session.get("role", "Mock Interview")
                itype = session.get("interview_type", "General")
                started = session.get("started_at", "")
                if started:
                    try:
                        started = datetime.fromisoformat(started.replace("Z", "")).strftime("%b %d")
                    except Exception:
                        pass
                if score < 50:
                    tier_cls = "tier-beginner"
                    tier_label = "Beginner"
                elif score < 65:
                    tier_cls = "tier-developing"
                    tier_label = "Developing"
                elif score < 80:
                    tier_cls = "tier-competent"
                    tier_label = "Competent"
                elif score < 90:
                    tier_cls = "tier-proficient"
                    tier_label = "Proficient"
                else:
                    tier_cls = "tier-expert"
                    tier_label = "Expert"

                q_count = session.get("question_count", 3)

                st.markdown(f"""
                <div class="sess-row {tier_cls}">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px;">
                    <p style="font-family:'Inter',sans-serif;font-weight:600;font-size:0.875rem;
                              color:#FFFFFF;margin:0;">{role}</p>
                    <span style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1rem;
                                 color:{sc_color};">{score:.0f}</span>
                  </div>
                  <p style="color:#777777;font-size:0.72rem;margin:0;font-family:'Inter',sans-serif;">
                    {tier_label} · {itype} · {q_count}q · {started}
                  </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(34,197,94,0.04);border:1px dashed rgba(34,197,94,0.18);
                        border-radius:16px;padding:2.5rem;text-align:center;">
              
              <p style="color:#777777;font-size:0.85rem;margin:0;font-family:'Inter',sans-serif;">
                No sessions yet — start your first interview!
              </p>
            </div>""", unsafe_allow_html=True)

    with col_chart:
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
          <p class="mp-section-title" style="margin:0;">Performance Trend</p>
          <div style="display:flex;gap:1rem;align-items:center;">
            <div style="display:flex;align-items:center;gap:4px;">
              <div style="width:7px;height:7px;border-radius:50%;background:#86EFAC;"></div>
              <span style="font-size:0.68rem;color:#777777;text-transform:uppercase;letter-spacing:0.05em;font-family:'Inter',sans-serif;">Score</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        score_hist = analytics.get("score_history", [])
        if score_hist:
            dates = [h.get("date", "") for h in score_hist]
            scores = [h.get("score", 0) for h in score_hist]
            line_chart(dates, scores, "Overall Score Over Time")
        else:
            st.markdown(f"""
            <div class="chart-glass">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.25rem;">
                <div>
                  <p style="font-size:0.68rem;color:#777777;text-transform:uppercase;
                             font-family:'Inter',sans-serif;font-weight:700;
                             letter-spacing:0.08em;margin:0 0 4px;">Current Average</p>
                  <div style="font-family:'Outfit',sans-serif;font-size:2.25rem;font-weight:800;
                              color:#86EFAC;line-height:1;letter-spacing:-0.04em;">
                    {avg_sc:.1f}
                    <span style="font-size:0.9rem;font-weight:400;color:#777777;">/100</span>
                  </div>
                </div>
                <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
                            color:#10B981;border-radius:99px;padding:4px 12px;
                            font-size:0.72rem;font-weight:700;font-family:'Inter',sans-serif;">+12% this week</div>
              </div>
              <!-- Mini bar chart placeholder -->
              <div style="display:flex;align-items:flex-end;gap:0.6rem;height:100px;padding-top:1rem;">
                {''.join([
                    f'<div style="flex:1;border-radius:5px 5px 0 0;overflow:hidden;height:{h}%;">'
                    f'<div style="width:100%;height:100%;background:rgba(134,239,172,{0.1 + h/400});'
                    f'border-radius:5px 5px 0 0;"></div></div>'
                    for h in [35, 52, 42, 70, 62, 88]
                ])}
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:0.6rem;
                          padding-top:0.6rem;border-top:1px solid rgba(255,255,255,0.05);">
                {''.join([f'<span style="font-size:0.62rem;font-family:Inter,sans-serif;font-weight:600;color:#777777;text-transform:uppercase;letter-spacing:0.05em;">{d}</span>'
                          for d in ['Mon','Tue','Wed','Thu','Fri','Today']])}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── AI-RECOMMENDED PRACTICE AREAS ─────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
      <span style="display:inline-flex;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#86EFAC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 5.7 5.7 1.9-5.7 1.9L12 18l-1.9-5.5L4.4 10.6 10.1 8.7z"/></svg></span>
      <p class="mp-section-title" style="margin:0;">AI-Recommended Practice Areas</p>
    </div>
    """, unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3, gap="medium")

    practice_areas = [
        (p1, "#F59E0B", "rgba(245,158,11,0.1)", '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>', "Speaking Pace",
         "Your pace increases by 20% during technical questions. Focus on deliberate pauses.",
         45, "IMPROVEMENT NEEDED", "behavioral"),
        (p2, "#86EFAC", "rgba(134,239,172,0.1)", '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#86EFAC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>', "System Design",
         "Scalability principles were well-articulated, but load balancing specifics could be sharper.",
         72, "PROFICIENCY", "technical"),
        (p3, "#86EFAC", "rgba(103,232,249,0.1)", '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#86EFAC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>', "Body Language",
         "Excellent eye contact and hand gestures. Maintain this energy for executive presence.",
         88, "MASTERY", "hr"),
    ]

    for col, color, bg_color, icon, title, desc, pct, label, itype in practice_areas:
        with col:
            st.markdown(f"""
            <div class="stitch-practice-card" style="border-top-color:{color}50;">
              <div style="width:44px;height:44px;border-radius:12px;background:{bg_color};
                          display:flex;align-items:center;justify-content:center;
                          font-size:1.2rem;margin-bottom:1rem;
                          border:1px solid {color}30;">
                {icon}
              </div>
              <h4 style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:700;
                         color:#FFFFFF;margin:0 0 0.4rem;">{title}</h4>
              <p style="color:#B5B5B5;font-size:0.82rem;line-height:1.7;margin:0 0 0.85rem;
                        font-family:'Inter',sans-serif;">{desc}</p>
              <div class="stitch-score-track">
                <div class="stitch-score-fill" style="width:{pct}%;background:{color};
                     box-shadow:0 0 8px {color}50;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:5px;">
                <span style="font-family:'Inter',sans-serif;font-size:0.65rem;
                             font-weight:700;letter-spacing:0.05em;color:#777777;">{label}</span>
                <span style="font-family:'Inter',sans-serif;font-size:0.65rem;
                             font-weight:700;color:{color};">{pct}%</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Practice {title} →", key=f"prac_{itype}", use_container_width=True):
                st.session_state["interview_type_preset"] = itype
                st.session_state["page"] = "interview"
                st.rerun()

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── CHARTS ROW ────────────────────────────────────────────────────────────
    col_radar, col_sw = st.columns([1, 1.2], gap="medium")

    with col_radar:
        _section("Skill Breakdown", _lu("target","#86EFAC",16))
        skill_scores = analytics.get("skill_scores", {})
        if skill_scores:
            radar_chart(list(skill_scores.keys()), list(skill_scores.values()))
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
                        border-radius:20px;padding:2.5rem;text-align:center;">
              
              <p style="color:#777777;font-size:0.85rem;margin:0;font-family:'Inter',sans-serif;">
                Skill radar unlocks after your first session
              </p>
            </div>""", unsafe_allow_html=True)

    with col_sw:
        _section("Strengths & Improvements", _lu("trending","#86EFAC",16))
        strong = analytics.get("strong_areas", [])
        weak   = analytics.get("weak_areas", [])

        if strong:
            for item in strong[:3]:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.6rem;
                            background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.18);
                            border-radius:10px;padding:0.55rem 1rem;margin-bottom:0.35rem;">
                  <span style="color:#10B981;font-size:0.8rem;">✓</span>
                  <span style="color:#B5B5B5;font-size:0.84rem;font-family:'Inter',sans-serif;">{item}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.04);border:1px dashed rgba(16,185,129,0.18);
                        border-radius:10px;padding:1.1rem;text-align:center;margin-bottom:0.5rem;">
              <p style="color:#777777;font-size:0.82rem;margin:0;font-family:'Inter',sans-serif;">
                Complete interviews to identify your strengths
              </p>
            </div>""", unsafe_allow_html=True)

        if weak:
            for item in weak[:3]:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.6rem;
                            background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.18);
                            border-radius:10px;padding:0.55rem 1rem;margin-bottom:0.35rem;">
                  <span style="color:#EF4444;font-size:0.8rem;">↑</span>
                  <span style="color:#B5B5B5;font-size:0.84rem;font-family:'Inter',sans-serif;">{item}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.04);border:1px dashed rgba(16,185,129,0.18);
                        border-radius:10px;padding:1.1rem;text-align:center;">
              <p style="color:#10B981;font-size:0.82rem;margin:0;font-family:'Inter',sans-serif;">
                No major weak areas identified.
              </p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── RECENT SESSIONS TABLE ─────────────────────────────────────────────────
    _section("All Sessions", _lu("clock","#86EFAC",16))

    if history:
        # Header row
        st.markdown("""
        <div class="sess-table-header">
          <span style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                       text-transform:uppercase;letter-spacing:0.08em;color:#777777;">Role</span>
          <span style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                       text-transform:uppercase;letter-spacing:0.08em;color:#777777;">Date</span>
          <span style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                       text-transform:uppercase;letter-spacing:0.08em;color:#777777;">Score</span>
          <span style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                       text-transform:uppercase;letter-spacing:0.08em;color:#777777;">Status</span>
          <span></span>
        </div>
        <div style="height:1px;background:rgba(255,255,255,0.05);margin-bottom:0.35rem;"></div>
        """, unsafe_allow_html=True)

        for session in history[:8]:
            score = session.get("overall_score") or 0
            sc_color = "#10B981" if score >= 75 else "#F59E0B" if score >= 50 else "#EF4444"
            st_color = "#10B981" if session.get("status") == "completed" else "#F59E0B"
            started = session.get("started_at", "")
            if started:
                try:
                    started = datetime.fromisoformat(started.replace("Z", "")).strftime("%b %d")
                except Exception:
                    pass

            ca, cb, cc, cd, ce = st.columns([2.5, 1.2, 0.8, 1, 0.7])
            with ca:
                st.markdown(f"""
                <div style="padding:6px 0;">
                  <p style="color:#FFFFFF;font-weight:600;margin:0;font-size:0.875rem;
                             font-family:'Inter',sans-serif;">{session.get('role','—')}</p>
                  <p style="color:#777777;font-size:0.72rem;margin:2px 0 0;font-family:'Inter',sans-serif;">
                    {session.get('interview_type','—')} · {session.get('experience_level','—')}
                  </p>
                </div>""", unsafe_allow_html=True)
            with cb:
                st.markdown(f"<p style='color:#777777;font-size:0.8rem;margin:0;padding-top:10px;font-family:Inter,sans-serif;'>{started}</p>", unsafe_allow_html=True)
            with cc:
                st.markdown(f"<p style='color:{sc_color};font-weight:800;font-size:1.05rem;margin:0;padding-top:6px;font-family:Outfit,sans-serif;letter-spacing:-0.02em;'>{score:.0f}</p>", unsafe_allow_html=True)
            with cd:
                st.markdown(f"""
                <span style="background:{st_color}18;color:{st_color};border-radius:99px;
                             padding:3px 10px;font-size:0.7rem;font-weight:700;
                             font-family:'Inter',sans-serif;letter-spacing:0.02em;">
                  {session.get('status','—').title()}
                </span>""", unsafe_allow_html=True)
            with ce:
                if st.button("View", key=f"view_{session['id']}", use_container_width=True):
                    st.session_state["view_session_id"] = session["id"]
                    st.session_state["page"] = "feedback"
                    st.rerun()
            st.markdown("<div style='height:1px;background:rgba(255,255,255,0.04);margin:1px 0;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(34,197,94,0.06),rgba(22,163,74,0.03));
                    border:1px solid rgba(34,197,94,0.15);border-radius:24px;
                    padding:3rem;text-align:center;">
          
          <h3 style="font-family:'Outfit',sans-serif;color:#FFFFFF;font-weight:800;margin:0 0 0.5rem;
                     letter-spacing:-0.02em;">No interviews yet</h3>
          <p style="color:#777777;margin:0 0 1.5rem;font-family:'Inter',sans-serif;font-size:0.875rem;">
            Start your first AI mock interview to see your analytics here.
          </p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        if st.button(":material/rocket_launch: Start your first interview", use_container_width=True, key="dash_first_btn"):
            st.session_state["page"] = "interview"
            st.rerun()

    # ── DATA & PRIVACY ──────────────────────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    with st.expander("Data & privacy", expanded=False):
        st.markdown("""
        <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px;padding:1rem 1.2rem;">
          <p style="color:#FFFFFF;font-weight:600;font-size:0.88rem;margin:0 0 0.25rem;
                    font-family:'Inter',sans-serif;">Clear All Sessions</p>
          <p style="color:#777777;font-size:0.78rem;margin:0;font-family:'Inter',sans-serif;line-height:1.6;">
            Permanently deletes all interview sessions, answers, and analytics.
            This action cannot be undone.
          </p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        confirm = st.checkbox("I understand this will permanently delete all my data", key="confirm_clear")
        if confirm:
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button(":material/delete: Confirm — delete everything", key="clear_all_btn", use_container_width=True):
                with st.spinner("Clearing all sessions..."):
                    result = clear_all_sessions()
                if "error" in result:
                    st.error(result["error"])
                else:
                    deleted = result.get("deleted", 0)
                    st.success(f"{deleted} session(s) deleted.")
                    st.session_state.pop("confirm_clear", None)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:2rem;padding-top:1.5rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;opacity:0.7;">
        <span style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:500;color:#777777;">
          © 2026 MockPilot AI. Elevate your career.
        </span>
        <div style="display:flex;gap:1.5rem;">
          <a href="#" style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:500;
                             color:#777777;text-decoration:none;">Terms</a>
          <a href="#" style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:500;
                             color:#777777;text-decoration:none;">Privacy</a>
          <a href="#" style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:500;
                             color:#777777;text-decoration:none;">Support</a>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
