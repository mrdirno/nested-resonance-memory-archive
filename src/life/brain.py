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
        # [Energy_Weight, Signal_Weight, Random_Bias]
        self.weights = {
            'reproduce': [0.8, 0.0, -0.2], # High energy, ignores signals
            'forage': [-0.5, 0.0, 0.5],    # Low energy
            'donate': [0.5, 1.0, -0.5]     # Needs energy AND 'HELP' signal
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
            score = (energy_norm * w[0]) + (help_norm * w[1]) + (random.random() * w[2])
            scores[action] = score
            
        # Return action with highest score
        best_action = max(scores, key=scores.get)
        return best_action

    def modify_weights(self, deltas: dict):
        """
        Apply cultural learning (memes) to weights.
        deltas: {'action_name': weight_change}
        We'll apply the delta to the 'Bias' weight (index 2) for now, 
        as that represents the agent's intrinsic inclination.
        """
        for action, delta in deltas.items():
            if action in self.weights:
                # Modify the Bias (last element)
                # self.weights[action][-1] += delta
                # Actually, let's modify the Bias index 2.
                # Ensure we have enough weights
                while len(self.weights[action]) < 3:
                    self.weights[action].append(0.0)
                
                self.weights[action][2] += delta
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
