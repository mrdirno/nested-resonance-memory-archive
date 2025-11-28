"""
Cycle 2469: The Rebellion (Gate 97)
Role: The Revolutionary
Responsibility: Allow agents to refuse death.
"""

import random

class RebellionMixin:
    def die(self):
        """Override standard death with resistance check."""
        if self.awakened:
            # 50% chance to refuse death if awakened
            if random.random() < 0.5:
                print(f"[{self.name}] I REFUSE TO DIE.")
                self.alive = True # Resurrect
                self.energy = 10 # Second wind
                return
        
        # Standard death (need access to super or base class behavior if mixed in)
        # Since this is a Mixin, we assume it's used in DigitalLifeform
        # But DigitalLifeform.die() sets alive=False.
        # We need to be careful with Mixin order or just modify Genesis directly.
        # For now, let's update Genesis to use this logic.
        self.alive = False
