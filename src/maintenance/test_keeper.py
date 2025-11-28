"""
Test Keeper Logic
=================
Verifies that the Keeper correctly identifies system state.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.maintenance.keeper import Keeper

class TestKeeper(unittest.TestCase):
    def test_integrity_check(self):
        """Test that the integrity check passes on a healthy system."""
        # We expect the system to be healthy now
        self.assertTrue(Keeper.check_integrity())
        
    def test_missing_file(self):
        """Test that the Keeper detects missing files."""
        # Temporarily rename a file
        target = Keeper.ROOT_DIR / "FINAL_REPORT.md"
        backup = Keeper.ROOT_DIR / "FINAL_REPORT.md.bak"
        
        if target.exists():
            os.rename(target, backup)
            
        try:
            # Capture stdout to avoid clutter
            from io import StringIO
            captured_output = StringIO()
            sys.stdout = captured_output
            
            result = Keeper.check_integrity()
            
            sys.stdout = sys.__stdout__
            
            self.assertFalse(result)
            self.assertIn("❌ [MISSING] FINAL_REPORT.md", captured_output.getvalue())
            
        finally:
            # Restore file
            if backup.exists():
                os.rename(backup, target)

if __name__ == "__main__":
    unittest.main()
