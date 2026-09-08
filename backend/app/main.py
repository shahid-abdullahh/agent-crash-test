from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.tasks import router as tasks_router
from app.api.runs import router as runs_router
from app.api.reliability import router as reliability_router
from app.api.comparison import router as comparison_router
from app.sandbox.router import router as sandbox_router

app = FastAPI(
    title="Agent Crash Test API",
    description="Test APIs the way autonomous agents actually use them. Controlled sandbox, real traces, deterministic evaluation & failure diagnosis.",
    version="0.1.0",
)

# CORS middleware for local frontend/tooling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(sandbox_router)
app.include_router(tasks_router)
app.include_router(runs_router)
app.include_router(reliability_router)
app.include_router(comparison_router)
