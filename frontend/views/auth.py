"""
MockPilot AI — Authentication Page
Glassmorphism login/signup with JWT support.
"""
import streamlit as st
from frontend.components.ui_components import inject_css
from frontend.api_client import login, signup


def render():
    inject_css()

    # Center the auth card
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        # Logo
        st.markdown("""
        <div style="text-align:center;margin-bottom:2rem;">
          <div style="display:inline-flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
            <div style="width:42px;height:42px;border-radius:12px;
                        background:linear-gradient(135deg,#7C3AED,#22D3EE);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.3rem;box-shadow:0 0 20px rgba(124,58,237,0.4);">🤖</div>
            <span style="font-size:1.5rem;font-weight:800;
                         background:linear-gradient(135deg,#A855F7,#22D3EE);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">MockPilot AI</span>
          </div>
          <p style="color:#64748B;font-size:0.85rem;margin:0;">Your AI Interview Co-Pilot</p>
        </div>
        """, unsafe_allow_html=True)

        # Tab toggle
        tab_login, tab_signup = st.tabs(["🔐  Login", "✨  Sign Up"])

        # ── Login ─────────────────────────────────────────────────
        with tab_login:
            st.markdown("""
            <div class="glass-card" style="margin-top:1rem;">
              <h3 style="font-size:1.2rem;font-weight:700;color:#F1F5F9;margin:0 0 0.3rem;">
                Welcome back 👋
              </h3>
              <p style="color:#64748B;font-size:0.85rem;margin:0 0 1.5rem;">
                Sign in to continue your interview practice
              </p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                email    = st.text_input("Email Address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In →", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Authenticating..."):
                        result = login(email, password)
                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.session_state["token"] = result["access_token"]
                        st.session_state["user"]  = result["user"]
                        st.success("✅ Login successful!")
                        st.session_state["page"] = "dashboard"
                        st.rerun()

        # ── Sign Up ───────────────────────────────────────────────
        with tab_signup:
            st.markdown("""
            <div class="glass-card" style="margin-top:1rem;">
              <h3 style="font-size:1.2rem;font-weight:700;color:#F1F5F9;margin:0 0 0.3rem;">
                Create your account 🚀
              </h3>
              <p style="color:#64748B;font-size:0.85rem;margin:0 0 1.5rem;">
                Start practicing interviews for free
              </p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("signup_form"):
                full_name = st.text_input("Full Name", placeholder="John Doe")
                username  = st.text_input("Username", placeholder="johndoe")
                email     = st.text_input("Email Address", placeholder="you@example.com")
                password  = st.text_input("Password (min 8 chars)", type="password", placeholder="••••••••")
                agree     = st.checkbox("I agree to the Terms of Service and Privacy Policy")
                submitted = st.form_submit_button("Create Account →", use_container_width=True)

            if submitted:
                if not all([full_name, username, email, password]):
                    st.error("Please fill in all fields.")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif not agree:
                    st.warning("Please accept the terms to continue.")
                else:
                    with st.spinner("Creating your account..."):
                        result = signup(email, username, password, full_name)
                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.session_state["token"] = result["access_token"]
                        st.session_state["user"]  = result["user"]
                        st.success("🎉 Account created! Welcome to MockPilot AI!")
                        st.session_state["page"] = "dashboard"
                        st.rerun()

        # Back link
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Home", key="back_home"):
            st.session_state["page"] = "landing"
            st.rerun()
