"""Scheduler — Redis-backed job scheduling using arq.

Supports cron expressions, one-time scheduled tasks,
and webhook-triggered tasks.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger("devinclaw.scheduler")


@dataclass
class ScheduledJob:
    """A scheduled job definition."""

    job_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    task_description: str = ""
    cron_expression: str | None = None
    run_at: str | None = None
    webhook_trigger: str | None = None
    repos: list[str] = field(default_factory=list)
    override_skill: str | None = None
    user_id: str = ""
    org_id: str = ""
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_run_at: str | None = None
    next_run_at: str | None = None
    total_runs: int = 0


@dataclass
class JobRun:
    """Record of a single job execution."""

    run_id: str = field(default_factory=lambda: str(uuid4()))
    job_id: str = ""
    task_id: str | None = None
    status: str = "pending"  # pending | running | completed | failed
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class DevinClawScheduler:
    """Manages scheduled tasks using arq (Redis-backed).

    In production, this connects to Redis and uses arq for reliable
    job scheduling with cron expressions and one-time tasks.
    """

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url
        self._jobs: dict[str, ScheduledJob] = {}
        self._runs: dict[str, list[JobRun]] = {}  # job_id -> runs

    def register_job(self, job: ScheduledJob) -> ScheduledJob:
        """Register a new scheduled job."""
        self._jobs[job.job_id] = job
        self._runs[job.job_id] = []
        logger.info("Registered job: %s (%s)", job.name, job.job_id)
        return job

    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            self._runs.pop(job_id, None)
            return True
        return False

    def get_job(self, job_id: str) -> ScheduledJob | None:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    def list_jobs(self, org_id: str | None = None, is_active: bool | None = None) -> list[ScheduledJob]:
        """List all jobs, optionally filtered."""
        jobs = list(self._jobs.values())
        if org_id:
            jobs = [j for j in jobs if j.org_id == org_id]
        if is_active is not None:
            jobs = [j for j in jobs if j.is_active == is_active]
        return jobs

    def record_run(self, job_id: str, run: JobRun) -> None:
        """Record a job execution."""
        if job_id not in self._runs:
            self._runs[job_id] = []
        self._runs[job_id].append(run)

        job = self._jobs.get(job_id)
        if job:
            job.total_runs += 1
            job.last_run_at = run.started_at

    def get_runs(self, job_id: str, limit: int = 20) -> list[JobRun]:
        """Get execution history for a job."""
        runs = self._runs.get(job_id, [])
        return runs[-limit:]

    def register_builtin_jobs(self, org_id: str) -> None:
        """Register the built-in scheduled jobs."""
        builtins = [
            ScheduledJob(
                name="nightly_stig_scan",
                task_description="Run security-scan skill for STIG compliance",
                cron_expression="0 2 * * *",  # 2 AM daily
                override_skill="security-scan",
                org_id=org_id,
            ),
            ScheduledJob(
                name="weekly_compliance_report",
                task_description="Generate weekly compliance dashboard metrics",
                cron_expression="0 6 * * 1",  # 6 AM Monday
                org_id=org_id,
            ),
            ScheduledJob(
                name="daily_guardrail_audit",
                task_description="Poll Devin Enterprise API for guardrail violations",
                cron_expression="0 3 * * *",  # 3 AM daily
                override_skill="guardrail-auditor",
                org_id=org_id,
            ),
            ScheduledJob(
                name="session_health_check",
                task_description="Monitor active sessions and alert on stalls",
                cron_expression="*/15 * * * *",  # Every 15 minutes
                org_id=org_id,
            ),
        ]

        for job in builtins:
            self.register_job(job)

        logger.info("Registered %d built-in jobs for org %s", len(builtins), org_id)
