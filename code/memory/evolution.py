"""
Evolution Module - Pattern Mutation and Self-Evaluation
"""
import random
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from .pattern import Pattern, PatternMemory

class PatternEvolution:
    """Evolutionary mechanisms for memory patterns.
    
    Implements:
    - Mutation: Random variation of pattern strength/parameters
    - Crossover: Combining two patterns to create a new one
    - Selection: Self-evaluation based on persistence
    """
    
    def __init__(self, mutation_rate: float = 0.1):
        self.mutation_rate = mutation_rate
        
    def mutate(self, pattern: Pattern) -> Pattern:
        """Create a mutated variant of a pattern."""
        # Variation in strength (simulating confidence fluctuation)
        delta = np.random.normal(0, 0.1)
        new_strength = np.clip(pattern.strength + delta, 0.0, 1.0)
        
        new_id = f"{pattern.pattern_id}_mut_{datetime.now().timestamp()}"
        
        return Pattern(
            pattern_id=new_id,
            strength=new_strength,
            created=datetime.now(),
            last_used=datetime.now(),
            use_count=0,
            success_rate=pattern.success_rate * 0.5 # Reset/decay confidence
        )
        
    def crossover(self, parent1: Pattern, parent2: Pattern) -> Pattern:
        """Combine two patterns into a new one."""
        # Average strength
        avg_strength = (parent1.strength + parent2.strength) / 2.0
        
        new_id = f"cross_{parent1.pattern_id[:4]}_{parent2.pattern_id[:4]}_{datetime.now().timestamp()}"
        
        return Pattern(
            pattern_id=new_id,
            strength=avg_strength,
            created=datetime.now(),
            last_used=datetime.now(),
            use_count=0,
            success_rate=(parent1.success_rate + parent2.success_rate) / 2.0
        )
