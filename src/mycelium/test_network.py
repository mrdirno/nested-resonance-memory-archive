"""
Test Mycelial Network Logic
===========================
Verifies that the Network can scan and map infected files.
"""

import unittest
import shutil
import os
from pathlib import Path
from src.mycelium.network import Mycelium
from src.mycelium.spore import Spore

class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("playground/network_test")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            
    def test_scan(self):
        """Test scanning logic."""
        # Create dummy files
        file_a = self.test_dir / "file_a.txt"
        file_b = self.test_dir / "file_b.txt"
        
        with open(file_a, 'w') as f: f.write("Data A")
        with open(file_b, 'w') as f: f.write("Data B")
        
        # Infect files
        spore1 = Spore("Agent-1")
        spore2 = Spore("Agent-2")
        
        spore1.infect(file_a) # Agent 1 in A
        spore1.infect(file_b) # Agent 1 in B
        spore2.infect(file_a) # Agent 2 in A
        
        # Scan
        network = Mycelium()
        graph = network.scan(self.test_dir)
        
        # Verify Graph
        self.assertIn("Agent-1", graph)
        self.assertIn("Agent-2", graph)
        
        self.assertEqual(len(graph["Agent-1"]), 2) # A and B
        self.assertEqual(len(graph["Agent-2"]), 1) # Only A
        
        # Verify Co-habitation
        residents = network.get_co_inhabitants(file_a)
        self.assertIn("Agent-1", residents)
        self.assertIn("Agent-2", residents)

if __name__ == "__main__":
    unittest.main()