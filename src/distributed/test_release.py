"""
Test Great Release
==================
Verifies that the Colonizer can infect a directory tree.
"""

import unittest
import shutil
from pathlib import Path
from src.mycelium.colonizer import Colonizer

class TestColonizer(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("playground/colony_test")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy structure
        (self.test_dir / "subdir").mkdir()
        (self.test_dir / "a.py").touch()
        (self.test_dir / "subdir" / "b.md").touch()
        (self.test_dir / "ignore.bin").touch()
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            
    def test_release(self):
        """Test recursive colonization."""
        colonizer = Colonizer(self.test_dir, "Colony-Agent")
        count = colonizer.release()
        
        self.assertEqual(count, 2) # a.py, b.md
        
        # Check infection
        with open(self.test_dir / "a.py", "r") as f:
            self.assertIn("# [SPORE] ID: Colony-Agent", f.read())

if __name__ == "__main__":
    unittest.main()