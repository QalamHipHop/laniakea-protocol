# laniakea/simulation/cosmic.py

import time
import random
from typing import Dict, Any, List

class CosmicEntity:
    def __init__(self, name: str, entity_type: str, position: List[float], mass: float):
        self.name = name
        self.entity_type = entity_type # e.g., 'Star', 'Planet', 'BlackHole', 'Galaxy'
        self.position = position # [x, y, z]
        self.mass = mass
        self.velocity = [0.0, 0.0, 0.0]

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class CosmicSimulator:
    """
    A simplified N-body simulation for the Laniakea Protocol.
    Simulates the gravitational interactions and evolution of cosmic entities.
    """
    G = 6.674e-11 # Gravitational constant (simplified)

    def __init__(self, time_step: float = 0.1):
        self.entities: List[CosmicEntity] = []
        self.time_step = time_step
        self.current_time = 0.0

    def add_entity(self, entity: CosmicEntity):
        """Adds a new entity to the simulation."""
        self.entities.append(entity)
        print(f"Added entity: {entity.name} ({entity.entity_type})")

    def _calculate_force(self, entity1: CosmicEntity, entity2: CosmicEntity) -> List[float]:
        """Calculates the gravitational force between two entities."""
        r_vec = np.array(entity2.position) - np.array(entity1.position)
        r_mag = np.linalg.norm(r_vec)
        
        if r_mag == 0:
            return [0.0, 0.0, 0.0] # Avoid division by zero
            
        # F = G * (m1 * m2) / r^2
        force_magnitude = (self.G * entity1.mass * entity2.mass) / (r_mag**2)
        
        # Force vector: F * (r_vec / r_mag)
        force_vector = force_magnitude * (r_vec / r_mag)
        return force_vector.tolist()

    def step_simulation(self):
        """Advances the simulation by one time step."""
        if len(self.entities) < 2:
            self.current_time += self.time_step
            return

        new_velocities = []
        new_positions = []

        for i, entity1 in enumerate(self.entities):
            total_force = np.array([0.0, 0.0, 0.0])
            
            for j, entity2 in enumerate(self.entities):
                if i != j:
                    force = self._calculate_force(entity1, entity2)
                    total_force += np.array(force)

            # Acceleration: a = F / m
            acceleration = total_force / entity1.mass
            
            # New Velocity: v_new = v_old + a * dt
            current_velocity = np.array(entity1.velocity)
            new_velocity = current_velocity + acceleration * self.time_step
            new_velocities.append(new_velocity.tolist())
            
            # New Position: p_new = p_old + v_new * dt
            current_position = np.array(entity1.position)
            new_position = current_position + new_velocity * self.time_step
            new_positions.append(new_position.tolist())

        # Update all entities simultaneously
        for i, entity in enumerate(self.entities):
            entity.velocity = new_velocities[i]
            entity.position = new_positions[i]
            
        self.current_time += self.time_step
        print(f"Simulation stepped to time: {self.current_time:.2f}")

# Example usage
if __name__ == '__main__':
    # Note: This requires numpy, which is pre-installed.
    import numpy as np 
    
    simulator = CosmicSimulator(time_step=10000.0) # Large time step for noticeable change
    
    # Add entities (simplified units)
    sun = CosmicEntity("Sun", "Star", [0.0, 0.0, 0.0], 1.989e30)
    earth = CosmicEntity("Earth", "Planet", [1.496e11, 0.0, 0.0], 5.972e24)
    earth.velocity = [0.0, 29780.0, 0.0] # Initial orbital velocity
    
    simulator.add_entity(sun)
    simulator.add_entity(earth)
    
    print(f"Initial Earth Position: {earth.position}")
    
    # Run simulation for a few steps
    for _ in range(5):
        simulator.step_simulation()
        
    print(f"Final Earth Position: {earth.position}")
