"""
MockPilot AI — Live Voice Interview Mode
WhatsApp-style real-time voice conversation with AI interviewer.
"""
import streamlit as st
import json
import os
from frontend.components.ui_components import inject_css

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")


def render():
    inject_css()
    _inject_voice_ui_css()

    # Header
    st.markdown("""
    <div class="fade-in-up" style="text-align:center;margin-bottom:1.5rem;">
      <h1 style="font-size:2rem;font-weight:800;
                 background:linear-gradient(135deg,#16A34A,#4ADE80);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 background-clip:text;margin:0;">🎙️ Live Voice Interview</h1>
      <p style="color:#64748B;margin:0.4rem 0 0;font-size:0.9rem;">
        Speak naturally — AI listens, responds, and interviews you in real time
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Session config — use active interview session OR let user configure inline
    role   = st.session_state.get("session_role", "")
    itype  = st.session_state.get("session_type", "")
    exp    = st.session_state.get("session_exp", "mid")

    # Normalise experience to API-friendly short form
    exp_map = {"Junior (0-2 yrs)": "junior", "Mid-Level (2-5 yrs)": "mid",
               "Senior (5-10 yrs)": "senior", "Lead / Principal (10+ yrs)": "lead"}
    exp = exp_map.get(exp, exp if exp in ("junior","mid","senior","lead") else "mid")

    # If no active session, let user pick role/type quickly
    if not role or not itype:
        st.markdown("""
        <div style="background:rgba(74,222,128,0.06);border:1px solid rgba(74,222,128,0.2);
                    border-radius:12px;padding:0.9rem 1.25rem;margin-bottom:1rem;">
          <p style="color:#4ADE80;font-size:0.8rem;font-weight:600;margin:0 0 0.6rem;
                    text-transform:uppercase;letter-spacing:0.5px;">⚡ Quick Setup</p>
          <p style="color:#64748B;font-size:0.78rem;margin:0;">
            No active interview session found. Configure below to start a voice conversation.
          </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            role = st.selectbox("🎯 Role", [
                "Software Engineer", "Data Scientist", "Product Manager",
                "ML Engineer", "Backend Developer", "Full Stack Developer",
                "Data Analyst", "System Architect", "AI Engineer",
            ], key="vc_quick_role")
        with c2:
            itype = st.selectbox("🧩 Type", [
                "Technical", "HR / Cultural Fit", "Behavioral (STAR)",
                "Data Science", "System Design", "Business Development",
            ], key="vc_quick_type")
        with c3:
            exp = st.selectbox("📊 Level",
                ["junior", "mid", "senior", "lead"],
                index=1, key="vc_quick_exp")
    else:
        role = role or "Software Engineer"
        itype = itype or "Technical"

    q_context = st.session_state.get("last_question", {})
    q_text    = q_context.get("question_text", "") if isinstance(q_context, dict) else ""
    token     = st.session_state.get("token", "")

    # Config bar (always shown)
    st.markdown(f"""
    <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);
                border-radius:12px;padding:0.75rem 1.25rem;margin-bottom:1.25rem;
                display:flex;gap:1.5rem;align-items:center;flex-wrap:wrap;">
      <span style="color:#16A34A;font-weight:600;font-size:0.85rem;">🎯 {role}</span>
      <span style="color:#64748B;font-size:0.8rem;">·</span>
      <span style="color:#B5B5B5;font-size:0.85rem;">🧩 {itype}</span>
      <span style="color:#64748B;font-size:0.8rem;">·</span>
      <span style="color:#B5B5B5;font-size:0.85rem;">📊 {exp.capitalize()}</span>
      <span style="margin-left:auto;background:#10B981;color:#fff;font-size:0.75rem;
                  border-radius:99px;padding:2px 12px;font-weight:600;">● LIVE</span>
    </div>
    """, unsafe_allow_html=True)


    # Current question context (if coming from interview room)
    if q_text:
        st.markdown(f"""
        <div style="background:rgba(74,222,128,0.06);border-left:3px solid #4ADE80;
                    border-radius:0 10px 10px 0;padding:0.75rem 1rem;margin-bottom:1rem;">
          <p style="color:#64748B;font-size:0.75rem;margin:0 0 0.3rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.5px;">Current Question</p>
          <p style="color:#CBD5E1;font-size:0.9rem;margin:0;line-height:1.6;">{q_text}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── THE VOICE CHAT COMPONENT ───────────────────────────────────
    _render_voice_chat_component(token, role, itype, exp, q_text)

    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back to Interview", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()


def _render_voice_chat_component(token: str, role: str, itype: str, exp: str, q_text: str):
    """Render the full WhatsApp-style voice chat HTML/JS component."""

    html = f"""
<div id="voice-chat-root">

  <!-- Chat messages area -->
  <div id="vc-messages" class="vc-messages">
    <div class="vc-msg vc-ai">
      <div class="vc-avatar">🤖</div>
      <div class="vc-bubble">
        <p>Hello! I'm your AI interviewer for the <strong>{role}</strong> ({itype}) interview.
        Click the microphone button below and speak your answer. I'll listen, understand,
        and respond naturally — just like a real interview call.</p>
        <span class="vc-time">Just now</span>
      </div>
    </div>
  </div>

  <!-- Status bar -->
  <div id="vc-status" class="vc-status-bar">
    <div id="vc-waveform" class="vc-waveform">
      <span></span><span></span><span></span><span></span><span></span>
      <span></span><span></span><span></span><span></span><span></span>
    </div>
    <span id="vc-status-text">Tap the mic to start speaking</span>
  </div>

  <!-- Controls -->
  <div class="vc-controls">
    <button id="vc-mic-btn" class="vc-mic-btn" onclick="toggleRecording()" title="Hold to speak">
      <svg id="vc-mic-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="28" height="28">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
        <line x1="8" y1="23" x2="16" y2="23"/>
      </svg>
    </button>
    <div class="vc-hint" id="vc-hint-text">Tap to speak · Tap again to send</div>
    <button id="vc-mute-btn" class="vc-side-btn" onclick="toggleAIVoice()" title="Toggle AI voice">
      🔊
    </button>
  </div>

</div>

<script>
// ── State ────────────────────────────────────────────────────────
let mediaRecorder = null;
let audioChunks   = [];
let isRecording   = false;
let aiVoiceOn     = true;
let convHistory   = [];
const TOKEN       = "{token}";
const BACKEND     = "{BACKEND}";
const ROLE        = {json.dumps(role)};
const ITYPE       = {json.dumps(itype)};
const EXP         = {json.dumps(exp)};
const Q_CONTEXT   = {json.dumps(q_text)};

// ── DOM refs ─────────────────────────────────────────────────────
const micBtn      = document.getElementById("vc-mic-btn");
const statusText  = document.getElementById("vc-status-text");
const waveform    = document.getElementById("vc-waveform");
const messages    = document.getElementById("vc-messages");
const hintText    = document.getElementById("vc-hint-text");

// ── Recording ─────────────────────────────────────────────────────
async function toggleRecording() {{
  if (!isRecording) {{
    await startRecording();
  }} else {{
    stopRecording();
  }}
}}

async function startRecording() {{
  try {{
    const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
    const options = {{ mimeType: "audio/webm;codecs=opus" }};

    // Fallback mime types
    let mimeType = "audio/webm";
    if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {{
      mimeType = "audio/webm;codecs=opus";
    }} else if (MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")) {{
      mimeType = "audio/ogg;codecs=opus";
    }} else if (MediaRecorder.isTypeSupported("audio/mp4")) {{
      mimeType = "audio/mp4";
    }}

    mediaRecorder = new MediaRecorder(stream, {{ mimeType }});
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {{
      if (e.data.size > 0) audioChunks.push(e.data);
    }};

    mediaRecorder.onstop = () => {{
      const ext = mimeType.includes("ogg") ? ".ogg" :
                  mimeType.includes("mp4") ? ".mp4" : ".webm";
      const blob = new Blob(audioChunks, {{ type: mimeType }});
      stream.getTracks().forEach(t => t.stop());
      sendAudio(blob, ext);
    }};

    mediaRecorder.start(250);
    isRecording = true;
    setUIRecording(true);
  }} catch(err) {{
    setStatus("⚠️ Mic access denied — please allow microphone", "error");
    console.error("Mic error:", err);
  }}
}}

function stopRecording() {{
  if (mediaRecorder && mediaRecorder.state !== "inactive") {{
    mediaRecorder.stop();
  }}
  isRecording = false;
  setUIRecording(false);
  setStatus("⏳ Processing your answer...", "processing");
}}

// ── Send audio to backend ─────────────────────────────────────────
async function sendAudio(blob, ext) {{
  if (blob.size < 500) {{
    setStatus("Audio too short — please speak for at least 1 second", "error");
    resetUI();
    return;
  }}

  const fd = new FormData();
  fd.append("audio", blob, "recording" + ext);
  fd.append("role", ROLE);
  fd.append("interview_type", ITYPE);
  fd.append("experience_level", EXP);
  fd.append("question_context", Q_CONTEXT);
  fd.append("conversation_history", JSON.stringify(convHistory));

  try {{
    setStatus("🎤 Transcribing...", "processing");
    const res = await fetch(BACKEND + "/api/voice/chat", {{
      method: "POST",
      headers: {{ "Authorization": "Bearer " + TOKEN }},
      body: fd,
    }});

    const data = await res.json();

    if (data.error && !data.transcript) {{
      setStatus("❌ " + data.error, "error");
      resetUI();
      return;
    }}

    // Show candidate bubble
    if (data.transcript) {{
      addMessage("candidate", data.transcript);
    }}

    // Show AI bubble
    if (data.ai_response) {{
      setTimeout(() => {{
        addMessage("ai", data.ai_response);

        // Update history
        convHistory.push({{
          candidate: data.transcript,
          ai: data.ai_response,
        }});
        if (convHistory.length > 10) convHistory = convHistory.slice(-10);

        // Speak AI response
        if (aiVoiceOn && data.tts_text) {{
          speakText(data.tts_text);
        }} else {{
          resetUI();
        }}
      }}, 400);
    }} else {{
      resetUI();
    }}

    setStatus("Tap the mic to speak again", "idle");

  }} catch(err) {{
    setStatus("❌ Network error — is the backend running?", "error");
    console.error("Send audio error:", err);
    resetUI();
  }}
}}

// ── TTS (Browser Speech Synthesis) ──────────────────────────────
function speakText(text) {{
  if (!window.speechSynthesis) {{ resetUI(); return; }}
  window.speechSynthesis.cancel(); // Stop any current speech
  const utterance = new SpeechSynthesisUtterance(text);

  // Pick a good voice
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v =>
    v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Neural"))
  ) || voices.find(v => v.lang.startsWith("en"));
  if (preferred) utterance.voice = preferred;

  utterance.rate = 0.95;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;

  setStatus("🤖 AI is speaking...", "speaking");
  setWaveformSpeaking(true);

  utterance.onend = () => {{ resetUI(); }};
  utterance.onerror = () => {{ resetUI(); }};

  window.speechSynthesis.speak(utterance);
}}

function toggleAIVoice() {{
  aiVoiceOn = !aiVoiceOn;
  const btn = document.getElementById("vc-mute-btn");
  btn.textContent = aiVoiceOn ? "🔊" : "🔇";
  btn.title = aiVoiceOn ? "Mute AI voice" : "Unmute AI voice";
  if (!aiVoiceOn) window.speechSynthesis.cancel();
}}

// ── UI Helpers ────────────────────────────────────────────────────
function setUIRecording(on) {{
  micBtn.classList.toggle("recording", on);
  setWaveformActive(on);
  if (on) {{
    setStatus("🔴 Recording... Tap again when done", "recording");
    hintText.textContent = "Tap again to send answer";
  }} else {{
    hintText.textContent = "Tap to speak · Tap again to send";
  }}
}}

function setStatus(msg, type) {{
  statusText.textContent = msg;
  statusText.className = "vc-status-" + (type || "idle");
}}

function setWaveformActive(on) {{
  waveform.classList.toggle("active", on);
  waveform.classList.remove("speaking");
}}

function setWaveformSpeaking(on) {{
  waveform.classList.toggle("speaking", on);
  waveform.classList.remove("active");
}}

function resetUI() {{
  setUIRecording(false);
  setWaveformSpeaking(false);
  setWaveformActive(false);
  setStatus("Tap the mic to speak again", "idle");
  hintText.textContent = "Tap to speak · Tap again to send";
}}

function addMessage(role, text) {{
  const isAI = role === "ai";
  const time = new Date().toLocaleTimeString([], {{hour:"2-digit", minute:"2-digit"}});
  const div = document.createElement("div");
  div.className = "vc-msg " + (isAI ? "vc-ai" : "vc-candidate");
  div.innerHTML = `
    ${{isAI ? '<div class="vc-avatar">🤖</div>' : ''}}
    <div class="vc-bubble">
      <p>${{escapeHtml(text)}}</p>
      <span class="vc-time">${{time}}</span>
    </div>
    ${{!isAI ? '<div class="vc-avatar vc-you">👤</div>' : ''}}
  `;
  // Animate in
  div.style.opacity = "0";
  div.style.transform = isAI ? "translateX(-20px)" : "translateX(20px)";
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  setTimeout(() => {{
    div.style.transition = "all 0.35s ease";
    div.style.opacity = "1";
    div.style.transform = "translateX(0)";
  }}, 10);
}}

function escapeHtml(text) {{
  return text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}}

// Preload voices on page load
window.speechSynthesis.onvoiceschanged = () => {{ window.speechSynthesis.getVoices(); }};
window.speechSynthesis.getVoices();
</script>
"""

    st.components.v1.html(html, height=620, scrolling=False)


def _inject_voice_ui_css():
    st.markdown("""
<style>
/* ── Voice Chat Container ── */
#voice-chat-root {
  font-family: 'Outfit', 'Inter', sans-serif;
  display: flex;
  flex-direction: column;
  height: 560px;
  background: rgba(7,7,15,0.6);
  border: 1px solid rgba(34,197,94,0.2);
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(12px);
}

/* Messages area */
.vc-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(34,197,94,0.3) transparent;
}

/* Single message row */
.vc-msg {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
  max-width: 85%;
}
.vc-ai { align-self: flex-start; }
.vc-candidate {
  align-self: flex-end;
  flex-direction: row-reverse;
}

/* Avatar circles */
.vc-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg,#22C55E,#4ADE80);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; flex-shrink: 0;
  box-shadow: 0 0 0 1px rgba(34,197,94,0.20);
}
.vc-you {
  background: linear-gradient(135deg,#10B981,#16A34A);
  box-shadow: 0 0 12px rgba(16,185,129,0.3);
}

/* Chat bubbles */
.vc-bubble {
  padding: 0.75rem 1rem;
  border-radius: 16px;
  max-width: calc(100% - 50px);
  position: relative;
}
.vc-ai .vc-bubble {
  background: rgba(34,197,94,0.15);
  border: 1px solid rgba(34,197,94,0.25);
  border-bottom-left-radius: 4px;
}
.vc-candidate .vc-bubble {
  background: rgba(16,185,129,0.12);
  border: 1px solid rgba(16,185,129,0.2);
  border-bottom-right-radius: 4px;
}
.vc-bubble p {
  color: #E2E8F0;
  font-size: 0.92rem;
  margin: 0 0 0.3rem;
  line-height: 1.65;
}
.vc-time {
  font-size: 0.7rem;
  color: #777777;
  display: block;
  text-align: right;
}

/* Status bar */
.vc-status-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1.25rem;
  background: rgba(255,255,255,0.03);
  border-top: 1px solid rgba(255,255,255,0.06);
}

/* Waveform visualizer */
.vc-waveform {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 24px;
}
.vc-waveform span {
  display: block;
  width: 3px;
  height: 4px;
  border-radius: 2px;
  background: #777777;
  transition: height 0.1s ease, background 0.3s ease;
}
.vc-waveform.active span {
  background: #16A34A;
  animation: wave-bounce 0.6s ease-in-out infinite alternate;
}
.vc-waveform.active span:nth-child(1)  { animation-delay: 0.0s; }
.vc-waveform.active span:nth-child(2)  { animation-delay: 0.1s; }
.vc-waveform.active span:nth-child(3)  { animation-delay: 0.2s; }
.vc-waveform.active span:nth-child(4)  { animation-delay: 0.3s; }
.vc-waveform.active span:nth-child(5)  { animation-delay: 0.0s; }
.vc-waveform.active span:nth-child(6)  { animation-delay: 0.1s; }
.vc-waveform.active span:nth-child(7)  { animation-delay: 0.2s; }
.vc-waveform.active span:nth-child(8)  { animation-delay: 0.3s; }
.vc-waveform.active span:nth-child(9)  { animation-delay: 0.0s; }
.vc-waveform.active span:nth-child(10) { animation-delay: 0.1s; }

.vc-waveform.speaking span {
  background: #4ADE80;
  animation: wave-bounce 0.4s ease-in-out infinite alternate;
}

@keyframes wave-bounce {
  from { height: 4px; }
  to   { height: 22px; }
}

#vc-status-text {
  font-size: 0.82rem;
  color: #64748B;
}
.vc-status-recording { color: #EF4444 !important; }
.vc-status-processing { color: #F59E0B !important; }
.vc-status-speaking   { color: #4ADE80 !important; }
.vc-status-error      { color: #EF4444 !important; }
.vc-status-idle       { color: #64748B !important; }

/* Controls bar */
.vc-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 1rem 1.5rem;
  background: rgba(255,255,255,0.02);
  border-top: 1px solid rgba(255,255,255,0.06);
  position: relative;
}

/* Main mic button */
.vc-mic-btn {
  width: 68px; height: 68px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg,#22C55E,#16A34A);
  color: white;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  box-shadow: 0 0 0 1px rgba(34,197,94,0.20);
  transition: all 0.2s ease;
  position: relative;
  outline: none;
}
.vc-mic-btn:hover {
  transform: scale(1.08);
  box-shadow: 0 0 0 1px rgba(34,197,94,0.20);
}
.vc-mic-btn.recording {
  background: linear-gradient(135deg,#EF4444,#F97316);
  box-shadow: 0 0 30px rgba(239,68,68,0.6);
  animation: mic-pulse 1.5s ease-in-out infinite;
}
@keyframes mic-pulse {
  0%, 100% { box-shadow: 0 0 30px rgba(239,68,68,0.6); }
  50%       { box-shadow: 0 0 50px rgba(239,68,68,0.9), 0 0 0 15px rgba(239,68,68,0.1); }
}

.vc-hint {
  font-size: 0.75rem;
  color: #777777;
  position: absolute;
  bottom: 0.3rem;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
}

/* Side button */
.vc-side-btn {
  width: 42px; height: 42px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.05);
  cursor: pointer;
  font-size: 1.2rem;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s ease;
  outline: none;
}
.vc-side-btn:hover {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.2);
}
</style>
""", unsafe_allow_html=True)
