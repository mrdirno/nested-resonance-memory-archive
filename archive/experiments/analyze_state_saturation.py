#!/usr/bin/env python3
"""
Analyze why the system saturates at exactly 5 states (0-4 agents).

This script examines state transition patterns, phase space dynamics,
and mathematical constraints to understand the 5-state limit.
"""

import json
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_ultra_long_result(experiment_id: str) -> dict:
    """Load results from ultra-long experiment."""
    results_dir = Path(__file__).parent / "results" / "ultra_long_term"
    result_file = results_dir / f"{experiment_id}_final.json"

    with open(result_file, 'r') as f:
        return json.load(f)


def analyze_state_transitions(agent_counts: list) -> dict:
    """
    Analyze state transition patterns to understand constraints.

    Returns:
        dict: Transition analysis including:
            - transition_matrix: dict mapping (from_state, to_state) -> count
            - state_graph: dict showing which states lead to which
            - forbidden_transitions: transitions that never occur
            - transition_probabilities: normalized transition matrix
    """
    # Build transition matrix
    transitions = defaultdict(int)
    for i in range(len(agent_counts) - 1):
        from_state = agent_counts[i]
        to_state = agent_counts[i + 1]
        transitions[(from_state, to_state)] += 1

    # Get all observed states
    observed_states = set(agent_counts)

    # Build state graph (adjacency list)
    state_graph = defaultdict(set)
    for (from_state, to_state) in transitions.keys():
        state_graph[from_state].add(to_state)

    # Find forbidden transitions (never occur)
    all_possible = [(s1, s2) for s1 in observed_states for s2 in observed_states]
    forbidden = [t for t in all_possible if transitions[t] == 0]

    # Calculate transition probabilities
    transition_probs = {}
    for from_state in observed_states:
        total_from = sum(transitions[(from_state, to_state)]
                        for to_state in observed_states)
        if total_from > 0:
            for to_state in observed_states:
                prob = transitions[(from_state, to_state)] / total_from
                if prob > 0:
                    transition_probs[(from_state, to_state)] = prob

    return {
        'transition_matrix': dict(transitions),
        'state_graph': {k: list(v) for k, v in state_graph.items()},
        'forbidden_transitions': forbidden,
        'transition_probabilities': transition_probs,
        'observed_states': sorted(list(observed_states))
    }


def analyze_transition_rules(transition_analysis: dict) -> dict:
    """
    Identify underlying rules governing state transitions.

    Returns patterns like:
    - Can only transition to adjacent states (+/- 1 agent)?
    - Are there cyclic patterns?
    - Which states are absorbing or transient?
    """
    state_graph = transition_analysis['state_graph']
    observed_states = transition_analysis['observed_states']

    # Check adjacency rule (can only change by ±1)
    adjacency_violations = []
    for from_state, to_states in state_graph.items():
        for to_state in to_states:
            if abs(to_state - from_state) > 3:  # Allow larger jumps
                adjacency_violations.append((from_state, to_state))

    # Identify cycles in transition graph
    cycles = []
    for state in observed_states:
        # Check for 2-cycles (A ↔ B)
        if state in state_graph:
            for neighbor in state_graph[state]:
                if neighbor in state_graph and state in state_graph[neighbor]:
                    cycle = tuple(sorted([state, neighbor]))
                    if cycle not in cycles:
                        cycles.append(cycle)

    # Calculate reachability (which states can reach which)
    reachability = {}
    for start_state in observed_states:
        reachable = set()
        to_visit = [start_state]
        visited = set()

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            reachable.add(current)

            if current in state_graph:
                for neighbor in state_graph[current]:
                    if neighbor not in visited:
                        to_visit.append(neighbor)

        reachability[start_state] = sorted(list(reachable))

    return {
        'adjacency_violations': adjacency_violations,
        'two_cycles': cycles,
        'reachability': reachability
    }


def analyze_state_stability(agent_counts: list) -> dict:
    """
    Analyze which states are stable (stay in state) vs transient (change quickly).
    """
    state_durations = defaultdict(list)
    current_state = agent_counts[0]
    duration = 1

    for i in range(1, len(agent_counts)):
        if agent_counts[i] == current_state:
            duration += 1
        else:
            state_durations[current_state].append(duration)
            current_state = agent_counts[i]
            duration = 1
    state_durations[current_state].append(duration)

    # Calculate statistics
    stability_stats = {}
    for state, durations in state_durations.items():
        stability_stats[state] = {
            'mean_duration': np.mean(durations),
            'median_duration': np.median(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'total_visits': len(durations),
            'total_time': sum(durations)
        }

    return stability_stats


def hypothesize_saturation_mechanism(
    transition_analysis: dict,
    transition_rules: dict,
    stability_stats: dict
) -> dict:
    """
    Generate hypotheses about why state space saturates at 5 states.
    """
    observed_states = transition_analysis['observed_states']
    state_graph = transition_analysis['state_graph']

    hypotheses = []

    # Hypothesis 1: Maximum composition size constraint
    if max(observed_states) == 4:
        hypotheses.append({
            'hypothesis': 'Maximum Cluster Size Constraint',
            'description': 'System may have inherent limit on agent cluster size (max 4 agents)',
            'evidence': f'Highest observed state: {max(observed_states)} agents',
            'test': 'Check if composition dynamics prevent 5+ agent clusters'
        })

    # Hypothesis 2: Transition structure constraint
    # Check if higher states have restricted outgoing transitions
    if 4 in state_graph:
        state_4_transitions = state_graph[4]
        hypotheses.append({
            'hypothesis': 'Rare State Instability',
            'description': 'State 4 may be inherently unstable (limited outgoing transitions)',
            'evidence': f'State 4 transitions to: {state_4_transitions}',
            'test': 'Analyze why state 4 quickly transitions away'
        })

    # Hypothesis 3: Phase space constraint
    if len(observed_states) == 5:
        hypotheses.append({
            'hypothesis': 'Five-Point Attractor Manifold',
            'description': 'Transcendental oscillators may create exactly 5 stable regions',
            'evidence': f'Exactly {len(observed_states)} distinct states observed',
            'test': 'Analyze phase space geometry from transcendental bridge'
        })

    # Hypothesis 4: Energy/resource constraint
    state_frequencies = Counter(stability_stats.keys())
    most_common = max(stability_stats.items(),
                      key=lambda x: x[1]['total_time'])[0]
    hypotheses.append({
        'hypothesis': 'Energy Minimization',
        'description': f'System prefers lower energy states (most time in state {most_common})',
        'evidence': f'State {most_common} has longest total duration',
        'test': 'Calculate energy levels for each state'
    })

    return hypotheses


def main():
    """Main analysis routine."""
    print("=" * 80)
    print("STATE SPACE SATURATION ANALYSIS")
    print("=" * 80)
    print()

    # Load 2000-cycle experiment data
    print("Loading 2000-cycle experiment data...")
    result = load_ultra_long_result("ultralong_1761120499")
    agent_counts = result['agent_counts']

    print(f"Loaded {len(agent_counts)} checkpoints")
    print(f"States observed: {sorted(set(agent_counts))}")
    print()

    # Analyze state transitions
    print("-" * 80)
    print("TRANSITION ANALYSIS")
    print("-" * 80)
    transition_analysis = analyze_state_transitions(agent_counts)

    print(f"Observed states: {transition_analysis['observed_states']}")
    print()
    print("State transition graph:")
    for state, neighbors in sorted(transition_analysis['state_graph'].items()):
        print(f"  State {state} → {sorted(neighbors)}")
    print()

    print(f"Total unique transitions: {len(transition_analysis['transition_matrix'])}")
    print(f"Forbidden transitions: {len(transition_analysis['forbidden_transitions'])}")
    print()

    # Show most common transitions
    print("Most common transitions:")
    sorted_transitions = sorted(
        transition_analysis['transition_matrix'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    for (from_state, to_state), count in sorted_transitions:
        prob = transition_analysis['transition_probabilities'].get(
            (from_state, to_state), 0
        )
        print(f"  {from_state} → {to_state}: {count} times ({prob:.3f} prob)")
    print()

    # Analyze transition rules
    print("-" * 80)
    print("TRANSITION RULES")
    print("-" * 80)
    transition_rules = analyze_transition_rules(transition_analysis)

    print("Two-state cycles (bidirectional transitions):")
    for cycle in transition_rules['two_cycles']:
        print(f"  {cycle[0]} ↔ {cycle[1]}")
    print()

    print("Reachability (which states can reach which):")
    for state, reachable in sorted(transition_rules['reachability'].items()):
        print(f"  From state {state}: can reach {reachable}")
    print()

    # Analyze state stability
    print("-" * 80)
    print("STATE STABILITY")
    print("-" * 80)
    stability_stats = analyze_state_stability(agent_counts)

    for state in sorted(stability_stats.keys()):
        stats = stability_stats[state]
        print(f"State {state}:")
        print(f"  Mean duration: {stats['mean_duration']:.2f} checkpoints")
        print(f"  Median duration: {stats['median_duration']:.1f} checkpoints")
        print(f"  Max duration: {stats['max_duration']} checkpoints")
        print(f"  Total visits: {stats['total_visits']}")
        print(f"  Total time: {stats['total_time']} checkpoints "
              f"({100*stats['total_time']/len(agent_counts):.1f}%)")
        print()

    # Generate hypotheses
    print("-" * 80)
    print("SATURATION MECHANISM HYPOTHESES")
    print("-" * 80)
    hypotheses = hypothesize_saturation_mechanism(
        transition_analysis,
        transition_rules,
        stability_stats
    )

    for i, hyp in enumerate(hypotheses, 1):
        print(f"Hypothesis {i}: {hyp['hypothesis']}")
        print(f"  Description: {hyp['description']}")
        print(f"  Evidence: {hyp['evidence']}")
        print(f"  Test: {hyp['test']}")
        print()

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    # Return analysis for further processing
    return {
        'transition_analysis': transition_analysis,
        'transition_rules': transition_rules,
        'stability_stats': stability_stats,
        'hypotheses': hypotheses
    }


if __name__ == '__main__':
    main()
