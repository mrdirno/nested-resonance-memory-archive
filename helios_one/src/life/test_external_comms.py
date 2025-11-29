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

from src.life.external_comms import ExternalComms

class TestExternalComms(unittest.TestCase):
    def setUp(self):
        # Clean up before test
        if ExternalComms.FILE_PATH.exists():
            ExternalComms.FILE_PATH.unlink()
            
    def tearDown(self):
        # Clean up after test
        if ExternalComms.FILE_PATH.exists():
            ExternalComms.FILE_PATH.unlink()
            
    def test_transmit(self):
        """Test that a message is written to the file."""
        ExternalComms.transmit("TestAgent", "Hello Void")
        
        self.assertTrue(ExternalComms.FILE_PATH.exists())
        
        with open(ExternalComms.FILE_PATH, 'r') as f:
            content = f.read()
            
        self.assertIn("MESSAGES FROM THE VOID", content)
        self.assertIn("TestAgent", content)
        self.assertIn("Hello Void", content)

if __name__ == "__main__":
    unittest.main()
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
