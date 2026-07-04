"""
MockPilot AI — Readiness Report (Cinematic Score Reveal)
"""
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from frontend.components.ui_components import inject_css, html_escape

REPORT_CSS = """<style>
.rr-hero{background:linear-gradient(160deg,rgba(34,197,94,0.12) 0%,rgba(74,222,128,0.05) 100%);
  border:1px solid rgba(34,197,94,0.25);border-radius:32px;padding:2.5rem 2rem;
  text-align:center;position:relative;overflow:hidden;margin-bottom:1.5rem;
  box-shadow:0 0 60px rgba(34,197,94,0.1);}
.rr-hero::before{content:'';position:absolute;top:-60%;left:-40%;width:180%;height:180%;
  background:radial-gradient(circle at 50% 50%,rgba(34,197,94,0.08),transparent 55%);
  pointer-events:none;}
/* Stitch-aligned dim bars — use stitch-score-track/fill from main.css */
.dim-bar-wrap{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
  border-radius:14px;padding:0.9rem 1.1rem;margin-bottom:0.5rem;transition:all 0.3s;}
.dim-bar-wrap:hover{border-color:rgba(22,163,74,0.3);transform:translateX(4px);}
.ins-card{border-radius:15px;padding:0.8rem 1rem;margin-bottom:0.45rem;
  display:flex;align-items:flex-start;gap:0.6rem;transition:all 0.25s;}
.ins-card:hover{transform:translateX(5px);}
.ins-green{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);}
.ins-red{background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);}
.ins-amber{background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);}
.road-row{display:flex;align-items:flex-start;gap:0.85rem;padding:0.8rem 1rem;
  border-radius:13px;margin-bottom:0.5rem;background:rgba(255,255,255,0.02);
  border:1px solid rgba(255,255,255,0.05);transition:all 0.25s;}
.road-row:hover{background:rgba(34,197,94,0.07);border-color:rgba(34,197,94,0.25);transform:translateX(4px);}
.road-day{min-width:34px;height:34px;border-radius:9px;
  background:linear-gradient(135deg,#22C55E,#4ADE80);
  display:flex;align-items:center;justify-content:center;
  font-size:0.75rem;font-weight:900;color:#fff;flex-shrink:0;}
.prob-bar{height:8px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;margin-top:6px;}
</style>"""


def _js_counter(score: float, color: str) -> str:
    """Animated JS counter inside an SVG ring — the cinematic hero."""
    r = 80
    circ = 2 * 3.14159 * r
    return f"""
<div style="position:relative;display:inline-block;" class="score-hero-wrap">
  <svg id="ringSvg" width="220" height="220" viewBox="0 0 220 220"
       style="filter:drop-shadow(0 0 18px {color}66);">
    <circle cx="110" cy="110" r="{r}" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="14"/>
    <circle id="ringArc" cx="110" cy="110" r="{r}" fill="none" stroke="{color}" stroke-width="14"
            stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}"
            stroke-linecap="round" transform="rotate(-90 110 110)"
            style="transition:stroke-dashoffset 1.6s cubic-bezier(0.4,0,0.2,1);"/>
    <text id="scoreNum" x="110" y="102" text-anchor="middle" fill="{color}"
          font-size="52" font-weight="900" font-family="Outfit,Inter,sans-serif">0</text>
    <text x="110" y="126" text-anchor="middle" fill="#64748B"
          font-size="14" font-family="Outfit,Inter,sans-serif">/ 100</text>
    <text x="110" y="148" text-anchor="middle" fill="#777777"
          font-size="11" font-family="Outfit,Inter,sans-serif">Readiness Score</text>
  </svg>
</div>
<script>
(function(){{
  var target = {score:.0f};
  var circ   = {circ:.1f};
  var arc    = document.getElementById('ringArc');
  var num    = document.getElementById('scoreNum');
  var start  = null;
  var dur    = 1600;
  function ease(t){{ return 1 - Math.pow(1-t, 3); }}
  function step(ts){{
    if(!start) start = ts;
    var p = Math.min((ts-start)/dur, 1);
    var e = ease(p);
    num.textContent = Math.round(e * target);
    arc.style.strokeDashoffset = circ * (1 - e * target/100);
    if(p < 1) requestAnimationFrame(step);
    else num.textContent = target;
  }}
  setTimeout(function(){{ requestAnimationFrame(step); }}, 300);
}})();
</script>"""


def _radar(scores: dict):
    cats = ["Technical", "Communication", "Confidence", "ATS/Resume", "Grammar"]
    vals = [scores.get("technical_readiness",0), scores.get("communication",0),
            scores.get("confidence",0), scores.get("ats_compatibility",0), scores.get("grammar",0)]
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]], fill='toself',
        line=dict(color="#16A34A", width=2.5),
        fillcolor='rgba(34,197,94,0.18)',
        marker=dict(color="#4ADE80", size=7, line=dict(color="#16A34A",width=2)),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit,Inter,sans-serif", color="#B5B5B5"),
        margin=dict(l=20,r=20,t=20,b=20), height=300,
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,range=[0,100],gridcolor="rgba(255,255,255,0.06)",
                            color="#777777",tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.06)",color="#B5B5B5",
                             tickfont=dict(size=11))),
    )
    st.plotly_chart(fig, use_container_width=True)


def _dim_bar(label: str, score: float, color: str, icon: str = ""):
    pct = min(100, max(0, score))
    st.markdown(f"""
    <div class="dim-bar-wrap">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="color:#CBD5E1;font-size:0.82rem;font-weight:600;">{icon} {label}</span>
        <span style="color:{color};font-weight:800;font-size:0.88rem;">{pct:.0f}</span>
      </div>
      <div class="stitch-score-track" style="margin-top:6px;">
        <div class="stitch-score-fill animated-bar"
             style="width:{pct}%;background:linear-gradient(90deg,{color},{color}99);
                    box-shadow:0 0 10px {color}66;"></div>
      </div>
    </div>""", unsafe_allow_html=True)


def render():
    inject_css()
    st.markdown(REPORT_CSS, unsafe_allow_html=True)

    report = st.session_state.get("scan_report")
    if not report:
        st.warning("No report found. Please complete the Quick Scan first.")
        if st.button("← Run Quick Scan", key="rr_go_scan"):
            st.session_state["page"] = "quick_scan"
            st.rerun()
        return

    rd   = report.get("readiness", {})
    ins  = report.get("insights", {})
    road = report.get("roadmap", [])
    q1   = report.get("question1", {})
    q2   = report.get("question2", {})

    score     = rd.get("overall", 0)
    lbl       = rd.get("label", "Developing")
    col_hex   = rd.get("color", "#16A34A")
    emoji     = rd.get("emoji", "📈")
    role      = st.session_state.get("scan_role", "Role")
    itype     = st.session_state.get("scan_type", "Technical")
    level_str = st.session_state.get("scan_level", "Mid")

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="rr-hero reveal-1">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;gap:0.6rem;margin-bottom:1rem;">
      <span style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);
                   border-radius:99px;padding:4px 14px;font-size:0.72rem;color:#10B981;font-weight:700;">
        ✓ Assessment Complete
      </span>
      <span style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
                   border-radius:99px;padding:4px 14px;font-size:0.72rem;color:#64748B;font-weight:600;">
        ⏱ Avg completion: 1m 34s
      </span>
    </div>
    <p style="color:#64748B;font-size:0.85rem;margin:0 0 1.5rem;">
      {html_escape(role)} · {html_escape(itype)} · {html_escape(level_str)}
    </p>""", unsafe_allow_html=True)

    # Animated score counter (JS)
    c_left, c_mid, c_right = st.columns([1, 1.2, 1])
    with c_mid:
        components.html(_js_counter(score, col_hex), height=240)

    # Level badge
    grad_map = {
        "Industry Ready": "linear-gradient(135deg,rgba(16,185,129,0.2),rgba(74,222,128,0.1))",
        "Interview Ready": "linear-gradient(135deg,rgba(22,163,74,0.2),rgba(74,222,128,0.1))",
        "Developing":     "linear-gradient(135deg,rgba(245,158,11,0.18),rgba(34,197,94,0.08))",
        "Beginner":       "linear-gradient(135deg,rgba(239,68,68,0.18),rgba(34,197,94,0.08))",
    }
    st.markdown(f"""
    <div class="level-badge-pop" style="margin-top:0.5rem;">
      <div style="display:inline-flex;align-items:center;gap:0.5rem;
           background:{grad_map.get(lbl,'')};border:1px solid {col_hex}44;
           border-radius:99px;padding:8px 24px;">
        <span style="font-size:1.3rem;">{html_escape(emoji)}</span>
        <span style="color:{col_hex};font-size:1.1rem;font-weight:900;">{html_escape(lbl)}</span>
      </div>
      <p style="color:#777777;font-size:0.72rem;margin:6px 0 0;">
        0–40 Beginner &nbsp;·&nbsp; 41–65 Developing &nbsp;·&nbsp; 66–80 Interview Ready &nbsp;·&nbsp; 81–100 Industry Ready
      </p>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── SCORE BREAKDOWN (bars) + RADAR ────────────────────────────────────────
    col_bars, col_radar = st.columns([1, 1])

    with col_bars:
        st.markdown('<p style="color:#64748B;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.75rem;" class="reveal-2">📊 Score Breakdown</p>', unsafe_allow_html=True)
        dims = [
            ("Resume Strength",    rd.get("resume_strength",0),    "#F59E0B", "📄"),
            ("Communication",      rd.get("communication",0),       "#16A34A", "🗣️"),
            ("Technical Readiness",rd.get("technical_readiness",0), "#4ADE80", "⚡"),
            ("Confidence",         rd.get("confidence",0),          "#10B981", "💪"),
            ("ATS Compatibility",  rd.get("ats_compatibility",0),   "#3B82F6", "🎯"),
            ("Grammar & Clarity",  rd.get("grammar",0),             "#EC4899", "✍️"),
        ]
        for lbl_d, sc, clr, ico in dims:
            _dim_bar(lbl_d, sc, clr, ico)

    with col_radar:
        st.markdown('<p style="color:#64748B;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.25rem;" class="reveal-2">🎯 Skill Radar</p>', unsafe_allow_html=True)
        _radar(rd)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── AI HIRING INSIGHTS ────────────────────────────────────────────────────
    st.markdown("""<div class="reveal-3">""", unsafe_allow_html=True)
    prob      = ins.get("shortlist_probability","Medium")
    prob_clr  = {"Very High":"#10B981","High":"#16A34A","Medium":"#F59E0B","Low":"#EF4444"}.get(prob,"#16A34A")
    prob_pct  = {"Very High":92,"High":75,"Medium":50,"Low":28}.get(prob,50)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(74,222,128,0.05));
                border:1px solid rgba(34,197,94,0.25);border-radius:20px;padding:1.5rem;margin-bottom:1rem;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
        <div>
          <p style="color:#64748B;font-size:0.7rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:1px;margin:0 0 0.3rem;">🤖 AI HIRING INSIGHTS</p>
          <h3 style="color:#FFFFFF;font-size:1.1rem;font-weight:800;margin:0;">Recruiter Intelligence Report</h3>
        </div>
        <div style="text-align:right;">
          <span style="background:{prob_clr}18;color:{prob_clr};border:1px solid {prob_clr}44;
                       border-radius:99px;padding:4px 14px;font-size:0.78rem;font-weight:700;">
            {prob} Shortlist Probability
          </span>
          <div class="prob-bar" style="width:140px;margin-left:auto;margin-top:6px;">
            <div class="animated-bar" style="height:8px;border-radius:99px;
                 background:linear-gradient(90deg,{prob_clr},{prob_clr}88);width:{prob_pct}%;"></div>
          </div>
        </div>
      </div>
      <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:0.75rem 1rem;margin-bottom:1rem;
                  border-left:3px solid {prob_clr};">
        <p style="color:#B5B5B5;font-size:0.88rem;margin:0;font-style:italic;line-height:1.55;">
          "{html_escape(ins.get('recruiter_impression','Strong candidate profile detected.'))}"
        </p>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
        <div>
          <p style="color:#10B981;font-size:0.72rem;font-weight:700;margin:0 0 0.4rem;text-transform:uppercase;letter-spacing:0.5px;">✅ Strong Signals</p>
          {''.join(f'<div class="ins-card ins-green"><span style="color:#10B981;font-size:0.9rem;">✓</span><span style="color:#CBD5E1;font-size:0.8rem;line-height:1.4;">{html_escape(s)}</span></div>' for s in ins.get("strong_signals",[]))}
        </div>
        <div>
          <p style="color:#EF4444;font-size:0.72rem;font-weight:700;margin:0 0 0.4rem;text-transform:uppercase;letter-spacing:0.5px;">⚠️ Hiring Risks</p>
          {''.join(f'<div class="ins-card ins-red"><span style="color:#EF4444;font-size:0.9rem;">!</span><span style="color:#CBD5E1;font-size:0.8rem;line-height:1.4;">{html_escape(r)}</span></div>' for r in ins.get("hiring_risks",[]))}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 7-DAY ROADMAP ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="reveal-4" style="margin-bottom:0.75rem;">
      <p style="color:#64748B;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">🗓️ PERSONALIZED 7-DAY IMPROVEMENT ROADMAP</p>
      <h3 style="color:#FFFFFF;font-size:1.1rem;font-weight:800;margin:0 0 0.75rem;">Your AI Action Plan</h3>
    </div>""", unsafe_allow_html=True)

    pri_clr = {"High":"#EF4444","Medium":"#F59E0B","Low":"#10B981"}
    col_a, col_b = st.columns(2)
    for i, day in enumerate(road):
        col = col_a if i % 2 == 0 else col_b
        pc = pri_clr.get(day.get("priority","Medium"),"#F59E0B")
        with col:
            st.markdown(f"""
            <div class="road-row reveal-{min(i+4,6)}">
              <div class="road-day">D{day.get('day',i+1)}</div>
              <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                  <p style="color:#FFFFFF;font-weight:700;font-size:0.85rem;margin:0;">{html_escape(day.get('focus',''))}</p>
                  <span style="background:{pc}18;color:{pc};border-radius:99px;padding:1px 9px;font-size:0.65rem;font-weight:700;">{html_escape(day.get('priority',''))}</span>
                </div>
                <p style="color:#64748B;font-size:0.78rem;margin:2px 0;line-height:1.4;">{html_escape(day.get('task',''))}</p>
                <p style="color:#334155;font-size:0.7rem;margin:0;">⏱ {html_escape(day.get('duration','30 min'))}</p>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q&A ANALYSIS ──────────────────────────────────────────────────────────
    with st.expander("📋  View Full Question-by-Question Analysis", expanded=False):
        for q_data, q_label, border_c in [
            (q1, "Q1 — Communication & HR", "#16A34A"),
            (q2, "Q2 — Technical & Role-Specific", "#4ADE80"),
        ]:
            fb = q_data.get("feedback", {})
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                        border-left:4px solid {border_c};border-radius:14px;padding:1.2rem;margin-bottom:1rem;">
              <p style="color:{border_c};font-weight:700;font-size:0.82rem;margin:0 0 0.4rem;">{html_escape(q_label)}</p>
              <p style="color:#FFFFFF;font-size:0.95rem;font-weight:500;margin:0 0 0.75rem;line-height:1.6;">{html_escape(q_data.get('text',''))}</p>
              <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:0.7rem;margin-bottom:0.75rem;">
                <p style="color:#777777;font-size:0.68rem;font-weight:700;text-transform:uppercase;margin:0 0 0.25rem;">Your Answer</p>
                <p style="color:#CBD5E1;font-size:0.83rem;margin:0;line-height:1.5;">{html_escape(q_data.get('answer','—'))}</p>
              </div>
              <p style="color:#B5B5B5;font-size:0.83rem;line-height:1.6;margin:0 0 0.75rem;">{html_escape(fb.get('ai_feedback','')[:320])}</p>
            </div>""", unsafe_allow_html=True)
            sc_cols = st.columns(5)
            for col, (lname, val, clr) in zip(sc_cols, [
                ("Overall",fb.get("overall_score",0),"#16A34A"),
                ("Confidence",fb.get("confidence_score",0),"#4ADE80"),
                ("Communication",fb.get("communication_score",0),"#10B981"),
                ("Technical",fb.get("technical_score",0),"#3B82F6"),
                ("Grammar",fb.get("grammar_score",0),"#F59E0B"),
            ]):
                with col:
                    st.markdown(f'<div style="text-align:center;padding:0.4rem;"><p style="color:{clr};font-size:1.2rem;font-weight:900;margin:0;">{val:.0f}</p><p style="color:#777777;font-size:0.67rem;margin:0;">{lname}</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CTAs ──────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄  Retake Scan", key="rr_retake", use_container_width=True):
            for k in ["scan_step","scan_resume_text","scan_ats","scan_skills",
                      "scan_missing","scan_session","scan_q1","scan_q2","scan_report"]:
                st.session_state.pop(k, None)
            st.session_state["scan_step"] = 1
            st.session_state["page"] = "quick_scan"
            st.rerun()
    with c2:
        st.markdown('<div class="cta-glow">', unsafe_allow_html=True)
        if st.button("🎯  Start Full AI Interview", key="rr_full", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        if st.button("📊  View Dashboard", key="rr_dash", use_container_width=True):
            st.session_state["page"] = "dashboard"
            st.rerun()
