"""
LaniakeA Protocol - Complete SCDA System
Integrates SCDA, KEA, and Dual Validation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from laniakea.intelligence.scda_model import SingleCellDigitalAccount
from src.intelligence.knowledge_extractor import KnowledgeExtractorAgent, Problem
from src.intelligence.dual_validation import DualValidationSystem

logger = logging.getLogger("SCDACompleteSystem")


class SCDACompleteSystem:
    """
    Complete SCDA Evolutionary System
    Manages the full lifecycle: Problem Discovery -> Solution -> Validation -> Evolution
    """
    
    def __init__(self, use_ai: bool = True):
        """
        Initialize complete SCDA system
        
        Args:
            use_ai: Whether to use AI for KEA and validation
        """
        self.use_ai = use_ai
        
        # Initialize components
        self.kea = KnowledgeExtractorAgent(use_openai=use_ai)
        self.validator = DualValidationSystem(use_ai=use_ai, use_quantum=True)
        
        # SCDA registry
        self.scda_registry: Dict[str, SingleCellDigitalAccount] = {}
        
        # Problem pool
        self.problem_pool: List[Problem] = []
        self.active_problems: Dict[str, Problem] = {}
        
        # Evolution log
        self.evolution_log = []
        
        logger.info("✅ SCDA Complete System initialized")
    
    def create_user(self, user_id: str) -> SingleCellDigitalAccount:
        """
        Create a new SCDA for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            New SCDA instance
        """
        if user_id in self.scda_registry:
            logger.warning(f"User {user_id} already exists")
            return self.scda_registry[user_id]
        
        scda = SingleCellDigitalAccount(identity=user_id)
        self.scda_registry[user_id] = scda
        
        logger.info(f"✅ Created SCDA for user {user_id}")
        logger.info(f"   Initial Complexity: {scda.complexity_index:.6f}")
        logger.info(f"   Initial Energy: {scda.energy:.2f}")
        
        return scda
    
    def get_user(self, user_id: str) -> Optional[SingleCellDigitalAccount]:
        """Get SCDA for a user"""
        return self.scda_registry.get(user_id)
    
    def refresh_problem_pool(self, 
                            category: Optional[str] = None,
                            difficulty_level: Optional[str] = None,
                            count: int = 20):
        """
        Refresh the problem pool with new problems from KEA
        
        Args:
            category: Problem category
            difficulty_level: Difficulty level
            count: Number of problems to generate
        """
        logger.info(f"🔄 Refreshing problem pool...")
        
        new_problems = self.kea.extract_problems(
            category=category,
            difficulty_level=difficulty_level,
            count=count
        )
        
        self.problem_pool.extend(new_problems)
        
        logger.info(f"✅ Added {len(new_problems)} problems to pool (total: {len(self.problem_pool)})")
    
    def get_problem_for_user(self, user_id: str) -> Optional[Problem]:
        """
        Get an appropriate problem for a user based on their SCDA complexity
        
        Args:
            user_id: User identifier
            
        Returns:
            Problem instance or None
        """
        scda = self.get_user(user_id)
        if not scda:
            logger.error(f"User {user_id} not found")
            return None
        
        # Ensure problem pool has problems
        if len(self.problem_pool) < 5:
            self.refresh_problem_pool(count=20)
        
        # Find problem matching user's complexity level
        # Problems should be challenging but not impossible
        target_difficulty = min(scda.complexity_index + 0.1, 0.95)
        
        # Find closest problem
        best_problem = None
        best_diff = float('inf')
        
        for problem in self.problem_pool:
            if problem.problem_id in self.active_problems:
                continue
            
            diff = abs(problem.difficulty - target_difficulty)
            if diff < best_diff:
                best_diff = diff
                best_problem = problem
        
        if best_problem:
            self.active_problems[best_problem.problem_id] = best_problem
            logger.info(f"✅ Assigned problem '{best_problem.title}' to user {user_id}")
            logger.info(f"   Difficulty: {best_problem.difficulty:.2f} (target: {target_difficulty:.2f})")
        
        return best_problem
    
    def submit_solution(self,
                       user_id: str,
                       problem_id: str,
                       answer: str,
                       methodology: str,
                       quality: float = 0.8) -> Dict[str, Any]:
        """
        Submit a solution for validation and potential evolution
        
        Args:
            user_id: User identifier
            problem_id: Problem identifier
            answer: Solution answer
            methodology: Solution methodology
            quality: Self-assessed quality (0.0 to 1.0)
            
        Returns:
            Result dictionary
        """
        logger.info(f"📝 Processing solution from user {user_id} for problem {problem_id}")
        
        # Get SCDA
        scda = self.get_user(user_id)
        if not scda:
            return {'success': False, 'error': 'User not found'}
        
        # Get problem
        problem = self.active_problems.get(problem_id)
        if not problem:
            return {'success': False, 'error': 'Problem not found or not active'}
        
        # Prepare solution data
        solution = {
            'answer': answer,
            'methodology': methodology,
            'quality': quality,
            'user_id': user_id,
            'submitted_at': datetime.utcnow().isoformat()
        }
        
        # Validate solution using Dual Validation
        validation_result = self.validator.validate(
            problem=problem.to_dict(),
            solution=solution
        )
        
        is_valid = validation_result['is_valid']
        confidence = validation_result['confidence']
        
        logger.info(f"🔍 Validation result: {'✅ VALID' if is_valid else '❌ INVALID'} (confidence: {confidence:.2%})")
        
        # Attempt evolution
        initial_complexity = scda.complexity_index
        
        evolution_success = scda.attempt_solve_problem(
            problem_difficulty=problem.difficulty,
            solution_quality=quality,
            is_valid=is_valid
        )
        
        final_complexity = scda.complexity_index
        complexity_gain = final_complexity - initial_complexity
        
        # Log evolution
        evolution_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'problem_id': problem_id,
            'problem_title': problem.title,
            'problem_difficulty': problem.difficulty,
            'solution_quality': quality,
            'validation': validation_result,
            'evolution_success': evolution_success,
            'initial_complexity': initial_complexity,
            'final_complexity': final_complexity,
            'complexity_gain': complexity_gain
        }
        
        self.evolution_log.append(evolution_record)
        
        # Remove from active problems if solved
        if evolution_success:
            del self.active_problems[problem_id]
        
        # Prepare result
        result = {
            'success': True,
            'evolution_success': evolution_success,
            'validation': validation_result,
            'complexity': {
                'initial': initial_complexity,
                'final': final_complexity,
                'gain': complexity_gain
            },
            'scda_state': scda.get_state()
        }
        
        if evolution_success:
            logger.info(f"🎉 Evolution successful! Complexity: {initial_complexity:.6f} → {final_complexity:.6f} (+{complexity_gain:.6f})")
        else:
            logger.info(f"❌ Evolution failed. Complexity unchanged: {initial_complexity:.6f}")
        
        return result
    
    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a user"""
        scda = self.get_user(user_id)
        if not scda:
            return None
        
        # Get user's evolution history
        user_evolutions = [e for e in self.evolution_log if e['user_id'] == user_id]
        
        successful_evolutions = [e for e in user_evolutions if e['evolution_success']]
        
        stats = {
            'user_id': user_id,
            'current_state': scda.get_state(),
            'total_attempts': len(user_evolutions),
            'successful_evolutions': len(successful_evolutions),
            'success_rate': len(successful_evolutions) / len(user_evolutions) if user_evolutions else 0,
            'total_complexity_gain': sum(e['complexity_gain'] for e in successful_evolutions),
            'average_problem_difficulty': sum(e['problem_difficulty'] for e in user_evolutions) / len(user_evolutions) if user_evolutions else 0,
            'recent_evolutions': user_evolutions[-5:]  # Last 5
        }
        
        return stats
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        total_users = len(self.scda_registry)
        total_evolutions = len(self.evolution_log)
        successful_evolutions = sum(1 for e in self.evolution_log if e['evolution_success'])
        
        stats = {
            'total_users': total_users,
            'total_problems_in_pool': len(self.problem_pool),
            'active_problems': len(self.active_problems),
            'total_evolution_attempts': total_evolutions,
            'successful_evolutions': successful_evolutions,
            'success_rate': successful_evolutions / total_evolutions if total_evolutions else 0,
            'validation_stats': self.validator.get_validation_stats()
        }
        
        return stats
    
    def save_state(self, filepath: str):
        """Save system state to file"""
        try:
            state = {
                'scda_registry': {uid: scda.get_state() for uid, scda in self.scda_registry.items()},
                'problem_pool': [p.to_dict() for p in self.problem_pool],
                'evolution_log': self.evolution_log,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"✅ System state saved to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")
    
    def load_state(self, filepath: str):
        """Load system state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Restore SCDA registry
            for uid, scda_state in state.get('scda_registry', {}).items():
                scda = SingleCellDigitalAccount(identity=uid)
                scda.complexity_index = scda_state['complexity_index']
                scda.energy = scda_state['energy']
                scda.knowledge_vector = scda_state['knowledge_vector']
                self.scda_registry[uid] = scda
            
            # Restore problem pool
            self.problem_pool = [Problem.from_dict(p) for p in state.get('problem_pool', [])]
            
            # Restore evolution log
            self.evolution_log = state.get('evolution_log', [])
            
            logger.info(f"✅ System state loaded from {filepath}")
            logger.info(f"   Users: {len(self.scda_registry)}")
            logger.info(f"   Problems: {len(self.problem_pool)}")
            logger.info(f"   Evolution records: {len(self.evolution_log)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load state: {e}")


# Example usage and demonstration
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    print("\n" + "="*60)
    print("LaniakeA Protocol - Complete SCDA System Demo")
    print("="*60)
    
    # Initialize system
    system = SCDACompleteSystem(use_ai=True)
    
    # Create users
    print("\n📝 Creating users...")
    user1 = system.create_user("Alice")
    user2 = system.create_user("Bob")
    
    # Refresh problem pool
    print("\n🔄 Generating problems...")
    system.refresh_problem_pool(category='physics', difficulty_level='intermediate', count=5)
    
    # Get problems for users
    print("\n📚 Assigning problems...")
    problem1 = system.get_problem_for_user("Alice")
    problem2 = system.get_problem_for_user("Bob")
    
    # Simulate Alice solving her problem
    print(f"\n🧪 Alice solving: {problem1.title}")
    result1 = system.submit_solution(
        user_id="Alice",
        problem_id=problem1.problem_id,
        answer="Detailed analysis of the dark matter distribution using gravitational lensing techniques. The NFW profile shows concentration parameter c=5.2, indicating a relaxed cluster. Total mass within virial radius is 2.3×10^14 solar masses.",
        methodology="Applied ray-tracing simulations with LENSTOOL. Used Bayesian MCMC for parameter fitting. Cross-validated with weak lensing shear data from HST observations.",
        quality=0.85
    )
    
    print(f"\n📊 Result for Alice:")
    print(f"   Evolution: {'✅ SUCCESS' if result1['evolution_success'] else '❌ FAILED'}")
    print(f"   Complexity: {result1['complexity']['initial']:.6f} → {result1['complexity']['final']:.6f}")
    print(f"   Gain: +{result1['complexity']['gain']:.6f}")
    
    # Get user stats
    print("\n📈 Alice's Statistics:")
    alice_stats = system.get_user_stats("Alice")
    print(f"   Total attempts: {alice_stats['total_attempts']}")
    print(f"   Success rate: {alice_stats['success_rate']:.2%}")
    print(f"   Total complexity gain: {alice_stats['total_complexity_gain']:.6f}")
    
    # System stats
    print("\n🌐 System Statistics:")
    sys_stats = system.get_system_stats()
    print(f"   Total users: {sys_stats['total_users']}")
    print(f"   Problems in pool: {sys_stats['total_problems_in_pool']}")
    print(f"   Evolution attempts: {sys_stats['total_evolution_attempts']}")
    print(f"   Success rate: {sys_stats['success_rate']:.2%}")
    
    # Save state
    print("\n💾 Saving system state...")
    system.save_state('/tmp/laniakea_scda_state.json')
    
    print("\n✅ Demo complete!")
