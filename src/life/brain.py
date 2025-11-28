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
        # [Energy_Weight, Signal_HELP_Weight, Random_Bias]
        self.weights = {
            'reproduce': [0.8, -0.5, -0.2], # High energy favors reproduction, HELP signals discourage it (danger?)
            'broadcast_help': [-0.8, 0.0, 0.1], # Low energy favors calling for help
            'idle': [0.0, 0.0, 0.5] # Default
        }
        
    def decide(self, state: dict) -> str:
        """
        Decide on an action based on state.
        State: {'energy': float, 'signals': dict}
        """
        energy_norm = min(1.0, state.get('energy', 0) / 200.0)
        signals = state.get('signals', {})
        help_signal_count = signals.get('HELP', 0)
        help_norm = min(1.0, help_signal_count / 10.0) # Normalize signal strength
        
        # Calculate scores
        scores = {}
        for action, w in self.weights.items():
            # Score = Energy*W0 + Help*W1 + Bias*W2
            # Handle variable weight lengths if we add more inputs later
            score = (energy_norm * w[0]) + (help_norm * w[1]) + (random.random() * w[2])
            scores[action] = score
            
        # Return action with highest score
        best_action = max(scores, key=scores.get)
        return best_action