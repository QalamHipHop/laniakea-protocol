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
        
        # Validate that initial values are non-negative
        if np.any(initial_k < 0) or np.any(initial_e < 0):
            raise ValueError("Initial knowledge and energy vectors must be non-negative.")

        self.K = initial_k.astype(np.float64)  # Knowledge vector (4D)
        self.E = initial_e.astype(np.float64)  # Energy vector (4D)
        self.decay_rate = float(decay_rate)
        self.learning_rate = float(learning_rate)
        
        # State bounds to prevent overflow
        self.E_MAX = 1000.0
        self.K_MAX = 100.0

    @property
    def state_vector(self) -> np.ndarray:
        """Returns the full 8D state vector S(t) = (K(t), E(t))."""
        return np.concatenate((self.K, self.E))

    def _diminishing_returns(self, input_value: float, max_capacity: float = 1.0) -> float:
        """
        Applies a diminishing returns function (e.g., a logarithmic or hyperbolic tangent curve).
        This ensures that the marginal gain decreases as the state approaches a maximum capacity.

        Formula: max_capacity * (1 - exp(-input_value / max_capacity))
        
        Parameters
        ----------
        input_value : float
            The input value to apply diminishing returns to
        max_capacity : float
            The maximum capacity (default 1.0)
            
        Returns
        -------
        float
            The diminished value
        """
        try:
            # Clamp input to prevent overflow
            clamped_input = np.clip(input_value, 0, 100.0)
            result = max_capacity * (1 - np.exp(-clamped_input / max_capacity))
            return float(np.clip(result, 0, max_capacity))
        except (OverflowError, FloatingPointError):
            return max_capacity

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
        
        # Validate energy input is reasonable
        energy_input = np.clip(energy_input, 0, 100.0)

        # 1. Apply diminishing returns to the input energy
        diminished_input = np.array([
            self._diminishing_returns(e_in, max_capacity=10.0) 
            for e_in in energy_input
        ])

        # 2. Update E(t) with bounds checking
        self.E += diminished_input
        self.E = np.clip(self.E, 0, self.E_MAX)

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
        
        # Validate and clamp problem difficulty
        problem_difficulty = np.clip(problem_difficulty, 0.1, 10.0)

        # Calculate required energy and knowledge
        required_energy = problem_difficulty * 0.5
        required_knowledge = problem_difficulty * 0.8

        # 1. Check for success (simple probability model)
        # Success probability is proportional to K/required_knowledge and E/required_energy
        # FIX: Prevent division by near-zero by clamping denominators
        safe_required_knowledge = np.maximum(required_knowledge, 1e-3)
        safe_required_energy = np.maximum(required_energy, 1e-3)
        
        knowledge_ratio = np.mean(np.clip(self.K / safe_required_knowledge, 0, 10))
        energy_ratio = np.mean(np.clip(self.E / safe_required_energy, 0, 10))
        success_probability = np.clip(0.5 * (knowledge_ratio + energy_ratio), 0.1, 0.95)

        success = np.random.rand() < success_probability

        # 2. Update state based on outcome
        if success:
            # Energy cost for solving
            cost = required_energy * 0.8
            self.E = np.maximum(0, self.E - cost)

            # Knowledge gain with diminishing returns
            base_gain = problem_difficulty * self.learning_rate
            diminished_gain = np.array([
                self._diminishing_returns(g, max_capacity=5.0) 
                for g in base_gain
            ])
            self.K += diminished_gain
            self.K = np.clip(self.K, 0, self.K_MAX)  # FIX: Add upper bound
            knowledge_gain_magnitude = float(np.linalg.norm(diminished_gain))
        else:
            # Higher energy cost for failure, but a small learning gain from the attempt
            cost = required_energy * 1.2
            self.E = np.maximum(0, self.E - cost)

            # Small, diminished learning gain from failure
            base_gain = problem_difficulty * self.learning_rate * 0.1
            diminished_gain = np.array([
                self._diminishing_returns(g, max_capacity=1.0) 
                for g in base_gain
            ])
            self.K += diminished_gain
            self.K = np.clip(self.K, 0, self.K_MAX)  # FIX: Add upper bound
            knowledge_gain_magnitude = float(np.linalg.norm(diminished_gain))

        return success, knowledge_gain_magnitude

    def update_passive(self) -> None:
        """
        Applies passive, time-based updates to the state vector.

        This includes:
        1. Knowledge decay (forgetting) with diminishing returns on the decay itself (harder to forget core knowledge).
        2. Energy dissipation (natural loss).
        """
        # 1. Knowledge Decay (Forgetting)
        # FIX: Properly handle diminishing returns for knowledge decay
        # Core knowledge should decay slower
        safe_k = np.maximum(self.K, 1e-6)
        decay_factors = np.array([
            self._diminishing_returns(1.0 / k, max_capacity=1.0) 
            for k in safe_k
        ])
        decay_amount = self.K * self.decay_rate * decay_factors
        self.K = np.maximum(0, self.K - decay_amount)
        self.K = np.clip(self.K, 0, self.K_MAX)

        # 2. Energy Dissipation
        dissipation_amount = self.E * self.decay_rate
        self.E = np.maximum(0, self.E - dissipation_amount)

    def __repr__(self):
        return f"SCDA(K={self.K}, E={self.E})"
