"""
Test configuration and fixtures for Laniakea Protocol
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator

from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from src.core.blockchain import LaniakeaChain
from src.config import get_bootstrap_nodes


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_blockchain() -> LaniakeaChain:
    """Create a mock blockchain for testing."""
    return LaniakeaChain(data_dir=":memory:")


@pytest.fixture
def sample_node_data():
    """Sample node data for testing."""
    return {
        "id": "test_node_001",
        "address": "127.0.0.1",
        "port": 8001,
        "capabilities": ["compute", "storage"],
        "stake": 1000.0
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "category": "computational",
        "description": "Test computation task",
        "difficulty": 0.5,
        "reward": 100.0
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
        {"id": "bootstrap_2", "address": "127.0.0.1", "port": 8001}
    ]