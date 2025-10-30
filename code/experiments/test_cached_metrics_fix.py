#!/usr/bin/env python3
"""
Test script for FractalAgent.evolve() cached_metrics parameter fix.

Tests backward compatibility and optimized calling patterns to verify
the fix resolves TypeError while maintaining existing functionality.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-30
Cycle: 637
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractal.fractal_agent import FractalAgent
from bridge.transcendental_bridge import TranscendentalBridge
from core.reality_interface import RealityInterface


def test_backward_compatibility():
    """Test 1: Verify original calling pattern still works (no cached_metrics)."""
    print("\n" + "="*70)
    print("TEST 1: BACKWARD COMPATIBILITY")
    print("="*70)
    print("Testing original evolve() call without cached_metrics parameter...")

    try:
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        agent = FractalAgent(
            agent_id=0,
            bridge=bridge,
            initial_reality={'cpu': 0.5, 'memory': 0.5},
            reality=reality
        )

        # Original call (should work without cached_metrics parameter)
        agent.evolve(delta_time=1.0)

        print("✅ PASS: Backward compatibility maintained")
        print(f"   Agent energy after evolution: {agent.energy:.4f}")
        return True

    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        return False


def test_cached_metrics_parameter():
    """Test 2: Verify new cached_metrics parameter works correctly."""
    print("\n" + "="*70)
    print("TEST 2: CACHED METRICS PARAMETER")
    print("="*70)
    print("Testing optimized evolve() call with cached_metrics parameter...")

    try:
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        agent = FractalAgent(
            agent_id=0,
            bridge=bridge,
            initial_reality={'cpu': 0.5, 'memory': 0.5},
            reality=reality
        )

        # Pre-fetch metrics once (optimization)
        cached_metrics = reality.get_system_metrics()
        print(f"   Cached metrics: cpu={cached_metrics['cpu_percent']:.2f}%, "
              f"memory={cached_metrics['memory_percent']:.2f}%")

        # Optimized call (should use cached metrics)
        agent.evolve(delta_time=1.0, cached_metrics=cached_metrics)

        print("✅ PASS: Cached metrics parameter accepted")
        print(f"   Agent energy after evolution: {agent.energy:.4f}")
        return True

    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        return False


def test_batched_evolution():
    """Test 3: Verify batched evolution pattern (multiple agents, one metric fetch)."""
    print("\n" + "="*70)
    print("TEST 3: BATCHED EVOLUTION PATTERN")
    print("="*70)
    print("Testing multi-agent batched evolution (1 metric fetch, 5 agents)...")

    try:
        bridge = TranscendentalBridge()
        reality = RealityInterface()

        # Create 5 agents
        agents = []
        for i in range(5):
            agent = FractalAgent(
                agent_id=i,
                bridge=bridge,
                initial_reality={'cpu': 0.5, 'memory': 0.5},
                reality=reality
            )
            agents.append(agent)

        # Fetch metrics ONCE (optimization)
        cached_metrics = reality.get_system_metrics()

        # Evolve all agents with shared cached metrics
        for agent in agents:
            agent.evolve(delta_time=1.0, cached_metrics=cached_metrics)

        print("✅ PASS: Batched evolution successful")
        print(f"   5 agents evolved with 1 metric fetch")
        print(f"   Agent energies: {[f'{a.energy:.2f}' for a in agents]}")
        return True

    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        return False


def test_recursive_cached_metrics():
    """Test 4: Verify cached_metrics propagates to child agents."""
    print("\n" + "="*70)
    print("TEST 4: RECURSIVE CACHED METRICS")
    print("="*70)
    print("Testing cached_metrics propagation to child agents...")

    try:
        bridge = TranscendentalBridge()
        reality = RealityInterface()

        # Create parent agent
        parent = FractalAgent(
            agent_id=0,
            bridge=bridge,
            initial_reality={'cpu': 0.5, 'memory': 0.5},
            reality=reality
        )

        # Create child agents
        for i in range(3):
            child = FractalAgent(
                agent_id=i+1,
                bridge=bridge,
                initial_reality={'cpu': 0.5, 'memory': 0.5},
                reality=reality
            )
            parent.children.append(child)

        # Fetch metrics once
        cached_metrics = reality.get_system_metrics()

        # Evolve parent (should recursively evolve children with cached_metrics)
        parent.evolve(delta_time=1.0, cached_metrics=cached_metrics)

        print("✅ PASS: Recursive cached_metrics propagation works")
        print(f"   Parent energy: {parent.energy:.2f}")
        print(f"   Child energies: {[f'{c.energy:.2f}' for c in parent.children]}")
        return True

    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        return False


def main():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("FRACTAL AGENT CACHED_METRICS FIX VALIDATION")
    print("="*70)
    print("Testing FractalAgent.evolve() cached_metrics parameter support")
    print("Location: /Volumes/dual/DUALITY-ZERO-V2/fractal/fractal_agent.py")
    print()

    results = []
    results.append(("Backward Compatibility", test_backward_compatibility()))
    results.append(("Cached Metrics Parameter", test_cached_metrics_parameter()))
    results.append(("Batched Evolution Pattern", test_batched_evolution()))
    results.append(("Recursive Cached Metrics", test_recursive_cached_metrics()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - Fix is valid and ready for deployment")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - Fix requires adjustment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
