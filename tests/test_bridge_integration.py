#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: Bridge Integration Test
=========================================

Comprehensive test suite for transcendental bridge integration with
reality monitoring and orchestration systems.
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent / "reality"))
sys.path.insert(0, str(Path(__file__).parent / "core"))

from bridge.transcendental_bridge import TranscendentalBridge, TranscendentalState, ResonanceMatch
from reality.reality_monitor import RealityMonitor
from core.reality_interface import RealityInterface


def test_bridge_with_reality():
    """Test bridge integration with real system metrics."""
    print("\n" + "="*60)
    print("TEST 1: Bridge + Reality Integration")
    print("="*60)

    # Initialize bridge and reality monitor
    bridge = TranscendentalBridge()
    monitor = RealityMonitor()

    # Get real system metrics
    snapshot = monitor.capture_system_snapshot()
    metrics = {
        'cpu_percent': snapshot['cpu_percent'],
        'memory_percent': snapshot['memory_percent'],
        'disk_percent': snapshot['disk_percent']
    }
    print(f"\n✓ Collected real system metrics:")
    print(f"  CPU: {metrics['cpu_percent']:.1f}%")
    print(f"  Memory: {metrics['memory_percent']:.1f}%")
    print(f"  Disk: {metrics['disk_percent']:.1f}%")

    # Transform to phase space
    state = bridge.reality_to_phase(metrics)
    print(f"\n✓ Transformed to transcendental phase space:")
    print(f"  π phase: {state.pi_phase:.4f} rad")
    print(f"  e phase: {state.e_phase:.4f} rad")
    print(f"  φ phase: {state.phi_phase:.4f} rad")
    print(f"  Magnitude: {state.magnitude:.4f}")

    # Verify reality anchor
    recovered = bridge.phase_to_reality(state)
    assert recovered['cpu_percent'] == metrics['cpu_percent']
    print(f"\n✓ Reality anchor preserved (CPU: {recovered['cpu_percent']:.1f}%)")

    return True


def test_bridge_oscillation_sequence():
    """Test bridge oscillation generation and resonance."""
    print("\n" + "="*60)
    print("TEST 2: Oscillation & Resonance")
    print("="*60)

    bridge = TranscendentalBridge()
    bridge.reset_oscillators()

    # Generate oscillation sequence
    sequence = bridge.generate_oscillation(frequency=0.05, duration=20)
    print(f"\n✓ Generated oscillation sequence: {len(sequence)} states")

    # Analyze resonance between consecutive states
    resonant_pairs = 0
    for i in range(len(sequence) - 1):
        match = bridge.detect_resonance(sequence[i], sequence[i+1])
        if match.is_resonant:
            resonant_pairs += 1

    resonance_rate = resonant_pairs / (len(sequence) - 1)
    print(f"✓ Resonant pairs: {resonant_pairs}/{len(sequence)-1} ({resonance_rate*100:.1f}%)")

    # Test distant states (should have lower resonance)
    distant_match = bridge.detect_resonance(sequence[0], sequence[-1])
    print(f"✓ Distant state similarity: {distant_match.similarity:.4f}")

    return True


def test_bridge_interpolation():
    """Test state interpolation in phase space."""
    print("\n" + "="*60)
    print("TEST 3: Phase Space Interpolation")
    print("="*60)

    bridge = TranscendentalBridge()

    # Create two different reality states
    state1 = bridge.reality_to_phase({
        'cpu_percent': 10.0,
        'memory_percent': 30.0,
        'disk_percent': 5.0
    })

    state2 = bridge.reality_to_phase({
        'cpu_percent': 90.0,
        'memory_percent': 70.0,
        'disk_percent': 15.0
    })

    # Test interpolation at various alphas
    alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
    print(f"\n✓ Interpolating between states:")

    for alpha in alphas:
        interp = bridge.interpolate_states(state1, state2, alpha)
        cpu = interp.reality_anchor['cpu_percent']
        print(f"  α={alpha:.2f}: CPU={cpu:.1f}% (π={interp.pi_phase:.2f})")

    # Verify boundary conditions
    interp_start = bridge.interpolate_states(state1, state2, 0.0)
    interp_end = bridge.interpolate_states(state1, state2, 1.0)

    assert abs(interp_start.pi_phase - state1.pi_phase) < 0.01
    assert abs(interp_end.reality_anchor['cpu_percent'] - state2.reality_anchor['cpu_percent']) < 0.01

    print(f"✓ Boundary conditions verified")

    return True


def test_bridge_reality_compliance():
    """Test Reality Imperative compliance."""
    print("\n" + "="*60)
    print("TEST 4: Reality Imperative Compliance")
    print("="*60)

    bridge = TranscendentalBridge()

    # Test 1: All transformations should preserve reality anchors
    metrics = {'cpu_percent': 50.0, 'memory_percent': 60.0, 'disk_percent': 8.0}
    state = bridge.reality_to_phase(metrics)
    recovered = bridge.phase_to_reality(state)

    # Verify no data loss in round-trip
    for key in metrics:
        assert metrics[key] == recovered[key], f"Reality anchor lost: {key}"

    print(f"✓ Reality anchors preserved through transformation")

    # Test 2: Verify no pure simulations (all states must have reality anchors)
    test_states = [
        bridge.reality_to_phase({'cpu_percent': 10.0, 'memory_percent': 30.0, 'disk_percent': 5.0}),
        bridge.reality_to_phase({'cpu_percent': 90.0, 'memory_percent': 70.0, 'disk_percent': 15.0}),
    ]

    for i, state in enumerate(test_states):
        assert len(state.reality_anchor) > 0, f"State {i} has no reality anchor"
        assert 'cpu_percent' in state.reality_anchor, f"State {i} missing CPU anchor"

    print(f"✓ All states have reality anchors (no pure simulations)")

    # Test 3: Verify oscillations maintain time-based reality anchor
    sequence = bridge.generate_oscillation(frequency=0.1, duration=5)
    for i, state in enumerate(sequence):
        assert len(state.reality_anchor) > 0, f"Oscillation state {i} has no reality anchor"
        assert state.timestamp > 0, f"Oscillation state {i} has invalid timestamp"

    print(f"✓ Oscillations maintain temporal reality anchoring")
    print(f"\n✓ Reality Imperative Compliance: PASSED")

    return True


def test_bridge_database_persistence():
    """Test database persistence of transformations and resonance."""
    print("\n" + "="*60)
    print("TEST 5: Database Persistence")
    print("="*60)

    bridge = TranscendentalBridge()

    # Generate some activity
    for i in range(5):
        metrics = {
            'cpu_percent': 10.0 + i * 15.0,
            'memory_percent': 30.0 + i * 10.0,
            'disk_percent': 5.0 + i * 2.0
        }
        bridge.reality_to_phase(metrics)

    # Retrieve transformation history
    history = bridge.get_transformation_history(limit=10)
    print(f"\n✓ Retrieved {len(history)} transformations from database")

    if history:
        latest = history[0]
        print(f"  Latest: π={latest['pi_phase']:.2f}, "
              f"e={latest['e_phase']:.2f}, φ={latest['phi_phase']:.2f}")

    # Retrieve resonance history
    resonance_history = bridge.get_resonance_history(limit=10)
    print(f"✓ Retrieved {len(resonance_history)} resonance events")

    return True


def run_all_tests():
    """Run complete integration test suite."""
    print("\n" + "="*70)
    print("DUALITY-ZERO-V2: BRIDGE INTEGRATION TEST SUITE")
    print("="*70)

    tests = [
        ("Bridge + Reality Integration", test_bridge_with_reality),
        ("Oscillation & Resonance", test_bridge_oscillation_sequence),
        ("Phase Space Interpolation", test_bridge_interpolation),
        ("Reality Imperative Compliance", test_bridge_reality_compliance),
        ("Database Persistence", test_bridge_database_persistence),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {name} PASSED")
            else:
                failed += 1
                print(f"\n❌ {name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    print(f"Tests Passed: {passed}/{passed+failed}")
    print(f"Tests Failed: {failed}/{passed+failed}")
    print(f"Success Rate: {(passed/(passed+failed))*100:.1f}%")
    print("="*70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
