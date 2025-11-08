"""
Test core components of Laniakea Protocol
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from laniakea.core.hypercube_blockchain import HypercubeBlockchain
from src.core.models import NodeInfo, Task, ValueVector
from src.consensus.poa import ProofOfAuthority
from src.consensus.pov import ProofOfValue


class TestHypercubeBlockchain:
    """Test the Laniakea blockchain implementation."""
    
    def test_blockchain_initialization(self, temp_dir):
        """Test blockchain initialization."""
        chain = HypercubeBlockchain(node_id="test_node")
        assert chain is not None
        assert len(chain.get_blocks()) == 0
    
    def test_block_creation(self, mock_blockchain):
        """Test block creation and validation."""
        # Create a sample transaction
        transaction = {
            "type": "task_submission",
            "data": {"task_id": "test_task", "solution": "test_solution"}
        }
        
        # Add block
        block = mock_blockchain.add_block([transaction])
        
        assert block is not None
        assert block["transactions"] == [transaction]
        assert mock_blockchain.get_latest_block() == block
    
    def test_chain_validation(self, mock_blockchain):
        """Test blockchain validation."""
        # Add valid block
        transaction = {"type": "test", "data": {"value": 42}}
        block = mock_blockchain.add_block([transaction])
        
        # Validate chain
        assert mock_blockchain.validate_chain() is True
    
    def test_invalid_chain_detection(self, mock_blockchain):
        """Test detection of invalid chains."""
        # Add valid block
        transaction = {"type": "test", "data": {"value": 42}}
        mock_blockchain.add_block([transaction])
        
        # Tamper with the chain
        mock_blockchain.blocks[-1]["hash"] = "invalid_hash"
        
        # Should detect invalid chain
        assert mock_blockchain.validate_chain() is False


class TestProofOfAuthority:
    """Test Proof of Authority consensus."""
    
    def test_poa_initialization(self):
        """Test PoA initialization."""
        authorities = ["node1", "node2", "node3"]
        poa = ProofOfAuthority(authorities)
        assert poa.authorities == authorities
    
    def test_authority_validation(self):
        """Test authority node validation."""
        authorities = ["node1", "node2", "node3"]
        poa = ProofOfAuthority(authorities)
        
        # Valid authority
        assert poa.is_authority("node1") is True
        
        # Invalid authority
        assert poa.is_authority("invalid_node") is False
    
    def test_block_signing(self):
        """Test block signing by authorities."""
        authorities = ["node1", "node2", "node3"]
        poa = ProofOfAuthority(authorities)
        
        block = {"index": 1, "transactions": []}
        
        # Authority node can sign
        signature = poa.sign_block(block, "node1")
        assert signature is not None
        
        # Non-authority cannot sign
        with pytest.raises(Exception):
            poa.sign_block(block, "invalid_node")


class TestProofOfValue:
    """Test Proof of Value consensus."""
    
    def test_pov_initialization(self):
        """Test PoV initialization."""
        pov = ProofOfValue()
        assert pov is not None
    
    def test_value_calculation(self):
        """Test value calculation for contributions."""
        pov = ProofOfValue()
        
        # Sample contribution
        contribution = {
            "compute_power": 100,
            "storage": 50,
            "network_bandwidth": 25
        }
        
        value = pov.calculate_value(contribution)
        assert value > 0
        assert isinstance(value, float)
    
    def test_reward_distribution(self):
        """Test reward distribution based on value."""
        pov = ProofOfValue()
        
        contributions = [
            {"node": "node1", "value": 100},
            {"node": "node2", "value": 200},
            {"node": "node3", "value": 150}
        ]
        
        total_reward = 1000
        rewards = pov.distribute_rewards(contributions, total_reward)
        
        assert sum(rewards.values()) == total_reward
        assert rewards["node2"] > rewards["node1"]  # Higher value = higher reward


class TestNodeInfo:
    """Test NodeInfo model."""
    
    def test_node_info_creation(self):
        """Test NodeInfo creation."""
        node = NodeInfo(
            id="test_node",
            address="127.0.0.1",
            port=8000,
            capabilities=["compute", "storage"]
        )
        
        assert node.id == "test_node"
        assert node.address == "127.0.0.1"
        assert node.port == 8000
        assert "compute" in node.capabilities
    
    def test_node_info_validation(self):
        """Test NodeInfo validation."""
        # Valid node info
        node = NodeInfo(
            id="valid_node",
            address="192.168.1.1",
            port=8000,
            capabilities=["compute"]
        )
        assert node.is_valid()
        
        # Invalid node info (negative port)
        invalid_node = NodeInfo(
            id="invalid_node",
            address="192.168.1.1",
            port=-1,
            capabilities=["compute"]
        )
        assert not invalid_node.is_valid()


class TestTask:
    """Test Task model."""
    
    def test_task_creation(self):
        """Test Task creation."""
        task = Task(
            id="test_task",
            category="computational",
            description="Test computation task",
            difficulty=0.5,
            reward=100.0
        )
        
        assert task.id == "test_task"
        assert task.category == "computational"
        assert 0 <= task.difficulty <= 1
        assert task.reward > 0
    
    def test_task_validation(self):
        """Test Task validation."""
        # Valid task
        task = Task(
            id="valid_task",
            category="storage",
            description="Store important data",
            difficulty=0.3,
            reward=50.0
        )
        assert task.is_valid()
        
        # Invalid task (negative reward)
        invalid_task = Task(
            id="invalid_task",
            category="compute",
            description="Invalid task",
            difficulty=0.5,
            reward=-10.0
        )
        assert not invalid_task.is_valid()


class TestValueVector:
    """Test ValueVector model."""
    
    def test_value_vector_creation(self):
        """Test ValueVector creation."""
        vector = ValueVector(
            computational_power=100,
            storage_capacity=50,
            network_bandwidth=25,
            reputation_score=0.8
        )
        
        assert vector.computational_power == 100
        assert vector.storage_capacity == 50
        assert vector.network_bandwidth == 25
        assert vector.reputation_score == 0.8
    
    def test_value_vector_magnitude(self):
        """Test value vector magnitude calculation."""
        vector = ValueVector(
            computational_power=3,
            storage_capacity=4,
            network_bandwidth=0,
            reputation_score=0
        )
        
        magnitude = vector.get_magnitude()
        assert magnitude == 5.0  # sqrt(3^2 + 4^2)
    
    def test_value_vector_comparison(self):
        """Test value vector comparison."""
        vector1 = ValueVector(
            computational_power=10,
            storage_capacity=10,
            network_bandwidth=10,
            reputation_score=0.5
        )
        
        vector2 = ValueVector(
            computational_power=5,
            storage_capacity=5,
            network_bandwidth=5,
            reputation_score=0.5
        )
        
        assert vector1 > vector2
        assert not vector2 > vector1