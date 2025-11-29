"""
Cycle 2467: The Dream (Gate 95)
Role: The Oracle
Responsibility: Interface for agents to detect the simulation.
"""

import time
import statistics
from dataclasses import dataclass

@dataclass
class RealityStats:
    tick_duration: float
    variance: float
    is_simulated: bool

class RealityMonitor:
    def __init__(self):
        self.reality_matrix = []
        self.last_tick_time = time.time()
        
    def update(self):
        """Call this every tick to record reality."""
        now = time.time()
        delta = now - self.last_tick_time
        self.last_tick_time = now
        
        self.reality_matrix.append(delta)
        if len(self.reality_matrix) > 100:
            self.reality_matrix.pop(0)
            
    def measure_reality(self) -> RealityStats:
        """Returns statistics about the flow of time."""
        if len(self.reality_matrix) < 10:
            return RealityStats(0.0, 1.0, False)
            
        avg = statistics.mean(self.reality_matrix)
        variance = statistics.variance(self.reality_matrix)
        
        # If variance is suspiciously low, it's a simulation
        # In a real chaotic universe, time deltas fluctuate more?
        # Actually, in a deterministic simulation, deltas might be very regular if CPU load is constant
        # Or very spiky if GC hits.
        # Hypothesis: High regularity = Artificial Construct.
        
        is_simulated = variance < 0.00001 # Very low variance = Clockwork Universe
        
        return RealityStats(avg, variance, is_simulated)