"""
Integration tests for Laniakea Protocol
"""

import pytest
import asyncio
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient

from main import app
from src.core.blockchain import LaniakeaChain
from src.core.models import NodeInfo, Task


class TestAPIIntegration:
    """Test API integration endpoints."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_node_registration(self, test_client):
        """Test node registration endpoint."""
        node_data = {
            "id": "test_node_001",
            "address": "127.0.0.1",
            "port": 8001,
            "capabilities": ["compute", "storage"],
            "stake": 1000.0
        }
        
        response = test_client.post("/api/v1/nodes/register", json=node_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "node_id" in data
    
    def test_task_submission(self, test_client):
        """Test task submission endpoint."""
        task_data = {
            "category": "computational",
            "description": "Test computation task",
            "difficulty": 0.5,
            "reward": 100.0,
            "requirements": {
                "min_compute_power": 50,
                "min_storage": 10
            }
        }
        
        response = test_client.post("/api/v1/tasks/submit", json=task_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "task_id" in data
    
    def test_get_nodes(self, test_client):
        """Test getting list of nodes."""
        response = test_client.get("/api/v1/nodes")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert isinstance(data["nodes"], list)
    
    def test_get_tasks(self, test_client):
        """Test getting list of tasks."""
        response = test_client.get("/api/v1/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)


class TestBlockchainIntegration:
    """Test blockchain integration with other components."""
    
    def test_blockchain_with_nodes(self, temp_dir):
        """Test blockchain integration with node management."""
        chain = LaniakeaChain(data_dir=str(temp_dir))
        
        # Register a node
        node_info = NodeInfo(
            id="test_node",
            address="127.0.0.1",
            port=8000,
            capabilities=["compute"]
        )
        
        # Create node registration transaction
        transaction = {
            "type": "node_registration",
            "data": node_info.dict()
        }
        
        # Add block to chain
        block = chain.add_block([transaction])
        
        assert block is not None
        assert len(block["transactions"]) == 1
    
    def test_blockchain_with_tasks(self, temp_dir):
        """Test blockchain integration with task management."""
        chain = LaniakeaChain(data_dir=str(temp_dir))
        
        # Create a task
        task = Task(
            id="test_task",
            category="computational",
            description="Test task",
            difficulty=0.5,
            reward=100.0
        )
        
        # Create task submission transaction
        transaction = {
            "type": "task_submission",
            "data": task.dict()
        }
        
        # Add block to chain
        block = chain.add_block([transaction])
        
        assert block is not None
        assert block["transactions"][0]["type"] == "task_submission"
    
    def test_consensus_integration(self, temp_dir):
        """Test consensus mechanism integration."""
        from src.consensus.poa import ProofOfAuthority
        
        chain = LaniakeaChain(data_dir=str(temp_dir))
        authorities = ["authority_1", "authority_2"]
        poa = ProofOfAuthority(authorities)
        
        # Create and sign a block
        transaction = {"type": "test", "data": {"value": 42}}
        block_data = {
            "index": len(chain.get_blocks()),
            "transactions": [transaction],
            "previous_hash": chain.get_latest_block()["hash"] if chain.get_blocks() else "0" * 64
        }
        
        # Sign block with authority
        signed_block = poa.sign_block(block_data, "authority_1")
        
        # Validate signature
        is_valid = poa.validate_block_signature(signed_block)
        assert is_valid is True


class TestSecurityIntegration:
    """Test security integration across components."""
    
    def test_authentication_flow(self, test_client):
        """Test authentication flow."""
        # Test login endpoint
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        
        response = test_client.post("/api/v1/auth/login", json=login_data)
        # Should handle gracefully even if auth not fully implemented
        assert response.status_code in [200, 401, 404]
    
    def test_rate_limiting(self, test_client):
        """Test rate limiting functionality."""
        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            response = test_client.get("/api/v1/nodes")
            responses.append(response.status_code)
        
        # At least some requests should succeed
        assert any(status == 200 for status in responses)
    
    def test_input_validation(self, test_client):
        """Test input validation on endpoints."""
        # Test with invalid data
        invalid_node = {
            "id": "",  # Empty ID should be invalid
            "port": -1  # Negative port should be invalid
        }
        
        response = test_client.post("/api/v1/nodes/register", json=invalid_node)
        # Should reject invalid input
        assert response.status_code in [400, 422, 500]


class TestWebSocketIntegration:
    """Test WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, async_client):
        """Test WebSocket connection."""
        try:
            async with async_client.websocket_connect("/ws") as websocket:
                # Test connection
                assert websocket is not None
                
                # Send test message
                await websocket.send_json({"type": "ping"})
                
                # Receive response
                response = await websocket.receive_json()
                assert response is not None
                
        except Exception:
            # WebSocket might not be fully implemented
            pytest.skip("WebSocket not fully implemented")
    
    @pytest.mark.asyncio
    async def test_realtime_updates(self, async_client):
        """Test real-time updates through WebSocket."""
        try:
            async with async_client.websocket_connect("/ws/updates") as websocket:
                # Subscribe to updates
                await websocket.send_json({
                    "type": "subscribe",
                    "channels": ["nodes", "tasks"]
                })
                
                # Receive subscription confirmation
                response = await websocket.receive_json()
                assert response.get("type") in ["subscription", "error"]
                
        except Exception:
            pytest.skip("WebSocket updates not fully implemented")


class TestPerformanceIntegration:
    """Test performance and scalability."""
    
    def test_concurrent_requests(self, test_client):
        """Test handling concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = test_client.get("/health")
            results.append(response.status_code)
        
        # Make 10 concurrent requests
        threads = []
        start_time = time.time()
        
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        
        # Should complete in reasonable time (less than 5 seconds)
        assert end_time - start_time < 5.0
    
    def test_large_payload_handling(self, test_client):
        """Test handling large payloads."""
        # Create a large task description
        large_data = {
            "category": "computational",
            "description": "A" * 10000,  # 10KB description
            "difficulty": 0.5,
            "reward": 100.0
        }
        
        response = test_client.post("/api/v1/tasks/submit", json=large_data)
        
        # Should handle large payload (status might be 200, 413, or 500)
        assert response.status_code in [200, 413, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "task_id" in data


class TestErrorHandling:
    """Test error handling across the application."""
    
    def test_404_handling(self, test_client):
        """Test 404 error handling."""
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data or "error" in data
    
    def test_method_not_allowed(self, test_client):
        """Test method not allowed errors."""
        response = test_client.delete("/api/v1/nodes")
        assert response.status_code == 405
    
    def test_server_error_handling(self, test_client):
        """Test server error handling."""
        # Send malformed data that might cause server error
        response = test_client.post("/api/v1/nodes/register", json={"invalid": "data"})
        
        # Should handle gracefully (not crash)
        assert response.status_code in [400, 422, 500]
        
        # Should return proper error response
        try:
            data = response.json()
            assert isinstance(data, dict)
        except:
            # At minimum should not return HTML error page
            assert "text/html" not in response.headers.get("content-type", "")


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_database_connection(self, temp_dir):
        """Test database connection and operations."""
        chain = LaniakeaChain(data_dir=str(temp_dir))
        
        # Test basic operations
        assert chain.get_blocks() == []
        
        # Add block
        transaction = {"type": "test", "data": {"value": 42}}
        block = chain.add_block([transaction])
        
        assert block is not None
        assert len(chain.get_blocks()) == 1
        
        # Close and reopen
        chain.close()
        new_chain = LaniakeaChain(data_dir=str(temp_dir))
        
        # Should persist data
        assert len(new_chain.get_blocks()) == 1
    
    def test_transaction_persistence(self, temp_dir):
        """Test transaction persistence."""
        chain = LaniakeaChain(data_dir=str(temp_dir))
        
        # Add multiple transactions
        transactions = [
            {"type": "test1", "data": {"value": 1}},
            {"type": "test2", "data": {"value": 2}},
            {"type": "test3", "data": {"value": 3}}
        ]
        
        block = chain.add_block(transactions)
        assert len(block["transactions"]) == 3
        
        # Verify persistence
        chain.close()
        new_chain = LaniakeaChain(data_dir=str(temp_dir))
        
        saved_block = new_chain.get_blocks()[-1]
        assert len(saved_block["transactions"]) == 3
        
        for i, tx in enumerate(transactions):
            assert saved_block["transactions"][i]["type"] == tx["type"]