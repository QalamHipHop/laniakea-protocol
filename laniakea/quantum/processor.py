# laniakea/quantum/processor.py

import numpy as np
from typing import List, Dict, Any

class QuantumCircuit:
    """
    A simplified representation of a Quantum Circuit for Laniakea Protocol.
    It uses basic linear algebra to simulate quantum operations.
    """
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        # Initialize state vector to |0...0>
        self.state_vector = np.zeros(2**num_qubits, dtype=complex)
        self.state_vector[0] = 1.0
        self.gates: List[Dict[str, Any]] = []

    def _apply_gate(self, gate_matrix: np.ndarray, target_qubit: int):
        """Applies a single-qubit gate to the state vector."""
        if target_qubit >= self.num_qubits:
            raise ValueError("Target qubit index out of range.")

        # Identity matrix for non-target qubits
        identity = np.identity(2)
        
        # Build the full tensor product operator
        op = 1
        for i in range(self.num_qubits):
            if i == target_qubit:
                op = np.kron(op, gate_matrix) if op.ndim > 1 else gate_matrix
            else:
                op = np.kron(op, identity) if op.ndim > 1 else identity
        
        # Apply the operator to the state vector
        self.state_vector = op @ self.state_vector

    def h_gate(self, target_qubit: int):
        """Hadamard Gate (H) - Creates superposition."""
        H = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
        self._apply_gate(H, target_qubit)
        self.gates.append({"type": "H", "target": target_qubit})

    def x_gate(self, target_qubit: int):
        """Pauli-X Gate (X) - Bit flip (NOT gate)."""
        X = np.array([[0, 1], [1, 0]])
        self._apply_gate(X, target_qubit)
        self.gates.append({"type": "X", "target": target_qubit})

    def measure(self) -> List[int]:
        """
        Simulates measurement of the quantum state.
        Returns a list of measured bits (0 or 1).
        """
        probabilities = np.abs(self.state_vector)**2
        # Choose a state based on probabilities
        measured_index = np.random.choice(2**self.num_qubits, p=probabilities)
        
        # Convert the index to a binary string and then to a list of integers
        binary_result = format(measured_index, f'0{self.num_qubits}b')
        return [int(bit) for bit in binary_result]

    def run(self) -> List[int]:
        """Executes the circuit and returns the measurement result."""
        print(f"Running Quantum Circuit with {self.num_qubits} qubits and {len(self.gates)} gates...")
        return self.measure()

class QuantumProcessor:
    """
    Manages the execution of quantum circuits within the Laniakea Protocol.
    """
    def __init__(self, max_qubits: int = 5):
        self.max_qubits = max_qubits
        self.job_queue: List[QuantumCircuit] = []

    def create_circuit(self, num_qubits: int) -> QuantumCircuit:
        """Creates a new quantum circuit."""
        if num_qubits > self.max_qubits:
            raise ValueError(f"Max qubits supported is {self.max_qubits}.")
        return QuantumCircuit(num_qubits)

    def submit_job(self, circuit: QuantumCircuit):
        """Submits a quantum circuit for execution."""
        self.job_queue.append(circuit)
        print(f"Job submitted. Queue size: {len(self.job_queue)}")

    def process_next_job(self) -> List[int] | None:
        """Processes the next job in the queue."""
        if not self.job_queue:
            return None
        
        circuit = self.job_queue.pop(0)
        result = circuit.run()
        print(f"Job processed. Result: {result}")
        return result

# Example usage
if __name__ == '__main__':
    processor = QuantumProcessor(max_qubits=3)
    
    # Create a circuit for a simple superposition (1 qubit)
    qc1 = processor.create_circuit(1)
    qc1.h_gate(0) # Apply Hadamard to put it in superposition |+>
    processor.submit_job(qc1)
    
    # Create a circuit for a Bell state (2 qubits) - requires CNOT which is not implemented here, so we use X for demonstration
    qc2 = processor.create_circuit(2)
    qc2.h_gate(0)
    qc2.x_gate(1)
    processor.submit_job(qc2)
    
    # Process jobs
    print("\n--- Processing Jobs ---")
    while processor.job_queue:
        processor.process_next_job()
