"""Skills routes — list, inspect, and register skills.

GET  /api/v1/skills          — list all skills
GET  /api/v1/skills/{name}   — skill definition + metadata
POST /api/v1/skills          — register new skill
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.api.middleware.rbac import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])

# In-memory custom skills store
_custom_skills: dict[str, dict[str, Any]] = {}


class SkillCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100, pattern=r"^[a-z][a-z0-9-]+$")
    description: str = Field(min_length=10, max_length=500)
    triggers: list[str] = Field(min_length=1)
    risk_level: str = Field(default="medium", pattern=r"^(low|medium|high|critical)$")
    default_arena_mode: str = Field(default="single-run", pattern=r"^(single-run|arena-run)$")
    arena_sessions: int = Field(default=1, ge=1, le=3)
    mcp_required: list[str] = Field(default_factory=list)
    spokes: list[str] = Field(default_factory=list)
    hard_gates: list[str] = Field(default_factory=list)


@router.get("")
async def list_skills(request: Request) -> dict[str, Any]:
    """List all registered skills with triggers and risk levels."""
    get_current_user(request)  # Auth check

    # Import skill_router_instance from main to get loaded skills
    from src.api.main import skill_router_instance

    skills = []
    if skill_router_instance:
        for skill in skill_router_instance.list_skills():
            skills.append({
                "skill_id": skill.skill_id,
                "name": skill.name,
                "description": skill.description,
                "triggers": skill.triggers,
                "risk_level": skill.risk_level,
                "default_arena_mode": skill.default_arena_mode,
                "arena_sessions": skill.arena_sessions,
                "mcp_required": skill.mcp_required,
                "spokes": skill.spokes,
                "hard_gates": skill.hard_gates,
                "source": "built-in",
            })

    # Add custom skills
    for custom in _custom_skills.values():
        skills.append({**custom, "source": "custom"})

    return {"skills": skills, "total": len(skills)}


@router.get("/{name}")
async def get_skill(request: Request, name: str) -> dict[str, Any]:
    """Get a specific skill definition and metadata."""
    get_current_user(request)

    from src.api.main import skill_router_instance

    # Check built-in skills
    if skill_router_instance:
        skill = skill_router_instance.get_skill_by_name(name)
        if skill:
            return {
                "skill_id": skill.skill_id,
                "name": skill.name,
                "description": skill.description,
                "triggers": skill.triggers,
                "sdlc_phase": skill.sdlc_phase,
                "risk_level": skill.risk_level,
                "default_arena_mode": skill.default_arena_mode,
                "arena_sessions": skill.arena_sessions,
                "mcp_required": skill.mcp_required,
                "spokes": skill.spokes,
                "inputs": skill.inputs,
                "outputs": skill.outputs,
                "hard_gates": skill.hard_gates,
                "source": "built-in",
            }

    # Check custom skills
    custom = _custom_skills.get(name)
    if custom:
        return {**custom, "source": "custom"}

    raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")


@router.post("", status_code=201)
async def create_skill(request: Request, body: SkillCreateRequest) -> dict[str, Any]:
    """Register a new skill (from skill-creator or manual)."""
    get_current_user(request)

    if body.name in _custom_skills:
        raise HTTPException(status_code=409, detail=f"Skill '{body.name}' already exists")

    skill_data = {
        "skill_id": f"devinclaw.{body.name.replace('-', '_')}.v1",
        "name": body.name,
        "description": body.description,
        "triggers": body.triggers,
        "risk_level": body.risk_level,
        "default_arena_mode": body.default_arena_mode,
        "arena_sessions": body.arena_sessions,
        "mcp_required": body.mcp_required,
        "spokes": body.spokes,
        "hard_gates": body.hard_gates,
    }
    _custom_skills[body.name] = skill_data

    return skill_data
