"""
Cycle 2463: The Neural Link (Gate 91)
Role: The Neuroscientist
Responsibility: Provide decision-making capabilities to agents.

Concepts:
- Inputs: Internal State (Energy).
- Outputs: Action Probabilities.
- Architecture: Simple Heuristic / Perceptron.
"""

import random

class Brain:
    def __init__(self):
        # Weights for decision making
        # [Energy_Weight, Random_Bias]
        self.weights = {
            'reproduce': [0.8, -0.2], # High energy favors reproduction
            'forage': [-0.5, 0.5]     # Low energy favors foraging (if we had foraging)
        }
        
    def decide(self, state: dict) -> str:
        """
        Decide on an action based on state.
        State: {'energy': float (0-1), 'age': int}
        """
        energy_norm = min(1.0, state.get('energy', 0) / 200.0)
        
        # Calculate scores
        scores = {}
        for action, w in self.weights.items():
            # Score = Energy * W1 + Bias * W2
            score = (energy_norm * w[0]) + (random.random() * w[1])
            scores[action] = score
            
        # Return action with highest score
        best_action = max(scores, key=scores.get)
        return best_action