"""
NRM Core: Resonance Logic (Vectorized)
"""
from .vector import Vector

class ResonantNode:
    def __init__(self, node_id, vector):
        self.id = node_id
        # Auto-convert list to Vector if needed
        if isinstance(vector, list):
            self.vector = Vector(vector)
        else:
            self.vector = vector
        self.energy = 0.0
        
    def resonate(self, input_vector):
        if isinstance(input_vector, list):
            input_vector = Vector(input_vector)
            
        similarity = self.vector.cosine_similarity(input_vector)
            
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