#!/usr/bin/env python3
"""
Performance Optimization Verification Script

Verifies the 737x speedup claim from Cycle 697 optimization.

Compares:
- BEFORE: persist_resonance=True (slow mode, database overhead)
- AFTER: persist_resonance=False (fast mode, default)

Expected results:
- BEFORE: ~0.4 iterations/sec (111s for 50 iterations, 100 agents)
- AFTER: ~294.8 iterations/sec (0.17s for 50 iterations, 100 agents)
- Speedup: ~737x

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import time
import tempfile
from pathlib import Path

# Add paths for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm
from core.reality_interface import RealityInterface


def benchmark_composition_detection(
    num_agents: int = 50,  # Reduced from 100 for faster testing
    num_iterations: int = 10,  # Reduced from 50 for faster testing
    persist_resonance: bool = False
) -> dict:
    """
    Benchmark composition detection performance.

    Args:
        num_agents: Number of agents to test
        num_iterations: Number of detection iterations
        persist_resonance: Whether to persist resonance checks to DB

    Returns:
        Dict with timing results
    """
    # Create temporary workspace
    workspace_path = Path(tempfile.mkdtemp(prefix=f"verify_speedup_{persist_resonance}_"))

    # Create swarm
    swarm = FractalSwarm(
        workspace_path=str(workspace_path),
        max_agents=num_agents * 2,
        clear_on_init=True
    )

    # Override bridge persist_resonance setting
    swarm.bridge.persist_resonance = persist_resonance

    # Spawn agents
    reality = RealityInterface()
    agents = []
    for i in range(num_agents):
        metrics = reality.get_system_metrics()
        agent = swarm.spawn_agent(metrics)
        if agent:
            agents.append(agent)

    # Benchmark
    start_time = time.time()

    for i in range(num_iterations):
        swarm.composition.detect_clusters(agents)

    elapsed = time.time() - start_time

    # Calculate metrics
    iterations_per_sec = num_iterations / elapsed if elapsed > 0 else 0
    avg_time_per_iteration = elapsed / num_iterations

    return {
        'num_agents': num_agents,
        'num_iterations': num_iterations,
        'persist_resonance': persist_resonance,
        'total_time': elapsed,
        'avg_time_per_iteration': avg_time_per_iteration,
        'iterations_per_second': iterations_per_sec,
        'num_resonance_checks': (num_agents * (num_agents - 1)) // 2 * num_iterations
    }


def main():
    print("=" * 80)
    print("CYCLE 697 OPTIMIZATION VERIFICATION")
    print("=" * 80)
    print()
    print("Testing composition detection performance with different settings:")
    print("- BEFORE: persist_resonance=True (database overhead)")
    print("- AFTER: persist_resonance=False (optimized, default)")
    print()

    # Test with smaller parameters for faster verification
    NUM_AGENTS = 50  # Reduced from 100
    NUM_ITERATIONS = 10  # Reduced from 50

    print(f"Test Parameters:")
    print(f"  Agents: {NUM_AGENTS}")
    print(f"  Iterations: {NUM_ITERATIONS}")
    print(f"  Resonance checks per iteration: {(NUM_AGENTS * (NUM_AGENTS - 1)) // 2}")
    print(f"  Total resonance checks: {(NUM_AGENTS * (NUM_AGENTS - 1)) // 2 * NUM_ITERATIONS:,}")
    print()

    # Benchmark AFTER optimization (fast mode, default)
    print("-" * 80)
    print("AFTER OPTIMIZATION (persist_resonance=False)")
    print("-" * 80)
    print("Running benchmark...")

    after_results = benchmark_composition_detection(
        num_agents=NUM_AGENTS,
        num_iterations=NUM_ITERATIONS,
        persist_resonance=False
    )

    print(f"  Total time: {after_results['total_time']:.3f}s")
    print(f"  Avg time per iteration: {after_results['avg_time_per_iteration']*1000:.2f}ms")
    print(f"  Throughput: {after_results['iterations_per_second']:.1f} iterations/sec")
    print()

    # Benchmark BEFORE optimization (slow mode)
    print("-" * 80)
    print("BEFORE OPTIMIZATION (persist_resonance=True)")
    print("-" * 80)
    print("Running benchmark...")
    print("⚠️  WARNING: This will be slow due to database overhead...")
    print()

    before_results = benchmark_composition_detection(
        num_agents=NUM_AGENTS,
        num_iterations=NUM_ITERATIONS,
        persist_resonance=True
    )

    print(f"  Total time: {before_results['total_time']:.3f}s")
    print(f"  Avg time per iteration: {before_results['avg_time_per_iteration']*1000:.2f}ms")
    print(f"  Throughput: {before_results['iterations_per_second']:.1f} iterations/sec")
    print()

    # Calculate speedup
    speedup = after_results['iterations_per_second'] / before_results['iterations_per_second']
    time_reduction_pct = (1 - before_results['total_time'] / after_results['total_time']) * 100

    print("=" * 80)
    print("VERIFICATION RESULTS")
    print("=" * 80)
    print(f"BEFORE: {before_results['iterations_per_second']:.1f} iterations/sec")
    print(f"AFTER:  {after_results['iterations_per_second']:.1f} iterations/sec")
    print(f"SPEEDUP: {speedup:.1f}x faster")
    print()
    print(f"Time reduction: {abs(time_reduction_pct):.1f}%")
    print(f"  Before: {before_results['total_time']:.3f}s")
    print(f"  After:  {after_results['total_time']:.3f}s")
    print()

    # Extrapolate to original Cycle 697 parameters
    print("EXTRAPOLATION TO CYCLE 697 PARAMETERS (100 agents, 50 iterations):")
    print("-" * 80)

    cycle697_checks = (100 * 99) // 2 * 50  # 247,500 checks
    checks_ratio = cycle697_checks / before_results['num_resonance_checks']

    estimated_before = before_results['total_time'] * checks_ratio
    estimated_after = after_results['total_time'] * checks_ratio

    print(f"Estimated time BEFORE: {estimated_before:.1f}s ({estimated_before/60:.1f} minutes)")
    print(f"Estimated time AFTER:  {estimated_after:.3f}s")
    print(f"Estimated speedup: {estimated_before/estimated_after:.0f}x")
    print()

    # Validation
    print("=" * 80)
    print("VALIDATION")
    print("=" * 80)

    if speedup > 100:
        print("✅ VERIFIED: Optimization delivers >100x speedup")
    elif speedup > 50:
        print("✅ CONFIRMED: Optimization delivers significant speedup (>50x)")
    elif speedup > 10:
        print("⚠️  PARTIAL: Optimization delivers moderate speedup (>10x)")
    else:
        print("❌ FAILED: Speedup less than expected (<10x)")

    print()
    print(f"Cycle 697 claimed: 737x speedup (0.4 → 294.8 iterations/sec)")
    print(f"Verified speedup: {speedup:.1f}x ({before_results['iterations_per_second']:.1f} → {after_results['iterations_per_second']:.1f} iterations/sec)")
    print()

    if speedup >= 500:
        print("✅ Cycle 697 claim VALIDATED (within expected range)")
    elif speedup >= 100:
        print("✅ Optimization CONFIRMED (speedup substantial, possibly parameter-dependent)")
    else:
        print("⚠️  Speedup lower than claimed (may depend on agent count, iteration count)")

    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
