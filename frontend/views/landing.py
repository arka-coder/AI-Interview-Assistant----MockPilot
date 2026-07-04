"""
MockPilot AI — Premium Landing Page
Linear · Vercel · Stripe · Arc aesthetic
"""
import streamlit as st
from frontend.components.ui_components import inject_css

LANDING_CSS = """
<style>
/* ── Landing-specific styles ── */
@keyframes meshShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes gradientText {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes orbFloat {
  0%, 100% { transform: translateY(0px) rotate(0deg) scale(1); }
  33%  { transform: translateY(-20px) rotate(1deg) scale(1.02); }
  66%  { transform: translateY(-10px) rotate(-0.5deg) scale(0.99); }
}
@keyframes conicSpin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes barWave {
  0%, 100% { height: 8px; }
  50%       { height: 28px; }
}
@keyframes countIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Hero wrapper */
.hero-wrapper {
  position: relative;
  padding: 3.5rem 0 2rem;
}
.hero-glow-1 {
  position: absolute; top: -20%; left: -10%;
  width: 600px; height: 600px; border-radius: 50%;
  background: radial-gradient(circle, rgba(34,197,94,0.12), transparent 65%);
  filter: blur(80px); pointer-events: none; z-index: 0;
}
.hero-glow-2 {
  position: absolute; top: 10%; right: -5%;
  width: 400px; height: 400px; border-radius: 50%;
  background: radial-gradient(circle, rgba(22,163,74,0.08), transparent 65%);
  filter: blur(60px); pointer-events: none; z-index: 0;
}

/* Hero title */
.hero-title {
  font-family: 'Outfit', sans-serif;
  font-size: clamp(2.8rem, 6.5vw, 4.8rem);
  font-weight: 900;
  line-height: 1.04;
  letter-spacing: -0.04em;
  margin: 0 0 1.25rem;
  color: #FFFFFF;
  position: relative; z-index: 1;
}
.hero-title-accent {
  background: linear-gradient(135deg, #86EFAC 0%, #22C55E 40%, #16A34A 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientText 5s linear infinite;
}

/* Hero subtitle */
.hero-sub {
  font-family: 'Inter', sans-serif;
  font-size: 1.1rem;
  color: #B5B5B5;
  max-width: 520px;
  line-height: 1.8;
  margin: 0 0 2.25rem;
  font-weight: 400;
  position: relative; z-index: 1;
}

/* Stats strip */
.stats-strip {
  display: flex;
  gap: 2rem;
  margin-top: 2rem;
  position: relative; z-index: 1;
}
.stat-item {
  display: flex; flex-direction: column; gap: 2px;
}
.stat-value {
  font-family: 'Outfit', sans-serif;
  font-size: 1.5rem; font-weight: 800;
  color: #FFFFFF; letter-spacing: -0.03em;
  animation: countIn 0.5s ease both;
}
.stat-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem; font-weight: 500;
  color: #777777; letter-spacing: 0.02em;
  text-transform: uppercase;
}

/* Hero visual / floating card */
.hero-visual {
  background: linear-gradient(160deg, rgba(28,28,32,0.9), rgba(18,18,21,0.95));
  backdrop-filter: blur(32px);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.04) inset,
    0 40px 80px rgba(0,0,0,0.5),
    0 0 60px rgba(34,197,94,0.15);
  border-radius: 32px;
  padding: 2.5rem 2rem;
  display: flex; flex-direction: column; align-items: center;
  animation: orbFloat 8s ease-in-out infinite;
  position: relative; overflow: hidden; margin-top: 1rem;
}
.hero-visual::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34,197,94,0.5), rgba(22,163,74,0.3), transparent);
}

/* Neural orb in hero */
.hero-orb {
  width: 180px; height: 180px; border-radius: 50%;
  background: conic-gradient(from 0deg, transparent, #22C55E, #16A34A, transparent);
  animation: conicSpin 5s linear infinite;
  display: flex; align-items: center; justify-content: center;
  position: relative; margin-bottom: 1.5rem;
  filter: drop-shadow(0 0 0 1px rgba(34,197,94,0.20));
}
.hero-orb::before {
  content: ''; position: absolute; inset: 6px;
  background: radial-gradient(circle at 35% 35%, #1C1C2E, #090B09);
  border-radius: 50%;
}
.hero-orb-inner {
  position: relative; z-index: 1;
  display: flex; flex-direction: column; align-items: center;
}
.hero-orb-val {
  font-family: 'Outfit', sans-serif;
  font-size: 2.8rem; font-weight: 900;
  color: #86EFAC; line-height: 1;
  letter-spacing: -0.04em;
}
.hero-orb-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.62rem; font-weight: 700;
  letter-spacing: 0.2em; color: #B5B5B5;
  text-transform: uppercase; margin-top: 4px;
}

/* Waveform bars */
.hero-waveform {
  display: flex; align-items: center; gap: 4px; height: 40px; margin-bottom: 0.75rem;
}
.hero-wave-bar {
  width: 4px; border-radius: 99px;
  background: linear-gradient(to top, #16A34A, #86EFAC);
  animation: barWave 1.2s ease-in-out infinite;
}

/* Feature bento card */
.bento-card {
  background: rgba(24,24,27,0.8);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 24px; padding: 2rem;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  height: 100%; position: relative; overflow: hidden;
}
.bento-card::after {
  content: ''; position: absolute; top: 0; right: 0; width: 100%; height: 100%;
  background: radial-gradient(circle at 80% 20%, rgba(34,197,94,0.06), transparent 55%);
  pointer-events: none;
}
.bento-card:hover {
  border-color: rgba(34,197,94,0.2);
  transform: translateY(-5px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 40px rgba(34,197,94,0.12);
}
.bento-icon {
  width: 48px; height: 48px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; margin-bottom: 1.1rem;
  border: 1px solid rgba(255,255,255,0.08);
}

/* How it works steps */
.step-card {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.85rem; position: relative; z-index: 1; text-align: center;
}
.step-num {
  width: 64px; height: 64px; border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Outfit', sans-serif;
  font-size: 1.5rem; font-weight: 900;
}

/* CTA Banner */
.cta-banner {
  background: rgba(18,18,21,0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 28px;
  padding: 4rem 2rem;
  text-align: center;
  position: relative; overflow: hidden;
}
.cta-banner::before {
  content: '';
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 60% 80% at 50% 120%, rgba(34,197,94,0.12), transparent),
    radial-gradient(ellipse 40% 40% at 50% -20%, rgba(22,163,74,0.08), transparent);
  pointer-events: none;
}
.cta-banner::after {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34,197,94,0.4), transparent);
}
</style>
"""

WAVEFORM_BARS = "".join([
    f'<div class="hero-wave-bar" style="height:{h}px;animation-delay:{d}s;"></div>'
    for h, d in [(12,0.1),(22,0.3),(16,0.2),(32,0.5),(20,0.15),(36,0.4),(14,0.25),(28,0.35),(18,0.1)]
])


def render():
    inject_css()
    st.markdown(LANDING_CSS, unsafe_allow_html=True)

    # ── HERO ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="hero-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="hero-glow-1"></div><div class="hero-glow-2"></div>', unsafe_allow_html=True)

    col_text, col_vis = st.columns([1.15, 0.85], gap="large")

    with col_text:
        st.markdown("""
        <div style="position:relative;z-index:1;">
          <div class="mp-badge reveal-1" style="margin-bottom:1.5rem;">
            <span class="ai-pulse"></span>
            Interview Readiness Suite
          </div>
          <h1 class="hero-title reveal-2">
            Walk Into Your Next<br>
            <span class="hero-title-accent">Interview Prepared</span>
          </h1>
          <p class="hero-sub reveal-3">
            MockPilot turns resumes, role targets, and practice answers into a focused
            readiness plan for high-stakes interviews.
          </p>
        </div>
        """, unsafe_allow_html=True)

        cta1, cta2 = st.columns(2, gap="small")
        with cta1:
            if st.button(":material/bolt: Start readiness scan", key="hero_cta_primary", use_container_width=True):
                st.session_state["page"] = "quick_scan"
                st.rerun()
        with cta2:
            if st.button(":material/play_arrow: Preview interview", key="hero_cta_secondary", use_container_width=True):
                st.session_state["page"] = "interview"
                st.rerun()

        st.markdown("""
        <div class="stats-strip reveal-4">
          <div class="stat-item">
            <div class="stat-value">98%</div>
            <div class="stat-label">Coaching signal</div>
          </div>
          <div style="width:1px;background:rgba(255,255,255,0.08);flex-shrink:0;"></div>
          <div class="stat-item">
            <div class="stat-value">2 min</div>
            <div class="stat-label">Quick readiness scan</div>
          </div>
          <div style="width:1px;background:rgba(255,255,255,0.08);flex-shrink:0;"></div>
          <div class="stat-item">
            <div class="stat-value">10+</div>
            <div class="stat-label">Role tracks</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_vis:
        st.markdown(f"""
        <div class="hero-visual">
          <div class="hero-orb">
            <div class="hero-orb-inner">
              <div class="hero-orb-val">82%</div>
              <div class="hero-orb-label">Clarity</div>
            </div>
          </div>
          <div class="hero-waveform">{WAVEFORM_BARS}</div>
          <p style="font-family:'Inter',sans-serif;font-size:0.8rem;color:#86EFAC;
                    font-style:italic;margin:0;text-align:center;letter-spacing:0.01em;">
            "Walk me through your most relevant project."
          </p>
          <div style="display:flex;gap:0.5rem;margin-top:1.25rem;flex-wrap:wrap;justify-content:center;">
            <span style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.25);
                         border-radius:99px;padding:3px 12px;font-size:0.7rem;font-weight:600;
                         font-family:'Inter',sans-serif;color:#6EE7B7;">
              Strong structure
            </span>
            <span style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);
                         border-radius:99px;padding:3px 12px;font-size:0.7rem;font-weight:600;
                         font-family:'Inter',sans-serif;color:#FCD34D;">
              Tighten pacing
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)

    # ── FEATURES BENTO GRID ──────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;margin-bottom:2.5rem;">
      <p style="font-family:'Inter',sans-serif;font-size:0.72rem;font-weight:700;
                letter-spacing:0.15em;text-transform:uppercase;color:#22C55E;margin:0 0 0.75rem;">
        Platform
      </p>
      <h2 style="font-family:'Outfit',sans-serif;font-size:2.25rem;font-weight:800;
                 color:#FFFFFF;letter-spacing:-0.03em;margin:0 0 0.75rem;line-height:1.2;">
        Preparation That Feels Like a Private Coach
      </h2>
      <p style="color:#B5B5B5;max-width:560px;margin:0 auto;font-size:0.95rem;line-height:1.8;">
        A focused workspace for resume intelligence, adaptive interview practice,
        and concrete next steps.
      </p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns([1.4, 1, 1], gap="medium")

    with f1:
        st.markdown("""
        <div class="bento-card" style="min-height:260px;">
          <div class="bento-icon" style="background:rgba(134,239,172,0.1);color:#86EFAC;border-color:rgba(134,239,172,0.2);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#9AF2BA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
          </div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.4rem;font-weight:700;
                     margin:0 0 0.75rem;letter-spacing:-0.02em;color:#FFFFFF;">AI Real-time Feedback</h3>
          <p style="color:#B5B5B5;font-size:0.9rem;line-height:1.75;margin:0;">
            Our neural engine analyzes your tone, word choice, and delivery
            in real-time, providing instant coaching during your session.
          </p>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="bento-card" style="min-height:260px;">
          <div class="bento-icon" style="background:rgba(103,232,249,0.1);color:#86EFAC;border-color:rgba(103,232,249,0.2);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#9AF2BA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
          </div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:700;
                     margin:0 0 0.75rem;color:#FFFFFF;">Realistic Simulations</h3>
          <p style="color:#B5B5B5;font-size:0.88rem;line-height:1.7;margin:0;">
            Practice against industry-specific AI personas for FAANG, Big Law, and Tier 1 Consulting.
          </p>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="bento-card" style="min-height:260px;">
          <div class="bento-icon" style="background:rgba(22,163,74,0.12);color:#16A34A;border-color:rgba(22,163,74,0.2);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#D6B971" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z"/></svg>
          </div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:700;
                     margin:0 0 0.75rem;color:#FFFFFF;">Personalized Question Banks</h3>
          <p style="color:#B5B5B5;font-size:0.88rem;line-height:1.7;margin:0;">
            Questions dynamically adapt to your background and career goals.
          </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    f4, f5 = st.columns([1, 2], gap="medium")

    with f4:
        st.markdown("""
        <div class="bento-card">
          <div class="bento-icon" style="background:rgba(103,232,249,0.1);color:#86EFAC;border-color:rgba(103,232,249,0.2);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#9AF2BA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/></svg>
          </div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:700;
                     margin:0 0 0.5rem;color:#FFFFFF;">Voice Mode</h3>
          <p style="color:#B5B5B5;font-size:0.85rem;line-height:1.7;margin:0;">
            Live speech recognition with Groq Whisper for a true interview feel.
          </p>
        </div>
        """, unsafe_allow_html=True)

    with f5:
        st.markdown("""
        <div class="bento-card" style="display:flex;align-items:center;justify-content:space-between;gap:2rem;">
          <div style="flex:1;">
            <h3 style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:700;
                       margin:0 0 0.5rem;color:#FFFFFF;">
              Neural Progress Tracking
            </h3>
            <p style="color:#B5B5B5;font-size:0.88rem;line-height:1.7;margin:0;">
              Visualize your growth with deep-dive analytics across 15+ soft and hard skill dimensions.
            </p>
          </div>
          <div style="display:flex;gap:6px;align-items:flex-end;flex-shrink:0;">
            <div style="width:16px;height:44px;background:rgba(134,239,172,0.08);border-radius:5px 5px 0 0;display:flex;flex-direction:column;justify-content:flex-end;">
              <div style="width:100%;height:40%;background:rgba(134,239,172,0.4);border-radius:5px 5px 0 0;box-shadow:0 0 10px rgba(134,239,172,0.3);"></div>
            </div>
            <div style="width:16px;height:64px;background:rgba(134,239,172,0.08);border-radius:5px 5px 0 0;display:flex;flex-direction:column;justify-content:flex-end;">
              <div style="width:100%;height:65%;background:rgba(134,239,172,0.55);border-radius:5px 5px 0 0;box-shadow:0 0 10px rgba(134,239,172,0.3);"></div>
            </div>
            <div style="width:16px;height:64px;background:rgba(134,239,172,0.08);border-radius:5px 5px 0 0;display:flex;flex-direction:column;justify-content:flex-end;">
              <div style="width:100%;height:88%;background:#86EFAC;border-radius:5px 5px 0 0;box-shadow:0 0 12px rgba(134,239,172,0.4);"></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)

    # ── HOW IT WORKS ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
                padding:4rem 2rem;border-radius:28px;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-30%;left:50%;transform:translateX(-50%);
                  width:50%;height:50%;border-radius:50%;
                  background:rgba(22,163,74,0.05);filter:blur(60px);pointer-events:none;"></div>
      <div style="text-align:center;margin-bottom:3rem;">
        <p style="font-family:'Inter',sans-serif;font-size:0.72rem;font-weight:700;
                  letter-spacing:0.15em;text-transform:uppercase;color:#16A34A;margin:0 0 0.75rem;">
          Process
        </p>
        <h2 style="font-family:'Outfit',sans-serif;font-size:2rem;font-weight:800;
                   color:#FFFFFF;margin:0;letter-spacing:-0.03em;">Your Path to a Sharper Interview</h2>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:2.5rem;max-width:860px;margin:0 auto;position:relative;">
        <div style="position:absolute;top:32px;left:18%;right:18%;height:1px;
                    background:linear-gradient(90deg,transparent,rgba(134,239,172,0.2),transparent);
                    pointer-events:none;"></div>
        <div class="step-card">
          <div class="step-num" style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.25);
               color:#86EFAC;box-shadow:0 0 30px rgba(34,197,94,0.2);">01</div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.15rem;font-weight:700;
                     margin:0 0 0.4rem;color:#FFFFFF;">Select Profile</h3>
          <p style="color:#B5B5B5;font-size:0.85rem;margin:0;line-height:1.7;">
            Define your role, company type, and seniority level.
          </p>
        </div>
        <div class="step-card">
          <div class="step-num" style="background:rgba(22,163,74,0.08);border:1px solid rgba(22,163,74,0.25);
               color:#86EFAC;">02</div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.15rem;font-weight:700;
                     margin:0 0 0.4rem;color:#FFFFFF;">AI Simulation</h3>
          <p style="color:#B5B5B5;font-size:0.85rem;margin:0;line-height:1.7;">
            Practice against adaptive questions with optional voice mode.
          </p>
        </div>
        <div class="step-card">
          <div class="step-num" style="background:rgba(22,163,74,0.1);border:1px solid rgba(22,163,74,0.25);
               color:#16A34A;">03</div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.15rem;font-weight:700;
                     margin:0 0 0.4rem;color:#FFFFFF;">Deep Analysis</h3>
          <p style="color:#B5B5B5;font-size:0.85rem;margin:0;line-height:1.7;">
            Receive a clear breakdown with the next actions to practice.
          </p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)

    # ── MODES SECTION ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
      <p style="font-family:'Inter',sans-serif;font-size:0.72rem;font-weight:700;
                letter-spacing:0.15em;text-transform:uppercase;color:#22C55E;margin:0 0 0.75rem;">
        Modes
      </p>
      <h2 style="font-family:'Outfit',sans-serif;font-size:2rem;font-weight:800;
                 color:#FFFFFF;margin:0 0 0.5rem;letter-spacing:-0.03em;">Choose Your Experience</h2>
      <p style="color:#B5B5B5;margin:0;">
        Two powerful modes built for every stage of your interview journey
      </p>
    </div>
    """, unsafe_allow_html=True)

    mode1, mode2 = st.columns(2, gap="medium")
    with mode1:
        st.markdown("""
        <div class="mode-card primary">
          <div style="display:inline-flex;align-items:center;gap:6px;
                      background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);
                      border-radius:99px;padding:4px 12px;margin-bottom:1.25rem;
                      font-family:'Inter',sans-serif;font-size:0.68rem;
                      font-weight:700;letter-spacing:0.06em;color:#16A34A;text-transform:uppercase;">
            Primary Workflow
          </div>
          <div class="mode-icon-svg"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#9AF2BA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.35rem;font-weight:800;
                     color:#FFFFFF;margin:0 0 0.4rem;letter-spacing:-0.02em;">Quick Readiness Scan</h3>
          <p style="color:#16A34A;font-weight:600;font-size:0.82rem;margin:0 0 0.85rem;">
            Under 2 minutes · Instant results
          </p>
          <p style="color:#B5B5B5;font-size:0.875rem;line-height:1.75;margin:0 0 1.5rem;flex:1;">
            Upload your resume, answer 2 targeted AI questions, and receive your
            <strong style="color:#FFFFFF;">Interview Readiness Score</strong> with
            AI hiring insights and a personalized 7-day improvement plan.
          </p>
          <div style="display:flex;flex-direction:column;gap:0.4rem;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="color:#10B981;font-size:0.85rem;">•</span>
              <span style="color:#B5B5B5;font-size:0.82rem;">Resume ATS analysis</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="color:#10B981;font-size:0.85rem;">•</span>
              <span style="color:#B5B5B5;font-size:0.82rem;">2 personalized AI questions</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="color:#10B981;font-size:0.85rem;">•</span>
              <span style="color:#B5B5B5;font-size:0.82rem;">6-dimension readiness score</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="color:#10B981;font-size:0.85rem;">•</span>
              <span style="color:#B5B5B5;font-size:0.82rem;">7-day improvement roadmap</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with mode2:
        st.markdown("""
        <div class="mode-card secondary">
          <div style="display:inline-flex;align-items:center;gap:6px;
                      background:rgba(22,163,74,0.08);border:1px solid rgba(22,163,74,0.25);
                      border-radius:99px;padding:4px 12px;margin-bottom:1.25rem;
                      font-family:'Inter',sans-serif;font-size:0.68rem;
                      font-weight:700;letter-spacing:0.06em;color:#16A34A;text-transform:uppercase;">
            Advanced Workflow
          </div>
          <div class="mode-icon-svg"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#D6B971" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg></div>
          <h3 style="font-family:'Outfit',sans-serif;font-size:1.35rem;font-weight:800;
                     color:#FFFFFF;margin:0 0 0.4rem;letter-spacing:-0.02em;">Full AI Mock Interview</h3>
          <p style="color:#86EFAC;font-weight:600;font-size:0.82rem;margin:0 0 0.85rem;">
            Up to 10 questions · Deep analysis
          </p>
          <p style="color:#B5B5B5;font-size:0.875rem;line-height:1.75;margin:0 0 1.5rem;flex:1;">
            Experience a complete AI-powered mock interview with adaptive follow-ups,
            real-time scoring, voice mode, and a comprehensive performance report.
          </p>
          <div style="display:flex;flex-direction:column;gap:0.4rem;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="color:#86EFAC;font-size:0.85rem;">•</span>
              <span style="color:#B5B5B5;font-size:0.82rem;">Adaptive 10-question flow</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="color:#86EFAC;font-size:0.85rem;">•</span>
              <span style="color:#B5B5B5;font-size:0.82rem;">Contextual follow-up questions</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="color:#86EFAC;font-size:0.85rem;">•</span>
              <span style="color:#B5B5B5;font-size:0.82rem;">Live voice mode (Groq Whisper)</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="color:#86EFAC;font-size:0.85rem;">•</span>
              <span style="color:#B5B5B5;font-size:0.82rem;">Historical analytics &amp; progress tracking</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    btn1, btn2 = st.columns(2, gap="medium")
    with btn1:
        if st.button(":material/bolt: Start quick readiness scan", key="mode1_cta", use_container_width=True):
            st.session_state["page"] = "quick_scan"
            st.rerun()
    with btn2:
        if st.button(":material/target: Start full interview", key="mode2_cta", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)

    # ── CTA BANNER ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="cta-banner">
      <div class="mp-badge" style="margin-bottom:1.5rem;display:inline-flex;">
        <span class="ai-pulse"></span>
        Free · No Setup · Instant Results
      </div>
      <h2 style="font-family:'Outfit',sans-serif;font-size:clamp(1.8rem,4vw,3rem);
                 font-weight:900;color:#FFFFFF;margin:0 0 1rem;letter-spacing:-0.04em;
                 position:relative;z-index:1;">
        Ready to practice with precision?
      </h2>
      <p style="color:#B5B5B5;font-size:1rem;max-width:520px;margin:0 auto 2rem;
                line-height:1.8;position:relative;z-index:1;">
        Run a readiness scan now, then move into a full interview when you want deeper feedback.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    _, cta_col, _ = st.columns([1, 2, 1])
    with cta_col:
        if st.button(":material/bolt: Start practicing now", key="cta_bottom_primary", use_container_width=True):
            st.session_state["page"] = "quick_scan"
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <br>
    <div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:1rem;padding-top:2rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
        <p style="font-family:'Inter',sans-serif;font-size:0.78rem;font-weight:500;
                  color:#777777;margin:0;">
          © 2026 MockPilot AI. Interview readiness, measured clearly.
        </p>
        <div style="display:flex;gap:1.5rem;">
          <a href="#" style="font-family:'Inter',sans-serif;font-size:0.78rem;font-weight:500;
                             color:#777777;text-decoration:none;transition:color 0.2s;"
             onmouseover="this.style.color='#B5B5B5'" onmouseout="this.style.color='#777777'">Terms</a>
          <a href="#" style="font-family:'Inter',sans-serif;font-size:0.78rem;font-weight:500;
                             color:#777777;text-decoration:none;"
             onmouseover="this.style.color='#B5B5B5'" onmouseout="this.style.color='#777777'">Privacy</a>
          <a href="#" style="font-family:'Inter',sans-serif;font-size:0.78rem;font-weight:500;
                             color:#777777;text-decoration:none;"
             onmouseover="this.style.color='#B5B5B5'" onmouseout="this.style.color='#777777'">Support</a>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
