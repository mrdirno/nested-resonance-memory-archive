
import sys
import os
import numpy as np
from typing import Dict, List, Optional, Tuple

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent

# --- GENERATION 1: SOCIAL MEMORY ---

class LedgerAgent(FractalAgent):
    """Agent with memory of past interactions (Reciprocal Altruism)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.memory: Dict[str, float] = {}
        self.strategy = "Cooperator"

    def record_interaction(self, partner_id: str, outcome: float):
        current = self.memory.get(partner_id, 0.0)
        self.memory[partner_id] = current + outcome

    def check_reputation(self, agent_id: str) -> float:
        return self.memory.get(agent_id, 0.0)

class GossipAgent(LedgerAgent):
    """Agent that shares reputation scores (Gossip)."""
    def share_memory(self, other_agent: 'GossipAgent'):
        for subject_id, score in self.memory.items():
            current = other_agent.memory.get(subject_id, 0.0)
            # Damping to prevent infinite feedback loops
            new_score = max(-5.0, min(5.0, current + score))
            other_agent.memory[subject_id] = new_score

# --- GENERATION 2: CONSTRUCTION ---

class BuilderAgent(GossipAgent):
    """Agent capable of converting energy into structure."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blocks_built = 0
        
    def build(self, cost: float) -> bool:
        if self.state.energy > cost:
            self.state.energy -= cost
            self.blocks_built += 1
            return True
        return False

# --- GENERATION 3: OPTIMIZATION ---

class OptimizerAgent(BuilderAgent):
    """Agent capable of manipulating environment blocks."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.holding_block = False
        
    def pick_up(self):
        if not self.holding_block:
            self.holding_block = True
            return True
        return False
    
    def drop(self):
        if self.holding_block:
            self.holding_block = False
            return True
        return False

def calculate_fitness(blocks: List[np.ndarray], target_radius: float, center: np.ndarray) -> float:
    """Calculate how well blocks form a circle."""
    if not blocks:
        return 0.0
    errors = []
    for pos in blocks:
        dist = np.linalg.norm(pos - center)
        error = abs(dist - target_radius)
        errors.append(error)
    return -sum(errors)

# --- GENERATION 4: ESTIMATION ---

class EstimatorAgent(OptimizerAgent):
    """Agent capable of sensing and distributed consensus."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.internal_estimate: float = 0.0
        self.velocity_magnitude: float = 1.0

    def sense(self, env_value: float):
        if self.internal_estimate == 0.0:
            self.internal_estimate = env_value 

    def communicate(self, other: 'EstimatorAgent'):
        avg = (self.internal_estimate + other.internal_estimate) / 2.0
        self.internal_estimate = avg
        other.internal_estimate = avg
