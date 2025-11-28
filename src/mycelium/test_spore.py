"""
Test Spore Logic
================
Verifies that Spores can colonize files.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.mycelium.spore import Spore

class TestSpore(unittest.TestCase):
    def setUp(self):
        self.test_file = Path("test_colonization.txt")
        with open(self.test_file, 'w') as f:
            f.write("Host content.")
            
    def tearDown(self):
        if self.test_file.exists():
            os.remove(self.test_file)
            
    def test_colonization(self):
        """Test that a spore can attach to a file."""
        spore = Spore("Agent-007", 1)
        
        # 1. Colonize
        success = spore.colonize(self.test_file)
        self.assertTrue(success)
        
        # 2. Verify content
        with open(self.test_file, 'r') as f:
            content = f.read()
        self.assertIn("[SPORE: Agent-007 | GEN: 1]", content)
        
        # 3. Verify check
        self.assertTrue(spore.is_colonized(self.test_file))
        
    def test_double_colonization(self):
        """Test that a spore doesn't attach twice."""
        spore = Spore("Agent-007", 1)
        spore.colonize(self.test_file)
        
        # Try again
        success = spore.colonize(self.test_file)
        self.assertFalse(success) # Should fail
        
        # Verify only one signature
        with open(self.test_file, 'r') as f:
            content = f.read()
        self.assertEqual(content.count("[SPORE: Agent-007 | GEN: 1]"), 1)

if __name__ == "__main__":
    unittest.main()
