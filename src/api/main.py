"""DevinClaw Federal — FastAPI application entry point."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.audit_log import AuditLogMiddleware
from src.api.middleware.inactivity_timeout import InactivityTimeoutMiddleware
from src.api.middleware.zero_trust import ZeroTrustMiddleware
from src.api.routes import audit, auth, compliance, memory, schedule, sessions, skills, tasks, visibility, ws
from src.config import settings
from src.core.skill_router import SkillRouter

logger = logging.getLogger("devinclaw")

skill_router_instance: SkillRouter | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle."""
    global skill_router_instance  # noqa: PLW0603

    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )
    logger.info("DevinClaw Federal v%s starting up", settings.app_version)

    # Load skill router
    skill_router_instance = SkillRouter(skills_dir=settings.skills_dir, audit_dir=settings.audit_dir)
    skill_router_instance.load()
    logger.info("Skill router loaded — %d skills registered", len(skill_router_instance.skills))

    yield

    logger.info("DevinClaw Federal shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Standalone DevinClaw Federal Orchestrator — production-grade AI modernization for federal systems.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middleware (order matters: last added = first executed) ---
app.add_middleware(AuditLogMiddleware)
app.add_middleware(InactivityTimeoutMiddleware)
app.add_middleware(ZeroTrustMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth.router)
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(skills.router, prefix="/api/v1")
app.include_router(schedule.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(compliance.router, prefix="/api/v1")
app.include_router(visibility.router)
app.include_router(ws.router)


# --- Health ---
@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "service": "devinclaw-federal",
    }
