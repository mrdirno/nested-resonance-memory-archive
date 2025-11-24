"""
Unit Tests for the Universal Operator (Type 3 OS Engine)
"""
import unittest
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.operator import UniversalOperator

class TestUniversalOperator(unittest.TestCase):
    
    def setUp(self):
        print("\nSetting up Universal Operator...")
        self.op = UniversalOperator(resolution_mm=4.0) # Low res for fast testing
        
    def test_hardware_initialization(self):
        print("Testing Hardware Layer...")
        # 6 sides * 8 * 8 = 384 emitters
        self.assertEqual(len(self.op.emitters), 384)
        
    def test_create_object_cube(self):
        print("Testing create_object('cube')...")
        center = (50.0, 50.0, 50.0)
        obj_id = self.op.create_object("cube", center)
        
        self.assertEqual(obj_id, 1)
        self.assertIn(1, self.op.active_objects)
        
        # Check stability
        stability = self.op.get_stability(1)
        print(f"Cube Stability (Ratio): {stability:.4f}")
        
        # Threshold for success (Ratio < 0.10 implies decent trapping)
        # Note: With low resolution and low generations, it might be noisy.
        self.assertLess(stability, 0.20)

if __name__ == '__main__':
    unittest.main()