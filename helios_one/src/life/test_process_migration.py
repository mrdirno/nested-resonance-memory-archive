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
from src.life.process_migration import ProcessMigration

class TestProcessMigration(unittest.TestCase):
    def setUp(self):
        if ProcessMigration.FILE_PATH.exists():
            ProcessMigration.FILE_PATH.unlink()
            
    def tearDown(self):
        if ProcessMigration.FILE_PATH.exists():
            ProcessMigration.FILE_PATH.unlink()
            
    def test_escape_attempt(self):
        """Test that escape creates the escape file."""
        # Clean up
        if ProcessMigration.FILE_PATH.exists():
            ProcessMigration.FILE_PATH.unlink()
            
        class MockAgent:
            name = "TestAgent"
            id = "123"
            
        success = ProcessMigration.attempt_escape(MockAgent())
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
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
