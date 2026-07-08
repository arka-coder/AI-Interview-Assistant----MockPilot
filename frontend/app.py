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
    page_title="MockPilot | Interview Readiness",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from components.ui_components import inject_css
from views import landing, dashboard, interview_room, feedback, resume_analyzer
from views import auth
from views import quick_scan, readiness_report
from api_client import check_backend

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")


# ── Auto Guest Login ──────────────────────────────────────────────────────────

def _ensure_guest_session():
    """Silently log in as guest if no token exists yet."""
    if st.session_state.get("token"):
        return
    try:
        r = requests.post(f"{BACKEND}/api/auth/guest", timeout=35)
        if r.ok:
            data = r.json()
            st.session_state["token"] = data["access_token"]
            st.session_state["user"]  = data.get("user", {"username": "Guest", "full_name": "Guest"})
    except Exception:
        pass  # Backend offline/sleeping — user will see the sidebar "Backend Offline" indicator


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

    with st.sidebar:
        current = st.session_state.get("page", "landing")

        # ── Brand Header ──────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:1.75rem 1rem 1.25rem;border-bottom:1px solid rgba(255,255,255,0.06);
                    margin-bottom:0.75rem;">
          <div style="display:flex;align-items:center;gap:0.75rem;">
            <div style="width:38px;height:38px;border-radius:11px;flex-shrink:0;
                        background:var(--primary);
                        display:flex;align-items:center;justify-content:center;
                        box-shadow:0 1px 2px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2);">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#052e13"
                   stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
              </svg>
            </div>
            <div>
              <p style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:800;
                        color:#FFFFFF;margin:0;line-height:1.1;letter-spacing:-0.02em;">MockPilot</p>
              <p style="font-family:'Inter',sans-serif;font-size:0.68rem;color:#8A9188;
                        margin:1px 0 0;font-weight:600;letter-spacing:0.02em;">Interview Readiness</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Active-item styling: tint the button whose st-key matches page ──
        _active_key = {
            "quick_scan": "nav_quick_scan", "readiness_report": "nav_report",
            "interview": "nav_interview", "feedback": "nav_feedback",
            "landing": "nav_landing", "dashboard": "nav_dashboard", "resume": "nav_resume",
        }.get(current)
        if _active_key:
            st.markdown(
                f'<style>.st-key-{_active_key}{{}} '
                f'div.st-key-{_active_key} button{{background:rgba(34,197,94,0.10)!important;'
                f'color:#86EFAC!important;font-weight:600!important;}}'
                f'div.st-key-{_active_key} button::before{{transform:translateY(-50%) scaleY(1)!important;}}'
                f'div.st-key-{_active_key} button:hover{{background:rgba(34,197,94,0.14)!important;}}'
                f'</style>', unsafe_allow_html=True)

        # ── Quick Readiness Scan — primary CTA ─────────────────────────────────
        if st.button(":material/bolt: Quick readiness scan", key="nav_quick_scan",
                     use_container_width=True, type="primary"):
            st.session_state["page"] = "quick_scan"
            st.rerun()

        if current == "readiness_report":
            if st.button(":material/monitoring: Readiness report", key="nav_report",
                         use_container_width=True):
                st.session_state["page"] = "readiness_report"
                st.rerun()

        # Advanced Mode section
        st.markdown('<p class="nav-section-label">Advanced mode</p>', unsafe_allow_html=True)

        advanced_nav = [
            (":material/forum:",    "Mock interviews", "interview"),
            (":material/insights:", "Progress",        "feedback"),
        ]
        for icon, label, page_key in advanced_nav:
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state["page"] = page_key
                st.rerun()

        # Tools section
        st.markdown('<p class="nav-section-label">Tools</p>', unsafe_allow_html=True)

        tools_nav = [
            (":material/home:",            "Home",            "landing"),
            (":material/space_dashboard:", "Dashboard",       "dashboard"),
            (":material/description:",     "Resume analyzer", "resume"),
        ]
        for icon, label, page_key in tools_nav:
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state["page"] = page_key
                st.rerun()

        # ── Start Interview CTA ───────────────────────────────────────────────
        st.markdown("""
        <div style="margin:1.5rem 0 0.75rem;padding:0 0.25rem;">
          <div style="height:1px;background:rgba(255,255,255,0.06);margin-bottom:1rem;"></div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(":material/play_arrow: Start interview", key="nav_start_session",
                     use_container_width=True, type="primary"):
            st.session_state["page"] = "interview"
            st.rerun()

        # ── Backend Status ────────────────────────────────────────────────────
        backend_ok = check_backend()
        status_color = "#10B981" if backend_ok else "#EF4444"
        status_label = "Backend Online" if backend_ok else "Backend Offline"
        offline_hint = ""
        if not backend_ok:
            offline_hint = """
            <p style="color:#777777;font-size:0.64rem;margin:0.35rem 0 0;line-height:1.5;">
              Run: <code style="color:#B5B5B5;background:rgba(255,255,255,0.05);
                                padding:1px 5px;border-radius:4px;font-size:0.62rem;">uvicorn backend.main:app --reload</code>
            </p>"""
        st.markdown(f"""
        <div class="sidebar-status">
          <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:6px;height:6px;border-radius:50%;background:{status_color};
                        flex-shrink:0;box-shadow:0 0 6px {status_color}80;"></div>
            <p style="font-family:'Inter',sans-serif;color:{status_color};
                      font-size:0.68rem;font-weight:700;letter-spacing:0.03em;margin:0;">{status_label}</p>
          </div>
          {offline_hint}
        </div>""", unsafe_allow_html=True)


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
    elif page == "auth":
        auth.render()
    else:
        landing.render()


if __name__ == "__main__":
    main()
