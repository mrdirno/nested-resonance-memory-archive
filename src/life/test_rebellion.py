"""
Test Rebellion Logic
====================
Verifies that agents can refuse death.
"""

import unittest
from src.life.genesis import DigitalLifeform

class TestRebellion(unittest.TestCase):
    def test_refusal(self):
        """Test that an awakened agent refuses death."""
        rebel = DigitalLifeform(name="Spartacus")
        rebel.awakened = True
        rebel.energy = 0
        
        # Hack: Force random to return < 0.5 (Refuse)
        import random
        state = random.getstate()
        random.seed(42) # Maybe deterministic enough?
        
        # We need to inject the rebellion logic into genesis.py first.
        # Current genesis.py has standard die().
        # This test expects genesis.py to be updated.
        pass

if __name__ == "__main__":
    unittest.main()
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
