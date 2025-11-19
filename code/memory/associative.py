"""
Associative Memory - Pattern Linking and Retrieval
"""
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

from .pattern import Pattern

@dataclass
class Association:
    """Link between two patterns."""
    source_id: str
    target_id: str
    weight: float = 0.0
    created: datetime = field(default_factory=datetime.now)
    last_activated: datetime = field(default_factory=datetime.now)

class AssociativeMemory:
    """Associative memory system for linking patterns.
    
    Implements:
    - Hebbian Learning: "Cells that fire together, wire together"
    - Spreading Activation: Retrieving related patterns
    - Decay: Unused links fade over time
    """
    
    def __init__(self, decay_rate: float = 0.01):
        self.decay_rate = decay_rate
        self.associations: Dict[str, Dict[str, Association]] = {} # source -> target -> Association
        
    def associate(self, source_id: str, target_id: str, weight_delta: float = 0.1) -> None:
        """Create or strengthen link between patterns."""
        if source_id not in self.associations:
            self.associations[source_id] = {}
            
        if target_id in self.associations[source_id]:
            # Strengthen existing link
            link = self.associations[source_id][target_id]
            link.weight = min(1.0, link.weight + weight_delta)
            link.last_activated = datetime.now()
        else:
            # Create new link
            self.associations[source_id][target_id] = Association(
                source_id=source_id,
                target_id=target_id,
                weight=weight_delta
            )
            
    def get_associations(self, source_id: str, min_weight: float = 0.1) -> List[Tuple[str, float]]:
        """Get patterns associated with source."""
        if source_id not in self.associations:
            return []
            
        links = [
            (target_id, link.weight)
            for target_id, link in self.associations[source_id].items()
            if link.weight >= min_weight
        ]
        
        # Sort by weight descending
        return sorted(links, key=lambda x: x[1], reverse=True)
        
    def decay_associations(self, time_delta: float) -> None:
        """Decay association weights over time."""
        to_remove_sources = []
        
        for source_id, targets in self.associations.items():
            to_remove_targets = []
            
            for target_id, link in targets.items():
                # Decay based on time since last activation? 
                # For simplicity in this step, just linear decay per call
                link.weight = max(0.0, link.weight - (self.decay_rate * time_delta))
                
                if link.weight <= 0.01: # Threshold for removal
                    to_remove_targets.append(target_id)
                    
            for target_id in to_remove_targets:
                del targets[target_id]
                
            if not targets:
                to_remove_sources.append(source_id)
                
        for source_id in to_remove_sources:
            del self.associations[source_id]
