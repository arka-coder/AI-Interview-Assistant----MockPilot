Write-Host "============================================================"
Write-Host " MockPilot AI — Starting Application"
Write-Host "============================================================"
Write-Host ""

if (-not (Test-Path ".env")) {
    Write-Host "[WARN] .env not found. Copying from .env.example..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" -Destination ".env"
    }
    Write-Host "[ACTION] Please edit .env and add your GROQ_API_KEY, then re-run."
    pause
    exit 1
}

Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000 ..."
Start-Process "cmd.exe" -ArgumentList "/k title MockPilot Backend & python -m uvicorn backend.main:app --reload --port 8000"
Start-Sleep -Seconds 3

Write-Host "[2/2] Starting Streamlit Frontend on http://localhost:8502 ..."
Start-Process "cmd.exe" -ArgumentList "/k title MockPilot Frontend & python -m streamlit run frontend/app.py"

Write-Host ""
Write-Host "✅ MockPilot AI is running!"
Write-Host "   Backend:  http://localhost:8000"
Write-Host "   Frontend: http://localhost:8502"
Write-Host "   API Docs: http://localhost:8000/docs"
Write-Host ""
