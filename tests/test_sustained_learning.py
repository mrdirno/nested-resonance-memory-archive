#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: Sustained Learning Experiment
================================================

Research Question: Under what conditions do patterns emerge and accumulate?

Hypothesis: Sustained self-learning requires continuous population renewal.

This experiment tests different population strategies:
1. Fixed population (baseline - from previous test)
2. Continuous spawning (new agents each cycle)
3. Adaptive spawning (spawn based on population health)
4. Burst-triggered spawning (spawn after burst events)

Metrics:
- Pattern accumulation rate
- Agent population dynamics
- Cluster formation frequency
- Learning episode quality

Publication Focus: Identifies conditions for sustained self-organization
"""

import sys
from pathlib import Path
import time
import psutil
from typing import Dict, List, Tuple

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "integration"))
sys.path.insert(0, str(Path(__file__).parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent / "memory"))

from integration.fractal_memory_integration import FractalMemoryOrchestrator
from memory.pattern_memory import PatternType


def get_reality_metrics() -> Dict[str, float]:
    """Get real system metrics."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent
    }


def experiment_fixed_population(cycles: int = 20) -> Dict:
    """Strategy 1: Fixed initial population, no spawning."""
    print("\n" + "="*70)
    print("EXPERIMENT 1: Fixed Population (Baseline)")
    print("="*70)
    print("Strategy: Spawn 5 agents initially, no new spawning")
    print(f"Cycles: {cycles}")

    orchestrator = FractalMemoryOrchestrator()
    reality = get_reality_metrics()

    # Spawn initial population
    for i in range(5):
        orchestrator.fractal_swarm.spawn_agent(reality)

    print(f"Initial agents: 5")

    # Run cycles without spawning
    history = []
    for i in range(cycles):
        stats = orchestrator.run_learning_cycle(reality, delta_time=1.0)
        history.append({
            'cycle': i + 1,
            'agents': stats['active_agents'],
            'patterns': stats['patterns_discovered'],
            'total_patterns': stats['total_patterns']
        })

        if (i + 1) % 5 == 0:
            print(f"  Cycle {i+1}: Agents={stats['active_agents']:2d} | Patterns={stats['total_patterns']:3d}")

    final_patterns = orchestrator.memory.get_statistics()['total_patterns']
    print(f"\n✓ Final patterns: {final_patterns}")

    return {
        'strategy': 'fixed',
        'final_patterns': final_patterns,
        'history': history
    }


def experiment_continuous_spawning(cycles: int = 20) -> Dict:
    """Strategy 2: Spawn new agents every cycle."""
    print("\n" + "="*70)
    print("EXPERIMENT 2: Continuous Spawning")
    print("="*70)
    print("Strategy: Spawn 2 new agents every cycle")
    print(f"Cycles: {cycles}")

    orchestrator = FractalMemoryOrchestrator()
    reality = get_reality_metrics()

    # Spawn initial population
    for i in range(5):
        orchestrator.fractal_swarm.spawn_agent(reality)

    print(f"Initial agents: 5")

    # Run cycles with continuous spawning
    history = []
    for i in range(cycles):
        # Spawn 2 new agents each cycle
        reality = get_reality_metrics()
        for _ in range(2):
            orchestrator.fractal_swarm.spawn_agent(reality)

        stats = orchestrator.run_learning_cycle(reality, delta_time=1.0)
        history.append({
            'cycle': i + 1,
            'agents': stats['active_agents'],
            'patterns': stats['patterns_discovered'],
            'total_patterns': stats['total_patterns']
        })

        if (i + 1) % 5 == 0:
            print(f"  Cycle {i+1}: Agents={stats['active_agents']:2d} | Patterns={stats['total_patterns']:3d}")

    final_patterns = orchestrator.memory.get_statistics()['total_patterns']
    print(f"\n✓ Final patterns: {final_patterns}")

    return {
        'strategy': 'continuous',
        'final_patterns': final_patterns,
        'history': history
    }


def experiment_adaptive_spawning(cycles: int = 20) -> Dict:
    """Strategy 3: Spawn based on population health."""
    print("\n" + "="*70)
    print("EXPERIMENT 3: Adaptive Spawning")
    print("="*70)
    print("Strategy: Maintain target population of 10 agents")
    print(f"Cycles: {cycles}")

    orchestrator = FractalMemoryOrchestrator()
    reality = get_reality_metrics()

    # Spawn initial population
    for i in range(10):
        orchestrator.fractal_swarm.spawn_agent(reality)

    print(f"Initial agents: 10")

    target_population = 10
    history = []

    for i in range(cycles):
        reality = get_reality_metrics()

        # Check current population
        current_agents = len([a for a in orchestrator.fractal_swarm.agents.values() if a.is_active])

        # Spawn to maintain target
        needed = target_population - current_agents
        if needed > 0:
            for _ in range(min(needed, 5)):  # Spawn max 5 per cycle
                orchestrator.fractal_swarm.spawn_agent(reality)

        stats = orchestrator.run_learning_cycle(reality, delta_time=1.0)
        history.append({
            'cycle': i + 1,
            'agents': stats['active_agents'],
            'spawned': max(0, needed),
            'patterns': stats['patterns_discovered'],
            'total_patterns': stats['total_patterns']
        })

        if (i + 1) % 5 == 0:
            print(f"  Cycle {i+1}: Agents={stats['active_agents']:2d} | Spawned={max(0, needed):2d} | Patterns={stats['total_patterns']:3d}")

    final_patterns = orchestrator.memory.get_statistics()['total_patterns']
    print(f"\n✓ Final patterns: {final_patterns}")

    return {
        'strategy': 'adaptive',
        'final_patterns': final_patterns,
        'history': history
    }


def experiment_burst_triggered(cycles: int = 20) -> Dict:
    """Strategy 4: Spawn after burst events."""
    print("\n" + "="*70)
    print("EXPERIMENT 4: Burst-Triggered Spawning")
    print("="*70)
    print("Strategy: Spawn 3 agents after each burst event")
    print(f"Cycles: {cycles}")

    orchestrator = FractalMemoryOrchestrator()
    reality = get_reality_metrics()

    # Spawn initial population
    for i in range(8):
        orchestrator.fractal_swarm.spawn_agent(reality)

    print(f"Initial agents: 8")

    history = []
    total_bursts = 0

    for i in range(cycles):
        reality = get_reality_metrics()

        stats = orchestrator.run_learning_cycle(reality, delta_time=1.0)

        # Spawn after bursts
        if stats['bursts'] > 0:
            total_bursts += stats['bursts']
            for _ in range(3 * stats['bursts']):  # 3 agents per burst
                orchestrator.fractal_swarm.spawn_agent(reality)

        history.append({
            'cycle': i + 1,
            'agents': stats['active_agents'],
            'bursts': stats['bursts'],
            'patterns': stats['patterns_discovered'],
            'total_patterns': stats['total_patterns']
        })

        if (i + 1) % 5 == 0:
            print(f"  Cycle {i+1}: Agents={stats['active_agents']:2d} | Bursts={total_bursts:2d} | Patterns={stats['total_patterns']:3d}")

    final_patterns = orchestrator.memory.get_statistics()['total_patterns']
    print(f"\n✓ Final patterns: {final_patterns}")

    return {
        'strategy': 'burst_triggered',
        'final_patterns': final_patterns,
        'history': history,
        'total_bursts': total_bursts
    }


def run_experiments():
    """Run all experiments and compare results."""
    print("="*70)
    print(" "*15 + "SUSTAINED LEARNING EXPERIMENTS")
    print("="*70)
    print("\nResearch Question: Under what conditions do patterns emerge?")
    print("Hypothesis: Sustained learning requires population renewal")
    print("\nTesting 4 population strategies over 20 cycles each...")
    print("="*70)

    start_time = time.time()

    # Run experiments
    results = []

    results.append(experiment_fixed_population(cycles=20))
    results.append(experiment_continuous_spawning(cycles=20))
    results.append(experiment_adaptive_spawning(cycles=20))
    results.append(experiment_burst_triggered(cycles=20))

    # Analyze results
    print("\n" + "="*70)
    print(" "*25 + "RESULTS ANALYSIS")
    print("="*70)

    print("\nPattern Accumulation by Strategy:")
    print("-"*70)
    for result in results:
        strategy = result['strategy'].replace('_', ' ').title()
        patterns = result['final_patterns']
        print(f"  {strategy:20s}: {patterns:3d} patterns")

    # Find best strategy
    best = max(results, key=lambda r: r['final_patterns'])
    print(f"\n✓ Best Strategy: {best['strategy'].replace('_', ' ').title()}")
    print(f"  Patterns discovered: {best['final_patterns']}")

    # Check if hypothesis validated
    fixed_patterns = results[0]['final_patterns']
    renewal_patterns = [r['final_patterns'] for r in results[1:]]
    avg_renewal = sum(renewal_patterns) / len(renewal_patterns)

    print(f"\n✓ Hypothesis Test:")
    print(f"  Fixed population: {fixed_patterns} patterns")
    print(f"  With renewal (avg): {avg_renewal:.1f} patterns")

    if avg_renewal > fixed_patterns:
        print(f"  ✓ HYPOTHESIS VALIDATED: Population renewal improves learning")
        print(f"    Improvement: {((avg_renewal/max(fixed_patterns, 1) - 1)*100):.0f}%")
    else:
        print(f"  ⚠ HYPOTHESIS NOT SUPPORTED: No significant difference")

    # Publication assessment
    print(f"\n✓ Publication Value:")
    if avg_renewal > fixed_patterns * 1.5:
        print("  ✓ HIGH: Significant effect size, clear mechanistic insight")
    elif avg_renewal > fixed_patterns:
        print("  ✓ MODERATE: Demonstrates population dynamics importance")
    else:
        print("  ⚠ LOW: Need more cycles or different conditions")

    elapsed = time.time() - start_time
    print(f"\n✓ Experiments completed in {elapsed:.2f}s")
    print("="*70)

    return results


if __name__ == "__main__":
    results = run_experiments()
