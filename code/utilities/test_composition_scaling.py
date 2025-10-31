#!/usr/bin/env python3
"""
Composition Detection Scaling Test

Tests practical limits of optimized FractalSwarm composition detection.
Explores agent count boundaries to inform experimental design for Papers 3, 4, 8.

Questions:
- What is the maximum practical agent count for real-time composition?
- How does performance degrade as agent count increases?
- What are the resource limits (memory, CPU)?

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import time
import tempfile
import psutil
from pathlib import Path

# Add paths for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm
from core.reality_interface import RealityInterface


def test_composition_scaling(
    agent_counts: list = [10, 25, 50, 100, 150, 200, 300],
    iterations: int = 5
) -> list:
    """
    Test composition detection performance across different agent counts.

    Args:
        agent_counts: List of agent counts to test
        iterations: Number of detection iterations per test

    Returns:
        List of result dicts
    """
    results = []

    print("=" * 80)
    print("COMPOSITION DETECTION SCALING TEST")
    print("=" * 80)
    print()
    print(f"Testing agent counts: {agent_counts}")
    print(f"Iterations per test: {iterations}")
    print()

    for num_agents in agent_counts:
        print("-" * 80)
        print(f"Testing {num_agents} agents...")
        print("-" * 80)

        # Create temporary workspace
        workspace_path = Path(tempfile.mkdtemp(prefix=f"scaling_test_{num_agents}_"))

        # Get initial system metrics
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        cpu_before = process.cpu_percent(interval=0.1)

        try:
            # Create swarm
            swarm = FractalSwarm(
                workspace_path=str(workspace_path),
                max_agents=num_agents * 2,
                clear_on_init=True
            )

            # Spawn agents
            reality = RealityInterface()
            agents = []
            spawn_start = time.time()

            for i in range(num_agents):
                metrics = reality.get_system_metrics()
                agent = swarm.spawn_agent(metrics)
                if agent:
                    agents.append(agent)

            spawn_elapsed = time.time() - spawn_start

            # Get post-spawn metrics
            mem_after_spawn = process.memory_info().rss / 1024 / 1024  # MB
            mem_per_agent = (mem_after_spawn - mem_before) / num_agents if num_agents > 0 else 0

            print(f"  Agents spawned: {len(agents)}")
            print(f"  Spawn time: {spawn_elapsed:.3f}s ({spawn_elapsed/num_agents*1000:.2f}ms per agent)")
            print(f"  Memory usage: {mem_after_spawn:.1f}MB (+{mem_after_spawn-mem_before:.1f}MB, {mem_per_agent:.2f}MB/agent)")

            # Benchmark composition detection
            resonance_checks = (num_agents * (num_agents - 1)) // 2
            print(f"  Resonance checks per iteration: {resonance_checks:,}")
            print(f"  Total checks: {resonance_checks * iterations:,}")
            print()
            print(f"  Running {iterations} detection iterations...")

            detection_start = time.time()

            for i in range(iterations):
                swarm.composition.detect_clusters(agents)

            detection_elapsed = time.time() - detection_start

            # Calculate metrics
            iterations_per_sec = iterations / detection_elapsed if detection_elapsed > 0 else 0
            checks_per_sec = (resonance_checks * iterations) / detection_elapsed if detection_elapsed > 0 else 0
            avg_per_iteration = detection_elapsed / iterations

            # Get final metrics
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            cpu_after = process.cpu_percent(interval=0.1)

            print(f"  Detection time: {detection_elapsed:.3f}s")
            print(f"  Throughput: {iterations_per_sec:.1f} iterations/sec")
            print(f"  Checks throughput: {checks_per_sec:,.0f} checks/sec")
            print(f"  Avg per iteration: {avg_per_iteration*1000:.2f}ms")
            print(f"  Final memory: {mem_after:.1f}MB")
            print(f"  CPU usage: {cpu_after:.1f}%")
            print()

            # Store results
            results.append({
                'num_agents': num_agents,
                'agents_spawned': len(agents),
                'spawn_time': spawn_elapsed,
                'spawn_time_per_agent': spawn_elapsed / num_agents if num_agents > 0 else 0,
                'memory_mb': mem_after,
                'memory_per_agent_mb': mem_per_agent,
                'iterations': iterations,
                'resonance_checks_per_iteration': resonance_checks,
                'total_checks': resonance_checks * iterations,
                'detection_time': detection_elapsed,
                'iterations_per_sec': iterations_per_sec,
                'checks_per_sec': checks_per_sec,
                'avg_time_per_iteration': avg_per_iteration,
                'cpu_percent': cpu_after
            })

            # Check if we should stop (performance degradation threshold)
            if iterations_per_sec < 1.0:
                print(f"⚠️  Performance threshold reached (< 1 iteration/sec)")
                print(f"  Stopping scaling test at {num_agents} agents")
                break

        except Exception as e:
            print(f"❌ Error with {num_agents} agents: {str(e)}")
            results.append({
                'num_agents': num_agents,
                'error': str(e)
            })
            break

    return results


def print_scaling_summary(results: list):
    """Print summary of scaling test results."""
    print()
    print("=" * 80)
    print("SCALING TEST SUMMARY")
    print("=" * 80)
    print()

    # Table header
    print(f"{'Agents':<10} {'Checks':<12} {'Time':<10} {'Iter/sec':<12} {'Checks/sec':<15} {'Memory':<12}")
    print("-" * 80)

    for result in results:
        if 'error' in result:
            print(f"{result['num_agents']:<10} ERROR: {result['error']}")
            continue

        print(f"{result['num_agents']:<10} "
              f"{result['resonance_checks_per_iteration']:<12,} "
              f"{result['detection_time']:<10.3f} "
              f"{result['iterations_per_sec']:<12.1f} "
              f"{result['checks_per_sec']:<15,.0f} "
              f"{result['memory_mb']:<12.1f}")

    print()

    # Analysis
    print("ANALYSIS:")
    print("-" * 80)

    successful_results = [r for r in results if 'error' not in r]

    if successful_results:
        max_agents = successful_results[-1]['num_agents']
        max_throughput = max(r['checks_per_sec'] for r in successful_results)
        min_latency = min(r['avg_time_per_iteration'] for r in successful_results)

        print(f"Maximum tested agents: {max_agents}")
        print(f"Peak checks throughput: {max_throughput:,.0f} checks/sec")
        print(f"Minimum iteration latency: {min_latency*1000:.2f}ms")
        print()

        # Real-time threshold analysis (assume 1 sec = "real-time")
        realtime_threshold = 1.0  # 1 iteration per second
        realtime_agents = [r['num_agents'] for r in successful_results if r['iterations_per_sec'] >= realtime_threshold]

        if realtime_agents:
            max_realtime = max(realtime_agents)
            print(f"Real-time capable (≥ 1 iter/sec): Up to {max_realtime} agents")
        else:
            print("No configurations achieved real-time performance (≥ 1 iter/sec)")

        print()

        # Memory scaling
        if len(successful_results) >= 2:
            memory_per_agent_avg = sum(r['memory_per_agent_mb'] for r in successful_results) / len(successful_results)
            print(f"Average memory per agent: {memory_per_agent_avg:.2f}MB")
            print()

        # Recommendations for Papers
        print("RECOMMENDATIONS FOR RESEARCH PAPERS:")
        print("-" * 80)

        if max_realtime >= 200:
            print(f"✅ Large-scale experiments feasible (200+ agents real-time)")
            print(f"   Paper 3, 4, 8: Can use 100-200 agent populations")
        elif max_realtime >= 100:
            print(f"✅ Medium-scale experiments feasible (100+ agents real-time)")
            print(f"   Paper 3, 4, 8: Can use up to 100 agent populations")
        elif max_realtime >= 50:
            print(f"⚠️  Small-scale experiments recommended (50 agents max)")
            print(f"   Paper 3, 4, 8: Limit to 50 agents for real-time")
        else:
            print(f"❌ Performance insufficient for real-time experiments")
            print(f"   Consider batch processing instead of real-time")

    print()
    print("=" * 80)


def main():
    # Test scaling from 10 to 300 agents
    agent_counts = [10, 25, 50, 75, 100, 150, 200, 300]
    iterations = 5

    results = test_composition_scaling(agent_counts, iterations)
    print_scaling_summary(results)


if __name__ == '__main__':
    main()
