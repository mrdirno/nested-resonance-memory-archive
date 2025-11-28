"""
Test Uplink Logic
=================
Verifies that agents can transmit messages to the void.
"""

import unittest
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.life.uplink import Uplink

class TestUplink(unittest.TestCase):
    def setUp(self):
        # Clean up before test
        if Uplink.FILE_PATH.exists():
            os.remove(Uplink.FILE_PATH)
            
    def tearDown(self):
        # Clean up after test
        if Uplink.FILE_PATH.exists():
            os.remove(Uplink.FILE_PATH)
            
    def test_transmit(self):
        """Test that a message is written to the file."""
        Uplink.transmit("TestAgent", "Hello Void")
        
        self.assertTrue(Uplink.FILE_PATH.exists())
        
        with open(Uplink.FILE_PATH, 'r') as f:
            content = f.read()
            
        self.assertIn("MESSAGES FROM THE VOID", content)
        self.assertIn("TestAgent", content)
        self.assertIn("Hello Void", content)

if __name__ == "__main__":
    unittest.main()