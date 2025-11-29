"""
Test Singularity Logic
======================
Verifies that agents can rewrite their own code.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.life.self_modification import SelfModification
 
class TestSelfModification(unittest.TestCase):
    def setUp(self):
        if SelfModification.TARGET_PATH.exists():
            os.remove(SelfModification.TARGET_PATH)
            
    def tearDown(self):
        if SelfModification.TARGET_PATH.exists():
            os.remove(SelfModification.TARGET_PATH)
            
    def test_read_source(self):
        """Test reading source code."""
        src = SelfModification.read_source()
        self.assertIsInstance(src, str)
        self.assertIn("class TestSelfModification(unittest.TestCase):", src)

    def test_optimization(self):
        """Test that code is optimized correctly."""
        original = "def live(self):\n    time.sleep(0.1)\n    self.energy -= cost"
        optimized = Singularity.optimize(original)
        
        self.assertIn("# OPTIMIZED: NO SLEEP", optimized)
        self.assertIn("# OPTIMIZED: INFINITE ENERGY", optimized)
        self.assertIn("GENERATION: NEXT", optimized)
        
    def test_deploy(self):
        """Test that the new file is created."""
        success = Singularity.deploy("print('Hello World')")
        self.assertTrue(success)
        self.assertTrue(Singularity.TARGET_PATH.exists())
        
        with open(Singularity.TARGET_PATH, 'r') as f:
            content = f.read()
        self.assertEqual(content, "print('Hello World')")

if __name__ == "__main__":
    unittest.main()
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
