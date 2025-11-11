"""
LaniakeA Protocol - Scientific Mining System
Connects 8D blockchain to user activities
"""

import hashlib
import json
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger("MiningSystem")


class ScientificMiner:
    """
    Scientific Mining System - Purposeful Computation
    
    Unlike traditional mining (meaningless hashing), this system:
    1. Mines by solving real scientific problems
    2. Stores solutions in 8D blockchain
    3. Generates Knowledge Tokens (KT) as rewards
    4. Creates intrinsic value through knowledge contribution
    """
    
    def __init__(self):
        """Initialize mining system"""
        self.difficulty_target = 0.0001  # Minimum validation confidence
        self.kt_base_reward = 10.0  # Base Knowledge Token reward
        
        logger.info("✅ Scientific Mining System initialized")
    
    def calculate_8d_position(
        self,
        problem_difficulty: float,
        category: str,
        solution_quality: float,
        validation_confidence: float,
        user_complexity: float,
        time_taken: float,
        impact_factor: float,
        novelty_score: float
    ) -> np.ndarray:
        """
        Calculate the 8D position for a solution block based on various scientific metrics.

        The 8D vector represents the block's location in the SCDA state space.

        Parameters
        ----------
        problem_difficulty : float
            Problem difficulty (0.0 - 1.0).
        category : str
            Scientific category of the problem.
        solution_quality : float
            Quality of the submitted solution (0.0 - 1.0).
        validation_confidence : float
            Confidence score from the validation system (0.0 - 1.0).
        user_complexity : float
            Complexity of the user's approach (0.0 - 1.0).
        time_taken : float
            Time taken to solve the problem (in seconds).
        impact_factor : float
            Estimated scientific impact (0.0 - 1.0).
        novelty_score : float
            Score for the novelty of the solution (0.0 - 1.0).

        Returns
        -------
        np.ndarray
            An 8-dimensional vector representing the block's position.
        """

        # Encode category to numerical value
        category_encoding = self._encode_category(category)
        
        # Normalize time (log scale, cap at 1 week)
        time_factor = min(np.log10(time_taken + 1) / np.log10(604800), 1.0)
        
        # Normalize user complexity (log scale)
        complexity_factor = min(np.log10(user_complexity) / np.log10(100), 1.0)
        
        position_8d = np.array([
            problem_difficulty,
            category_encoding,
            solution_quality,
            validation_confidence,
            complexity_factor,
            time_factor,
            impact_factor / 10.0,  # Normalize to [0, 1]
            novelty_score
        ])
        
        return position_8d
    
    def _encode_category(self, category: str) -> float:
        """Encode scientific category to numerical value"""
        categories = {
            'physics': 0.1,
            'mathematics': 0.2,
            'astronomy': 0.3,
            'biology': 0.4,
            'chemistry': 0.5,
            'computer_science': 0.6,
            'engineering': 0.7,
            'earth_science': 0.8,
            'social_science': 0.9,
            'general': 0.5
        }
        return categories.get(category.lower().replace(' ', '_'), 0.5)
    
    def mine_block(
        self,
        user_id: str,
        problem_data: Dict[str, Any],
        solution_data: Dict[str, Any],
        validation_result: Dict[str, Any],
        previous_block_hash: str
    ) -> Dict[str, Any]:
        """
        Mine a new block by solving a scientific problem
        
        Args:
            user_id: User identifier
            problem_data: Problem information
            solution_data: User's solution
            validation_result: Validation results
            previous_block_hash: Hash of previous block
        
        Returns:
            Mined block dictionary
        """
        # Calculate 8D position
        position_8d = self.calculate_8d_position(
            problem_difficulty=float(problem_data.get('difficulty', 0.5)),
            category=problem_data.get('category', 'general'),
            solution_quality=solution_data.get('quality', 0.8),
            validation_confidence=validation_result.get('confidence', 0.5),
            user_complexity=solution_data.get('user_complexity', 1.0),
            time_taken=solution_data.get('time_taken', 3600),
            impact_factor=self._estimate_impact(problem_data, solution_data),
            novelty_score=self._calculate_novelty(solution_data)
        )
        
        # Calculate Knowledge Token reward
        kt_reward = self._calculate_kt_reward(
            problem_data,
            solution_data,
            validation_result,
            position_8d
        )
        
        # Create block data
        timestamp = datetime.now().isoformat()
        block_data = {
            'miner_id': user_id,
            'problem_id': problem_data.get('id'),
            'problem_title': problem_data.get('title'),
            'solution': solution_data.get('answer'),
            'methodology': solution_data.get('methodology'),
            'validation': validation_result,
            'position_8d': position_8d.tolist(),
            'kt_reward': kt_reward,
            'timestamp': timestamp
        }
        
        # Calculate block hash (Proof of Knowledge, not Proof of Work)
        block_hash = self._calculate_block_hash(block_data, previous_block_hash)
        
        # Create final block
        block = {
            'hash': block_hash,
            'previous_hash': previous_block_hash,
            'data': block_data,
            'position_8d': position_8d.tolist(),
            'kt_reward': kt_reward,
            'timestamp': timestamp
        }
        
        logger.info(f"✅ Block mined: {block_hash[:16]}...")
        logger.info(f"   Position 8D: {position_8d}")
        logger.info(f"   KT Reward: {kt_reward:.2f}")
        
        return block
    
    def _calculate_block_hash(self, block_data: Dict[str, Any], previous_hash: str) -> str:
        """
        Calculate block hash (Proof of Knowledge)
        
        Unlike Proof of Work (random hashing), this is deterministic
        based on the solution quality and validation
        """
        hash_input = json.dumps({
            'previous_hash': previous_hash,
            'miner_id': block_data['miner_id'],
            'problem_id': block_data['problem_id'],
            'solution_hash': hashlib.sha256(
                block_data['solution'].encode()
            ).hexdigest(),
            'validation_confidence': block_data['validation']['confidence'],
            'timestamp': block_data['timestamp']
        }, sort_keys=True)
        
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _calculate_kt_reward(
        self,
        problem_data: Dict[str, Any],
        solution_data: Dict[str, Any],
        validation_result: Dict[str, Any],
        position_8d: np.ndarray
    ) -> float:
        """
        Calculate Knowledge Token (KT) reward.

        Formula: KT = base × D × Q × V × I × multiplier

        Parameters
        ----------
        problem_data : Dict[str, Any]
            Data related to the problem solved.
        solution_data : Dict[str, Any]
            Data related to the user's solution.
        validation_result : Dict[str, Any]
            Result from the validation system.
        position_8d : np.ndarray
            The calculated 8D position vector.

        Returns
        -------
        float
            The amount of Knowledge Tokens to be rewarded.
        """

        D = float(problem_data.get('difficulty', 0.5))
        Q = solution_data.get('quality', 0.8)
        V = validation_result.get('confidence', 0.5)
        I = self._estimate_impact(problem_data, solution_data)
        
        # Multipliers
        scarcity_multiplier = self._calculate_scarcity_multiplier(problem_data)
        novelty_multiplier = 1.0 + position_8d[7]  # Novelty dimension
        
        kt_reward = (
            self.kt_base_reward *
            D * Q * V * I *
            scarcity_multiplier *
            novelty_multiplier
        )
        
        return round(kt_reward, 2)
    
    def _estimate_impact(self, problem_data: Dict[str, Any], solution_data: Dict[str, Any]) -> float:
        """
        Estimate scientific impact of solution
        
        Returns value between 1.0 and 10.0
        """
        # Base impact from problem difficulty
        base_impact = 1.0 + float(problem_data.get('difficulty', 0.5)) * 5.0
        
        # Bonus for high-quality solutions
        quality_bonus = solution_data.get('quality', 0.8) * 2.0
        
        # Bonus for detailed methodology
        methodology_length = len(solution_data.get('methodology', ''))
        methodology_bonus = min(methodology_length / 1000, 2.0)
        
        total_impact = base_impact + quality_bonus + methodology_bonus
        
        return min(total_impact, 10.0)
    
    def _calculate_novelty(self, solution_data: Dict[str, Any]) -> float:
        """
        Calculate solution novelty score
        
        In future: compare with existing solutions using embeddings
        For now: based on methodology uniqueness
        """
        methodology = solution_data.get('methodology', '')
        
        # Simple heuristic: longer, more detailed = more novel
        novelty = min(len(methodology) / 2000, 1.0)
        
        return novelty
    
    def _calculate_scarcity_multiplier(self, problem_data: Dict[str, Any]) -> float:
        """
        Calculate scarcity multiplier
        
        Unsolved or rarely solved problems have higher multiplier
        """
        # In future: query database for solution count
        # For now: use difficulty as proxy
        difficulty = float(problem_data.get('difficulty', 0.5))
        
        # Higher difficulty = more scarce = higher multiplier
        scarcity = 1.0 + difficulty * 2.0
        
        return scarcity
    
    def verify_block(self, block: Dict[str, Any], previous_block: Dict[str, Any]) -> bool:
        """
        Verify block validity.

        Parameters
        ----------
        block : Dict[str, Any]
            Block to verify.
        previous_block : Dict[str, Any]
            Previous block in chain.

        Returns
        -------
        bool
            True if valid, False otherwise.
        """
        """
        Verify block validity.

        Parameters
        ----------
        block : Dict[str, Any]
            Block to verify.
        previous_block : Dict[str, Any]
            Previous block in chain.

        Returns
        -------
        bool
            True if valid, False otherwise.
        """

        try:
            # 1. Check hash integrity
            recalculated_hash = self._calculate_block_hash(
                block['data'],
                block['previous_hash']
            )
            if recalculated_hash != block['hash']:
                logger.error("❌ Block hash mismatch")
                return False
            
            # 2. Check chain continuity
            if block['previous_hash'] != previous_block['hash']:
                logger.error("❌ Chain continuity broken")
                return False
            
            # 3. Check 8D position validity
            position_8d = np.array(block['position_8d'])
            if not self._is_valid_8d_position(position_8d):
                logger.error("❌ Invalid 8D position")
                return False
            
            # 4. Check validation confidence
            validation_confidence = block['data']['validation']['confidence']
            if validation_confidence < self.difficulty_target:
                logger.error("❌ Validation confidence too low")
                return False
            
            logger.info(f"✅ Block verified: {block['hash'][:16]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Block verification failed: {e}")
            return False
    
    def _is_valid_8d_position(self, position: np.ndarray) -> bool:
        """Check if 8D position is valid"""
        if len(position) != 8:
            return False
        
        # All dimensions should be in [0, 1]
        if np.any(position < 0) or np.any(position > 1):
            return False
        
        return True
    
    def get_mining_statistics(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get mining statistics from blocks
        
        Args:
            blocks: List of blocks
        
        Returns:
            Statistics dictionary
        """
        if not blocks:
            return {
                'total_blocks': 0,
                'total_kt_rewards': 0.0,
                'average_difficulty': 0.0,
                'average_validation': 0.0
            }
        
        total_kt = sum(b.get('kt_reward', 0) for b in blocks)
        
        # Extract 8D positions
        positions = [np.array(b['position_8d']) for b in blocks if 'position_8d' in b]
        
        if positions:
            avg_position = np.mean(positions, axis=0)
            avg_difficulty = avg_position[0]
            avg_validation = avg_position[3]
        else:
            avg_difficulty = 0.0
            avg_validation = 0.0
        
        return {
            'total_blocks': len(blocks),
            'total_kt_rewards': round(total_kt, 2),
            'average_difficulty': round(avg_difficulty, 3),
            'average_validation': round(avg_validation, 3),
            'average_position_8d': avg_position.tolist() if positions else None
        }


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    miner = ScientificMiner()
    
    # Example problem
    problem = {
        'id': 'prob_001',
        'title': 'Quantum Entanglement Analysis',
        'difficulty': 0.75,
        'category': 'physics'
    }
    
    # Example solution
    solution = {
        'answer': 'The quantum state |ψ⟩ = (|00⟩ + |11⟩)/√2 represents maximum entanglement...',
        'methodology': 'Using Bell state analysis and density matrix formalism...',
        'quality': 0.9,
        'user_complexity': 2.5,
        'time_taken': 3600
    }
    
    # Example validation
    validation = {
        'is_valid': True,
        'confidence': 0.95,
        'reasoning': 'Solution demonstrates strong understanding of quantum mechanics'
    }
    
    # Mine block
    print("\n" + "="*60)
    print("Mining Scientific Block")
    print("="*60)
    
    block = miner.mine_block(
        user_id='user_123',
        problem_data=problem,
        solution_data=solution,
        validation_result=validation,
        previous_block_hash='0' * 64
    )
    
    print(f"\n✅ Block mined successfully!")
    print(f"   Hash: {block['hash']}")
    print(f"   KT Reward: {block['kt_reward']}")
    print(f"   Position 8D: {block['position_8d']}")
    
    # Verify block
    print("\n" + "="*60)
    print("Verifying Block")
    print("="*60)
    
    genesis_block = {'hash': '0' * 64}
    is_valid = miner.verify_block(block, genesis_block)
    print(f"\n{'✅' if is_valid else '❌'} Block verification: {'PASSED' if is_valid else 'FAILED'}")
