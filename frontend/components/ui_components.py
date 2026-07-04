"""
MockPilot AI — Reusable UI Components
Inject CSS, render cards, score rings, charts, and HTML blocks.
"""
import streamlit as st
import plotly.graph_objects as go
import os
from html import escape


# ── CSS Injection ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _load_css(_mtime: float) -> str:
    """Read CSS from disk and refresh the cache when the file changes."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            return f.read()
    return ""


def inject_css():
    """Inject the cached global stylesheet."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "main.css")
    css = _load_css(os.path.getmtime(css_path) if os.path.exists(css_path) else 0)
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ── Chart Theme ───────────────────────────────────────────────────────────────

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Outfit, sans-serif", color="#B5B5B5", size=11),
    margin=dict(l=10, r=10, t=10, b=10),
)


def html_escape(value) -> str:
    """Escape dynamic text before placing it inside unsafe HTML blocks."""
    return escape("" if value is None else str(value), quote=True)


# ── Typography ────────────────────────────────────────────────────────────────

def hero_title(title: str, subtitle: str = ""):
    title = html_escape(title)
    subtitle = html_escape(subtitle)
    st.markdown(f"""
    <div class="fade-in-up" style="text-align:center;padding:2rem 0 1rem;">
      <h1 style="font-family:'Outfit',sans-serif;font-size:3.5rem;font-weight:800;
                 color:#FFFFFF;margin:0;line-height:1.05;letter-spacing:-0.045em;">
        {title}
      </h1>
      {f'<p style="color:#B5B5B5;font-size:1.0625rem;margin-top:1rem;font-family:Inter,sans-serif;line-height:1.7;max-width:640px;margin-left:auto;margin-right:auto;">{subtitle}</p>' if subtitle else ''}
    </div>""", unsafe_allow_html=True)


def section_header(text: str, icon: str = ""):
    text = html_escape(text)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem;">
      {f'<span style="font-size:1.1rem;">{icon}</span>' if icon else ''}
      <p class="mp-section-title" style="margin:0;">{text}</p>
    </div>""", unsafe_allow_html=True)


def badge(text: str, color: str = "#22C55E"):
    text = html_escape(text)
    st.markdown(f"""
    <span style="background:{color}18;color:{color};border:1px solid {color}35;
                 border-radius:99px;padding:3px 12px;font-size:0.72rem;font-weight:700;
                 font-family:'Inter',sans-serif;letter-spacing:0.04em;">
      {text}
    </span>""", unsafe_allow_html=True)


# ── Cards ─────────────────────────────────────────────────────────────────────

def metric_card(label: str, value: str, delta: str = "", icon: str = ""):
    label = html_escape(label)
    value = html_escape(value)
    delta = html_escape(delta)
    delta_html = ""
    if delta:
        color  = "#10B981" if not delta.startswith("-") else "#EF4444"
        arrow  = "up" if not delta.startswith("-") else "down"
        delta_html = f'<div class="kpi-trend {arrow}" style="margin-top:6px;">{delta}</div>'
    st.markdown(f"""
    <div class="kpi-card">
      {f'<div class="kpi-icon" style="background:rgba(34,197,94,0.1);color:#86EFAC;">{icon}</div>' if icon else ''}
      <div class="kpi-num">{value}</div>
      <div class="kpi-lbl">{label}</div>
      {delta_html}
    </div>""", unsafe_allow_html=True)


def feature_card(icon: str, title: str, desc: str):
    title = html_escape(title)
    desc = html_escape(desc)
    st.markdown(f"""
    <div class="stitch-feat-card">
      <div class="stitch-feat-icon" style="background:rgba(34,197,94,0.1);color:#86EFAC;">
        {icon}
      </div>
      <h3 style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:700;
                 color:#FFFFFF;margin:0 0 0.5rem;">{title}</h3>
      <p style="color:#B5B5B5;font-size:0.875rem;margin:0;line-height:1.7;">{desc}</p>
    </div>""", unsafe_allow_html=True)


def score_card(label: str, score: float, color: str = "#22C55E"):
    label = html_escape(label)
    pct  = max(0, min(100, score))
    circ = 2 * 3.14159 * 36
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;padding:1.25rem;">
      <p class="kpi-lbl" style="margin:0 0 0.75rem;">{label}</p>
      <div style="position:relative;display:inline-block;">
        <svg width="90" height="90" viewBox="0 0 90 90">
          <circle cx="45" cy="45" r="36" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="7"/>
          <circle cx="45" cy="45" r="36" fill="none" stroke="{color}" stroke-width="7"
                  stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ*(1-pct/100):.1f}"
                  stroke-linecap="round" transform="rotate(-90 45 45)"
                  style="transition:stroke-dashoffset 1.2s cubic-bezier(0.22,1,0.36,1);
                         filter:drop-shadow(0 0 6px {color}80);"/>
        </svg>
        <span style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                     font-family:'Outfit',sans-serif;font-size:1.15rem;font-weight:800;
                     color:{color};">{pct:.0f}</span>
      </div>
    </div>""", unsafe_allow_html=True)


def info_card(title: str, content: str, icon: str = "💡", border_color: str = "#22C55E"):
    title = html_escape(title)
    content = html_escape(content)
    st.markdown(f"""
    <div class="glass-card" style="border-left:2px solid {border_color};">
      <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
        <span style="font-size:1.1rem;">{icon}</span>
        <h4 style="font-family:'Inter',sans-serif;font-size:0.9rem;font-weight:600;
                   color:#FFFFFF;margin:0;">{title}</h4>
      </div>
      <p style="color:#B5B5B5;font-size:0.85rem;margin:0;line-height:1.7;">{content}</p>
    </div>""", unsafe_allow_html=True)


def list_card(title: str, items: list, icon: str = "checkmark", color: str = "#10B981"):
    title = html_escape(title)
    icon_char = "✓" if icon in ("checkmark", "✅") else icon
    items_html = "".join([
        f'<li style="color:#B5B5B5;font-size:0.84rem;margin-bottom:0.4rem;'
        f'display:flex;align-items:flex-start;gap:6px;">'
        f'<span style="color:{color};flex-shrink:0;margin-top:2px;">{icon_char}</span>'
        f'<span>{html_escape(item)}</span></li>'
        for item in items
    ])
    st.markdown(f"""
    <div class="glass-card">
      <p style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                text-transform:uppercase;letter-spacing:0.08em;color:#777777;margin:0 0 0.75rem;">
        {title}
      </p>
      <ul style="margin:0;padding:0;list-style:none;">{items_html}</ul>
    </div>""", unsafe_allow_html=True)


def skeleton_loader(rows: int = 3, card_height: int = 80):
    """Display shimmer skeleton loading placeholders."""
    for _ in range(rows):
        st.markdown(
            f'<div class="skeleton" style="height:{card_height}px;margin-bottom:0.75rem;"></div>',
            unsafe_allow_html=True
        )


def empty_state(
    icon: str = "🎯",
    title: str = "Nothing here yet",
    desc: str = "",
    cta_label: str = "",
    cta_page: str = "",
):
    """Premium empty state component with optional CTA."""
    title = html_escape(title)
    desc = html_escape(desc)
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(34,197,94,0.05),rgba(22,163,74,0.03));
                border:1px dashed rgba(34,197,94,0.2);border-radius:24px;
                padding:3rem 2rem;text-align:center;">
      <div style="font-size:3rem;margin-bottom:0.75rem;
                  filter:drop-shadow(0 0 12px rgba(34,197,94,0.3));">{icon}</div>
      <h3 style="font-family:'Outfit',sans-serif;color:#FFFFFF;font-weight:800;
                 font-size:1.2rem;margin:0 0 0.5rem;letter-spacing:-0.02em;">{title}</h3>
      {f'<p style="color:#777777;font-size:0.875rem;margin:0;font-family:Inter,sans-serif;line-height:1.7;">{desc}</p>' if desc else ''}
    </div>""", unsafe_allow_html=True)
    if cta_label and cta_page:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        if st.button(cta_label, use_container_width=True):
            st.session_state["page"] = cta_page
            st.rerun()


# ── Charts ────────────────────────────────────────────────────────────────────

def radar_chart(categories: list, values: list, title: str = "Skill Breakdown"):
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        line=dict(color="#22C55E", width=2),
        fillcolor='rgba(34,197,94,0.1)',
        marker=dict(color="#86EFAC", size=5, line=dict(color="#22C55E", width=1.5)),
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="rgba(255,255,255,0.05)",
                tickfont=dict(size=9, color="#777777"),
                linecolor="rgba(255,255,255,0.05)",
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.05)",
                tickfont=dict(size=10, color="#B5B5B5"),
                linecolor="rgba(255,255,255,0.05)",
            ),
        ),
        showlegend=False,
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def line_chart(dates: list, scores: list, title: str = "Score Progress"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=scores,
        mode='lines+markers',
        line=dict(color="#22C55E", width=2.5, shape="spline"),
        marker=dict(color="#86EFAC", size=7, line=dict(color="#22C55E", width=1.5)),
        fill='tozeroy',
        fillcolor='rgba(34,197,94,0.07)',
        hovertemplate='<b>%{y:.0f}</b><br>%{x}<extra></extra>',
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", showline=False,
            zeroline=False, tickfont=dict(size=10, color="#777777"),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", range=[0, 105],
            showline=False, zeroline=False, tickfont=dict(size=10, color="#777777"),
        ),
        hovermode="x unified",
        height=260,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def bar_chart(labels: list, values: list, title: str = "Scores"):
    colors = ["#22C55E" if v >= 75 else "#F59E0B" if v >= 50 else "#EF4444" for v in values]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=colors, cornerradius=6, opacity=0.85),
        text=[f"{v:.0f}" for v in values],
        textposition='outside',
        textfont=dict(color="#B5B5B5", size=11),
        hovertemplate='<b>%{y:.0f}</b><extra></extra>',
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=10, color="#777777"),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", range=[0, 120],
            zeroline=False, tickfont=dict(size=10, color="#777777"),
        ),
        bargap=0.25,
        height=240,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Interview Room Components ─────────────────────────────────────────────────

def ai_avatar(thinking: bool = False):
    label  = "Thinking..." if thinking else "AI Interviewer"
    st_clr = "#F59E0B" if thinking else "#10B981"
    anim   = "pulse-anim" if thinking else ""
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:0.6rem;">
      <div class="{anim}" style="width:72px;height:72px;border-radius:50%;
                   background:var(--primary);
                   display:flex;align-items:center;justify-content:center;
                   box-shadow:0 0 0 1px rgba(34,197,94,0.30), 0 10px 28px rgba(34,197,94,0.14);position:relative;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#052e13"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/>
          <path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>
        </svg>
        <div style="position:absolute;bottom:3px;right:3px;
                    width:12px;height:12px;border-radius:50%;
                    background:{st_clr};border:2px solid #090B09;"></div>
      </div>
      <p style="color:#777777;font-size:0.75rem;margin:0;font-family:'Inter',sans-serif;
                font-weight:500;">{label}</p>
    </div>""", unsafe_allow_html=True)


def question_display(text: str, q_num: int, total: int):
    text = html_escape(text)
    pips = "".join([
        f'<div style="width:26px;height:4px;border-radius:99px;'
        f'background:{"#22C55E" if i < q_num else "rgba(255,255,255,0.08)"};'
        f'box-shadow:{"0 0 6px rgba(34,197,94,0.5)" if i < q_num else "none"};"></div>'
        for i in range(total)
    ])
    st.markdown(f"""
    <div class="stitch-q-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <span class="q-badge">Question {q_num}/{total}</span>
        <div style="display:flex;gap:4px;align-items:center;">{pips}</div>
      </div>
      <p style="font-family:'Inter',sans-serif;font-size:1.1rem;font-weight:500;
                color:#FFFFFF;line-height:1.75;margin:0;">{text}</p>
    </div>""", unsafe_allow_html=True)


def timer_display(seconds: int):
    mins  = seconds // 60
    secs  = seconds % 60
    color = "#10B981" if seconds > 60 else "#F59E0B" if seconds > 30 else "#EF4444"
    st.markdown(f"""
    <div style="text-align:center;">
      <span style="font-family:'Outfit',sans-serif;font-size:2rem;font-weight:800;
                   color:{color};font-variant-numeric:tabular-nums;letter-spacing:0.04em;">
        {mins:02d}:{secs:02d}
      </span>
    </div>""", unsafe_allow_html=True)


def mic_visualizer(active: bool = False):
    c = "#22C55E" if active else "#777777"
    bars = "".join([
        f'<div class="waveform-bar" style="height:{h}px;background:{c};'
        f'animation-delay:{0.1*i:.1f}s;'
        f'{"" if active else "animation:none;"}"></div>'
        for i, h in enumerate([10, 18, 26, 18, 34, 18, 26, 18, 10])
    ])
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;gap:4px;
                height:50px;background:rgba(255,255,255,0.02);
                border-radius:14px;border:1px solid rgba(255,255,255,0.06);">
      {bars}
    </div>""", unsafe_allow_html=True)


# ── Loaders ───────────────────────────────────────────────────────────────────

def thinking_loader(text: str = "AI is thinking..."):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;
                background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.16);
                border-radius:14px;padding:1rem 1.5rem;">
      <div style="width:18px;height:18px;border-radius:50%;
                  border:2.5px solid transparent;
                  border-top-color:#16A34A;
                  animation:spin 0.8s linear infinite;flex-shrink:0;"></div>
      <p style="color:#B5B5B5;margin:0;font-size:0.88rem;font-family:'Inter',sans-serif;">{text}</p>
    </div>""", unsafe_allow_html=True)


# ── Session State Helpers ─────────────────────────────────────────────────────

def is_logged_in() -> bool:
    return bool(st.session_state.get("token") and st.session_state.get("user"))


def require_auth():
    """Redirect to auth page if not logged in."""
    if not is_logged_in():
        st.session_state["page"] = "auth"
        st.rerun()
