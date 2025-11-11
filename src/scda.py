import numpy as np
from typing import Tuple

# Define the dimensions for the 8D vector
DIMENSIONS = 8

class SCDA:
    """
    Self-Correcting Distributed Agent (SCDA) class.

    The SCDA operates on an 8-dimensional state vector S(t) = (K(t), E(t)),
    where K(t) is the 4D Knowledge vector and E(t) is the 4D Energy vector.
    The core mechanism involves energy management, problem-solving, and
    passive state updates, all governed by diminishing returns principles.
    """

    def __init__(self, initial_k: np.ndarray, initial_e: np.ndarray, decay_rate: float = 0.01, learning_rate: float = 0.1):
        """
        Initialize the SCDA with 8D state vectors.

        Parameters
        ----------
        initial_k : np.ndarray
            Initial 4D Knowledge vector (K).
        initial_e : np.ndarray
            Initial 4D Energy vector (E).
        decay_rate : float, optional
            Rate at which passive energy/knowledge decays (default is 0.01).
        learning_rate : float, optional
            Rate at which knowledge is gained during problem-solving (default is 0.1).

        Raises
        ------
        ValueError
            If initial vectors are not 4-dimensional.
        """

        if initial_k.shape != (DIMENSIONS // 2,) or initial_e.shape != (DIMENSIONS // 2,):
            raise ValueError(f"Initial vectors must be {DIMENSIONS // 2}-dimensional.")

        self.K = initial_k  # Knowledge vector (4D)
        self.E = initial_e  # Energy vector (4D)
        self.decay_rate = decay_rate
        self.learning_rate = learning_rate

    @property
    def state_vector(self) -> np.ndarray:
        """Returns the full 8D state vector S(t) = (K(t), E(t))."""
        return np.concatenate((self.K, self.E))

    def _diminishing_returns(self, input_value: float, max_capacity: float = 1.0) -> float:
        """
        Applies a diminishing returns function (e.g., a logarithmic or hyperbolic tangent curve).
        This ensures that the marginal gain decreases as the state approaches a maximum capacity.

        Formula: max_capacity * (1 - exp(-input_value / max_capacity))
        """
        return max_capacity * (1 - np.exp(-input_value / max_capacity))

    def energy_management(self, energy_input: np.ndarray) -> None:
        """
        Manages the energy vector E(t) by applying input and the diminishing returns principle.

        The energy input is a 4D vector representing external energy gain or loss.

        Parameters
        ----------
        energy_input : np.ndarray
            A 4D vector representing new energy input.

        Raises
        ------
        ValueError
            If energy input is not 4-dimensional.
        """

        if energy_input.shape != (DIMENSIONS // 2,):
            raise ValueError(f"Energy input must be {DIMENSIONS // 2}-dimensional.")

        # 1. Apply diminishing returns to the input energy
        diminished_input = np.array([self._diminishing_returns(e_in, max_capacity=10.0) for e_in in energy_input])

        # 2. Update E(t)
        self.E += diminished_input

        # 3. Apply a small maintenance cost (proportional to current state)
        maintenance_cost = self.E * self.decay_rate * 0.1
        self.E = np.maximum(0, self.E - maintenance_cost)

    def problem_solving(self, problem_difficulty: np.ndarray) -> Tuple[bool, float]:
        """
        Simulates the SCDA attempting to solve a problem.

        The success and knowledge gain are dependent on the current Knowledge (K)
        and the available Energy (E) relative to the problem's difficulty.

        Parameters
        ----------
        problem_difficulty : np.ndarray
            A 4D vector representing the difficulty of the problem.

        Returns
        -------
        Tuple[bool, float]
            A tuple (success_status, knowledge_gain_magnitude).

        Raises
        ------
        ValueError
            If problem difficulty is not 4-dimensional.
        """

        if problem_difficulty.shape != (DIMENSIONS // 2,):
            raise ValueError(f"Problem difficulty must be {DIMENSIONS // 2}-dimensional.")

        # Calculate required energy and knowledge
        required_energy = problem_difficulty * 0.5
        required_knowledge = problem_difficulty * 0.8

        # 1. Check for success (simple probability model)
        # Success probability is proportional to K/required_knowledge and E/required_energy
        knowledge_ratio = np.mean(self.K / (required_knowledge + 1e-6))
        energy_ratio = np.mean(self.E / (required_energy + 1e-6))
        success_probability = np.clip(0.5 * (knowledge_ratio + energy_ratio), 0.1, 0.95)

        success = np.random.rand() < success_probability

        # 2. Update state based on outcome
        if success:
            # Energy cost for solving
            cost = required_energy * 0.8
            self.E = np.maximum(0, self.E - cost)

            # Knowledge gain with diminishing returns
            base_gain = problem_difficulty * self.learning_rate
            diminished_gain = np.array([self._diminishing_returns(g, max_capacity=5.0) for g in base_gain])
            self.K += diminished_gain
            knowledge_gain_magnitude = np.linalg.norm(diminished_gain)
        else:
            # Higher energy cost for failure, but a small learning gain from the attempt
            cost = required_energy * 1.2
            self.E = np.maximum(0, self.E - cost)

            # Small, diminished learning gain from failure
            base_gain = problem_difficulty * self.learning_rate * 0.1
            diminished_gain = np.array([self._diminishing_returns(g, max_capacity=1.0) for g in base_gain])
            self.K += diminished_gain
            knowledge_gain_magnitude = np.linalg.norm(diminished_gain)

        return success, knowledge_gain_magnitude

    def update_passive(self) -> None:
        """
        Applies passive, time-based updates to the state vector.

        This includes:
        1. Knowledge decay (forgetting) with diminishing returns on the decay itself (harder to forget core knowledge).
        2. Energy dissipation (natural loss).
        """
        # 1. Knowledge Decay (Forgetting)
        # Decay is applied, but the decay rate itself is diminished for higher K values
        # This models that core knowledge is harder to forget.
        diminished_decay_factor = np.array([self._diminishing_returns(k, max_capacity=1.0) for k in (1.0 / (self.K + 1e-6))])
        decay_amount = self.K * self.decay_rate * diminished_decay_factor
        self.K = np.maximum(0, self.K - decay_amount)

        # 2. Energy Dissipation
        dissipation_amount = self.E * self.decay_rate
        self.E = np.maximum(0, self.E - dissipation_amount)

    def __repr__(self):
        return f"SCDA(K={self.K}, E={self.E})"

# Example usage (for testing purposes, not part of the class)
if __name__ == '__main__':
    # Initial state vectors (4D each)
    initial_k = np.array([0.5, 0.3, 0.7, 0.1])
    initial_e = np.array([1.0, 0.8, 0.5, 0.2])

    scda_agent = SCDA(initial_k, initial_e)
    print(f"Initial State: {scda_agent.state_vector}")

    # Energy Management
    energy_boost = np.array([2.0, 1.5, 0.5, 0.1])
    scda_agent.energy_management(energy_boost)
    print(f"After Energy Boost: {scda_agent.state_vector}")

    # Problem Solving
    problem = np.array([1.0, 1.0, 1.0, 1.0])
    success, gain = scda_agent.problem_solving(problem)
    print(f"Problem Solved: {success}, Knowledge Gain: {gain:.4f}")
    print(f"After Problem Solving: {scda_agent.state_vector}")

    # Passive Update
    scda_agent.update_passive()
    print(f"After Passive Update: {scda_agent.state_vector}")
