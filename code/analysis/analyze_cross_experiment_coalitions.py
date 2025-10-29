#!/usr/bin/env python3
"""
Cross-Experiment Coalition Analysis
====================================

Purpose: Analyze semantic relationships discovered by NRM V2 consolidation
across C175, C176, and C177 experimental hypotheses.

This script examines:
1. Which hypotheses from different experiments synchronize together
2. What semantic features drive cross-experiment coalitions
3. Predictive power of consolidation for experimental outcomes
4. Novel insights from hypothesis linkage

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29 (Cycle 489)
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict, Counter


def load_consolidation_results(results_path: Path) -> Dict:
    """Load consolidation results from JSON file."""
    with open(results_path, 'r') as f:
        return json.load(f)


def extract_cross_experiment_coalitions(
    results: Dict
) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract coalitions that link hypotheses from different experiments.

    Returns:
        Tuple of (nrem_cross_coalitions, rem_cross_coalitions)
    """
    nrem_cross = []
    rem_cross = []

    # Check NREM coalitions
    for coalition in results['nrem']['coalition_details']:
        members = coalition['members']
        experiments = set()
        for member in members:
            if 'c176' in member:
                experiments.add('C176')
            elif 'c177' in member:
                experiments.add('C177')
            elif 'c175' in member:
                experiments.add('C175')

        if len(experiments) > 1:
            coalition['experiments'] = list(experiments)
            nrem_cross.append(coalition)

    # Check REM coalitions
    for coalition in results['rem']['coalition_details']:
        members = coalition['members']
        experiments = set()
        for member in members:
            if 'c176' in member:
                experiments.add('C176')
            elif 'c177' in member:
                experiments.add('C177')
            elif 'c175' in member:
                experiments.add('C175')

        if len(experiments) > 1:
            coalition['experiments'] = list(experiments)
            rem_cross.append(coalition)

    return nrem_cross, rem_cross


def analyze_hypothesis_co_occurrence(
    results: Dict
) -> Dict[Tuple[str, str], Dict]:
    """
    Analyze which hypothesis pairs appear together most frequently.

    Returns:
        Dict mapping (hypothesis1, hypothesis2) -> stats
    """
    pair_stats = defaultdict(lambda: {
        'nrem_count': 0,
        'rem_count': 0,
        'nrem_coherences': [],
        'rem_coherences': []
    })

    # Process NREM coalitions
    for coalition in results['nrem']['coalition_details']:
        members = coalition['members']
        coherence = coalition['coherence']

        # Generate all pairs
        for i, m1 in enumerate(members):
            for m2 in members[i+1:]:
                pair = tuple(sorted([m1, m2]))
                pair_stats[pair]['nrem_count'] += 1
                pair_stats[pair]['nrem_coherences'].append(coherence)

    # Process REM coalitions
    for coalition in results['rem']['coalition_details']:
        members = coalition['members']
        coherence = coalition['coherence']

        # Generate all pairs
        for i, m1 in enumerate(members):
            for m2 in members[i+1:]:
                pair = tuple(sorted([m1, m2]))
                pair_stats[pair]['rem_count'] += 1
                pair_stats[pair]['rem_coherences'].append(coherence)

    # Compute average coherences
    for pair in pair_stats:
        if pair_stats[pair]['nrem_coherences']:
            pair_stats[pair]['nrem_avg_coherence'] = sum(
                pair_stats[pair]['nrem_coherences']
            ) / len(pair_stats[pair]['nrem_coherences'])
        else:
            pair_stats[pair]['nrem_avg_coherence'] = 0.0

        if pair_stats[pair]['rem_coherences']:
            pair_stats[pair]['rem_avg_coherence'] = sum(
                pair_stats[pair]['rem_coherences']
            ) / len(pair_stats[pair]['rem_coherences'])
        else:
            pair_stats[pair]['rem_avg_coherence'] = 0.0

        pair_stats[pair]['total_count'] = (
            pair_stats[pair]['nrem_count'] + pair_stats[pair]['rem_count']
        )

    return dict(pair_stats)


def identify_semantic_clusters(pair_stats: Dict) -> List[Set[str]]:
    """
    Identify clusters of hypotheses that frequently co-occur.

    Uses simple connected components on co-occurrence graph.
    """
    # Build adjacency list (threshold: appear together at least 3 times)
    adjacency = defaultdict(set)

    for (h1, h2), stats in pair_stats.items():
        if stats['total_count'] >= 3:
            adjacency[h1].add(h2)
            adjacency[h2].add(h1)

    # Find connected components via DFS
    visited = set()
    clusters = []

    def dfs(node, cluster):
        visited.add(node)
        cluster.add(node)
        for neighbor in adjacency[node]:
            if neighbor not in visited:
                dfs(neighbor, cluster)

    for node in adjacency:
        if node not in visited:
            cluster = set()
            dfs(node, cluster)
            clusters.append(cluster)

    return clusters


def generate_insights(
    results: Dict,
    cross_nrem: List[Dict],
    cross_rem: List[Dict],
    pair_stats: Dict,
    clusters: List[Set[str]]
) -> List[str]:
    """Generate key insights from cross-experiment coalition analysis."""
    insights = []

    # Insight 1: Cross-experiment linkage frequency
    total_nrem = results['nrem']['coalitions']
    total_rem = results['rem']['coalitions']
    cross_nrem_count = len(cross_nrem)
    cross_rem_count = len(cross_rem)

    insights.append(
        f"Cross-Experiment Linkage: {cross_nrem_count}/{total_nrem} NREM "
        f"({100*cross_nrem_count/total_nrem:.1f}%) and "
        f"{cross_rem_count}/{total_rem} REM ({100*cross_rem_count/total_rem:.1f}%) "
        f"coalitions linked hypotheses from different experiments."
    )

    # Insight 2: Most frequently co-occurring pairs
    top_pairs = sorted(
        pair_stats.items(),
        key=lambda x: x[1]['total_count'],
        reverse=True
    )[:5]

    insights.append("\nTop 5 Most Frequently Co-Occurring Hypothesis Pairs:")
    for (h1, h2), stats in top_pairs:
        insights.append(
            f"  - {h1} + {h2}: "
            f"{stats['total_count']} coalitions "
            f"(NREM coherence: {stats['nrem_avg_coherence']:.3f}, "
            f"REM coherence: {stats['rem_avg_coherence']:.3f})"
        )

    # Insight 3: Semantic clusters
    insights.append(f"\nSemantic Clusters Discovered: {len(clusters)}")
    for i, cluster in enumerate(clusters, 1):
        insights.append(f"  Cluster {i} (size={len(cluster)}): {', '.join(cluster)}")

    # Insight 4: NREM vs REM consolidation patterns
    nrem_avg_coherence = sum(
        c['coherence'] for c in results['nrem']['coalition_details']
    ) / len(results['nrem']['coalition_details'])

    rem_avg_coherence = sum(
        c['coherence'] for c in results['rem']['coalition_details']
    ) / len(results['rem']['coalition_details'])

    insights.append(
        f"\nConsolidation Dynamics:"
        f"\n  NREM (Slow-Wave): {total_nrem} coalitions, "
        f"avg coherence={nrem_avg_coherence:.3f}, "
        f"{results['nrem']['hebbian_updates']} Hebbian updates"
        f"\n  REM (High-Freq): {total_rem} coalitions, "
        f"avg coherence={rem_avg_coherence:.3f}, "
        f"exploratory mode"
    )

    # Insight 5: Computational efficiency
    total_patterns = results['patterns']['total_count']
    total_cpu = results['total']['cpu_time_ms']
    patterns_per_ms = total_patterns / total_cpu

    insights.append(
        f"\nComputational Efficiency:"
        f"\n  Patterns processed: {total_patterns}"
        f"\n  Total CPU time: {total_cpu:.2f} ms"
        f"\n  Throughput: {patterns_per_ms:.2f} patterns/ms"
        f"\n  Memory usage: {results['total']['memory_usage_mb']:.2f} MB"
    )

    return insights


def main():
    """Run cross-experiment coalition analysis."""

    print("\n" + "="*80)
    print("CROSS-EXPERIMENT COALITION ANALYSIS")
    print("="*80 + "\n")

    # Load C176-C177 consolidation results
    results_path = Path(__file__).parent.parent.parent / "data" / "results" / "nrmv2_c176_c177_consolidation.json"

    if not results_path.exists():
        print(f"ERROR: Results file not found at {results_path}")
        return

    print(f"Loading consolidation results from:")
    print(f"  {results_path}\n")

    results = load_consolidation_results(results_path)

    # Extract cross-experiment coalitions
    print("Extracting cross-experiment coalitions...")
    cross_nrem, cross_rem = extract_cross_experiment_coalitions(results)

    print(f"  Found {len(cross_nrem)} NREM cross-experiment coalitions")
    print(f"  Found {len(cross_rem)} REM cross-experiment coalitions\n")

    # Analyze hypothesis co-occurrence
    print("Analyzing hypothesis co-occurrence patterns...")
    pair_stats = analyze_hypothesis_co_occurrence(results)
    print(f"  Detected {len(pair_stats)} unique hypothesis pairs\n")

    # Identify semantic clusters
    print("Identifying semantic clusters...")
    clusters = identify_semantic_clusters(pair_stats)
    print(f"  Found {len(clusters)} semantic clusters\n")

    # Generate insights
    print("-"*80)
    print("KEY INSIGHTS")
    print("-"*80 + "\n")

    insights = generate_insights(
        results, cross_nrem, cross_rem, pair_stats, clusters
    )

    for insight in insights:
        print(insight)

    # Detailed cross-experiment coalitions
    if cross_nrem or cross_rem:
        print("\n" + "-"*80)
        print("CROSS-EXPERIMENT COALITIONS (Detailed)")
        print("-"*80 + "\n")

        if cross_nrem:
            print("NREM Coalitions:")
            for i, coalition in enumerate(cross_nrem, 1):
                print(f"  {i}. Coherence={coalition['coherence']:.3f}, "
                      f"Experiments={coalition['experiments']}")
                print(f"     Members: {', '.join(coalition['members'])}")

        if cross_rem:
            print(f"\nREM Coalitions:")
            for i, coalition in enumerate(cross_rem, 1):
                print(f"  {i}. Coherence={coalition['coherence']:.3f}, "
                      f"Experiments={coalition['experiments']}")
                print(f"     Members: {', '.join(coalition['members'])}")

    # Save analysis results
    analysis_path = results_path.parent / "nrmv2_cross_experiment_analysis.json"

    analysis_results = {
        'source': str(results_path.name),
        'date': results['date'],
        'cross_experiment_coalitions': {
            'nrem': cross_nrem,
            'rem': cross_rem
        },
        'pair_statistics': {
            f"{h1}+{h2}": stats
            for (h1, h2), stats in sorted(
                pair_stats.items(),
                key=lambda x: x[1]['total_count'],
                reverse=True
            )
        },
        'semantic_clusters': [
            {'cluster_id': i, 'members': list(cluster)}
            for i, cluster in enumerate(clusters, 1)
        ],
        'insights': insights
    }

    with open(analysis_path, 'w') as f:
        json.dump(analysis_results, f, indent=2)

    print(f"\n\nAnalysis results saved to: {analysis_path}")
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    main()
