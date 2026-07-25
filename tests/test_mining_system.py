"""
Unit tests for the Scientific Mining System.

The miner class lives at :mod:`laniakea.blockchain.mining_system` and is
responsible for connecting the 8D blockchain to user activities by
mining knowledge tokens (KT) for validated scientific problem
solutions.
"""

import hashlib

import numpy as np
import pytest

from laniakea.blockchain.mining_system import ScientificMiner


def test_miner_initialization():
    miner = ScientificMiner()
    assert miner.difficulty_target == 0.0001
    assert miner.kt_base_reward == 10.0


def test_calculate_8d_position():
    miner = ScientificMiner()
    position = miner.calculate_8d_position(
        problem_difficulty=0.7,
        category="Physics",
        solution_quality=0.9,
        validation_confidence=0.95,
        user_complexity=0.8,
        time_taken=120.0,
        impact_factor=6.0,
        novelty_score=0.5,
    )
    assert isinstance(position, np.ndarray)
    assert position.shape == (8,)
    # All 8 coordinates should be finite
    assert np.all(np.isfinite(position))
    # The category encoding is non-zero for a known category
    assert position[1] > 0


def test_encode_category_known_and_unknown():
    miner = ScientificMiner()
    # Known categories should be encoded with the expected values
    assert miner._encode_category("Physics") == 0.1
    assert miner._encode_category("Mathematics") == 0.2
    # Unknown categories fall back to a neutral 0.5
    assert miner._encode_category("Laniakea Cosmology") == 0.5


def test_calculate_kt_reward_monotonic():
    """Higher confidence/quality/difficulty should produce a higher KT reward."""
    miner = ScientificMiner()
    problem = {"difficulty": 0.7, "category": "physics", "id": "p1", "title": "t"}
    solution = {"quality": 0.8, "user_complexity": 1.0, "time_taken": 60.0}
    high = miner._calculate_kt_reward(
        problem,
        solution,
        {"confidence": 0.9},
        np.array([0.7, 0.1, 0.8, 0.9, 0.0, 0.0, 0.5, 0.5]),
    )
    low = miner._calculate_kt_reward(
        problem,
        solution,
        {"confidence": 0.1},
        np.array([0.7, 0.1, 0.8, 0.9, 0.0, 0.0, 0.5, 0.5]),
    )
    assert high > 0
    assert low >= 0
    assert high > low


def test_mine_block_produces_valid_block():
    miner = ScientificMiner()
    problem = {"difficulty": 0.7, "category": "Physics", "id": "p-1", "title": "T"}
    solution = {"quality": 0.9, "user_complexity": 1.0, "time_taken": 120.0, "answer": "42"}
    validation = {"confidence": 0.95}
    prev_hash = hashlib.sha256(b"genesis").hexdigest()

    block = miner.mine_block(
        user_id="alice",
        problem_data=problem,
        solution_data=solution,
        validation_result=validation,
        previous_block_hash=prev_hash,
    )
    assert isinstance(block, dict)
    assert block["data"]["miner_id"] == "alice"
    assert block["data"]["problem_id"] == "p-1"
    assert block["previous_hash"] == prev_hash
    assert "hash" in block
    assert isinstance(block["position_8d"], list)
    assert len(block["position_8d"]) == 8
    # A high-quality solve should mint positive KT
    assert block["kt_reward"] > 0


def test_verify_block_round_trip():
    miner = ScientificMiner()
    problem = {"difficulty": 0.5, "category": "Physics", "id": "p-2", "title": "T"}
    solution = {"quality": 0.7, "user_complexity": 1.0, "time_taken": 60.0, "answer": "x"}
    validation = {"confidence": 0.8}
    prev_hash = hashlib.sha256(b"prev").hexdigest()

    previous_block = {
        "hash": prev_hash,
        "previous_hash": "",
        "data": {
            "miner_id": "genesis",
            "problem_id": "0",
            "solution": "genesis",
            "validation": {"confidence": 1.0},
            "timestamp": "1970-01-01T00:00:00",
        },
        "position_8d": [0.0] * 8,
    }
    block = miner.mine_block("bob", problem, solution, validation, prev_hash)
    # The freshly-mined block should verify against the genesis block
    assert miner.verify_block(block, previous_block) is True
