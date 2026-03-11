"""Audit routes — searchable audit trail, export, and evidence packs.

GET /api/v1/audit                    — searchable audit trail
GET /api/v1/audit/export             — export as JSON/CSV
GET /api/v1/audit/evidence-packs     — list evidence packs
GET /api/v1/audit/evidence-packs/{id} — download evidence pack
"""

from __future__ import annotations

import csv
import io
import json
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from src.api.middleware.rbac import get_current_user
from src.config import settings

router = APIRouter(prefix="/audit", tags=["audit"])


def _get_audit_writer():  # noqa: ANN201
    from src.core.audit_writer import AuditWriter
    return AuditWriter(audit_dir=settings.audit_dir)


@router.get("")
async def list_audit_entries(
    request: Request,
    date: str | None = Query(None, description="Date filter (YYYY-MM-DD)"),
    event_type: str | None = Query(None),
    user_id: str | None = Query(None),
    session_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Search and filter the audit trail."""
    get_current_user(request)

    writer = _get_audit_writer()
    entries = writer.read_entries(
        date=date,
        event_type=event_type,
        user_id=user_id,
        session_id=session_id,
        limit=limit,
        offset=offset,
    )

    return {
        "items": entries,
        "total": len(entries),
        "limit": limit,
        "offset": offset,
    }


@router.get("/export")
async def export_audit(
    request: Request,
    format: str = Query("json", pattern=r"^(json|csv)$"),
    date: str | None = Query(None),
    event_type: str | None = Query(None),
) -> StreamingResponse:
    """Export audit trail as JSON or CSV for SIEM integration."""
    get_current_user(request)

    writer = _get_audit_writer()
    entries = writer.read_entries(date=date, event_type=event_type, limit=10000)

    if format == "csv":
        output = io.StringIO()
        if entries:
            csv_writer = csv.DictWriter(output, fieldnames=entries[0].keys())
            csv_writer.writeheader()
            for entry in entries:
                row = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in entry.items()}
                csv_writer.writerow(row)

        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit-export.csv"},
        )

    # JSON export
    return StreamingResponse(
        io.BytesIO(json.dumps(entries, indent=2, default=str).encode()),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=audit-export.json"},
    )


@router.get("/evidence-packs")
async def list_evidence_packs(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """List all evidence packs."""
    get_current_user(request)

    evidence_dir = os.path.join(settings.audit_dir, "evidence-packs")
    if not os.path.exists(evidence_dir):
        return {"items": [], "total": 0, "limit": limit, "offset": offset}

    packs = []
    for filename in sorted(os.listdir(evidence_dir), reverse=True):
        if filename.endswith(".json"):
            filepath = os.path.join(evidence_dir, filename)
            try:
                with open(filepath) as f:
                    data = json.load(f)
                packs.append({
                    "filename": filename,
                    "session_id": data.get("session_id", ""),
                    "skill_id": data.get("skill_id", ""),
                    "timestamp": data.get("timestamp", ""),
                })
            except (json.JSONDecodeError, OSError):
                continue

    total = len(packs)
    items = packs[offset : offset + limit]

    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/evidence-packs/{pack_id}")
async def get_evidence_pack(request: Request, pack_id: str) -> dict[str, Any]:
    """Download a specific evidence pack."""
    get_current_user(request)

    evidence_dir = os.path.join(settings.audit_dir, "evidence-packs")

    # Try exact filename match
    filepath = os.path.join(evidence_dir, f"{pack_id}.json")
    if not os.path.exists(filepath) and os.path.exists(evidence_dir):
        # Try finding by session_id prefix
        for filename in os.listdir(evidence_dir):
            if pack_id in filename and filename.endswith(".json"):
                filepath = os.path.join(evidence_dir, filename)
                break

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Evidence pack not found")

    with open(filepath) as f:
        return json.load(f)
