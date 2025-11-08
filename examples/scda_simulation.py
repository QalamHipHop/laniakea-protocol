import time
import sys
import os
from pathlib import Path

# Add project root to Python path to import src.scda
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.scda import SingleCellDigitalAccount, generate_hard_problem, validate_solution

def simulate_evolution(scda: SingleCellDigitalAccount, steps: int):
    """
    Simulates the SCDA evolution cycle for a given number of steps.
    """
    print("\n--- Starting Lanika SCDA Evolution Simulation ---")
    
    for step in range(1, steps + 1):
        print(f"\n--- Step {step} ---")
        
        # 1. Passive Update (Energy Replenishment)
        scda.passive_update()
        
        # 2. Problem Discovery (KEA)
        problem = generate_hard_problem(scda.complexity_index)
        problem_difficulty = problem["D"]
        
        print(f"Current C(t): {scda.complexity_index:.4f} | Energy: {scda.energy:.2f}")
        print(f"KEA discovered Hard Problem with Difficulty D(P): {problem_difficulty:.4f}")
        
        # 3. User Solution (Simulated)
        # We simulate a solution quality and a validation result.
        # The quality is assumed to be high if the problem is hard, for simulation purposes.
        simulated_solution_quality = min(1.0, problem_difficulty + 0.1)
        
        # 4. Validation (Simulated)
        # The validation function uses the SCDA's current state to determine success
        is_valid = validate_solution(scda, problem, simulated_solution_quality)
        
        # 5. Attempt Solve
        scda.attempt_solve_problem(
            problem_difficulty=problem_difficulty,
            solution_quality=simulated_solution_quality,
            is_valid=is_valid
        )
        
        if scda.energy <= 0:
            print(f"Simulation stopped at step {step}: SCDA ran out of energy.")
            break
            
        time.sleep(0.1) # Slow down simulation for readability

if __name__ == "__main__":
    # 1. Initialize the SCDA
    lanika_account = SingleCellDigitalAccount(identity="Lanika_Test_Unit_001")
    
    # 2. Run the simulation
    SIMULATION_STEPS = 10
    simulate_evolution(lanika_account, SIMULATION_STEPS)
    
    # 3. Final State Report
    print("\n--- Final SCDA State ---")
    final_state = lanika_account.get_state()
    for key, value in final_state.items():
        if isinstance(value, float):
            print(f"{key.replace('_', ' ').title()}: {value:.4f}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
            
    print(f"Total Knowledge Acquired: {len(lanika_account.knowledge_vector)}")
    print("--------------------------")
