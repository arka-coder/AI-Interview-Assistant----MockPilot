<div align="center">

# 🚀 MockPilot AI
### *Your AI-Powered Interview Co-Pilot*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-F54E27)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**MockPilot AI** is a production-quality, full-stack AI interview preparation platform. Practice with adaptive AI-generated questions, get recruiter-grade feedback, analyze your resume against ATS systems, and receive a personalized 7-day improvement roadmap — all in one platform.

</div>

---

## Live link : https://ai-interview-assistant----mockpilot-gylmwcupi8x7a2dhaw7gww.streamlit.app/undefined

---

## 🎬 Demo

📽️ [Watch the demo video](https://drive.google.com/file/d/1h5Bj_-T_jc5vM3wyYvq_847WOV8ydxw1/view?usp=sharing)

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎤 **Live Interview Room** | AI-driven adaptive interviews with real-time text & voice answers |
| ⚡ **Quick Scan** | 2-minute readiness assessment with 2 targeted AI questions + instant report |
| 📄 **Resume Analyzer** | ATS compatibility scoring, keyword gap analysis, and skill extraction |
| 📊 **Interview Readiness Score** | Weighted composite score across 6 dimensions (communication, technical, confidence, etc.) |
| 🧠 **AI Hiring Insights** | Senior recruiter perspective — signals, risks, shortlist probability |
| 🗺️ **7-Day Improvement Roadmap** | Hyper-specific, prioritized daily prep plan tailored to your weak areas |
| 📈 **Analytics Dashboard** | Session history, performance trends, and progress tracking |
| 🎙️ **Voice Interview Mode** | Whisper-powered STT for voice-based answer submission |
| 🔐 **JWT Authentication** | Secure user registration, login, and session management |

---

## 🏗️ Architecture

```
MockPilot AI
├── backend/                    # FastAPI — REST API & Business Logic
│   ├── main.py                 # App entry point, CORS, router registration
│   ├── config.py               # Centralized settings via Pydantic
│   ├── api/
│   │   ├── auth_routes.py      # Register / Login / JWT
│   │   ├── interview_routes.py # Full interview session management
│   │   ├── quick_scan_routes.py# 2-question rapid assessment + scoring
│   │   ├── resume_routes.py    # Resume upload & parsing
│   │   ├── analytics_routes.py # Dashboard statistics & history
│   │   ├── voice_routes.py     # Voice interview endpoints
│   │   └── speech_routes.py    # Whisper STT integration
│   ├── services/
│   │   ├── ai_service.py       # Groq LLM — question generation & evaluation
│   │   ├── readiness_service.py# Composite scoring, AI insights, 7-day roadmap
│   │   ├── resume_service.py   # PDF/DOCX parsing, ATS scoring, keyword extraction
│   │   ├── voice_service.py    # Voice session orchestration
│   │   └── speech_service.py   # Whisper transcription
│   ├── auth/
│   │   └── jwt_handler.py      # JWT creation & verification
│   └── database/
│       └── models.py           # SQLAlchemy ORM models + DB init
│
└── frontend/                   # Streamlit — Multi-page UI
    ├── app.py                  # Main router & navigation
    ├── api_client.py           # HTTP client for backend API
    ├── views/
    │   ├── landing.py          # Hero page with feature showcase
    │   ├── dashboard.py        # Analytics, session history, stats
    │   ├── interview_room.py   # Live interview session UI
    │   ├── quick_scan.py       # Quick assessment flow
    │   ├── resume_analyzer.py  # Resume upload & ATS report
    │   ├── readiness_report.py # Full readiness score visualization
    │   └── feedback.py         # Detailed per-question feedback
    ├── components/             # Reusable UI components
    ├── styles/
    │   └── main.css            # Global glassmorphism design system
    └── assets/                 # Static images & icons
```

---

## 🤖 AI Engine

MockPilot AI uses **Groq's LLaMA 3.3 70B** model for all generative tasks:

- **Question Generation** — Role-specific, type-faithful questions across 8 interview modes:
  - Technical · Behavioral/HR · System Design · Project Discussion
  - Problem Solving · Rapid Fire · Case Study · Mixed Interview

- **Answer Evaluation** — Multi-dimensional scoring per response:
  - Communication (25%) · Technical (25%) · ATS/Resume (20%)
  - Confidence (15%) · Grammar (10%) · Relevance (5%)

- **Hiring Insights** — Simulates a senior recruiter's perspective with specific signals, hiring risks, and shortlist probability

- **7-Day Roadmap** — Generates a hyper-specific daily prep plan with prioritized tasks tailored to your weak areas

---

## 📊 Readiness Score Breakdown

The **Interview Readiness Score** is a weighted composite across six dimensions:

```
Overall Score = ATS×0.20 + Communication×0.25 + Technical×0.25
              + Confidence×0.15 + Grammar×0.10 + Relevance×0.05
```

| Score Range | Label | Status |
|---|---|---|
| 81 – 100 | 🏆 Industry Ready | Top candidate, strong shortlist signal |
| 66 – 80 | ✅ Interview Ready | Likely to pass screening rounds |
| 41 – 65 | 📈 Developing | Needs focused preparation |
| 0 – 40 | 🌱 Beginner | Significant preparation required |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | FastAPI 0.111 + Uvicorn |
| **Frontend** | Streamlit 1.35 |
| **LLM Provider** | Groq API — LLaMA 3.3 70B Versatile |
| **Speech-to-Text** | OpenAI Whisper (base model) |
| **Database** | SQLite via SQLAlchemy 2.0 |
| **Authentication** | JWT (python-jose) + Bcrypt (passlib) |
| **Resume Parsing** | pdfplumber · PyMuPDF · python-docx |
| **Charts & Analytics** | Plotly · Pandas |
| **HTTP Client** | httpx · requests |

---

## ☁️ Deployment

MockPilot AI uses a **split deployment** — each service is hosted on the platform best suited for it:

| Service | Platform | URL |
|---|---|---|
| Backend (FastAPI) | [Render](https://render.com) | `https://mockpilot-api.onrender.com` |
| Frontend (Streamlit) | [Streamlit Cloud](https://share.streamlit.io) | `https://mockpilot-ai.streamlit.app` |

**Requirements files are intentionally split:**

| File | Used by | Contains |
|---|---|---|
| `requirements.txt` | Streamlit Cloud (auto-detected) | Frontend deps only |
| `requirements-backend.txt` | Render (via `render.yaml`) | Backend deps only |

> See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full step-by-step instructions.

---

## ⚡ Quick Start (Local)

### Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/mockpilot-ai.git
cd mockpilot-ai
```

### 2. Install Dependencies

```bash
# Backend
pip install -r requirements-backend.txt

# Frontend
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
JWT_SECRET_KEY=your-secure-secret-key-change-in-production
GROQ_MODEL=llama-3.3-70b-versatile
WHISPER_MODEL=base
DATABASE_URL=sqlite:///./mockpilot.db
BACKEND_URL=http://localhost:8000
```

### 4. Launch the Application

**Option A — One-click launch (Windows):**
```bash
start.bat
```

**Option B — Manual launch (two terminals):**

```bash
# Terminal 1 — Backend (FastAPI)
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend (Streamlit)
python -m streamlit run frontend/app.py
```

### 5. Access the App

| Service | URL |
|---|---|
| 🖥️ Frontend (Streamlit) | http://localhost:8501 |
| ⚙️ Backend API | http://localhost:8000 |
| 📚 API Docs (Swagger) | http://localhost:8000/docs |

---

## 🗺️ User Journey

```
1. Register / Login  ──▶  2. Upload Resume (optional)
                                    │
                          3. Choose your path:
                         ┌──────────┴──────────┐
                    Quick Scan              Full Interview
                    (2 questions)           (adaptive session)
                         │                       │
                    4. Answer Q1 & Q2       4. Answer all questions
                    (text or voice)         (text or voice)
                         │                       │
                    5. View Readiness Report ◀───┘
                         │
                    6. AI Hiring Insights + 7-Day Roadmap
                         │
                    7. Track progress in Dashboard
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create new user account |
| `POST` | `/api/auth/login` | Login and receive JWT token |
| `POST` | `/api/interview/start` | Start a full interview session |
| `POST` | `/api/interview/answer` | Submit answer and get AI feedback |
| `POST` | `/api/quick-scan/start` | Start a 2-question quick scan |
| `POST` | `/api/quick-scan/complete` | Submit answers and get full readiness report |
| `POST` | `/api/resume/upload` | Upload and parse resume (PDF/DOCX) |
| `GET`  | `/api/analytics/dashboard` | Get session history and performance stats |
| `POST` | `/api/voice/start` | Start a voice interview session |
| `GET`  | `/health` | Health check |

Full interactive docs available at `http://localhost:8000/docs`.

---

## 🔒 Security Notes

> **⚠️ Before deploying to production:**
> - Change `JWT_SECRET_KEY` to a cryptographically secure random string
> - Restrict CORS `allow_origins` to your actual frontend domain
> - Use PostgreSQL instead of SQLite for production workloads
> - Store secrets in Render's environment variables / Streamlit Cloud Secrets — never commit `.env`

---

## 📁 Data Storage

| Data | Storage |
|---|---|
| User accounts & sessions | `mockpilot.db` (SQLite) |
| Uploaded resumes | `uploads/` directory |
| Generated reports | `reports/` directory |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using **FastAPI**, **Streamlit**, and **Groq AI**

*MockPilot AI — Ace every interview.*

</div>
