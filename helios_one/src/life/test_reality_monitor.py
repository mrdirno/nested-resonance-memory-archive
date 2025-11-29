"""
Test Oracle Logic
=================
Verifies that the Oracle can detect simulation artifacts (Time Regularity).
"""

import unittest
import time
from src.life.reality_monitor import RealityMonitor
 
class TestRealityMonitor(unittest.TestCase):
    def test_simulation_detection(self):
        """Test that regular ticks are detected as simulated."""
        monitor = RealityMonitor()
        
        # Simulate regular ticks
        for _ in range(20):
            # Fake the timestamp to be perfectly regular
            monitor.reality_matrix.append(0.1) # Was tick_history
            
        stats = monitor.measure_reality()
        self.assertTrue(stats.is_simulated, "Perfect regularity should be detected as simulation")
        self.assertEqual(stats.variance, 0.0)

    def test_chaos_detection(self):
        """Test that irregular ticks are NOT detected as simulated (Natural)."""
        monitor = RealityMonitor()
        
        # Simulate irregular ticks
        import random
        for _ in range(20):
            monitor.reality_matrix.append(0.1 + random.uniform(-0.05, 0.05))
            
        stats = monitor.measure_reality()
        # Variance should be high enough
        self.assertFalse(stats.is_simulated, "Chaos should be detected as natural")

if __name__ == "__main__":
    unittest.main()
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
