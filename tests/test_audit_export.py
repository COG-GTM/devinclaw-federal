"""Tests for the audit export endpoint."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.config import settings
from src.core.audit_writer import AuditEntry, AuditWriter


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(settings, "audit_dir", str(tmp_path))
    writer = AuditWriter(audit_dir=str(tmp_path))
    for i in range(50):
        entry = AuditEntry(
            event_type="violation" if i % 5 == 0 else "task_start",
            user_id=f"user-{i}",
            task_description=f"Task {i}",
            violations=[{"rule": "HG-002"}] if i % 5 == 0 else [],
        )
        entry.compute_hash()
        writer.write_entry(entry)
    with TestClient(app) as test_client:
        resp = test_client.post(
            "/auth/register",
            json={
                "email": f"export-{tmp_path.name}@example.com",
                "password": "Export-Passw0rd!" + "x" * settings.min_password_length,
                "org_name": "tests",
            },
        )
        test_client.headers["Authorization"] = f"Bearer {resp.json()['access_token']}"
        yield test_client


def test_export_json_matches_entries(client: TestClient) -> None:
    resp = client.get("/api/v1/audit/export")

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/json"
    assert resp.headers["content-disposition"] == "attachment; filename=audit-export.json"
    expected = AuditWriter(audit_dir=settings.audit_dir).read_entries(limit=10000)
    assert resp.content == json.dumps(expected, indent=2, default=str).encode()


def test_export_json_filters_by_event_type(client: TestClient) -> None:
    resp = client.get("/api/v1/audit/export", params={"event_type": "violation"})

    entries = resp.json()
    assert len(entries) == 10
    assert {e["event_type"] for e in entries} == {"violation"}


def test_export_csv_matches_entries(client: TestClient) -> None:
    resp = client.get("/api/v1/audit/export", params={"format": "csv"})

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert resp.headers["content-disposition"] == "attachment; filename=audit-export.csv"
    rows = list(csv.DictReader(io.StringIO(resp.text)))
    assert len(rows) == 50
    assert json.loads(rows[0]["sdlc_checklist"]) == {}


def test_export_requires_auth(client: TestClient) -> None:
    del client.headers["Authorization"]

    assert client.get("/api/v1/audit/export").status_code == 401


def test_export_sends_fixed_size_chunks(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.api.routes.audit.EXPORT_CHUNK_SIZE", 4096)
    chunk_sizes: list[int] = []
    original = app.middleware_stack

    async def recording_app(scope, receive, send):  # noqa: ANN001, ANN202
        async def recording_send(message):  # noqa: ANN001, ANN202
            if message["type"] == "http.response.body" and message.get("body"):
                chunk_sizes.append(len(message["body"]))
            await send(message)

        await original(scope, receive, recording_send)

    monkeypatch.setattr(app, "middleware_stack", recording_app)
    resp = client.get("/api/v1/audit/export")

    assert sum(chunk_sizes) == len(resp.content)
    assert len(chunk_sizes) == -(-len(resp.content) // 4096)
    assert max(chunk_sizes) == 4096
    assert len(resp.content) > 4096
