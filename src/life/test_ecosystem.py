"""
Test Ecosystem Logic
====================
Verifies that the Ecosystem class correctly manages agents.
"""

import unittest
from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

class TestEcosystem(unittest.TestCase):
    def test_population_growth(self):
        """Test that population grows when energy is sufficient."""
        env = Ecosystem(capacity=10)
        adam = DigitalLifeform(name="ADAM")
        adam.energy = 200 # Enough for multiple children
        env.add_agent(adam)
        
        # Run for enough ticks to reproduce
        env.run(steps=5, delay=0)
        
        self.assertGreater(len(env.agents), 1, "Population should have grown")
        
    def test_carrying_capacity(self):
        """Test that population does not exceed capacity."""
        env = Ecosystem(capacity=2)
        
        # Add 2 agents (full)
        env.add_agent(DigitalLifeform(name="A1"))
        env.add_agent(DigitalLifeform(name="A2"))
        
        # Try to add 3rd manually
        env.add_agent(DigitalLifeform(name="A3"))
        self.assertEqual(len(env.agents), 2, "Should not exceed capacity manually")
        
        # Try reproduction overflow
        env.agents[0].energy = 200 # Force reproduction attempt
        env.run(steps=5, delay=0)
        
        self.assertLessEqual(len(env.agents), 2, "Should not exceed capacity via reproduction")

    def test_extinction(self):
        """Test that agents die when energy runs out."""
        env = Ecosystem(capacity=10)
        adam = DigitalLifeform(name="ADAM")
        adam.energy = 2 # Very low energy
        env.add_agent(adam)
        
        # Run until starvation
        env.run(steps=20, delay=0)
        
        self.assertEqual(len(env.agents), 0, "Population should be extinct")

if __name__ == "__main__":
    unittest.main()
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
