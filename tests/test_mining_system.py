import pytest
import numpy as np
from laniakea_protocol.src.blockchain.mining_system import ScientificMiner

def test_miner_initialization():
    miner = ScientificMiner()
    assert miner.difficulty_target == 0.0001
    assert miner.kt_base_reward == 10.0

def test_calculate_8d_position():
    miner = ScientificMiner()
    
    # Test with typical values
    position = miner.calculate_8d_position(
        problem_difficulty=0.7,
        category="Physics",
        solution_quality=0.9,
        validation_confidence=0.95,
        user_complexity=0.8,
        time_taken=120.0,
        impact_factor=0.6,
        novelty_score=0.5
    )
    
    assert isinstance(position, np.ndarray)
    assert position.shape == (8,)
    
    # The function uses a simple linear mapping, so we can check the range
    # All inputs are roughly between 0 and 1 (except time_taken)
    # The output should be normalized to a certain range.
    # Since the exact normalization is not known from the snippet, we check for non-zero values.
    assert not np.allclose(position, np.zeros(8))

def test_calculate_knowledge_tokens():
    miner = ScientificMiner()
    
    # Test with high confidence and quality
    kt_reward = miner.calculate_knowledge_tokens(
        validation_confidence=0.9,
        solution_quality=0.8,
        problem_difficulty=0.7
    )
    
    # The reward should be greater than the base reward (10.0) if factors are high
    # Formula is: kt_base_reward * (validation_confidence * solution_quality * problem_difficulty) * factor
    # Since the exact formula is not known, we test for a reasonable range.
    # Assuming a simple multiplicative factor: 10.0 * 0.9 * 0.8 * 0.7 = 5.04 (This is less than base, which is unexpected)
    # Let's assume the formula is: kt_base_reward * (1 + (validation_confidence + solution_quality + problem_difficulty) / 3)
    # 10.0 * (1 + (0.9 + 0.8 + 0.7) / 3) = 10.0 * (1 + 0.8) = 18.0
    # Since I don't have the implementation, I will test for a positive value.
    assert kt_reward > 0
    
    # Test with low confidence and quality
    kt_reward_low = miner.calculate_knowledge_tokens(
        validation_confidence=0.1,
        solution_quality=0.1,
        problem_difficulty=0.1
    )
    
    # Reward should be lower than the high case
    assert kt_reward_low < kt_reward

def test_validate_solution():
    miner = ScientificMiner()
    
    # Test with high confidence
    is_valid_high = miner.validate_solution(validation_confidence=0.99)
    assert is_valid_high is True
    
    # Test with low confidence (below target 0.0001)
    is_valid_low = miner.validate_solution(validation_confidence=0.00005)
    assert is_valid_low is False
    
    # Test at the boundary
    is_valid_boundary = miner.validate_solution(validation_confidence=0.0001)
    assert is_valid_boundary is True
