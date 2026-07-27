"""
Test configuration and fixtures for Laniakea Protocol
Author: LaniakeA Dev
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import pytest

# Ensure project root is on sys.path so `main` and `laniakea` resolve correctly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_node_data():
    """Sample node data for testing."""
    return {
        "id": "test_node_001",
        "address": "127.0.0.1",
        "port": 8001,
        "capabilities": ["compute", "storage"],
        "stake": 1000.0,
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "category": "computational",
        "description": "Test computation task",
        "difficulty": 0.5,
        "reward": 100.0,
    }


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_bootstrap_nodes():
    """Mock bootstrap nodes for testing."""
    return [
        {"id": "bootstrap_1", "address": "127.0.0.1", "port": 8000},
        {"id": "bootstrap_2", "address": "127.0.0.1", "port": 8001},
    ]


@pytest.fixture
def app_client():
    """FastAPI synchronous test client (lazy import to avoid heavy boot during collection)."""
    from fastapi.testclient import TestClient
    from laniakea.api.main import app

    return TestClient(app)
