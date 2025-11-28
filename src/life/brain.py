"""
Cycle 2545: The Neural Network (Gate 173)
Role: The Neuroscientist
Responsibility: Provide decision-making capabilities to agents via a Neural Network.

Concepts:
- Inputs: Internal State + Environment.
- Outputs: Action Probabilities.
- Architecture: Feed Forward (Input -> Hidden -> Output).
"""

import random
import math

class Brain:
    def __init__(self):
        # 4 Inputs: [Energy, Signal_Help, Signal_Threat, Signal_Food]
        # 5 Outputs: [Forage, Reproduce, Donate, Flee, Hunt]
        # Hidden Layer: 4 Neurons
        
        self.input_size = 4
        self.hidden_size = 4
        self.output_size = 5
        
        # Random initialization
        self.w1 = [[random.uniform(-1, 1) for _ in range(self.hidden_size)] for _ in range(self.input_size)]
        self.b1 = [random.uniform(-1, 1) for _ in range(self.hidden_size)]
        
        self.w2 = [[random.uniform(-1, 1) for _ in range(self.output_size)] for _ in range(self.hidden_size)]
        self.b2 = [random.uniform(-1, 1) for _ in range(self.output_size)]
        
        self.actions = ['forage', 'reproduce', 'donate', 'flee', 'hunt', 'meditate', 'operate']
        # Map actions to constants
        self.action_map = {
            'forage': 'pi_phase',
            'reproduce': 'e_phase',
            'donate': 'phi_phase',
            'flee': 'pi_phase', # Harmonics
            'hunt': 'e_phase',
            'meditate': 'spatial_phase', # Cycle 2548: Resonance Trapping
            'operate': 'phi_phase' # Cycle 2557: The Operator (Harmonic of Donate)
        }
        self.weights = {} # Cycle 2540: Hebbian Weights
        
    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
        
    def forward(self, inputs):
        # Input -> Hidden
        hidden = []
        for j in range(self.hidden_size):
            activation = self.b1[j]
            for i in range(self.input_size):
                activation += inputs[i] * self.w1[i][j]
            hidden.append(self.sigmoid(activation))
            
        # Hidden -> Output
        outputs = []
        for k in range(self.output_size):
            activation = self.b2[k]
            for j in range(self.hidden_size):
                activation += hidden[j] * self.w2[j][k]
            outputs.append(self.sigmoid(activation))
            
        return outputs
        
    def decide(self, state: dict) -> str:
        """
        Decide on an action based on state.
        State: {'energy': float, 'signals': dict}
        """
        # Normalize Inputs
        energy = min(1.0, state.get('energy', 0) / 500.0)
        signals = state.get('signals', {})
        
        def get_signal_strength(key):
            val = signals.get(key, 0)
            if isinstance(val, tuple) or isinstance(val, list):
                return 1.0 # Presence detected
            return float(val)
        
        s_help = min(1.0, get_signal_strength('HELP') / 5.0)
        s_threat = min(1.0, get_signal_strength('PREDATOR') / 5.0)
        s_food = min(1.0, get_signal_strength('FOOD') / 5.0)
        
        inputs = [energy, s_help, s_threat, s_food]
        
        # Inference
        outputs = self.forward(inputs)
        
        # Selection (Argmax)
        max_val = -1
        max_idx = 0
        for i, val in enumerate(outputs):
            if val > max_val:
                max_val = val
                max_idx = i
                
        return self.actions[max_idx]

    def modify_weights(self, deltas: dict):
        # Placeholder for backprop or evolutionary mutation
        pass
