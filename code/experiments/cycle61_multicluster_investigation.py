#!/usr/bin/env python3
"""
Cycle 61: Multi-Cluster Regime Investigation

Hypothesis from Cycle 60:
  At extreme burst thresholds (>1000), the system transitions from single-cluster
  dynamics to multi-cluster dynamics, where multiple independent clusters can
  coexist simultaneously.

Evidence from threshold=1200:
  - Gap states (1, 2, 4, 9 missing)
  - State 6 dominant (53.3%)
  - Observed max = 10 (predicted 8, deviation = +2)

Test Approach:
  1. Run extended experiment at threshold=1200
  2. Track cluster formation events (not just agent counts)
  3. Analyze whether multiple clusters exist simultaneously
  4. Determine if gap states correlate with multi-cluster states

Expected:
  If multi-cluster hypothesis is correct:
    - Multiple clusters should coexist at high agent counts
    - Gap states occur when clusters burst independently
    - Dominant state (6) represents stable multi-cluster configuration
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from workspace_utils import get_workspace_path, get_results_path


def run_multicluster_analysis(burst_threshold: float, cycles: int = 500) -> dict:
    """
    Run experiment with detailed cluster tracking.

    Args:
        burst_threshold: Burst threshold to test
        cycles: Number of cycles

    Returns:
        dict with detailed cluster analysis
    """
    print(f"="*80)
    print(f"MULTI-CLUSTER REGIME INVESTIGATION")
    print(f"="*80)
    print(f"Burst Threshold: {burst_threshold}")
    print(f"Cycles: {cycles}")
    print()

    # Create swarm
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=burst_threshold)

    # Tracking
    agent_counts = []
    cluster_counts = []
    checkpoint_interval = 10

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Spawn
        if len(swarm.agents) < 15:  # Higher limit for multi-cluster
            swarm.spawn_agent(reality_metrics)

        # Evolve
        result = swarm.evolve_cycle(delta_time=1.0)

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            agent_count = len(swarm.agents)
            cluster_count = len(swarm.composition.clusters)

            agent_counts.append(agent_count)
            cluster_counts.append(cluster_count)

            # Progress every 100 cycles
            if cycle % 100 == 0:
                elapsed = time.time() - start_time
                print(f"  Cycle {cycle}/{cycles} - "
                      f"Agents: {agent_count}, "
                      f"Clusters: {cluster_count}, "
                      f"Time: {elapsed:.1f}s")

    duration = time.time() - start_time

    # Analysis
    states = sorted(set(agent_counts))
    state_counts = Counter(agent_counts)

    # Cluster analysis
    max_clusters = max(cluster_counts) if cluster_counts else 0
    avg_clusters = sum(cluster_counts) / len(cluster_counts) if cluster_counts else 0

    # Multi-cluster states (where clusters > 1)
    multicluster_indices = [i for i, c in enumerate(cluster_counts) if c > 1]
    multicluster_agent_counts = [agent_counts[i] for i in multicluster_indices]

    # Check correlation between agent count and cluster count
    agent_cluster_correlation = defaultdict(list)
    for i in range(len(agent_counts)):
        agent_cluster_correlation[agent_counts[i]].append(cluster_counts[i])

    print()
    print(f"="*80)
    print(f"ANALYSIS RESULTS")
    print(f"="*80)
    print()

    print(f"Agent Statistics:")
    print(f"  States observed: {states}")
    print(f"  Max agents: {max(states) if states else 0}")
    print(f"  Duration: {duration:.2f}s")
    print()

    print(f"Cluster Statistics:")
    print(f"  Max clusters: {max_clusters}")
    print(f"  Average clusters: {avg_clusters:.2f}")
    print(f"  Multi-cluster checkpoints: {len(multicluster_indices)}/{len(cluster_counts)} "
          f"({100*len(multicluster_indices)/len(cluster_counts):.1f}%)")
    print()

    # Analyze agent counts during multi-cluster states
    if multicluster_agent_counts:
        mc_counter = Counter(multicluster_agent_counts)
        print(f"Agent counts during multi-cluster states:")
        for count in sorted(mc_counter.keys()):
            freq = mc_counter[count]
            pct = 100 * freq / len(multicluster_agent_counts)
            print(f"  {count} agents: {freq} times ({pct:.1f}%)")
        print()

    # Agent-Cluster correlation
    print(f"Agent Count → Cluster Count correlation:")
    for agent_count in sorted(agent_cluster_correlation.keys()):
        cluster_list = agent_cluster_correlation[agent_count]
        avg_clusters_for_count = sum(cluster_list) / len(cluster_list)
        max_clusters_for_count = max(cluster_list)
        print(f"  {agent_count} agents: avg {avg_clusters_for_count:.1f} clusters, "
              f"max {max_clusters_for_count} clusters")
    print()

    # Gap state analysis
    all_possible = set(range(max(states) + 1)) if states else set()
    gap_states = sorted(all_possible - set(states))

    if gap_states:
        print(f"Gap States (missing): {gap_states}")
        print(f"  Hypothesis: Gaps occur due to independent cluster bursts")
    else:
        print(f"No gap states observed")
    print()

    # Multi-cluster hypothesis test
    multicluster_evidence = {
        'max_clusters_greater_than_1': max_clusters > 1,
        'frequent_multicluster': len(multicluster_indices) / len(cluster_counts) > 0.2,
        'gap_states_present': len(gap_states) > 0,
        'high_agent_counts_correlate_with_multiclusters': False
    }

    # Check if high agent counts correlate with multiple clusters
    high_agent_states = [s for s in states if s >= 6]
    if high_agent_states:
        high_agent_multicluster_rate = sum(
            1 for i, a in enumerate(agent_counts)
            if a in high_agent_states and cluster_counts[i] > 1
        ) / sum(1 for a in agent_counts if a in high_agent_states)
        multicluster_evidence['high_agent_counts_correlate_with_multiclusters'] = (
            high_agent_multicluster_rate > 0.3
        )
        print(f"Multi-cluster rate at high agent counts (≥6): {high_agent_multicluster_rate:.1%}")
        print()

    hypothesis_supported = sum(multicluster_evidence.values()) >= 3

    print(f"="*80)
    print(f"MULTI-CLUSTER HYPOTHESIS TEST")
    print(f"="*80)
    for criterion, passed in multicluster_evidence.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {criterion}")
    print()

    if hypothesis_supported:
        print(f"🎉 MULTI-CLUSTER HYPOTHESIS SUPPORTED!")
        print()
        print(f"Extreme burst thresholds (≥1000) enable multi-cluster regime where")
        print(f"multiple independent clusters coexist, creating qualitatively different")
        print(f"dynamics than single-cluster regime.")
    else:
        print(f"⚠️ MULTI-CLUSTER HYPOTHESIS NOT CLEARLY SUPPORTED")
        print(f"   May need longer observation or different threshold")

    print(f"="*80)

    return {
        'burst_threshold': burst_threshold,
        'cycles': cycles,
        'agent_counts': agent_counts,
        'cluster_counts': cluster_counts,
        'states': states,
        'gap_states': gap_states,
        'max_clusters': max_clusters,
        'avg_clusters': avg_clusters,
        'multicluster_frequency': len(multicluster_indices) / len(cluster_counts),
        'hypothesis_supported': hypothesis_supported,
        'multicluster_evidence': multicluster_evidence,
        'duration': duration
    }


def main():
    """Run multi-cluster regime investigation."""
    print("="*80)
    print("CYCLE 61: MULTI-CLUSTER REGIME INVESTIGATION")
    print("="*80)
    print()

    result = run_multicluster_analysis(burst_threshold=1200, cycles=500)

    # Save
    results_dir = Path(__file__).parent / "results" / "multicluster"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle61_multicluster_1200.json"

    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Results saved: {results_file}")

    return result


if __name__ == "__main__":
    main()
