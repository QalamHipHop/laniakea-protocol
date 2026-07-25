"""Tests for the /evolution/* API surface.

The full LLM-backed ``suggest`` and ``improve`` flows need a real (or
mocked) LLM; here we cover the deterministic parts:

* ``/evolution/status`` returns 200 with a structured body
* ``/evolution/scan`` returns aggregate stats and a top_files list
* ``/evolution/improve`` refuses without ``confirm=true``
* ``/evolution/improve`` refuses to touch files outside the project root
* ``/evolution/log`` returns the on-disk tail
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from laniakea.api.main import app


client = TestClient(app)


def test_evolution_status_returns_200_and_shape():
    resp = client.get("/evolution/status")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    for key in (
        "engine_version",
        "last_scan",
        "last_suggestions",
        "evolution_log_path",
        "evolution_log_entries",
        "project_root",
    ):
        assert key in body, f"missing key {key}"
    assert isinstance(body["last_suggestions"], list)
    assert isinstance(body["evolution_log_entries"], int)


def test_evolution_scan_returns_aggregate_stats():
    resp = client.post("/evolution/scan?top_n=5")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_files"] > 0
    assert body["total_lines"] > 0
    assert isinstance(body["top_files"], list)
    assert len(body["top_files"]) <= 5
    for f in body["top_files"]:
        assert "filepath" in f
        assert "complexity_score" in f


def test_evolution_improve_requires_confirm(tmp_path: Path):
    resp = client.post(
        "/evolution/improve",
        json={
            "filepath": "laniakea/api/self_evolution_api.py",
            "suggestion": {"description": "noop"},
            "confirm": False,
        },
    )
    assert resp.status_code == 400
    assert "confirm=true" in resp.json()["detail"]


def test_evolution_improve_refuses_outside_root():
    resp = client.post(
        "/evolution/improve",
        json={
            "filepath": "/etc/passwd",
            "suggestion": {"description": "noop"},
            "confirm": True,
        },
    )
    assert resp.status_code == 400
    assert "outside project root" in resp.json()["detail"]


def test_evolution_log_returns_entries_when_log_exists():
    log_path = Path("evolution_log.json")
    if not log_path.exists():
        pytest.skip("evolution_log.json not present in this checkout")
    resp = client.get("/evolution/log?limit=2")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["path"].endswith("evolution_log.json")
    assert body["count"] >= 1
    assert isinstance(body["entries"], list)
