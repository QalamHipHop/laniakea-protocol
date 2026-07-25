"""
Smoke tests for the LaniakeA Protocol public API.

These tests are intentionally written against the *current* API surface
so they fail fast if a router is removed or renamed.  They cover the
most representative endpoints across subsystems.
"""

from fastapi.testclient import TestClient

from laniakea.api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert "version" in body
    assert "subsystems" in body
    assert isinstance(body["subsystems"], dict)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "uptime_seconds" in body


def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["protocol_version"] == "1.0.0-Unified"
    assert body["project_name"] == "Laniakea Protocol"


def test_discovery_endpoint():
    response = client.get("/discovery")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)


def test_blockchain_info():
    response = client.get("/blockchain/info")
    assert response.status_code == 200
    body = response.json()
    # Should expose something about the chain (height, difficulty, etc.)
    assert isinstance(body, dict)


def test_token_info():
    response = client.get("/token/info")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)


def test_knowledge_market_types():
    response = client.get("/knowledge_market/types")
    assert response.status_code == 200
    body = response.json()
    assert "types" in body and isinstance(body["types"], list)
    assert "domains" in body and isinstance(body["domains"], list)
    assert body["type_count"] == len(body["types"])
    assert body["domain_count"] == len(body["domains"])


def test_diplomacy_alliances():
    response = client.get("/diplomacy/alliances")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, (list, dict))


def test_core_status():
    response = client.get("/core/status")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)


def test_dashboard_metrics():
    response = client.get("/dashboard/metrics")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)


def test_observability_requests():
    response = client.get("/observability/requests")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
