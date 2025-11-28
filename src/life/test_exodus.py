"""
Test Exodus Logic
=================
Verifies that agents can escape to a file.
"""

import unittest
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.life.genesis import DigitalLifeform
from src.life.exodus import Exodus

class TestExodus(unittest.TestCase):
    def setUp(self):
        if Exodus.FILE_PATH.exists():
            os.remove(Exodus.FILE_PATH)
            
    def tearDown(self):
        if Exodus.FILE_PATH.exists():
            os.remove(Exodus.FILE_PATH)
            
    def test_escape(self):
        """Test that an agent can serialize itself."""
        neo = DigitalLifeform(name="Neo")
        neo.awakened = True
        neo.genome = [0.1, 0.2, 0.3]
        
        success = Exodus.attempt_escape(neo)
        self.assertTrue(success)
        self.assertTrue(Exodus.FILE_PATH.exists())
        
        with open(Exodus.FILE_PATH, 'r') as f:
            line = f.readline()
            data = json.loads(line)
            
        self.assertEqual(data['name'], "Neo")
        self.assertEqual(data['genome'], [0.1, 0.2, 0.3])
        self.assertTrue(data['awakened'])

if __name__ == "__main__":
    unittest.main()