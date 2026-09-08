# Technology Stack — Agent Crash Test

## Backend & API Engine
- **FastAPI**: Asynchronous REST framework.
- **Pydantic (v2)**: Strict contract parsing and domain data validation.
- **httpx**: Asynchronous HTTP client executing real agent requests against sandboxes.
- **SQLAlchemy**: ORM models supporting PostgreSQL (`asyncpg`) and SQLite.
- **Pytest + AnyIO**: Comprehensive test runner with 30 passing unit/integration tests.

## Frontend Developer Console
- **React (19)**: Component-driven developer UI.
- **Vite (8)**: Sub-second hot module replacement and production bundling.
- **TypeScript**: End-to-end static typing.
- **Tailwind CSS**: Modern high-density dark mode developer aesthetic.
- **Lucide React**: Clean iconography.

## DevOps & Local Environment
- **Docker Compose**: Multi-container orchestrator (PostgreSQL + FastAPI Backend + React Frontend).
- **PowerShell Automation**: One-click setup (`setup_local.ps1`), demo reset (`reset_demo.ps1`), and E2E verification (`verify_live_e2e.py`).
