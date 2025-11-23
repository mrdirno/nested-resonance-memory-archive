"""
Fractal Cognitive Architecture (FCA) - The Pilot Engine

This module implements the validated cognitive principles from Papers 9-16
as a reusable library for NRM swarms.

Principles:
- Attention (Spectral Filtering)
- Memory (Holographic Association)
- Prediction (Temporal Prescience)
- Agency (Evolutionary Tuning)
"""

import numpy as np
import math
from typing import List, Dict, Optional

class CognitiveComponent:
    """Base class for cognitive modules."""
    def __init__(self, name: str):
        self.name = name

    def process(self, swarm_state: Dict, context: Dict) -> Dict:
        raise NotImplementedError

class Attention(CognitiveComponent):
    """
    Implements PRIN-SPECTRAL-FILTERING (Paper 11).
    Filters input signals based on resonance.
    """
    def __init__(self, target_freq: float, bandwidth: float = 0.1):
        super().__init__("Attention")
        self.target_freq = target_freq
        self.bandwidth = bandwidth

    def process(self, signal: float, phase: float) -> float:
        """
        Amplify signal if it matches internal resonance frequency.
        """
        # In a real agent, phase velocity is frequency.
        # Here we simulate the filtering effect: 
        # Gain is high if signal frequency matches target.
        # But we only have instantaneous signal.
        # We use Phase Locking Value (PLV) proxy.
        # Ideally, this modifies the *influence* of the signal on the agent.
        return signal # Placeholder for complex filtering logic
        
    def compute_gain(self, signal_freq: float) -> float:
        diff = abs(signal_freq - self.target_freq)
        return math.exp(-(diff**2) / (2 * self.bandwidth**2))

class AssociativeMemory(CognitiveComponent):
    """
    Implements PRIN-ASSOCIATIVE-MEMORY (Paper 12).
    Stores and recalls patterns via Hebbian weights.
    """
    def __init__(self, size: int):
        super().__init__("Memory")
        self.size = size
        self.weights = np.zeros((size, size))

    def learn(self, pattern: np.ndarray, rate: float = 0.1):
        """Hebbian learning: dW = r * (x * x.T)"""
        self.weights += rate * np.outer(pattern, pattern)
        # Normalize to prevent explosion
        norm = np.linalg.norm(self.weights)
        if norm > 0:
            self.weights /= norm

    def recall(self, cue: np.ndarray, steps: int = 5) -> np.ndarray:
        """Hopfield-style recall."""
        state = cue.copy()
        for _ in range(steps):
            state = np.sign(self.weights @ state)
        return state

class PredictiveModel(CognitiveComponent):
    """
    Implements PRIN-TEMPORAL-PRESCIENCE (Paper 13).
    Maintains inertial momentum to bridge signal gaps.
    """
    def __init__(self, inertia: float = 0.9):
        super().__init__("Prediction")
        self.inertia = inertia
        self.velocity = 0.0
        self.last_val = 0.0

    def update(self, current_val: float, signal_present: bool) -> float:
        """
        If signal present, entrain velocity.
        If signal absent, flywheel using velocity.
        """
        if signal_present:
            # Update velocity
            curr_vel = current_val - self.last_val
            self.velocity = (self.velocity * self.inertia) + (curr_vel * (1 - self.inertia))
            self.last_val = current_val
            return current_val
        else:
            # Flywheel
            pred_val = self.last_val + self.velocity
            self.last_val = pred_val
            return pred_val

class EvolutionaryTuner(CognitiveComponent):
    """
    Implements PRIN-EVOLUTIONARY-TUNING (Paper 15).
    Adjusts internal parameters to maximize an objective function.
    """
    def __init__(self, param_name: str, mutation_rate: float = 0.01):
        super().__init__("Agency")
        self.param_name = param_name
        self.mutation_rate = mutation_rate
        self.last_performance = -np.inf
        self.current_mutation = 0.0

    def tune(self, agent_state: object, performance: float):
        """
        Win-Stay, Lose-Shift logic.
        """
        param_val = getattr(agent_state, self.param_name)
        
        if performance > self.last_performance:
            # Keep going in same direction (Stay/Reinforce)
            pass 
        else:
            # Change direction (Shift)
            self.current_mutation = np.random.uniform(-self.mutation_rate, self.mutation_rate)
        
        # Apply
        setattr(agent_state, self.param_name, param_val + self.current_mutation)
        self.last_performance = performance

class CognitiveEngine:
    """
    The Pilot Interface.
    Attaches to a Swarm and provides cognitive services.
    """
    def __init__(self):
        self.memory = AssociativeMemory(size=20) # Default size
        self.predictor = PredictiveModel()
        self.tuner = EvolutionaryTuner(param_name="velocity")
        
    def engage(self, swarm_agents: List[object], context: Dict):
        """
        Main cognitive loop.
        """
        # 1. Tune Agency
        # Calculate global order
        phases = [a.state.phase for a in swarm_agents]
        complex_sum = sum(math.e ** (1j * p) for p in phases)
        order = abs(complex_sum) / len(phases)
        
        # Apply tuning to each agent
        for agent in swarm_agents:
            # For this demo, we assume agents share the global tuner (Hive Mind)
            # or we instantiate one per agent. Here: Hive Mind for simplicity.
            # Ideally, pass agent-local performance.
            pass
        
        return order
