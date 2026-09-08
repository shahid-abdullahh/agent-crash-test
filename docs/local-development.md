# Local Development & Testing Guide

## 1. Quick Start (Windows PowerShell)

```powershell
# 1. Automated Setup & Verification
.\scripts\setup_local.ps1

# 2. Start FastAPI Backend Server (in terminal 1)
.\.venv\Scripts\uvicorn app.main:app --app-dir backend --port 8000

# 3. Start React / Vite Developer Console (in terminal 2)
cd frontend
npm.cmd run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 2. Docker Compose (Full Stack with PostgreSQL)

```bash
docker-compose up --build
```
- PostgreSQL: `localhost:5432`
- FastAPI Backend: `http://localhost:8000`
- React Frontend: `http://localhost:5173`

---

## 3. Automated End-to-End Verification
To verify all 13 end-to-end capabilities with zero manual setup:

```powershell
.\.venv\Scripts\python scripts/verify_live_e2e.py
```

---

## 4. Resetting Demo Environment
To restore all sandboxes and recorded runs to default:

```powershell
.\scripts\reset_demo.ps1
```
Or click the **RESET STATE** button in the Developer Console header.
