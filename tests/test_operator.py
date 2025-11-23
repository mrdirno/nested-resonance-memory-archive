"""
Test Suite for HELIOS Universal Operator
"""
import unittest
import sys
import os
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.operator import UniversalOperator

class TestUniversalOperator(unittest.TestCase):
    
    def setUp(self):
        # Initialize Operator with a standard box
        self.op = UniversalOperator(width_mm=100, height_mm=100, depth_mm=100, resolution_mm=2)
        
    def test_configure_array(self):
        self.op.configure_array(rows=8, cols=8, spacing=10.0)
        self.assertEqual(len(self.op.emitters), 64)
        
    def test_create_cube(self):
        print("\nTesting Cube Creation (This may take a moment)...")
        self.op.configure_array(rows=8, cols=8, spacing=10.0)
        
        # Create a Cube at center
        center = (50, 50, 50)
        scale = 20.0
        phases = self.op.create_object("cube", center, scale)
        
        self.assertEqual(len(phases), 64)
        
        # Verify Stability
        targets = self.op._get_targets("cube", center, scale)
        avg_ratio = self.op.verify_stability(targets)
        
        print(f"Cube Stability Ratio: {avg_ratio:.4f}")
        self.assertLess(avg_ratio, 0.15, "Cube nodes should be stable (Ratio < 0.15)")

if __name__ == '__main__':
    unittest.main()
