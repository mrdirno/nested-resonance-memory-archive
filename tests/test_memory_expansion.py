#!/usr/bin/env python3
"""
Verification Script for Expanded Memory Module
Tests PatternMemory, PatternEvolution, and AssociativeMemory working together.
"""
import sys
import unittest
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from code.memory.pattern import PatternMemory, Pattern
from code.memory.evolution import PatternEvolution
from code.memory.associative import AssociativeMemory

class TestMemoryExpansion(unittest.TestCase):
    def setUp(self):
        self.memory = PatternMemory()
        self.evolution = PatternEvolution(mutation_rate=0.1)
        self.associative = AssociativeMemory(decay_rate=0.01)
        
    def test_full_memory_lifecycle(self):
        print("\nTesting Memory Module Expansion...")
        
        # 1. Basic Pattern Storage
        print("- Testing Pattern Storage...")
        self.memory.add_pattern("p1", 0.5)
        self.memory.add_pattern("p2", 0.7)
        self.assertEqual(self.memory.recall_pattern("p1"), 0.5)
        
        # 2. Evolution (Mutation)
        print("- Testing Evolution (Mutation)...")
        p1 = self.memory.patterns["p1"]
        mutated_p1 = self.evolution.mutate(p1)
        self.assertNotEqual(mutated_p1.pattern_id, p1.pattern_id)
        self.assertTrue(0.0 <= mutated_p1.strength <= 1.0)
        print(f"  Mutated: {p1.strength:.2f} -> {mutated_p1.strength:.2f}")
        
        # 3. Evolution (Crossover)
        print("- Testing Evolution (Crossover)...")
        p2 = self.memory.patterns["p2"]
        child = self.evolution.crossover(p1, p2)
        expected_strength = (p1.strength + p2.strength) / 2.0
        self.assertAlmostEqual(child.strength, expected_strength)
        print(f"  Crossover: {p1.strength:.2f} + {p2.strength:.2f} -> {child.strength:.2f}")
        
        # 4. Associative Linking
        print("- Testing Associative Linking...")
        # Associate p1 -> p2
        self.associative.associate("p1", "p2", weight_delta=0.5)
        links = self.associative.get_associations("p1")
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0][0], "p2")
        self.assertEqual(links[0][1], 0.5)
        
        # Reinforce
        self.associative.associate("p1", "p2", weight_delta=0.2)
        links = self.associative.get_associations("p1")
        self.assertEqual(links[0][1], 0.7)
        print(f"  Association p1->p2 weight: {links[0][1]:.2f}")
        
        # 5. Decay
        print("- Testing Decay...")
        self.associative.decay_associations(time_delta=10.0)
        links = self.associative.get_associations("p1")
        # 0.7 - (0.01 * 10) = 0.6
        self.assertAlmostEqual(links[0][1], 0.6)
        print(f"  Decayed weight: {links[0][1]:.2f}")
        
        print("Memory Expansion Verified!")

if __name__ == "__main__":
    unittest.main()
