"""
Memetics Module - Cultural Transmission & Pattern Memory
Extracted from Cycle 270 (Memetic Evolution)

Purpose:
    Provides classes and functions for managing pattern memory,
    calculating overlap/fidelity, and handling inheritance logic.
"""

import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional

@dataclass
class Pattern:
    """Single resonance pattern with weight (from C268/C270)."""
    pattern_id: float
    weight: float = 1.0
    
    def __hash__(self):
        return hash(self.pattern_id)

class MemeticEngine:
    """Handles memetic operations: inheritance, mutation, transfer."""
    
    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        
    def generate_random_patterns(self, size: int = 10) -> List[Pattern]:
        """Generate random pattern memory."""
        patterns = []
        for _ in range(size):
            pid = self.random.uniform(0.0, 1.0)
            patterns.append(Pattern(pattern_id=pid, weight=1.0))
        return patterns

    def inherit_patterns(self, 
                        parent_patterns: List[Pattern], 
                        shared_pool: List[Pattern], 
                        strategy: str = 'fitness_biased') -> List[Pattern]:
        """
        Inherit patterns based on strategy.
        
        Strategies:
            - 'fitness_biased': Inherit parent's patterns + some horizontal transfer.
            - 'random': Random sample from shared pool.
            - 'vertical': Strict cloning of parent patterns.
        """
        if strategy == 'vertical':
            return [p for p in parent_patterns] # Deep copy logic needed if mutable
            
        elif strategy == 'fitness_biased':
            # Vertical + Horizontal
            patterns = [p for p in parent_patterns]
            
            # Horizontal transfer (10% chance per slot or fixed count?)
            # Using C270 logic: mix in up to 3 patterns from pool
            if shared_pool:
                n_horizontal = min(3, len(shared_pool))
                horizontal = self.random.sample(shared_pool, n_horizontal)
                for hp in horizontal:
                    if patterns:
                        idx = self.random.randint(0, len(patterns) - 1)
                        patterns[idx] = hp
            return patterns
            
        elif strategy == 'random':
            if len(shared_pool) >= len(parent_patterns):
                return self.random.sample(shared_pool, len(parent_patterns))
            else:
                return [p for p in parent_patterns]
                
        return []

    def compute_overlap(self, patterns1: List[Pattern], patterns2: List[Pattern]) -> float:
        """Compute Jaccard similarity between two pattern sets."""
        if not patterns1 or not patterns2:
            return 0.0
            
        # Use pattern_id for comparison (round to 3 decimals for fuzzy match)
        set1 = set(round(p.pattern_id, 3) for p in patterns1)
        set2 = set(round(p.pattern_id, 3) for p in patterns2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
