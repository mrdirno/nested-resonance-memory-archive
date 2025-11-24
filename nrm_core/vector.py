"""
NRM Core: Vector Mathematics
"""
import math

class Vector:
    def __init__(self, values):
        self.values = tuple(float(v) for v in values)
        
    def __repr__(self):
        return f"Vector{self.values}"
        
    def __len__(self):
        return len(self.values)
        
    def __getitem__(self, index):
        return self.values[index]
        
    def dot(self, other):
        if len(self) != len(other):
            raise ValueError("Vector dimensions must match")
        return sum(a * b for a, b in zip(self.values, other.values))
        
    @property
    def magnitude(self):
        return math.sqrt(sum(x * x for x in self.values))
        
    def normalize(self):
        mag = self.magnitude
        if mag == 0:
            return Vector([0.0] * len(self))
        return Vector([x / mag for x in self.values])
        
    def cosine_similarity(self, other):
        dot = self.dot(other)
        mag_a = self.magnitude
        mag_b = other.magnitude
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)
        
    def __add__(self, other):
        if len(self) != len(other):
            raise ValueError("Vector dimensions must match")
        return Vector([a + b for a, b in zip(self.values, other.values)])
        
    def __mul__(self, scalar):
        return Vector([x * scalar for x in self.values])
