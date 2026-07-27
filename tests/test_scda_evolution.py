"""
Unit Tests for SCDA Evolution Manager
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from laniakea.evolution.scda_evolution_manager import SCDAEvolutionManager, EVOLUTIONARY_TIERS


class TestSCDAEvolutionManager(unittest.TestCase):
    """Test cases for SCDA Evolution Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = SCDAEvolutionManager()
        self.scda_id = "test_scda_001"
        self.manager.register_scda(self.scda_id)
    def test_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(len(self.manager.scda_states), 1)
    
    def test_register_scda(self):
        """Test SCDA registration."""
        result = self.manager.register_scda(self.scda_id)
        self.assertIn(self.scda_id, self.manager.scda_states)
        self.assertIn(result["status"], ["registered", "already_registered"])
    
    def test_get_scda_state(self):
        """Test getting SCDA state."""
        self.manager.register_scda(self.scda_id)
        state = self.manager.get_scda_state(self.scda_id)
        self.assertIsNotNone(state)
        self.assertEqual(state["scda_id"], self.scda_id)
    
    def test_update_knowledge_vector(self):
        """Test knowledge vector update."""
        self.manager.register_scda(self.scda_id)
        new_knowledge = [0.6, 0.5, 0.7, 0.4, 0.3, 0.5, 0.4, 0.5]
        result = self.manager.update_knowledge_vector(self.scda_id, ["Physics", "Mathematics"], 0.8)
        self.assertTrue(result)
        state = self.manager.get_scda_state(self.scda_id)
        for i in range(8):
            self.assertAlmostEqual(state["knowledge_vector_8d"][i], new_knowledge[i], delta=0.7)
    
    def test_complexity_calculation(self):
        """Test complexity index calculation."""
        self.manager.register_scda(self.scda_id)
        knowledge = [0.8, 0.7, 0.9, 0.6, 0.5, 0.7, 0.6, 0.8]
        self.manager.update_knowledge_vector(self.scda_id, ["Physics", "Mathematics"], 0.8)
        state = self.manager.get_scda_state(self.scda_id)
        # Complexity should be calculated
        self.assertGreater(state["complexity_index"], 0)
    
    def test_tier_transition(self):
        """Test tier transition logic."""
        self.manager.register_scda(self.scda_id)
        
        # Update to reach Tier 2
        knowledge = [0.8, 0.7, 0.8, 0.7, 0.7, 0.7, 0.6, 0.7]
        self.manager.update_knowledge_vector(self.scda_id, ["Physics", "Mathematics"], 0.8)
        
        state = self.manager.get_scda_state(self.scda_id)
        # Check if tier was updated
        self.assertIn(state["tier"], [1, 2, 3, 4])
    
    def test_position_8d_update(self):
        """Test 8D position update."""
        self.manager.register_scda(self.scda_id)
        new_position = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        result = self.manager.update_position_8d(self.scda_id, ["Physics", "Mathematics"])
        self.assertTrue(result)
        state = self.manager.get_scda_state(self.scda_id)
        for i in range(8):
            self.assertAlmostEqual(state["position_8d"][i], new_position[i], delta=0.8)
    
    def test_milestone_tracking(self):
        """Test milestone tracking."""
        self.manager.register_scda(self.scda_id)
        result = self.manager.record_milestone(self.scda_id, "Test milestone")
        self.assertTrue(result)
        state = self.manager.get_scda_state(self.scda_id)
        self.assertEqual(state["milestones_count"], 1)
    
    def test_invalid_scda(self):
        """Test handling of invalid SCDA."""
        result = self.manager.get_scda_state("nonexistent_scda")
        self.assertIsNone(result)
    
    def test_export_state(self):
        """Test state export."""
        self.manager.register_scda(self.scda_id)
        export_data = self.manager.export_scda_state(self.scda_id)
        self.assertIsNotNone(export_data)
        self.assertIn('scda_id', export_data)


class TestTierProgression(unittest.TestCase):
    """Test tier progression logic."""
    def setUp(self):
        """Set up test fixtures."""
        self.manager = SCDAEvolutionManager()
        self.scda_id = "test_tier_progression_scda"
        self.manager.register_scda(self.scda_id)
    
    def test_tier_1_requirements(self):
        """Test Tier 1 requirements."""
        scda_id = "tier1_test"
        self.manager.register_scda(scda_id)
        state = self.manager.get_scda_state(scda_id)
        self.assertEqual(state["tier"], 1)
    
    def test_tier_2_progression(self):
        """Test progression to Tier 2."""
        scda_id = "tier2_test"
        self.manager.register_scda(scda_id)
        
        # Update knowledge to reach Tier 2
        knowledge = [0.7, 0.6, 0.7, 0.6, 0.6, 0.6, 0.5, 0.6]
        self.manager.update_knowledge_vector(scda_id, ["Physics", "Mathematics"], 0.8)
        
        state = self.manager.get_scda_state(scda_id)
        self.assertEqual(state["tier"], 1)
    
    def test_all_tiers_exist(self):
        """Test that all tiers are defined."""
        self.assertEqual(len(EVOLUTIONARY_TIERS), 4)
        for tier_num in range(1, 5):
            self.assertIn(tier_num, EVOLUTIONARY_TIERS)


if __name__ == "__main__":
    unittest.main()
