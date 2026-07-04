"""
MockPilot AI — Resume Analyzer Page
Upload, parse, ATS score, skill extraction, personalized question generation.
"""
import streamlit as st
from frontend.components.ui_components import (
    inject_css, section_header, info_card, list_card, html_escape
)
from frontend.api_client import upload_resume, list_resumes, delete_resume
from frontend.api_client import BACKEND
import requests


def render():
    inject_css()

    # ── Delete button styling ─────────────────────────────────────
    st.markdown("""
    <style>
    /* × delete icon button — matches default Streamlit button height */
    .del-btn button {
      background: rgba(239,68,68,0.08) !important;
      border: 1px solid rgba(239,68,68,0.25) !important;
      color: #EF4444 !important;
      border-radius: 10px !important;
      font-size: 1.1rem !important;
      font-weight: 700 !important;
      transition: all 0.2s ease !important;
      width: 100% !important;
    }
    .del-btn button:hover {
      background: rgba(239,68,68,0.2) !important;
      border-color: #EF4444 !important;
      box-shadow: 0 0 12px rgba(239,68,68,0.3) !important;
    }
    /* confirm state */
    .del-confirm button {
      background: rgba(239,68,68,0.25) !important;
      border: 1px solid #EF4444 !important;
      color: #FCA5A5 !important;
      font-size: 0.75rem !important;
      font-weight: 700 !important;
      border-radius: 10px !important;
      width: 100% !important;
    }
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="stitch-banner fade-in-up" style="margin-bottom:2rem;">
      <div style="display:flex;align-items:center;gap:1rem;">
        <div style="width:52px;height:52px;border-radius:16px;
                    background:linear-gradient(135deg,rgba(34,197,94,0.3),rgba(74,222,128,0.2));
                    display:flex;align-items:center;justify-content:center;font-size:1.5rem;
                    border:1px solid rgba(34,197,94,0.3);flex-shrink:0;">
          📄
        </div>
        <div>
          <h1 style="font-size:2rem;font-weight:800;
                     background:linear-gradient(135deg,#d2bbff,#5de6ff);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     background-clip:text;margin:0;letter-spacing:-0.02em;">Resume Analyzer</h1>
          <p style="color:#ccc3d8;font-size:0.9rem;margin:4px 0 0;">
            Upload your resume · Get ATS score · Generate personalized interview questions
          </p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    tab_upload, tab_library = st.tabs(["📤  Upload Resume", "📚  My Resumes"])

    # ── Upload Tab ────────────────────────────────────────────────
    with tab_upload:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:1rem;">
          <h3 style="font-size:1rem;font-weight:700;color:#FFFFFF;margin:0 0 0.4rem;">
            📄 Upload Resume
          </h3>
          <p style="color:#64748B;font-size:0.85rem;margin:0;">
            Supported: PDF, DOCX, TXT · Max 10MB
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="hide-uploader">', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Drop your resume here",
            type=["pdf", "docx", "doc", "txt"],
            label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if not uploaded:
            st.markdown("""
            <div class="stitch-upload-zone">
              <span style="font-size:2.5rem;display:block;margin-bottom:0.75rem;">📄</span>
              <p style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:700;color:#FFFFFF;margin:0 0 0.25rem;">
                Drop your resume here
              </p>
              <p style="color:#64748B;font-size:0.85rem;margin:0;">
                Click the invisible zone above to upload
              </p>
            </div>
            """, unsafe_allow_html=True)

        if uploaded:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"""
                <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);
                            border-radius:10px;padding:0.7rem 1rem;display:flex;align-items:center;gap:0.7rem;">
                  <span style="font-size:1.5rem;">📄</span>
                  <div>
                    <p style="color:#FFFFFF;font-weight:600;font-size:0.9rem;margin:0;">{html_escape(uploaded.name)}</p>
                    <p style="color:#64748B;font-size:0.75rem;margin:2px 0 0;">
                      {uploaded.size / 1024:.1f} KB
                    </p>
                  </div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                analyze_btn = st.button("🔍  Analyze", use_container_width=True, key="analyze_btn")

            if analyze_btn:
                with st.spinner("Analyzing your resume…"):
                    result = upload_resume(uploaded.read(), uploaded.name)

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state["analyzed_resume"] = result
                    st.success("✅ Resume analyzed successfully!")

        # Show results
        resume_data = st.session_state.get("analyzed_resume")
        if resume_data:
            _render_analysis(resume_data)

    # ── Library Tab ───────────────────────────────────────────────
    with tab_library:
        with st.spinner("Loading your resumes..."):
            resumes = list_resumes()

        if not resumes:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:3rem;">
              <p style="font-size:2.5rem;">📂</p>
              <h3 style="color:#FFFFFF;">No resumes uploaded yet</h3>
              <p style="color:#64748B;">Upload your first resume to get started.</p>
            </div>""", unsafe_allow_html=True)
        else:
            for r in resumes:
                rid = r['id']
                ats = r.get("ats_score") or 0
                ats_color = "#10B981" if ats >= 70 else "#F59E0B" if ats >= 45 else "#EF4444"
                confirm_key = f"del_confirm_{rid}"

                # vertical_alignment="center" keeps View and × on the same baseline
                col_a, col_b, col_c, col_d = st.columns(
                    [3, 1, 0.9, 0.9], vertical_alignment="center"
                )

                with col_a:
                    st.markdown(f"""
                    <div>
                      <p style="color:#FFFFFF;font-weight:600;font-size:0.9rem;margin:0;">
                        📄 {html_escape(r['filename'])}
                      </p>
                      <p style="color:#64748B;font-size:0.78rem;margin:2px 0 0;">
                        Uploaded {html_escape(r.get('uploaded_at','')[:10])}
                      </p>
                    </div>""", unsafe_allow_html=True)

                with col_b:
                    st.markdown(f"""
                    <p style="color:{ats_color};font-weight:700;font-size:0.95rem;
                               margin:0;">ATS: {ats:.0f}</p>""",
                                unsafe_allow_html=True)

                with col_c:
                    if st.button("View", key=f"view_r_{rid}", use_container_width=True):
                        st.session_state["analyzed_resume"] = r

                with col_d:
                    if st.session_state.get(confirm_key):
                        # Second click → actually delete
                        st.markdown('<div class="del-confirm">', unsafe_allow_html=True)
                        if st.button("Sure?", key=f"del_sure_{rid}", use_container_width=True):
                            result = delete_resume(rid)
                            if result.get("ok"):
                                st.session_state.pop(confirm_key, None)
                                if st.session_state.get("analyzed_resume", {}).get("id") == rid:
                                    st.session_state.pop("analyzed_resume", None)
                                st.success(f"Deleted {r['filename']}")
                                st.rerun()
                            else:
                                st.error("❌ Delete failed")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        # First click → show × (confirmation on next click)
                        st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                        if st.button("✕", key=f"del_r_{rid}", use_container_width=True,
                                     help="Delete this resume"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("<hr style='border-color:rgba(255,255,255,0.05);margin:0.5rem 0;'>",
                            unsafe_allow_html=True)


def _render_analysis(data: dict):
    """Render full resume analysis output."""
    st.markdown("<br>", unsafe_allow_html=True)

    # ── ATS Score ─────────────────────────────────────────────────
    ats = data.get("ats_score") or 0
    ats_color = "#10B981" if ats >= 70 else "#F59E0B" if ats >= 45 else "#EF4444"
    ats_label = "Excellent" if ats >= 70 else "Moderate" if ats >= 45 else "Needs Work"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(34,197,94,0.08),rgba(74,222,128,0.04));
                border:1px solid rgba(34,197,94,0.25);border-left:4px solid {ats_color};
                border-radius:24px;padding:1.5rem 2rem;
                display:flex;align-items:center;gap:2rem;margin-bottom:1.5rem;
                box-shadow:0 0 40px rgba(34,197,94,0.1);">
      <div style="text-align:center;min-width:100px;flex-shrink:0;">
        <div style="width:90px;height:90px;border-radius:50%;
                    background:conic-gradient(from 0deg, {ats_color} {ats:.0f}%, rgba(255,255,255,0.05) {ats:.0f}%);
                    display:flex;align-items:center;justify-content:center;position:relative;
                    margin:0 auto;box-shadow:0 0 20px {ats_color}40;">
          <div style="position:absolute;inset:6px;border-radius:50%;background:#0F120F;
                      display:flex;align-items:center;justify-content:center;flex-direction:column;">
            <h1 style="font-family:'Outfit',sans-serif;font-size:1.75rem;font-weight:900;
                       color:{ats_color};margin:0;line-height:1;">{ats:.0f}</h1>
            <p style="color:rgba(255,255,255,0.4);font-size:0.55rem;font-weight:700;
                      letter-spacing:0.1em;text-transform:uppercase;margin:0;">ATS</p>
          </div>
        </div>
      </div>
      <div>
        <h3 style="color:#e3e0f3;font-weight:700;margin:0 0 0.3rem;font-family:'Outfit',sans-serif;">
          {ats_label} ATS Compatibility
        </h3>
        <p style="color:#ccc3d8;font-size:0.88rem;margin:0;line-height:1.65;">
          Your resume has been scored against common ATS keyword requirements.
          {'Great job! Your resume is highly optimized.' if ats >= 70 else 'Consider adding more relevant keywords and quantifying achievements.'}
        </p>
      </div>
    </div>""", unsafe_allow_html=True)

    section_header("Resume Analysis", "🔍")
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        # Skills
        skills = data.get("extracted_skills", {})
        if skills:
            if isinstance(skills, dict):
                for category, skill_list in skills.items():
                    if skill_list:
                        tags = " ".join([
                            f'<span class="stitch-skill-badge">'
                            f'{html_escape(s)}</span>'
                            for s in skill_list
                        ])
                        st.markdown(f"""
                        <div style="margin-bottom:1rem;">
                          <p style="font-family:'Space Grotesk',sans-serif;color:#ccc3d8;
                                    font-size:0.7rem;font-weight:700;
                                    text-transform:uppercase;letter-spacing:0.1em;margin:0 0 0.5rem;">
                            {html_escape(category)}
                          </p>
                          <div>{tags}</div>
                        </div>""", unsafe_allow_html=True)

        # Detected roles
        roles = data.get("detected_roles", [])
        if roles:
            st.markdown("<br>", unsafe_allow_html=True)
            role_tags = " ".join([
                f'<span class="stitch-skill-badge cyan">'
                f'{html_escape(r)}</span>' for r in roles
            ])
            st.markdown(f"""
            <div>
              <p style="font-family:'Space Grotesk',sans-serif;color:#ccc3d8;
                        font-size:0.7rem;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.1em;margin:0 0 0.5rem;">
                Detected Roles
              </p>
              <div>{role_tags}</div>
            </div>""", unsafe_allow_html=True)

    with col_right:
        # Keyword matches
        matched = data.get("keyword_matches", [])
        if matched:
            list_card("✅ Matched Keywords", matched[:8], "✅", "#10B981")

        st.markdown("<br>", unsafe_allow_html=True)

        # Missing keywords
        missing = data.get("missing_keywords", [])
        if missing:
            list_card("❌ Missing Keywords", missing[:6], "❌", "#EF4444")

    # Suggestions
    suggestions = data.get("improvement_suggestions", [])
    if suggestions:
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("Improvement Suggestions", "💡")
        for i, s in enumerate(suggestions):
            st.markdown(f"""
            <div class="stitch-suggestion-card">
              <span class="stitch-suggestion-num">{i+1}</span>
              <p style="color:#e3e0f3;font-size:0.88rem;margin:0;line-height:1.65;">{html_escape(s)}</p>
            </div>""", unsafe_allow_html=True)

    # CTA
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎯  Start Interview Based on This Resume", use_container_width=True):
        st.session_state["interview_stage"] = "setup"
        st.session_state["page"] = "interview"
        st.rerun()
