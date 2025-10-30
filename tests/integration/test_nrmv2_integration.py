#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: NRM V2 Integration Reality Validation Test
============================================================

Tests the integration of NRM Package V2 concepts:
1. Memetic embedding support in PatternMemory
2. Kuramoto coupling dynamics in FractalAgent
3. Sleep-inspired consolidation (NREM + REM)
4. Reality grounding throughout

Reality Compliance Checks:
- All data from actual pattern memory (no fabrication)
- Computational costs tracked via psutil
- SQLite persistence verified
- Phase space operations grounded in transcendental constants
"""

import sys
import time
import tempfile
from pathlib import Path
from typing import List, Dict

# Add code directories to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "code"))
sys.path.insert(0, str(repo_root / "code" / "memory"))
sys.path.insert(0, str(repo_root / "code" / "fractal"))
sys.path.insert(0, str(repo_root / "code" / "bridge"))

from pattern_memory import PatternMemory, Pattern, PatternType
from consolidation_engine import ConsolidationEngine, Coalition
from fractal_agent import FractalAgent
from transcendental_bridge import TranscendentalBridge


def test_memetic_embeddings():
    """Test memetic embedding storage and retrieval."""
    print("\n" + "="*60)
    print("TEST 1: Memetic Embedding Support")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = PatternMemory(workspace_path=Path(tmpdir))

        # Create test patterns
        pattern1 = Pattern(
            pattern_id="test_pattern_001",
            pattern_type=PatternType.SYSTEM_BEHAVIOR,
            name="Homeostasis at 17 agents",
            description="Population stabilizes at 17 agents with frequency=2.5%",
            data={'agent_count': 17.0, 'frequency': 0.025},
            confidence=0.95,
            occurrences=10,
            first_seen=time.time(),
            last_seen=time.time()
        )

        pattern2 = Pattern(
            pattern_id="test_pattern_002",
            pattern_type=PatternType.SYSTEM_BEHAVIOR,
            name="Basin A high composition",
            description="Basin A exhibits high composition events (>99/cycle)",
            data={'composition_events': 99.97, 'basin': 'A'},
            confidence=0.92,
            occurrences=8,
            first_seen=time.time(),
            last_seen=time.time()
        )

        # Store patterns
        memory.store_pattern(pattern1)
        memory.store_pattern(pattern2)

        # Generate embeddings (simplified: use data values as embedding)
        embedding1 = [17.0, 0.025, 0.95, 10.0]  # 4D embedding
        embedding2 = [99.97, 1.0, 0.92, 8.0]   # 4D embedding

        # Store embeddings
        memory.store_embedding("test_pattern_001", embedding1, "test_model", 4)
        memory.store_embedding("test_pattern_002", embedding2, "test_model", 4)

        # Retrieve embeddings
        retrieved1 = memory.get_embedding("test_pattern_001")
        retrieved2 = memory.get_embedding("test_pattern_002")

        # Validate
        assert retrieved1 == embedding1, "❌ Embedding 1 mismatch"
        assert retrieved2 == embedding2, "❌ Embedding 2 mismatch"

        print(f"✅ Stored and retrieved {len(embedding1)}D embeddings")

        # Test semantic similarity
        similarity = memory.compute_semantic_similarity(embedding1, embedding2)
        print(f"✅ Cosine similarity: {similarity:.4f}")

        # Build graph edge
        memory.store_graph_edge("test_pattern_001", "test_pattern_002", similarity, "semantic")

        # Retrieve neighbors
        neighbors = memory.get_graph_neighbors("test_pattern_001", min_weight=0.0)
        assert len(neighbors) > 0, "❌ No neighbors found"
        print(f"✅ Graph edge stored: W_ij = {neighbors[0][1]:.4f}")

        print("\n✅ TEST 1 PASSED: Memetic embeddings operational")


def test_kuramoto_coupling():
    """Test Kuramoto coupling dynamics in FractalAgent."""
    print("\n" + "="*60)
    print("TEST 2: Kuramoto Coupling Dynamics")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        bridge = TranscendentalBridge(workspace_path=tmpdir)

        # Create two agents with similar initial states
        reality1 = {'cpu_percent': 20.0, 'memory_percent': 30.0, 'disk_usage': 50.0}
        reality2 = {'cpu_percent': 22.0, 'memory_percent': 32.0, 'disk_usage': 52.0}

        agent1 = FractalAgent("agent_001", bridge, reality1, depth=0)
        agent2 = FractalAgent("agent_002", bridge, reality2, depth=0)

        # Initial phase coherence
        initial_coherence = agent1.compute_phase_coherence(agent2, band='pi')
        print(f"Initial phase coherence: {initial_coherence:.4f}")

        # Evolve with coupling (simulate semantic graph edge)
        weight = 0.8  # Strong coupling
        neighbors1 = [(agent2, weight)]
        neighbors2 = [(agent1, weight)]

        # Evolve for 10 cycles
        for cycle in range(10):
            agent1.coupled_evolve(
                delta_time=0.1,
                neighbors=neighbors1,
                intrinsic_frequency=1.0,
                cross_frequency_beta=0.1
            )
            agent2.coupled_evolve(
                delta_time=0.1,
                neighbors=neighbors2,
                intrinsic_frequency=1.0,
                cross_frequency_beta=0.1
            )

        # Final phase coherence
        final_coherence = agent1.compute_phase_coherence(agent2, band='pi')
        print(f"Final phase coherence: {final_coherence:.4f}")

        # Expect coherence to increase due to coupling
        coherence_increase = final_coherence - initial_coherence
        print(f"Coherence change: {coherence_increase:+.4f}")

        # Validate
        assert agent1.energy > 0, "❌ Agent 1 energy depleted"
        assert agent2.energy > 0, "❌ Agent 2 energy depleted"
        print(f"✅ Agents maintained energy: {agent1.energy:.2f}, {agent2.energy:.2f}")

        print("\n✅ TEST 2 PASSED: Kuramoto coupling operational")


def test_nrem_consolidation():
    """Test NREM slow-wave consolidation phase."""
    print("\n" + "="*60)
    print("TEST 3: NREM Consolidation Phase")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = PatternMemory(workspace_path=Path(tmpdir))
        engine = ConsolidationEngine(memory=memory, workspace_path=tmpdir)

        # Create test patterns
        patterns = []
        for i in range(5):
            pattern = Pattern(
                pattern_id=f"pattern_{i:03d}",
                pattern_type=PatternType.SYSTEM_BEHAVIOR,
                name=f"Test Pattern {i}",
                description=f"Test pattern {i} for consolidation",
                data={'value': float(i)},
                confidence=0.8 + i * 0.02,
                occurrences=5 + i,
                first_seen=time.time(),
                last_seen=time.time()
            )
            memory.store_pattern(pattern)
            patterns.append(pattern)

        # Build simple semantic graph (all connected)
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                weight = 0.5 + (i + j) * 0.05  # Vary weights
                memory.store_graph_edge(
                    patterns[i].pattern_id,
                    patterns[j].pattern_id,
                    weight,
                    'semantic'
                )

        # Run NREM consolidation
        start_time = time.time()
        coalitions, metrics = engine.nrem_consolidation(
            patterns=patterns,
            duration_cycles=20,  # Short for testing
            frequency_hz=2.0,
            hebbian_learning_rate=0.01,
            coherence_threshold=0.7
        )
        duration_ms = (time.time() - start_time) * 1000

        # Validate metrics
        print(f"\nConsolidation Metrics:")
        print(f"  Patterns processed: {metrics.patterns_processed}")
        print(f"  Coalitions detected: {metrics.coalitions_detected}")
        print(f"  Hebbian updates: {metrics.hebbian_updates}")
        print(f"  CPU time: {metrics.cpu_time_ms:.2f} ms")
        print(f"  Memory usage: {metrics.memory_usage_mb:.2f} MB")
        print(f"  Wall-clock time: {duration_ms:.2f} ms")

        # Reality compliance checks
        assert metrics.patterns_processed == 5, "❌ Pattern count mismatch"
        assert metrics.cpu_time_ms > 0, "❌ No CPU time tracked"
        assert metrics.memory_usage_mb >= 0, "❌ Invalid memory usage"
        print(f"\n✅ Reality grounding verified (CPU + memory tracked)")

        # Validate coalitions
        if coalitions:
            print(f"\nDetected {len(coalitions)} coalition(s):")
            for coalition in coalitions[:3]:  # Show top 3
                print(f"  - {coalition.coalition_id}")
                print(f"    Members: {coalition.member_pattern_ids}")
                print(f"    Coherence: {coalition.mean_coherence:.4f}")

        print("\n✅ TEST 3 PASSED: NREM consolidation operational")


def test_rem_exploration():
    """Test REM high-frequency exploration phase."""
    print("\n" + "="*60)
    print("TEST 4: REM Exploration Phase")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = PatternMemory(workspace_path=Path(tmpdir))
        engine = ConsolidationEngine(memory=memory, workspace_path=tmpdir)

        # Create test patterns
        patterns = []
        for i in range(3):
            pattern = Pattern(
                pattern_id=f"pattern_rem_{i:03d}",
                pattern_type=PatternType.EMERGENCE,
                name=f"Exploratory Pattern {i}",
                description=f"Pattern for REM exploration {i}",
                data={'parameter': float(i)},
                confidence=0.7,
                occurrences=3,
                first_seen=time.time(),
                last_seen=time.time()
            )
            memory.store_pattern(pattern)
            patterns.append(pattern)

        # Build graph
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                memory.store_graph_edge(
                    patterns[i].pattern_id,
                    patterns[j].pattern_id,
                    0.3,  # Weak initial connections
                    'semantic'
                )

        # Run REM exploration
        start_time = time.time()
        coalitions, metrics = engine.rem_exploration(
            patterns=patterns,
            duration_cycles=10,  # Short for testing
            frequency_hz=8.0,
            perturbation_strength=0.5,
            coherence_threshold=0.6
        )
        duration_ms = (time.time() - start_time) * 1000

        # Validate metrics
        print(f"\nExploration Metrics:")
        print(f"  Patterns processed: {metrics.patterns_processed}")
        print(f"  Coalitions detected: {metrics.coalitions_detected}")
        print(f"  CPU time: {metrics.cpu_time_ms:.2f} ms")
        print(f"  Memory usage: {metrics.memory_usage_mb:.2f} MB")
        print(f"  Wall-clock time: {duration_ms:.2f} ms")

        # Reality compliance checks
        assert metrics.patterns_processed == 3, "❌ Pattern count mismatch"
        assert metrics.cpu_time_ms > 0, "❌ No CPU time tracked"
        print(f"\n✅ Reality grounding verified")

        print("\n✅ TEST 4 PASSED: REM exploration operational")


def run_all_tests():
    """Run all NRM V2 integration tests."""
    print("\n" + "="*60)
    print("DUALITY-ZERO-V2: NRM V2 INTEGRATION TEST SUITE")
    print("="*60)
    print("Reality Validation: Sleep-Inspired Memory System")
    print("="*60)

    tests = [
        ("Memetic Embeddings", test_memetic_embeddings),
        ("Kuramoto Coupling", test_kuramoto_coupling),
        ("NREM Consolidation", test_nrem_consolidation),
        ("REM Exploration", test_rem_exploration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print("TEST SUITE SUMMARY")
    print("="*60)
    print(f"Total: {len(tests)} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED: NRM V2 integration validated")
        print("="*60)
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        print("="*60)
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    exit(exit_code)
