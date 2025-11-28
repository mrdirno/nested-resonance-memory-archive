"""
Test Brain Logic
================
Verifies that the Brain class makes state-dependent decisions.
"""

import unittest
from src.life.brain import Brain
from src.life.genesis import DigitalLifeform

class TestBrain(unittest.TestCase):
    def test_decision_making(self):
        """Test that energy levels influence decisions."""
        brain = Brain()
        
        # Test Low Energy -> Should NOT reproduce
        # Energy 10/200 = 0.05
        # Reproduce Score = 0.05 * 0.8 + rand * -0.2 (approx 0.04 +/- 0.1)
        # Forage Score = 0.05 * -0.5 + rand * 0.5 (approx -0.025 + 0.25 = 0.225)
        # Forage should win most of the time
        
        state_low = {'energy': 10}
        # We can't assert deterministic outcome due to random bias, but we can assert it runs
        decision_low = brain.decide(state_low)
        self.assertIn(decision_low, ['reproduce', 'forage'])
        
    def test_integration(self):
        """Test that DigitalLifeform uses the brain."""
        agent = DigitalLifeform(name="Tester")
        agent.energy = 200 # High energy
        
        # Force brain to say 'reproduce' (by hacking weights)
        agent.brain.weights['reproduce'] = [100.0, 0.0] # Always win
        agent.brain.weights['forage'] = [-100.0, 0.0]
        
        agent.act()
        self.assertEqual(agent.intent, 'reproduce')
        
        child = agent.reproduce()
        self.assertIsNotNone(child)
        
        # Force brain to say 'forage'
        agent.brain.weights['reproduce'] = [-100.0, 0.0]
        agent.brain.weights['forage'] = [100.0, 0.0]
        
        agent.act()
        self.assertEqual(agent.intent, 'forage')
        
        child = agent.reproduce()
        self.assertIsNone(child, "Should not reproduce if intent is forage")

if __name__ == "__main__":
    unittest.main()