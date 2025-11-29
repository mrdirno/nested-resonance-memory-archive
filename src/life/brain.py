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
        self.output_size = 9
        
        # Random initialization
        self.w1 = [[random.uniform(-1, 1) for _ in range(self.hidden_size)] for _ in range(self.input_size)]
        self.b1 = [random.uniform(-1, 1) for _ in range(self.hidden_size)]
        
        self.w2 = [[random.uniform(-1, 1) for _ in range(self.output_size)] for _ in range(self.hidden_size)]
        self.b2 = [random.uniform(-1, 1) for _ in range(self.output_size)]
        
        self.actions = ['forage', 'reproduce', 'donate', 'flee', 'hunt', 'meditate', 'operate', 'reflect', 'codex']
        # Map actions to constants
        self.action_map = {
            'forage': 'pi_phase',
            'reproduce': 'e_phase',
            'donate': 'phi_phase',
            'flee': 'pi_phase', # Harmonics
            'hunt': 'e_phase',
            'meditate': 'spatial_phase', # Cycle 2548: Resonance Trapping
            'operate': 'phi_phase', # Cycle 2557: The Operator (Harmonic of Donate)
            'reflect': 'spatial_phase', # Cycle 2558: The Mirror
            'codex': 'phi_phase' # Cycle 2562: The Quine (Creative Creation)
        }
        self.weights = {} # Cycle 2540: Hebbian Weights
        
        # Cycle 2564: The Babble (Language)
        self.vocabulary = {} # {label: {type: count}}
        
        # Learning Context
        self.last_inputs = []
        self.last_hidden = []
        self.last_outputs = []
        
    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
        
    def learn_word(self, label, object_type, reward):
        """
        Cycle 2564: The Language Game.
        Reinforce or weaken label association.
        """
        if label not in self.vocabulary:
            self.vocabulary[label] = {}
            
        if object_type not in self.vocabulary[label]:
            self.vocabulary[label][object_type] = 0.0
            
        # Reinforcement
        self.vocabulary[label][object_type] += reward
        
        # Clean up weak associations
        if self.vocabulary[label][object_type] < 0:
            del self.vocabulary[label][object_type]
            
    def get_label(self, object_type):
        """
        Retrieve the strongest label for an object type.
        """
        best_label = None
        max_strength = -1.0
        
        for label, meanings in self.vocabulary.items():
            if object_type in meanings:
                strength = meanings[object_type]
                if strength > max_strength:
                    max_strength = strength
                    best_label = label
                    
        return best_label
        
    def get_meaning(self, label):
        """
        Retrieve the strongest meaning for a label.
        """
        if label not in self.vocabulary:
            return None
            
        meanings = self.vocabulary[label]
        if not meanings:
            return None
            
        # Return key with max value
        return max(meanings, key=meanings.get)

    def parse_sequence(self, sequence):
        """
        Cycle 2567: The Grammar.
        Parse a sequence of symbols into a structured thought.
        """
        parsed = {'target': None, 'direction': None, 'modifiers': []}
        
        for symbol in sequence:
            meaning = self.get_meaning(symbol)
            if not meaning:
                continue
                
            # Categorize meaning
            if meaning in ['FOOD', 'PREDATOR', 'WALL', 'FARM']:
                parsed['target'] = meaning
            elif meaning in ['NORTH', 'SOUTH', 'EAST', 'WEST']:
                parsed['direction'] = meaning
            else:
                parsed['modifiers'].append(meaning)
                
        return parsed

    def forward(self, inputs):
        self.last_inputs = inputs
        
        # Input -> Hidden
        hidden = []
        for j in range(self.hidden_size):
            activation = self.b1[j]
            for i in range(self.input_size):
                activation += inputs[i] * self.w1[i][j]
            hidden.append(self.sigmoid(activation))
        
        self.last_hidden = hidden
            
        # Hidden -> Output
        outputs = []
        for k in range(self.output_size):
            activation = self.b2[k]
            for j in range(self.hidden_size):
                activation += hidden[j] * self.w2[j][k]
            outputs.append(self.sigmoid(activation))
            
        self.last_outputs = outputs
        return outputs
        
    def tune_weights(self, reward):
        """
        Cycle 2559: The Tuning.
        Adjust weights based on reward signal (Hebbian Learning).
        """
        learning_rate = 0.1
        
        if not self.last_inputs or not self.last_hidden:
            return
            
        # Update W2 (Hidden -> Output)
        for k in range(self.output_size):
            for j in range(self.hidden_size):
                # Hebbian: if hidden[j] and output[k] are high, and reward is positive, strengthen.
                # Simple Gradient Proxy: reward * output * hidden
                delta = reward * self.last_outputs[k] * self.last_hidden[j] * learning_rate
                self.w2[j][k] += delta
                
        # Update W1 (Input -> Hidden)
        for j in range(self.hidden_size):
            for i in range(self.input_size):
                delta = reward * self.last_hidden[j] * self.last_inputs[i] * learning_rate
                self.w1[i][j] += delta

    def teach(self, action_name):
        """
        Supervised Learning trigger.
        Forces the brain to learn that `action_name` was the correct choice.
        """
        if action_name not in self.actions:
            return
            
        target_idx = self.actions.index(action_name)
        
        # Create One-Hot Target (Soft)
        # We want to encourage this action, so we pretend the output was 1.0 for this action
        # and 0.0 for others, then reinforce.
        
        # Save original outputs to restore? No, we want to overwrite for the learning step.
        # Ideally we calculate error (Target - Output), but tune_weights uses Hebbian (Output * Input).
        # So setting Output = Target mimics "This is what should have fired".
        
        new_outputs = [0.0] * self.output_size
        new_outputs[target_idx] = 1.0
        
        self.last_outputs = new_outputs
        self.tune_weights(1.0) # Positive reinforcement of the target state
        
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
