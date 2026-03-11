"""Application configuration — loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """DevinClaw Federal configuration.

    All values can be overridden via environment variables.
    """

    # --- App ---
    app_name: str = "DevinClaw Federal"
    app_version: str = "1.0.0"
    debug: bool = False

    # --- Database ---
    database_url: str = "postgresql+asyncpg://devinclaw:devinclaw@localhost:5432/devinclaw"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- JWT / Auth ---
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15  # STIG V-220630
    jwt_ip_binding_enabled: bool = True

    # --- Account lockout (NIST AC-7) ---
    max_failed_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    # --- Password policy (STIG V-220629) ---
    min_password_length: int = 14

    # --- Devin integration ---
    devin_api_key: str = ""
    devin_api_base_url: str = "https://api.devin.ai/v1"
    devin_cli_path: str = "devin"
    devin_poll_interval_seconds: int = 30

    # --- Paths ---
    skills_dir: str = "skills"
    audit_dir: str = "audit"
    knowledge_dir: str = "knowledge"

    # --- Arena ---
    divergence_threshold: float = 0.35
    max_arena_sessions: int = 3

    # --- Session / Cost Limits (Section 4: Guardrail Engine) ---
    max_concurrent_sessions_per_org: int = 50
    max_concurrent_sessions_per_user: int = 10
    max_session_duration_minutes: int = 240
    max_monthly_cost_per_org: float = 50000.0
    cost_per_session_minute: float = 0.50

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
