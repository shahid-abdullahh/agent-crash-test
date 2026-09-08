# ==============================================================================
# Agent Crash Test — Local Setup & Verification Script (Windows PowerShell)
# ==============================================================================
Write-Host ">>> [1/4] Checking Python Virtual Environment..." -ForegroundColor Cyan
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating Python virtual environment in .venv..." -ForegroundColor Yellow
    python -m venv .venv
}
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r backend\requirements.txt

Write-Host "`n>>> [2/4] Running Backend Test Suite (Pytest)..." -ForegroundColor Cyan
.\.venv\Scripts\python -m pytest -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed! Aborting." -ForegroundColor Red
    exit 1
}

Write-Host "`n>>> [3/4] Installing & Building Frontend..." -ForegroundColor Cyan
Push-Location frontend
if (-not (Test-Path "node_modules")) {
    npm.cmd install
}
npm.cmd run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed! Aborting." -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host "`n>>> [4/4] Local Environment Ready!" -ForegroundColor Green
Write-Host "To start the backend:" -ForegroundColor White
Write-Host "  .\.venv\Scripts\uvicorn app.main:app --app-dir backend --port 8000" -ForegroundColor Yellow
Write-Host "To start the frontend:" -ForegroundColor White
Write-Host "  cd frontend; npm.cmd run dev" -ForegroundColor Yellow
Write-Host "Open Developer Console: http://localhost:5173" -ForegroundColor Green
