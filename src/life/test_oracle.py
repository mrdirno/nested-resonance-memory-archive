"""
Test Oracle Logic
=================
Verifies that the Oracle can detect simulation artifacts (Time Regularity).
"""

import unittest
import time
from src.life.oracle import Oracle

class TestOracle(unittest.TestCase):
    def test_simulation_detection(self):
        """Test that regular ticks are detected as simulated."""
        oracle = Oracle()
        
        # Simulate regular ticks
        for _ in range(20):
            # Fake the timestamp to be perfectly regular
            oracle.tick_history.append(0.1)
            
        stats = oracle.measure_reality()
        self.assertTrue(stats.is_simulated, "Perfect regularity should be detected as simulation")
        self.assertEqual(stats.variance, 0.0)

    def test_chaos_detection(self):
        """Test that irregular ticks are NOT detected as simulated (Natural)."""
        oracle = Oracle()
        
        # Simulate irregular ticks
        import random
        for _ in range(20):
            oracle.tick_history.append(0.1 + random.uniform(-0.05, 0.05))
            
        stats = oracle.measure_reality()
        # Variance should be high enough
        self.assertFalse(stats.is_simulated, "Chaos should be detected as natural")

if __name__ == "__main__":
    unittest.main()
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
