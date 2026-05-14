@echo off
echo ============================================================
echo  MockPilot AI — Starting Application
echo ============================================================
echo.

:: Check .env
if not exist .env (
    echo [WARN] .env not found. Copying from .env.example...
    copy .env.example .env
    echo [ACTION] Please edit .env and add your GROQ_API_KEY, then re-run.
    pause
    exit /b 1
)

:: Start Backend
echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "MockPilot Backend" cmd /k "python -m uvicorn backend.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul

:: Start Frontend
echo [2/2] Starting Streamlit Frontend on http://localhost:8501 ...
start "MockPilot Frontend" cmd /k "python -m streamlit run frontend/app.py"

echo.
echo ✅ MockPilot AI is running!
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:8501
echo    API Docs: http://localhost:8000/docs
echo.
pause
