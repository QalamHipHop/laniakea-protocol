import pytest
from fastapi.testclient import TestClient
from laniakea.api.main import app # Assuming laniakea is the package name

# Initialize the TestClient
client = TestClient(app)

def test_read_main():
    """Test the root endpoint for basic connectivity and information."""
    response = client.get("/")
    assert response.status_code == 200
    # The root endpoint should return the project title and version
    assert "title" in response.json()
    assert "version" in response.json()
    assert response.json()["title"] == "Laniakea Protocol API" # Assuming a default title

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Laniakea Protocol API is operational"}

def test_get_protocol_metrics():
    """Test the endpoint to retrieve protocol metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_transactions" in data
    assert "current_block_height" in data
    assert isinstance(data["total_users"], int)

def test_post_new_transaction():
    """Test the endpoint to submit a new transaction."""
    transaction_data = {
        "sender": "0xSenderAddress",
        "recipient": "0xRecipientAddress",
        "amount": 100.5,
        "data": {"type": "knowledge_transfer"}
    }
    response = client.post("/transaction", json=transaction_data)
    assert response.status_code == 200
    assert "message" in response.json()
    assert "transaction_id" in response.json()

def test_get_block_by_height():
    """Test retrieving a block by its height."""
    # Assuming block 1 exists
    response = client.get("/blockchain/block/1")
    assert response.status_code == 200
    data = response.json()
    assert data["index"] == 1
    assert "transactions" in data

    # Test non-existent block
    response_404 = client.get("/blockchain/block/999999")
    assert response_404.status_code == 404
    assert "detail" in response_404.json()

# Note: The actual implementation of the API endpoints in laniakea/api/main.py
# is not fully known, so these tests are based on common API patterns
# and the imports seen in the snippet. They serve as a good starting point.
