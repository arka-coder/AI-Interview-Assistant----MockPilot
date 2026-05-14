"""
MockPilot AI — Redesigned Hackathon Landing Page
2-Minute Interview Readiness Engine · Dark futuristic UI.
"""
import streamlit as st
from frontend.components.ui_components import inject_css

LANDING_CSS = """
<style>
@keyframes float {
  0%,100% { transform:translateY(0px); }
  50%      { transform:translateY(-12px); }
}
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.hero-badge {
  display:inline-flex;align-items:center;gap:0.5rem;
  background:rgba(124,58,237,0.15);border:1px solid rgba(168,85,247,0.4);
  border-radius:99px;padding:6px 20px;margin-bottom:1.5rem;
  animation:aiPulse 3s ease-in-out infinite;
}
.hero-title {
  font-size:clamp(2.6rem,6.5vw,5rem);font-weight:900;line-height:1.03;
  margin:0 auto 1.2rem;max-width:860px;letter-spacing:-2px;
}
.hero-sub {
  font-size:1.1rem;color:#94A3B8;max-width:560px;
  margin:0 auto 2.5rem;line-height:1.75;text-align:center;
}
.cta-primary {
  background:linear-gradient(135deg,#7C3AED,#6D28D9);
  border:1px solid rgba(168,85,247,0.5);
  color:#fff;font-weight:700;font-size:1rem;
  padding:0.85rem 2rem;border-radius:14px;
  cursor:pointer;transition:all 0.3s ease;width:100%;
  box-shadow:0 0 24px rgba(124,58,237,0.35);
}
.cta-primary:hover {
  transform:translateY(-3px);
  box-shadow:0 0 40px rgba(124,58,237,0.55);
}
.cta-secondary {
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.12);
  color:#94A3B8;font-weight:600;font-size:0.9rem;
  padding:0.85rem 2rem;border-radius:14px;
  cursor:pointer;transition:all 0.3s ease;width:100%;
}
.cta-secondary:hover {
  border-color:rgba(34,211,238,0.4);color:#22D3EE;
  background:rgba(34,211,238,0.06);transform:translateY(-2px);
}
.stat-pill {
  display:inline-flex;align-items:center;gap:0.4rem;
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
  border-radius:99px;padding:6px 16px;
  font-size:0.8rem;color:#94A3B8;font-weight:500;margin:4px;
}
.mode-card {
  background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
  border-radius:24px;padding:2rem;height:100%;
  transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
  position:relative;overflow:hidden;
}
.mode-card::before {
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  transform:scaleX(0);transform-origin:left;transition:transform 0.4s ease;
}
.mode-card.primary::before { background:linear-gradient(90deg,#7C3AED,#A855F7,#22D3EE); }
.mode-card.secondary::before { background:linear-gradient(90deg,#22D3EE,#3B82F6); }
.mode-card:hover { transform:translateY(-8px); }
.mode-card.primary:hover { border-color:rgba(168,85,247,0.4);box-shadow:0 24px 60px rgba(124,58,237,0.25); }
.mode-card.secondary:hover { border-color:rgba(34,211,238,0.3);box-shadow:0 24px 60px rgba(34,211,238,0.15); }
.mode-card:hover::before { transform:scaleX(1); }
.mode-badge {
  display:inline-flex;align-items:center;gap:0.4rem;
  border-radius:99px;padding:4px 14px;font-size:0.72rem;font-weight:700;
  letter-spacing:0.5px;margin-bottom:1.2rem;
}
.feat-card {
  background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
  border-radius:18px;padding:1.4rem;height:100%;
  transition:all 0.3s ease;
}
.feat-card:hover {
  border-color:rgba(168,85,247,0.3);
  transform:translateY(-5px);
  box-shadow:0 16px 40px rgba(124,58,237,0.18);
}
.step-connector {
  display:flex;align-items:center;justify-content:center;
  color:rgba(124,58,237,0.4);font-size:1.5rem;
}
.flow-step {
  background:rgba(255,255,255,0.03);border:1px solid rgba(124,58,237,0.2);
  border-radius:18px;padding:1.5rem;text-align:center;
  position:relative;
}
.flow-step-num {
  width:44px;height:44px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:1rem;font-weight:900;color:#fff;margin:0 auto 1rem;
}
.cta-banner {
  background:linear-gradient(135deg,rgba(124,58,237,0.18),rgba(34,211,238,0.08));
  border:1px solid rgba(124,58,237,0.3);border-radius:28px;
  padding:3rem 2rem;text-align:center;position:relative;overflow:hidden;
}
</style>
"""


def render():
    inject_css()
    st.markdown(LANDING_CSS, unsafe_allow_html=True)

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:4rem 1rem 1.5rem;position:relative;">

      <div class="hero-badge fade-in">
        <span style="width:7px;height:7px;border-radius:50%;background:#A855F7;
                     animation:aiPulse 2s infinite;display:inline-block;"></span>
        <span style="color:#A855F7;font-size:0.75rem;font-weight:700;letter-spacing:0.5px;">
          AI-POWERED · 2-MINUTE READINESS ENGINE
        </span>
      </div>

      <div class="hero-title fade-in-up" style="text-align:center;">
        <span style="background:linear-gradient(135deg,#F1F5F9 20%,#A855F7 55%,#22D3EE);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     background-clip:text;display:block;">
          Know if you're interview ready
        </span>
        <span style="background:linear-gradient(135deg,#A855F7 0%,#22D3EE 100%);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     background-clip:text;font-size:0.62em;display:block;margin-top:0.1em;">
          in under 2 minutes.
        </span>
      </div>

      <p class="hero-sub fade-in" style="text-align:center !important;margin-left:auto;margin-right:auto;">
        AI-powered readiness analysis using resume intelligence, communication scoring,
        ATS evaluation, and adaptive AI interviews — all in one platform.
      </p>

      <div style="display:flex;justify-content:center;gap:0.6rem;flex-wrap:wrap;margin-bottom:2.5rem;">
        <span class="stat-pill">⚡ 2-Min Readiness Score</span>
        <span class="stat-pill">🎙️ Voice Recognition</span>
        <span class="stat-pill">📄 ATS Resume Analysis</span>
        <span class="stat-pill">🤖 Groq LLaMA AI</span>
        <span class="stat-pill">📊 6-Dimension Scoring</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Primary + Secondary CTAs
    _, c1, gap, c2, _ = st.columns([0.8, 1.3, 0.3, 1.3, 0.8])
    with c1:
        if st.button("⚡  Start Quick Readiness Scan", key="hero_cta_primary", use_container_width=True):
            st.session_state["page"] = "quick_scan"
            st.rerun()
    with c2:
        if st.button("🎯  Try Full AI Interview", key="hero_cta_secondary", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── TWO MODES ─────────────────────────────────────────────────────────────
    st.markdown("""
    <h2 style="text-align:center;font-size:1.9rem;font-weight:900;margin-bottom:0.5rem;
               background:linear-gradient(135deg,#F1F5F9 40%,#A855F7);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
      Choose Your Experience
    </h2>
    <p style="text-align:center;color:#64748B;margin-bottom:2rem;font-size:0.9rem;">
      Two powerful modes built for every stage of your interview journey
    </p>""", unsafe_allow_html=True)

    mode1, mode2 = st.columns(2)

    with mode1:
        st.markdown("""
        <div class="mode-card primary">
          <div class="mode-badge" style="background:rgba(168,85,247,0.15);
               border:1px solid rgba(168,85,247,0.4);color:#A855F7;">
            ⚡ PRIMARY FEATURE
          </div>
          <div style="font-size:2.5rem;margin-bottom:0.75rem;
               animation:float 3s ease-in-out infinite;">🎯</div>
          <h3 style="font-size:1.4rem;font-weight:900;color:#F1F5F9;margin:0 0 0.5rem;">
            Quick Readiness Scan
          </h3>
          <p style="color:#A855F7;font-weight:700;font-size:0.88rem;margin:0 0 1rem;">
            Under 2 minutes · Instant results
          </p>
          <p style="color:#94A3B8;font-size:0.87rem;line-height:1.65;margin:0 0 1.5rem;">
            Upload your resume, answer 2 targeted AI questions, and receive your
            <strong style="color:#F1F5F9;">Interview Readiness Score</strong> with
            AI hiring insights and a personalized 7-day improvement plan.
          </p>
          <div style="display:flex;flex-direction:column;gap:0.4rem;margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#10B981;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">Resume ATS analysis</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#10B981;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">2 personalized AI questions</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#10B981;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">6-dimension readiness score</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#10B981;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">AI hiring insights + recruiter verdict</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#10B981;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">7-day improvement roadmap</span>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("⚡  Start Quick Readiness Scan", key="mode1_cta", use_container_width=True):
            st.session_state["page"] = "quick_scan"
            st.rerun()

    with mode2:
        st.markdown("""
        <div class="mode-card secondary">
          <div class="mode-badge" style="background:rgba(34,211,238,0.1);
               border:1px solid rgba(34,211,238,0.3);color:#22D3EE;">
            🏆 ADVANCED FEATURE
          </div>
          <div style="font-size:2.5rem;margin-bottom:0.75rem;
               animation:float 3.5s ease-in-out infinite;">🤖</div>
          <h3 style="font-size:1.4rem;font-weight:900;color:#F1F5F9;margin:0 0 0.5rem;">
            Full AI Mock Interview
          </h3>
          <p style="color:#22D3EE;font-weight:700;font-size:0.88rem;margin:0 0 1rem;">
            Up to 10 questions · Deep analysis
          </p>
          <p style="color:#94A3B8;font-size:0.87rem;line-height:1.65;margin:0 0 1.5rem;">
            Experience a complete AI-powered mock interview with adaptive follow-ups,
            real-time scoring, voice mode, and a comprehensive performance report.
          </p>
          <div style="display:flex;flex-direction:column;gap:0.4rem;margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#22D3EE;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">Adaptive 10-question flow</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#22D3EE;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">Contextual follow-up questions</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#22D3EE;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">Live voice mode (Groq Whisper)</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#22D3EE;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">Question-by-question AI coaching</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <span style="color:#22D3EE;font-size:0.85rem;">✓</span>
              <span style="color:#94A3B8;font-size:0.82rem;">Historical analytics & progress tracking</span>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🎯  Start Full AI Interview", key="mode2_cta", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── HOW QUICK SCAN WORKS ──────────────────────────────────────────────────
    st.markdown("""
    <h2 style="text-align:center;font-size:1.8rem;font-weight:900;margin-bottom:0.5rem;
               background:linear-gradient(135deg,#F1F5F9,#22D3EE);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
      Quick Scan in 3 Steps
    </h2>
    <p style="text-align:center;color:#64748B;margin-bottom:2rem;font-size:0.88rem;">
      Complete your readiness assessment in under 2 minutes
    </p>""", unsafe_allow_html=True)

    s1, arr1, s2, arr2, s3 = st.columns([1, 0.2, 1, 0.2, 1])
    flow_steps = [
        (s1, "1", "#7C3AED", "📄", "Upload Resume", "PDF/DOCX/TXT analysis for ATS scoring and skill detection"),
        (s2, "2", "#A855F7", "🎯", "Select Role", "Choose your target role, level, and interview type"),
        (s3, "3", "#22D3EE", "⚡", "2 AI Questions", "Answer 2 personalized questions, get instant readiness score"),
    ]
    for col, num, color, icon, title, desc in flow_steps:
        with col:
            st.markdown(f"""
            <div class="flow-step">
              <div class="flow-step-num" style="background:linear-gradient(135deg,{color},{color}99);
                   box-shadow:0 0 20px {color}44;">{num}</div>
              <div style="font-size:1.8rem;margin-bottom:0.5rem;">{icon}</div>
              <h4 style="color:#F1F5F9;font-weight:700;font-size:0.95rem;margin:0 0 0.4rem;">{title}</h4>
              <p style="color:#64748B;font-size:0.8rem;margin:0;line-height:1.5;">{desc}</p>
            </div>""", unsafe_allow_html=True)
    for col in [arr1, arr2]:
        with col:
            st.markdown('<div class="step-connector" style="height:100%;display:flex;align-items:center;padding-top:3rem;">→</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── FEATURES GRID ─────────────────────────────────────────────────────────
    st.markdown("""
    <h2 style="text-align:center;font-size:1.8rem;font-weight:900;margin-bottom:0.4rem;
               background:linear-gradient(135deg,#F1F5F9 40%,#A855F7);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
      Everything Built In
    </h2>
    <p style="text-align:center;color:#64748B;margin-bottom:2rem;font-size:0.88rem;">
      Production-grade AI tools for serious interview preparation
    </p>""", unsafe_allow_html=True)

    features = [
        ("🎯", "#7C3AED", "Readiness Score",     "Composite score across 6 dimensions: resume, communication, technical, confidence, ATS, and grammar."),
        ("🧠", "#A855F7", "AI Hiring Insights",  "Simulated recruiter perspective: shortlist probability, strong signals, and hiring risks."),
        ("🗓️", "#22D3EE", "7-Day Roadmap",       "AI-generated personalized daily action plan to close your readiness gaps before the interview."),
        ("📄", "#10B981", "ATS Intelligence",    "Upload any resume and instantly see ATS score, matched/missing keywords, and fix suggestions."),
        ("🎙️", "#F59E0B", "Voice Interviews",    "Speak your answers naturally. Groq Whisper transcribes instantly with high accuracy."),
        ("📊", "#EF4444", "Deep Analytics",      "Track progress across sessions, see score trends, and discover strengths and weak areas."),
    ]
    r1, r2 = st.columns(3), st.columns(3)
    for i, (icon, color, title, desc) in enumerate(features):
        col = r1[i] if i < 3 else r2[i - 3]
        with col:
            st.markdown(f"""
            <div class="feat-card fade-in-up" style="margin-bottom:1rem;">
              <div style="width:42px;height:42px;border-radius:13px;
                          background:{color}15;border:1px solid {color}30;
                          display:flex;align-items:center;justify-content:center;
                          font-size:1.2rem;margin-bottom:0.75rem;">{icon}</div>
              <h4 style="font-size:0.92rem;font-weight:700;color:#F1F5F9;margin:0 0 0.35rem;">{title}</h4>
              <p style="color:#64748B;font-size:0.8rem;margin:0;line-height:1.6;">{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CTA Banner ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="cta-banner">
      <div style="display:inline-flex;align-items:center;gap:0.5rem;
           background:rgba(124,58,237,0.15);border:1px solid rgba(168,85,247,0.3);
           border-radius:99px;padding:4px 16px;margin-bottom:1.2rem;">
        <span style="width:6px;height:6px;border-radius:50%;background:#A855F7;
                     animation:aiPulse 2s infinite;display:inline-block;"></span>
        <span style="color:#A855F7;font-size:0.72rem;font-weight:700;letter-spacing:0.5px;">
          FREE · NO SETUP · INSTANT RESULTS
        </span>
      </div>
      <h2 style="font-size:2rem;font-weight:900;color:#F1F5F9;margin:0 0 0.5rem;">
        Ready to know your interview score?
      </h2>
      <p style="color:#94A3B8;margin:0 0 0.5rem;font-size:0.92rem;">
        Join thousands of candidates who got interview-ready with MockPilot AI.
      </p>
    </div>""", unsafe_allow_html=True)

    _, btn1, gap, btn2, _ = st.columns([0.8, 1.2, 0.3, 1.2, 0.8])
    with btn1:
        if st.button("⚡  Get My Readiness Score", key="cta_bottom_primary", use_container_width=True):
            st.session_state["page"] = "quick_scan"
            st.rerun()
    with btn2:
        if st.button("🎯  Full Mock Interview →", key="cta_bottom_secondary", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()

    # ── Footer
    st.markdown("""<br><hr>
    <div style="text-align:center;padding:1.5rem 0;">
      <p style="background:linear-gradient(135deg,#A855F7,#22D3EE);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;font-weight:900;font-size:1.1rem;margin:0 0 0.3rem;">
        MockPilot AI
      </p>
      <p style="color:#475569;font-size:0.75rem;margin:0;">
        2-Minute Interview Readiness Engine · Powered by Groq LLaMA 3.3-70B &amp; Whisper
      </p>
    </div>""", unsafe_allow_html=True)
