"""
MockPilot AI — Main Streamlit Application
2-Minute Interview Readiness Engine · Central router.
"""
import streamlit as st
import requests
import sys, os

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(ROOT))

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="MockPilot AI — 2-Minute Interview Readiness Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from frontend.components.ui_components import inject_css
from frontend.views import landing, dashboard, interview_room, feedback, resume_analyzer
from frontend.views import quick_scan, readiness_report
from frontend.api_client import check_backend

BACKEND = "http://localhost:8000"


# ── Auto Guest Login ──────────────────────────────────────────────────────────

def _ensure_guest_session():
    """Silently log in as guest if no token exists yet."""
    if st.session_state.get("token"):
        return
    try:
        r = requests.post(f"{BACKEND}/api/auth/guest", timeout=5)
        if r.ok:
            data = r.json()
            st.session_state["token"] = data["access_token"]
            st.session_state["user"]  = data.get("user", {"username": "Guest", "full_name": "Guest"})
    except Exception:
        pass


# ── Session defaults ──────────────────────────────────────────────────────────
defaults = {
    "page": "landing",
    "token": None,
    "user": None,
    "interview_stage": "setup",
    "scan_step": 1,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

_ensure_guest_session()


# ── Sidebar Navigation ────────────────────────────────────────────────────────

def render_sidebar():
    inject_css()

    # Extra sidebar CSS
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { background:rgba(7,7,15,0.97) !important; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div { gap: 1px !important; }
    [data-testid="stSidebar"] .stButton { margin-bottom: 0 !important; }
    .nav-active button {
      background:rgba(124,58,237,0.18) !important;
      border-color:rgba(168,85,247,0.4) !important;
      color:#A855F7 !important;
      box-shadow:0 0 16px rgba(124,58,237,0.2) !important;
    }
    .nav-section-label {
      color:#334155;font-size:0.65rem;font-weight:700;
      text-transform:uppercase;letter-spacing:1px;
      padding:0.75rem 0.5rem 0.3rem;
    }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:1.2rem 0 0.75rem;border-bottom:1px solid rgba(255,255,255,0.06);
                    margin-bottom:1rem;">
          <div style="display:flex;align-items:center;gap:0.6rem;">
            <div style="width:38px;height:38px;border-radius:12px;
                        background:linear-gradient(135deg,#7C3AED,#22D3EE);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.2rem;box-shadow:0 0 16px rgba(124,58,237,0.4);">⚡</div>
            <div>
              <p style="font-size:1.1rem;font-weight:900;
                        background:linear-gradient(135deg,#A855F7,#22D3EE);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text;margin:0;line-height:1.1;">MockPilot AI</p>
              <p style="color:#334155;font-size:0.62rem;margin:0;letter-spacing:0.3px;">
                Interview Readiness Engine
              </p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        current = st.session_state.get("page", "landing")

        # ── Primary feature
        st.markdown('<p class="nav-section-label">⚡ Quick Mode</p>', unsafe_allow_html=True)

        # Quick Scan — primary highlighted
        is_scan = current in ("quick_scan", "readiness_report")
        st.markdown(f'<div class="{"nav-active" if is_scan else ""}">', unsafe_allow_html=True)
        if st.button("⚡  Quick Readiness Scan", key="nav_quick_scan", use_container_width=True):
            st.session_state["page"] = "quick_scan"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if current == "readiness_report":
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
            if st.button("📊  Readiness Report", key="nav_report", use_container_width=True):
                st.session_state["page"] = "readiness_report"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Advanced features
        st.markdown('<p class="nav-section-label">🏆 Advanced Mode</p>', unsafe_allow_html=True)

        advanced_nav = [
            ("🤖", "Full AI Interview",   "interview"),
            ("📋", "Interview Feedback",  "feedback"),
        ]
        for icon, label, page_key in advanced_nav:
            is_active = current == page_key
            st.markdown(f'<div class="{"nav-active" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state["page"] = page_key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Tools
        st.markdown('<p class="nav-section-label">🛠 Tools</p>', unsafe_allow_html=True)

        tools_nav = [
            ("🏠", "Home",          "landing"),
            ("📊", "Dashboard",     "dashboard"),
            ("📄", "Resume Analyzer","resume"),
        ]
        for icon, label, page_key in tools_nav:
            is_active = current == page_key
            st.markdown(f'<div class="{"nav-active" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state["page"] = page_key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Backend status
        st.markdown("<br>", unsafe_allow_html=True)
        backend_ok = check_backend()
        status_color = "#10B981" if backend_ok else "#EF4444"
        status_label = "Backend Online" if backend_ok else "Backend Offline"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.4rem;padding:0.4rem;
                    border-top:1px solid rgba(255,255,255,0.04);margin-top:0.5rem;">
          <div style="width:7px;height:7px;border-radius:50%;background:{status_color};
                      {'animation:aiPulse 2s infinite;' if backend_ok else ''}"></div>
          <p style="color:{status_color};font-size:0.7rem;margin:0;">{status_label}</p>
        </div>""", unsafe_allow_html=True)

        if not backend_ok:
            st.markdown("""
            <p style="color:#334155;font-size:0.65rem;padding:0 0.4rem;">
              Start: <code style="color:#A855F7;">uvicorn backend.main:app --reload</code>
            </p>""", unsafe_allow_html=True)


# ── Page Router ───────────────────────────────────────────────────────────────

def main():
    render_sidebar()
    page = st.session_state.get("page", "landing")

    if page == "landing":
        landing.render()
    elif page == "quick_scan":
        quick_scan.render()
    elif page == "readiness_report":
        readiness_report.render()
    elif page == "dashboard":
        dashboard.render()
    elif page == "interview":
        interview_room.render()
    elif page == "feedback":
        feedback.render()
    elif page == "resume":
        resume_analyzer.render()

    else:
        landing.render()


if __name__ == "__main__":
    main()
