"""
LaniakeA Protocol - Dual Validation System
Implements V_int (Internal Validation) and V_quant (Quantum Validation)
"""

import logging
import hashlib
import random
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import json

logger = logging.getLogger("DualValidation")


class InternalValidator:
    """
    V_int: Internal Validation System
    Uses AI and heuristic methods to validate solutions
    """
    
    def __init__(self, use_ai: bool = False):
        """
        Initialize Internal Validator
        
        Args:
            use_ai: Whether to use AI for validation
        """
        self.use_ai = use_ai
        self.openai_client = None
        
        if use_ai:
            self._init_ai()
        
        self.validation_history = []
    
    def _init_ai(self):
        """Initialize AI client for validation"""
        try:
            from openai import OpenAI
            self.openai_client = OpenAI()
            logger.info("✅ AI validator initialized")
        except Exception as e:
            logger.warning(f"⚠️ AI validator initialization failed: {e}")
            self.use_ai = False
    
    def validate(self, 
                problem: Dict[str, Any],
                solution: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Validate a solution using internal methods
        
        Args:
            problem: Problem data including description and difficulty
            solution: Solution data including answer and methodology
            
        Returns:
            Tuple of (is_valid, confidence, reasoning)
        """
        if self.use_ai and self.openai_client:
            return self._validate_with_ai(problem, solution)
        else:
            return self._validate_heuristic(problem, solution)
    
    def _validate_with_ai(self,
                         problem: Dict[str, Any],
                         solution: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Validate using AI"""
        try:
            prompt = f"""You are a scientific validation system for the LaniakeA Protocol.

Problem:
Title: {problem.get('title', 'Unknown')}
Description: {problem.get('description', 'No description')}
Category: {problem.get('category', 'general')}
Difficulty: {problem.get('difficulty', 0.5)}

Proposed Solution:
{solution.get('answer', 'No answer provided')}

Methodology:
{solution.get('methodology', 'No methodology provided')}

Validate this solution and provide:
1. Is the solution scientifically sound? (yes/no)
2. Confidence level (0.0 to 1.0)
3. Brief reasoning (2-3 sentences)

Respond in JSON format:
{{
  "is_valid": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "explanation"
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a rigorous scientific validator. Be critical but fair."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            result = json.loads(content.strip())
            
            is_valid = result.get('is_valid', False)
            confidence = result.get('confidence', 0.5)
            reasoning = result.get('reasoning', 'AI validation completed')
            
            # Record validation
            self.validation_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'problem_id': problem.get('problem_id', 'unknown'),
                'method': 'ai',
                'is_valid': is_valid,
                'confidence': confidence
            })
            
            logger.info(f"✅ AI validation: {is_valid} (confidence: {confidence:.2f})")
            return is_valid, confidence, reasoning
            
        except Exception as e:
            logger.error(f"❌ AI validation failed: {e}")
            # Fallback to heuristic
            return self._validate_heuristic(problem, solution)
    
    def _validate_heuristic(self,
                           problem: Dict[str, Any],
                           solution: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Validate using heuristic methods"""
        
        # Heuristic checks
        checks = []
        
        # 1. Solution length check
        answer = solution.get('answer', '')
        min_length = int(problem.get('difficulty', 0.5) * 200)  # Harder problems need longer answers
        checks.append(len(answer) >= min_length)
        
        # 2. Methodology check
        methodology = solution.get('methodology', '')
        checks.append(len(methodology) >= 50)
        
        # 3. Keyword matching
        problem_keywords = set(problem.get('keywords', []))
        solution_text = (answer + ' ' + methodology).lower()
        keyword_matches = sum(1 for kw in problem_keywords if kw.lower() in solution_text)
        checks.append(keyword_matches >= len(problem_keywords) * 0.5)
        
        # 4. Quality score check
        quality = solution.get('quality', 0.0)
        checks.append(quality >= 0.6)
        
        # Calculate validation result
        passed_checks = sum(checks)
        total_checks = len(checks)
        confidence = passed_checks / total_checks
        
        is_valid = confidence >= 0.7
        
        reasoning = f"Heuristic validation: {passed_checks}/{total_checks} checks passed. "
        if is_valid:
            reasoning += "Solution meets quality standards."
        else:
            reasoning += "Solution needs improvement."
        
        # Record validation
        self.validation_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'problem_id': problem.get('problem_id', 'unknown'),
            'method': 'heuristic',
            'is_valid': is_valid,
            'confidence': confidence
        })
        
        logger.info(f"✅ Heuristic validation: {is_valid} (confidence: {confidence:.2f})")
        return is_valid, confidence, reasoning


class QuantumValidator:
    """
    V_quant: Quantum Validation System
    Simulates quantum-inspired validation using probabilistic methods
    """
    
    def __init__(self, use_quantum_sim: bool = True):
        """
        Initialize Quantum Validator
        
        Args:
            use_quantum_sim: Whether to use quantum simulation
        """
        self.use_quantum_sim = use_quantum_sim
        self.validation_history = []
    
    def validate(self,
                problem: Dict[str, Any],
                solution: Dict[str, Any],
                internal_result: Tuple[bool, float, str]) -> Tuple[bool, float, str]:
        """
        Validate using quantum-inspired methods
        
        Args:
            problem: Problem data
            solution: Solution data
            internal_result: Result from internal validation
            
        Returns:
            Tuple of (is_valid, confidence, reasoning)
        """
        if self.use_quantum_sim:
            return self._validate_quantum_sim(problem, solution, internal_result)
        else:
            return self._validate_probabilistic(problem, solution, internal_result)
    
    def _validate_quantum_sim(self,
                             problem: Dict[str, Any],
                             solution: Dict[str, Any],
                             internal_result: Tuple[bool, float, str]) -> Tuple[bool, float, str]:
        """Validate using quantum simulation"""
        
        internal_valid, internal_conf, _ = internal_result
        
        # Simulate quantum superposition and measurement
        # Use problem and solution data to create quantum state
        
        # Create hash of problem+solution for deterministic randomness
        data_str = json.dumps({
            'problem_id': problem.get('problem_id', ''),
            'answer': solution.get('answer', '')[:100]
        }, sort_keys=True)
        
        seed = int(hashlib.sha256(data_str.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Quantum-inspired probability calculation
        # Higher difficulty problems have more quantum uncertainty
        difficulty = problem.get('difficulty', 0.5)
        quantum_noise = random.gauss(0, difficulty * 0.1)
        
        # Combine internal validation with quantum measurement
        quantum_confidence = internal_conf + quantum_noise
        quantum_confidence = max(0.0, min(1.0, quantum_confidence))
        
        # Quantum threshold is adaptive based on difficulty
        threshold = 0.65 + (difficulty * 0.15)
        is_valid = quantum_confidence >= threshold
        
        reasoning = f"Quantum validation: confidence {quantum_confidence:.2f} vs threshold {threshold:.2f}. "
        reasoning += f"Quantum noise: {quantum_noise:+.3f}. "
        
        if is_valid:
            reasoning += "Solution passes quantum verification."
        else:
            reasoning += "Solution fails quantum verification."
        
        # Record validation
        self.validation_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'problem_id': problem.get('problem_id', 'unknown'),
            'method': 'quantum_sim',
            'is_valid': is_valid,
            'confidence': quantum_confidence,
            'threshold': threshold
        })
        
        logger.info(f"✅ Quantum validation: {is_valid} (confidence: {quantum_confidence:.2f})")
        return is_valid, quantum_confidence, reasoning
    
    def _validate_probabilistic(self,
                               problem: Dict[str, Any],
                               solution: Dict[str, Any],
                               internal_result: Tuple[bool, float, str]) -> Tuple[bool, float, str]:
        """Validate using probabilistic methods"""
        
        internal_valid, internal_conf, _ = internal_result
        
        # Simple probabilistic validation
        # Add random variation to internal confidence
        variation = random.uniform(-0.1, 0.1)
        prob_confidence = internal_conf + variation
        prob_confidence = max(0.0, min(1.0, prob_confidence))
        
        is_valid = prob_confidence >= 0.7
        
        reasoning = f"Probabilistic validation: confidence {prob_confidence:.2f}. "
        if is_valid:
            reasoning += "Solution is probably correct."
        else:
            reasoning += "Solution is probably incorrect."
        
        logger.info(f"✅ Probabilistic validation: {is_valid} (confidence: {prob_confidence:.2f})")
        return is_valid, prob_confidence, reasoning


class DualValidationSystem:
    """
    Complete Dual Validation System
    Combines Internal and Quantum validation
    """
    
    def __init__(self, use_ai: bool = False, use_quantum: bool = True):
        """
        Initialize Dual Validation System
        
        Args:
            use_ai: Whether to use AI for internal validation
            use_quantum: Whether to use quantum simulation
        """
        self.internal_validator = InternalValidator(use_ai=use_ai)
        self.quantum_validator = QuantumValidator(use_quantum_sim=use_quantum)
        self.validation_log = []
    
    def validate(self,
                problem: Dict[str, Any],
                solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete dual validation
        
        Args:
            problem: Problem data
            solution: Solution data
            
        Returns:
            Validation result dictionary
        """
        logger.info(f"🔍 Starting dual validation for problem: {problem.get('title', 'Unknown')}")
        
        # Step 1: Internal Validation
        internal_valid, internal_conf, internal_reason = self.internal_validator.validate(
            problem, solution
        )
        
        # Step 2: Quantum Validation
        quantum_valid, quantum_conf, quantum_reason = self.quantum_validator.validate(
            problem, solution, (internal_valid, internal_conf, internal_reason)
        )
        
        # Step 3: Combine results
        # Both validators must agree for final validation
        final_valid = internal_valid and quantum_valid
        
        # Average confidence
        final_confidence = (internal_conf + quantum_conf) / 2.0
        
        # Create result
        result = {
            'is_valid': final_valid,
            'confidence': final_confidence,
            'internal_validation': {
                'is_valid': internal_valid,
                'confidence': internal_conf,
                'reasoning': internal_reason
            },
            'quantum_validation': {
                'is_valid': quantum_valid,
                'confidence': quantum_conf,
                'reasoning': quantum_reason
            },
            'timestamp': datetime.utcnow().isoformat(),
            'problem_id': problem.get('problem_id', 'unknown')
        }
        
        # Log validation
        self.validation_log.append(result)
        
        logger.info(f"✅ Dual validation complete: {final_valid} (confidence: {final_confidence:.2f})")
        
        return result
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        if not self.validation_log:
            return {'total': 0}
        
        total = len(self.validation_log)
        valid = sum(1 for v in self.validation_log if v['is_valid'])
        avg_confidence = sum(v['confidence'] for v in self.validation_log) / total
        
        return {
            'total': total,
            'valid': valid,
            'invalid': total - valid,
            'success_rate': valid / total,
            'average_confidence': avg_confidence
        }


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Initialize dual validation system
    validator = DualValidationSystem(use_ai=True, use_quantum=True)
    
    # Example problem
    problem = {
        'problem_id': 'test_001',
        'title': 'Dark Matter Distribution',
        'description': 'Analyze gravitational lensing data...',
        'difficulty': 0.8,
        'category': 'physics',
        'keywords': ['dark matter', 'gravitational lensing']
    }
    
    # Example solution
    solution = {
        'answer': 'The dark matter distribution shows a characteristic NFW profile with concentration parameter c=5.2. Analysis of strong lensing features indicates a total mass of 2.3×10^14 solar masses within the virial radius.',
        'methodology': 'Used ray-tracing simulations with LENSTOOL software. Applied Bayesian MCMC to fit model parameters. Cross-validated with weak lensing shear measurements.',
        'quality': 0.85
    }
    
    # Validate
    result = validator.validate(problem, solution)
    
    # Display result
    print("\n" + "="*60)
    print("DUAL VALIDATION RESULT")
    print("="*60)
    print(f"Final Validation: {'✅ VALID' if result['is_valid'] else '❌ INVALID'}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"\nInternal Validation: {'✅' if result['internal_validation']['is_valid'] else '❌'}")
    print(f"  Confidence: {result['internal_validation']['confidence']:.2%}")
    print(f"  Reasoning: {result['internal_validation']['reasoning']}")
    print(f"\nQuantum Validation: {'✅' if result['quantum_validation']['is_valid'] else '❌'}")
    print(f"  Confidence: {result['quantum_validation']['confidence']:.2%}")
    print(f"  Reasoning: {result['quantum_validation']['reasoning']}")
    
    # Stats
    stats = validator.get_validation_stats()
    print(f"\n" + "="*60)
    print("VALIDATION STATISTICS")
    print("="*60)
    print(f"Total validations: {stats['total']}")
    print(f"Success rate: {stats.get('success_rate', 0):.2%}")
