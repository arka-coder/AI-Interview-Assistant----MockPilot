"""
MockPilot AI — Reusable UI Components
Inject CSS, render cards, score rings, charts, and HTML blocks.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os


# ── CSS Injection ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _load_css() -> str:
    """Read CSS from disk once and cache it."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            return f.read()
    return ""


def inject_css():
    """Inject the cached global stylesheet."""
    css = _load_css()
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)



# ── Typography ────────────────────────────────────────────────────────────────

def hero_title(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="fade-in-up" style="text-align:center;padding:2rem 0 1rem;">
      <h1 style="font-size:3rem;font-weight:800;
                 background:linear-gradient(135deg,#A855F7,#22D3EE);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 background-clip:text;margin:0;line-height:1.1;">
        {title}
      </h1>
      {f'<p style="color:#94A3B8;font-size:1.15rem;margin-top:0.75rem;">{subtitle}</p>' if subtitle else ''}
    </div>""", unsafe_allow_html=True)


def section_header(text: str, icon: str = ""):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1.2rem;">
      <span style="font-size:1.3rem;">{icon}</span>
      <h2 style="font-size:1.4rem;font-weight:700;
                 background:linear-gradient(135deg,#A855F7,#22D3EE);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 background-clip:text;margin:0;">{text}</h2>
    </div>""", unsafe_allow_html=True)


def badge(text: str, color: str = "#7C3AED"):
    st.markdown(f"""
    <span style="background:{color}22;color:{color};border:1px solid {color}44;
                 border-radius:99px;padding:2px 12px;font-size:0.78rem;font-weight:600;">
      {text}
    </span>""", unsafe_allow_html=True)


# ── Cards ─────────────────────────────────────────────────────────────────────

def metric_card(label: str, value: str, delta: str = "", icon: str = ""):
    delta_html = ""
    if delta:
        color = "#10B981" if not delta.startswith("-") else "#EF4444"
        arrow = "↑" if not delta.startswith("-") else "↓"
        delta_html = f'<p style="color:{color};font-size:0.8rem;margin:4px 0 0;">{arrow} {delta}</p>'
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
      <div style="font-size:1.8rem;">{icon}</div>
      <p style="color:#94A3B8;font-size:0.8rem;margin:6px 0 4px;font-weight:500;
                text-transform:uppercase;letter-spacing:0.5px;">{label}</p>
      <h3 style="font-size:1.9rem;font-weight:800;
                 background:linear-gradient(135deg,#A855F7,#22D3EE);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 background-clip:text;margin:0;">{value}</h3>
      {delta_html}
    </div>""", unsafe_allow_html=True)


def feature_card(icon: str, title: str, desc: str):
    st.markdown(f"""
    <div class="glass-card fade-in-up"
         style="border-top:3px solid #7C3AED;">
      <div style="font-size:2.2rem;margin-bottom:0.6rem;">{icon}</div>
      <h3 style="font-size:1.05rem;font-weight:700;color:#F1F5F9;margin:0 0 0.5rem;">{title}</h3>
      <p style="color:#94A3B8;font-size:0.88rem;margin:0;line-height:1.6;">{desc}</p>
    </div>""", unsafe_allow_html=True)


def score_card(label: str, score: float, color: str = "#7C3AED"):
    pct = max(0, min(100, score))
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
      <p style="color:#94A3B8;font-size:0.78rem;margin:0 0 0.5rem;
                text-transform:uppercase;letter-spacing:0.5px;">{label}</p>
      <div style="position:relative;display:inline-block;">
        <svg width="90" height="90" viewBox="0 0 90 90">
          <circle cx="45" cy="45" r="36" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
          <circle cx="45" cy="45" r="36" fill="none" stroke="{color}" stroke-width="8"
                  stroke-dasharray="{2*3.14159*36}" stroke-dashoffset="{2*3.14159*36*(1-pct/100)}"
                  stroke-linecap="round" transform="rotate(-90 45 45)"
                  style="transition:stroke-dashoffset 1s ease;"/>
        </svg>
        <span style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                     font-size:1.1rem;font-weight:800;color:{color};">{pct:.0f}</span>
      </div>
    </div>""", unsafe_allow_html=True)


def info_card(title: str, content: str, icon: str = "💡", border_color: str = "#7C3AED"):
    st.markdown(f"""
    <div class="glass-card" style="border-left:3px solid {border_color};">
      <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
        <span style="font-size:1.2rem;">{icon}</span>
        <h4 style="font-size:0.95rem;font-weight:700;color:#F1F5F9;margin:0;">{title}</h4>
      </div>
      <p style="color:#CBD5E1;font-size:0.88rem;margin:0;line-height:1.65;">{content}</p>
    </div>""", unsafe_allow_html=True)


def list_card(title: str, items: list, icon: str = "✅", color: str = "#10B981"):
    items_html = "".join([
        f'<li style="color:#CBD5E1;font-size:0.88rem;margin-bottom:0.35rem;">'
        f'<span style="color:{color};">{icon}</span> {item}</li>'
        for item in items
    ])
    st.markdown(f"""
    <div class="glass-card">
      <h4 style="font-size:0.95rem;font-weight:700;color:#F1F5F9;margin:0 0 0.8rem;">{title}</h4>
      <ul style="margin:0;padding-left:0;list-style:none;">{items_html}</ul>
    </div>""", unsafe_allow_html=True)


# ── Charts ────────────────────────────────────────────────────────────────────

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Outfit, Inter, sans-serif", color="#94A3B8"),
    margin=dict(l=10, r=10, t=30, b=10),
)


def radar_chart(categories: list, values: list, title: str = "Skill Breakdown"):
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        line=dict(color="#A855F7", width=2),
        fillcolor='rgba(124,58,237,0.18)',
        marker=dict(color="#A855F7", size=6),
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=title, font=dict(size=14, color="#F1F5F9")),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="rgba(255,255,255,0.06)",
                            color="#475569"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#94A3B8"),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def line_chart(dates: list, scores: list, title: str = "Score Progress"):
    fig = go.Figure(go.Scatter(
        x=dates, y=scores, mode='lines+markers',
        line=dict(color="#A855F7", width=3, shape="spline"),
        marker=dict(color="#22D3EE", size=8, line=dict(color="#A855F7", width=2)),
        fill='tozeroy',
        fillcolor='rgba(124,58,237,0.08)',
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=title, font=dict(size=14, color="#F1F5F9")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", range=[0, 105]),
    )
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(labels: list, values: list, title: str = "Scores"):
    colors = ["#7C3AED" if v >= 75 else "#F59E0B" if v >= 50 else "#EF4444" for v in values]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=colors, cornerradius=6),
        text=[f"{v:.0f}" for v in values],
        textposition='outside',
        textfont=dict(color="#94A3B8", size=12),
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=title, font=dict(size=14, color="#F1F5F9")),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", range=[0, 115]),
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Interview Room Components ─────────────────────────────────────────────────

def ai_avatar(thinking: bool = False):
    pulse = "pulse" if thinking else ""
    label = "Thinking..." if thinking else "AI Interviewer"
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:0.6rem;">
      <div class="{pulse}" style="width:80px;height:80px;border-radius:50%;
                   background:linear-gradient(135deg,#7C3AED,#22D3EE);
                   display:flex;align-items:center;justify-content:center;
                   font-size:2rem;box-shadow:0 0 30px rgba(124,58,237,0.4);
                   position:relative;">
        🤖
        <div style="position:absolute;bottom:4px;right:4px;
                    width:14px;height:14px;border-radius:50%;
                    background:{'#F59E0B' if thinking else '#10B981'};
                    border:2px solid #07070F;"></div>
      </div>
      <p style="color:#94A3B8;font-size:0.8rem;margin:0;">{label}</p>
    </div>""", unsafe_allow_html=True)


def question_display(text: str, q_num: int, total: int):
    st.markdown(f"""
    <div class="glass-card glow-anim" style="border-top:3px solid #7C3AED;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <span style="background:rgba(124,58,237,0.2);color:#A855F7;
                     border-radius:99px;padding:3px 14px;font-size:0.8rem;font-weight:600;
                     border:1px solid rgba(124,58,237,0.3);">
          Question {q_num} of {total}
        </span>
        <div style="height:6px;flex:1;margin:0 1rem;
                    background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">
          <div style="height:100%;width:{int(q_num/total*100)}%;
                      background:linear-gradient(90deg,#7C3AED,#22D3EE);
                      border-radius:99px;transition:width 0.5s ease;"></div>
        </div>
      </div>
      <p style="font-size:1.15rem;font-weight:500;color:#F1F5F9;
                line-height:1.7;margin:0;">{text}</p>
    </div>""", unsafe_allow_html=True)


def timer_display(seconds: int):
    mins = seconds // 60
    secs = seconds % 60
    color = "#10B981" if seconds > 60 else "#F59E0B" if seconds > 30 else "#EF4444"
    st.markdown(f"""
    <div style="text-align:center;">
      <span style="font-size:2rem;font-weight:800;color:{color};
                   font-variant-numeric:tabular-nums;letter-spacing:2px;">
        {mins:02d}:{secs:02d}
      </span>
    </div>""", unsafe_allow_html=True)


def mic_visualizer(active: bool = False):
    bars = "".join([
        f'<div style="width:4px;height:{h}px;background:{"#A855F7" if active else "#475569"};'
        f'border-radius:2px;animation:{"pulse" if active else "none"} {0.3+i*0.1:.1f}s ease-in-out infinite alternate;"></div>'
        for i, h in enumerate([14, 22, 30, 22, 38, 22, 30, 22, 14])
    ])
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;gap:4px;
                height:50px;background:rgba(255,255,255,0.03);
                border-radius:12px;border:1px solid rgba(255,255,255,0.07);">
      {bars}
    </div>""", unsafe_allow_html=True)


# ── Loaders ───────────────────────────────────────────────────────────────────

def thinking_loader(text: str = "AI is thinking..."):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;
                background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.2);
                border-radius:12px;padding:1rem 1.5rem;">
      <div style="width:20px;height:20px;border-radius:50%;
                  border:3px solid transparent;
                  border-top-color:#A855F7;
                  animation:spin 0.8s linear infinite;"></div>
      <p style="color:#A855F7;margin:0;font-size:0.95rem;">{text}</p>
    </div>""", unsafe_allow_html=True)


# ── Session State Helpers ─────────────────────────────────────────────────────

def is_logged_in() -> bool:
    return bool(st.session_state.get("token") and st.session_state.get("user"))


def require_auth():
    """Redirect to auth page if not logged in."""
    if not is_logged_in():
        st.session_state["page"] = "auth"
        st.rerun()
