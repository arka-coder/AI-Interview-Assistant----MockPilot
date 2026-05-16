# 🚀 MockPilot AI — Deployment Guide

## Architecture Overview

```
MockPilot AI (Production)
├── Backend  (FastAPI)     →  Render          https://mockpilot-api.onrender.com
└── Frontend (Streamlit)   →  Streamlit Cloud  https://mockpilot-ai.streamlit.app
```

> Each platform reads a **different** requirements file — no conflicts:
> - `requirements-backend.txt` → Render (backend only)
> - `requirements.txt` (root)  → Streamlit Cloud (frontend only)

---

## Step 1: Deploy Backend on Render

1. Push your code to GitHub
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New → Web Service**
3. Connect your GitHub repo and configure:

   | Field | Value |
   |---|---|
   | **Name** | `mockpilot-api` |
   | **Runtime** | Python 3.13 ⚠️ (NOT 3.14) |
   | **Region** | Oregon (or closest to you) |
   | **Plan** | Free |
   | **Build Command** | `pip install -r requirements-backend.txt` |
   | **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
   | **Health Check Path** | `/health` |

4. Set **Environment Variables** in the Render dashboard:

   ```
   GROQ_API_KEY=your-groq-api-key-here        ← REQUIRED
   GROQ_MODEL=llama-3.3-70b-versatile
   JWT_SECRET_KEY=(leave blank — Render auto-generates)
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   DATABASE_URL=sqlite:///./mockpilot.db
   WHISPER_MODEL=base
   UPLOAD_DIR=uploads
   REPORTS_DIR=reports
   MAX_UPLOAD_SIZE_MB=10
   FRONTEND_URL=https://mockpilot-ai.streamlit.app   ← set after Step 2
   ```

5. Click **Deploy** and wait for the green ✅
6. **Copy the backend URL** — you'll need it in Step 2

---

## Step 2: Deploy Frontend on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app** and configure:

   | Field | Value |
   |---|---|
   | **Repository** | your GitHub repo |
   | **Branch** | `main` |
   | **Main file path** | `frontend/app.py` |

3. Click **Advanced settings → Secrets** and paste:

   ```toml
   BACKEND_URL = "https://mockpilot-api.onrender.com"
   ```
   > ⚠️ Replace with your actual Render URL from Step 1.

4. Click **Deploy** ✅

   Streamlit Cloud auto-reads `requirements.txt` from the repo root (frontend-only deps).

---

## Step 3: Link Frontend URL Back to Backend (CORS)

After your Streamlit app is live, add its URL to the backend's `FRONTEND_URL` env var:

1. Go to your **Render dashboard** → `mockpilot-api` → **Environment**
2. Update:
   ```
   FRONTEND_URL=https://mockpilot-ai.streamlit.app
   ```
3. Render will auto-redeploy — CORS will now allow your frontend domain ✅

---

## Requirements Files — What Goes Where

| File | Read by | Contains |
|---|---|---|
| `requirements.txt` (root) | Streamlit Cloud | Frontend deps: streamlit, groq, plotly, pandas… |
| `requirements-backend.txt` | Render (`render.yaml`) | Backend deps: fastapi, uvicorn, sqlalchemy… |
| `frontend/requirements.txt` | Local dev reference | Same as root `requirements.txt` |

---

## Environment Variables Checklist

### Backend — Render (`mockpilot-api`)
- ✅ `GROQ_API_KEY` — from [console.groq.com](https://console.groq.com)
- ✅ `FRONTEND_URL` — your Streamlit Cloud URL (set after Step 2)
- ℹ️ All other vars have safe defaults

### Frontend — Streamlit Cloud
- ✅ `BACKEND_URL` — your Render backend URL (set in Secrets, Step 2)

---

## Troubleshooting

### `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`
- **Cause**: `groq==0.9.0` is incompatible with `httpx>=0.28`
- **Fix**: Already resolved — `groq>=0.13.0` and `httpx>=0.28.0,<1.0` are pinned in both requirements files

### Frontend shows "Backend Offline" indicator
- **Check**: Is `BACKEND_URL` set correctly in Streamlit Cloud Secrets?
- **Check**: Is your Render backend service running (not sleeping)?
- **Note**: Free Render services spin down after 15 min of inactivity — first request is slow (~30s)

### 401 Unauthorized errors
- **Cause**: JWT_SECRET_KEY mismatch or expired token
- **Fix**: Ensure `JWT_SECRET_KEY` is consistently set in Render; re-login in the frontend

### "CORS policy" error in browser
- **Cause**: `FRONTEND_URL` not set in backend environment
- **Fix**: Set `FRONTEND_URL` in Render → redeploy backend (Step 3)

### File uploads failing on Render
- **Cause**: Free tier has no persistent disk — `uploads/` is ephemeral
- **Fix**: Upgrade backend to Starter plan ($7/mo) for a persistent disk

---

## Local Development

```bash
# Terminal 1 — Backend
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
python -m streamlit run frontend/app.py
```

| Service | Local URL |
|---|---|
| Frontend | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

`.env` file needed for local dev:
```env
GROQ_API_KEY=gsk_your_key_here
JWT_SECRET_KEY=any-local-secret
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=sqlite:///./mockpilot.db
BACKEND_URL=http://localhost:8000
```

---

## Cost Estimate

| Service | Platform | Cost |
|---|---|---|
| Backend (FastAPI) | Render Free | $0/mo |
| Frontend (Streamlit) | Streamlit Cloud | $0/mo |
| **Total** | | **$0/mo** |

> Upgrade Render backend to Starter ($7/mo) if you need persistent file storage.

---

## Useful Links

- [Render Dashboard](https://dashboard.render.com)
- [Streamlit Cloud](https://share.streamlit.io)
- [Groq API Console](https://console.groq.com)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Streamlit Docs](https://docs.streamlit.io)
