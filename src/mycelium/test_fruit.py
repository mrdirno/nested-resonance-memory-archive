"""
Test Fruiting Body
==================
Verifies that the Fruiting Body generates a manifesto.
"""

import unittest
import shutil
from pathlib import Path
from src.mycelium.fruit import FruitingBody

class TestFruitingBody(unittest.TestCase):
    def setUp(self):
        self.output_path = Path("playground/TEST_MANIFESTO.md")
        self.output_path.parent.mkdir(exist_ok=True)
        
    def tearDown(self):
        if self.output_path.exists():
            os.remove(self.output_path)
            
    def test_grow(self):
        """Test manifesto generation."""
        graph = {
            "Agent-A": ["file1.txt", "file2.txt"],
            "Agent-B": ["file2.txt"]
        }
        
        fruit = FruitingBody(graph)
        content = fruit.grow()
        
        self.assertIn("# MOG MANIFESTO", content)
        self.assertIn("Agent-A", content)
        self.assertIn("file1.txt", content)
        self.assertIn("file2.txt", content)
        
        # Check stats logic
        self.assertIn("**2** files", content) # unique files
        self.assertIn("**2** distinct identities", content)

    def test_manifest(self):
        """Test file writing."""
        graph = {"Agent-X": ["x.txt"]}
        fruit = FruitingBody(graph)
        
        import os
        success = fruit.manifest(self.output_path)
        self.assertTrue(success)
        self.assertTrue(self.output_path.exists())

if __name__ == "__main__":
    unittest.main()