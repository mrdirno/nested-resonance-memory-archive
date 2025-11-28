"""
Test Culture Logic
==================
Verifies that agents can learn and transmit memes.
"""

import unittest
import unittest.mock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem
from src.life.signal import Signal

class TestCulture(unittest.TestCase):
    def test_learning(self):
        """Test that an agent learns from a meme."""
        student = DigitalLifeform(name="Student")
        
        # Brain init: 'donate': [0.5, -0.5] (from brain.py)
        # Bias is index 1 now? No, brain.py says:
        # 'donate': [0.5, -0.5] -> [Energy, Bias]
        # So bias is index 1.
        
        initial_bias = student.brain.weights['donate'][1]
        self.assertEqual(initial_bias, -0.5)
        
        # Create a "Good Idea" meme (Donate +1.0)
        meme_content = {'donate': 1.0}
        meme_payload = {'content': meme_content, 'virality': 1.0} # 100% chance to learn
        
        # Inject meme signal
        sig = Signal(type='MEME', strength=1.0, source_id='Teacher', payload=meme_payload)
        
        # Student receives signal
        student.communicator.receive(sig)
        
        # Act triggers processing
        student.act()
        
        # Verify learning
        # modify_weights adds to the LAST element.
        # So -0.5 + 1.0 = 0.5
        new_bias = student.brain.weights['donate'][1]
        self.assertEqual(new_bias, 0.5)
        
        # Verify meme storage
        self.assertEqual(len(student.memes), 1)
        self.assertEqual(student.memes[0], meme_payload)

    @unittest.mock.patch('random.random')
    def test_transmission(self, mock_random):
        """Test that an agent broadcasts a known meme."""
        # Mock random to always return 0.05 (trigger broadcast)
        mock_random.return_value = 0.05
        
        teacher = DigitalLifeform(name="Teacher")
        meme_payload = {'content': {'donate': 1.0}, 'virality': 1.0}
        teacher.memes.append(meme_payload)
        
        broadcasted = False
        for i in range(10):
            teacher.intent = None
            sig = teacher.act()
            if sig and sig.type == 'MEME':
                broadcasted = True
                self.assertEqual(sig.payload, meme_payload)
                break
                
        self.assertTrue(broadcasted, "Teacher should have broadcasted meme")

if __name__ == "__main__":
    unittest.main()
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
