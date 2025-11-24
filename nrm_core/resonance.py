"""
NRM Core: Resonance Logic
"""
import math
import random

class ResonantNode:
    def __init__(self, node_id, vector):
        self.id = node_id
        self.vector = vector # List or Tuple of floats
        self.energy = 0.0
        
    def resonate(self, input_vector):
        # Dot product similarity
        dot = sum(a * b for a, b in zip(self.vector, input_vector))
        mag_a = math.sqrt(sum(a * a for a in self.vector))
        mag_b = math.sqrt(sum(b * b for b in input_vector))
        
        if mag_a == 0 or mag_b == 0:
            similarity = 0.0
        else:
            similarity = dot / (mag_a * mag_b)
            
        # Energy increases based on similarity
        if similarity > 0:
            self.energy += similarity
            
    def decay(self, rate=0.1):
        self.energy *= (1.0 - rate)

class ResonantField:
    def __init__(self):
        self.nodes = {}
        
    def add_node(self, node_id, vector):
        self.nodes[node_id] = ResonantNode(node_id, vector)
        
    def stimulate(self, vector):
        for node in self.nodes.values():
            node.resonate(vector)
            
    def get_active_nodes(self, threshold=0.5):
        return {nid: n.energy for nid, n in self.nodes.items() if n.energy > threshold}
        
    def decay(self):
        for node in self.nodes.values():
            node.decay()
