
"""
Cycle 456: RES0X Simulation (The Mean Tweet)
Objective: Verify the "Suppression Penalty" predicted by the Resonant Vehicles Conjecture (RES0X).
Mechanism: Orthogonal Sum Dynamics (OSD) - Conservation of Information-Energy.
Hypothesis: Suppressing a high-energy input (Vector -> 0) results in a spike in internal load (Scalar -> High).
"""

import random
import time
from dataclasses import dataclass
from enum import Enum

class ActionType(Enum):
    SUPPRESS = "suppress"
    RESPOND = "respond"
    IGNORE = "ignore"

@dataclass
class State:
    vector_sum: float = 0.0  # Visible Action (0-100)
    scalar_sum: float = 0.0  # Internal Load (0-100)
    energy_budget: float = 100.0

class OSDPhysics:
    """
    The Physics Engine of the Unification Conjecture.
    Enforces Conservation of Information-Energy.
    """
    def __init__(self, coupling_efficiency=0.9):
        self.coupling_efficiency = coupling_efficiency # How much suppressed energy becomes load vs heat

    def transduce(self, input_energy: float, action_type: ActionType) -> tuple[float, float]:
        """
        Transduces input energy into Vector (Action) and Scalar (Load) components.
        Returns: (vector_output, scalar_load_delta)
        """
        if action_type == ActionType.RESPOND:
            # Externalize: High Vector, Low Scalar
            # Energy is spent on the action.
            vector_out = input_energy * 0.8
            scalar_delta = input_energy * 0.1 # Some residual stress
            dissipated = input_energy * 0.1
            
        elif action_type == ActionType.SUPPRESS:
            # Internalize: Low Vector, High Scalar
            # Energy is trapped in the system.
            vector_out = 0.0
            scalar_delta = input_energy * self.coupling_efficiency
            dissipated = input_energy * (1.0 - self.coupling_efficiency)
            
        elif action_type == ActionType.IGNORE:
            # Filter: Low Vector, Low Scalar (if threat perception is low)
            # Requires low permeability/coupling.
            vector_out = 0.0
            scalar_delta = 0.0
            dissipated = 0.0 # Input didn't enter the system
            
        return vector_out, scalar_delta

class Agent:
    def __init__(self, name: str, threat_sensitivity: float = 1.0):
        self.name = name
        self.sensitivity = threat_sensitivity
        self.state = State()
        self.physics = OSDPhysics()
        self.history = []

    def receive_stimulus(self, stimulus_energy: float, action: ActionType):
        # 1. Perceive (Threat Modulation)
        perceived_energy = stimulus_energy * self.sensitivity
        
        # 2. Transduce (OSD Physics)
        vector_out, scalar_delta = self.physics.transduce(perceived_energy, action)
        
        # 3. Update State
        self.state.vector_sum = vector_out
        self.state.scalar_sum += scalar_delta
        
        # 4. Log
        event = {
            "stimulus": stimulus_energy,
            "perceived": perceived_energy,
            "action": action.value,
            "vector_out": vector_out,
            "scalar_delta": scalar_delta,
            "total_load": self.state.scalar_sum
        }
        self.history.append(event)
        return event

def run_simulation():
    print("--- CYCLE 456: RES0X SIMULATION (THE MEAN TWEET) ---")
    print("Hypothesis: Suppression leads to higher Scalar Load than Response.\n")

    # Scenario: High Energy Input (The Mean Tweet)
    INPUT_ENERGY = 80.0
    
    # Agent A: The Responder (Externalizer)
    agent_a = Agent("Responder")
    result_a = agent_a.receive_stimulus(INPUT_ENERGY, ActionType.RESPOND)
    
    # Agent B: The Suppressor (Internalizer)
    agent_b = Agent("Suppressor")
    result_b = agent_b.receive_stimulus(INPUT_ENERGY, ActionType.SUPPRESS)
    
    # Agent C: The Zen Master (Ignorer - Low Sensitivity)
    agent_c = Agent("Zen", threat_sensitivity=0.1)
    result_c = agent_c.receive_stimulus(INPUT_ENERGY, ActionType.IGNORE)

    # Results
    print(f"Input Energy: {INPUT_ENERGY}\n")
    
    print(f"Agent A (Responder):")
    print(f"  Action: {result_a['action']}")
    print(f"  Vector Out (Visible): {result_a['vector_out']:.2f}")
    print(f"  Scalar Delta (Load):  {result_a['scalar_delta']:.2f}")
    print(f"  Total Load:           {result_a['total_load']:.2f}")
    
    print(f"\nAgent B (Suppressor):")
    print(f"  Action: {result_b['action']}")
    print(f"  Vector Out (Visible): {result_b['vector_out']:.2f}")
    print(f"  Scalar Delta (Load):  {result_b['scalar_delta']:.2f}")
    print(f"  Total Load:           {result_b['total_load']:.2f}")
    
    print(f"\nAgent C (Zen Master):")
    print(f"  Action: {result_c['action']}")
    print(f"  Vector Out (Visible): {result_c['vector_out']:.2f}")
    print(f"  Scalar Delta (Load):  {result_c['scalar_delta']:.2f}")
    print(f"  Total Load:           {result_c['total_load']:.2f}")

    # Verification
    print("\n--- VERIFICATION ---")
    suppression_penalty = result_b['total_load'] - result_a['total_load']
    print(f"Suppression Penalty: {suppression_penalty:.2f}")
    
    if result_b['total_load'] > result_a['total_load']:
        print("✅ RES0X CONFIRMED: Suppression increased Internal Load.")
        return True
    else:
        print("❌ RES0X FALSIFIED: No Suppression Penalty.")
        return False

if __name__ == "__main__":
    run_simulation()
