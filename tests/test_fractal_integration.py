#!/usr/bin/env python3
"""
Integration Test for Fractal Module
Verifies that Agent, Composition, Decomposition, Resonance, and Memory work together.
"""
import sys
import unittest
import numpy as np
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from code.fractal.agent import FractalAgent
from code.fractal.composition import CompositionEngine
from code.fractal.decomposition import DecompositionEngine
from code.fractal.resonance import ResonanceDetector
from code.memory.pattern import PatternMemory

class TestFractalIntegration(unittest.TestCase):
    def setUp(self):
        self.comp_engine = CompositionEngine(resonance_threshold=0.8, energy_threshold=10.0)
        self.decomp_engine = DecompositionEngine(energy_threshold=5.0)
        self.res_detector = ResonanceDetector(threshold=0.8)
        
    def test_agent_lifecycle(self):
        """Test full lifecycle: Creation -> Resonance -> Composition -> Memory -> Decomposition"""
        print("\nTesting Fractal Agent Lifecycle...")
        
        # 1. Create Agents
        agents = [
            FractalAgent(agent_id=f"a{i}", energy=20.0, phase=0.0)
            for i in range(3)
        ]
        # Align phases for resonance
        for a in agents:
            a.state.phase = 1.0 
            
        # 2. Detect Resonance
        print("- Checking Resonance...")
        matrix = self.res_detector.calculate_resonance_matrix(agents)
        self.assertTrue(np.all(matrix > 0.9), "Agents should be resonant")
        
        clusters = self.comp_engine.detect_clusters(agents)
        self.assertEqual(len(clusters), 1, "Should detect 1 cluster")
        self.assertEqual(len(clusters[0]), 3, "Cluster should have 3 agents")
        
        # 3. Compose
        print("- Executing Composition...")
        cluster_agent = self.comp_engine.compose(clusters[0])
        self.assertIsNotNone(cluster_agent, "Composition should succeed")
        self.assertEqual(cluster_agent.state.depth, 1, "Cluster depth should be 1")
        self.assertEqual(len(cluster_agent.state.children_ids), 3, "Cluster should have 3 children")
        self.assertAlmostEqual(cluster_agent.state.energy, 60.0, places=1, msg="Energy should be summed")
        
        # 4. Memory
        print("- Testing Memory Transfer...")
        # Add pattern to cluster
        cluster_agent.remember_pattern("test_pattern", 0.9)
        self.assertEqual(cluster_agent.recall_pattern("test_pattern"), 0.9)
        
        # 5. Decompose
        print("- Executing Decomposition...")
        # Force energy low to trigger decomposition
        cluster_agent.state.energy = 4.0 
        
        can_decomp, reason = self.decomp_engine.can_decompose(cluster_agent)
        self.assertTrue(can_decomp, f"Should be able to decompose: {reason}")
        
        constituents = self.decomp_engine.decompose(cluster_agent)
        self.assertIsNotNone(constituents, "Decomposition should succeed")
        self.assertEqual(len(constituents), 3, "Should release 3 constituents")
        
        # Check memory inheritance
        for agent in constituents:
            self.assertEqual(agent.state.depth, 0, "Constituents should be depth 0")
            self.assertEqual(agent.recall_pattern("test_pattern"), 0.9, "Memory should be inherited")
            
        print("Lifecycle Test Passed!")

if __name__ == "__main__":
    unittest.main()
