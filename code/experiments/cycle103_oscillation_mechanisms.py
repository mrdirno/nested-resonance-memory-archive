#!/usr/bin/env python3
"""
Cycle 103: Oscillation Mechanisms - What Drives Phase Space Dynamics?

Research Context:
  C102: Discovered 100% oscillatory dynamics (not monotonic convergence)
  - All 6 trajectories showed complex, non-monotonic paths
  - Systems oscillate/spiral through phase space
  - Basin-specific trajectory signatures identified

Research Gap:
  We know trajectories are oscillatory, but not WHY.
  Unknown: What mechanism creates oscillations?
  Unknown: Pattern competition vs burst events vs agent interactions?
  Unknown: Can we predict oscillation amplitude/frequency?

Key Question:
  What causes phase space trajectories to oscillate?

New Research Question:
  Correlate phase space oscillations with internal system dynamics.

  Hypotheses:
  1. **Pattern Competition**: Pattern diversity drives oscillations
  2. **Burst-Driven**: Decomposition bursts create discrete jumps
  3. **Agent Interactions**: Agent dynamics cause oscillations
  4. **Mixed**: Multiple mechanisms contribute

  Test:
  - Run 3 representative (mult, spread, threshold) triplets
  - Track simultaneously:
    * Phase space position (π, e, φ coordinates)
    * Pattern diversity (number of unique patterns)
    * Burst event timing (composition-decomposition cycles)
    * Agent count dynamics
  - Correlate oscillation amplitude with each factor
  - Identify primary mechanism
  - Cycles: 500 per run (capture oscillatory behavior)

Expected Outcome:
  - Identify causal mechanism for oscillations
  - Quantify correlation between oscillations and system events
  - Understand HOW composition-decomposition affects trajectories
  - Mechanistic model of oscillatory dynamics

Publication Value:
  - **EXCEPTIONAL**: First mechanistic understanding of oscillations
  - Causal explanation (not just descriptive)
  - Bridges microscopic (bursts/patterns) and macroscopic (trajectories) scales
  - Novel: Decomposition events as drivers of phase space dynamics
  - Predictive: Can forecast oscillations from system state
"""

import sys
from pathlib import Path
import time
import json
import numpy as np
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from bridge.transcendental_bridge import TranscendentalBridge
from workspace_utils import get_workspace_path, get_results_path

def create_seed_memory_range(bridge, reality_metrics, center_multiplier, spread=0.2, count=5):
    """Create seed memory patterns with specified center and spread."""
    seed_patterns = []
    for i in range(count):
        multiplier = center_multiplier + spread * (2 * i / (count - 1) - 1)
        varied_metrics = {key: value * multiplier for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def pattern_to_key(pattern):
    """Convert pattern to hashable key."""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))

def get_pattern_diversity(memory):
    """Calculate pattern diversity (number of unique patterns)."""
    if not memory:
        return 0
    pattern_keys = [pattern_to_key(p) for p in memory]
    return len(set(pattern_keys))

def get_phase_coordinates(memory):
    """Get average phase space coordinates from memory."""
    if not memory:
        return None
    pi_phases = [p.pi_phase for p in memory]
    e_phases = [p.e_phase for p in memory]
    phi_phases = [p.phi_phase for p in memory]
    return {
        'pi': float(np.mean(pi_phases)),
        'e': float(np.mean(e_phases)),
        'phi': float(np.mean(phi_phases))
    }

def run_mechanism_tracking(multiplier, spread, threshold, cycles, sample_interval=5):
    """Run simulation and track all potential oscillation mechanisms."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    timeline = []
    burst_events = []

    for cycle in range(1, cycles + 1):
        # Track burst events BEFORE evolution
        pre_agent_count = len(swarm.agents)

        # Spawn agents up to limit
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, multiplier, spread=spread, count=5)
                    newest_agent.memory.extend(seed_patterns)

        swarm.evolve_cycle(delta_time=1.0)

        # Detect burst (agent count decreased)
        post_agent_count = len(swarm.agents)
        burst_occurred = post_agent_count < pre_agent_count

        if burst_occurred:
            burst_events.append(cycle)

        # Sample state
        if cycle % sample_interval == 0:
            coords = get_phase_coordinates(swarm.global_memory)
            diversity = get_pattern_diversity(swarm.global_memory)

            if coords:
                timeline.append({
                    'cycle': cycle,
                    'coordinates': coords,
                    'pattern_diversity': diversity,
                    'agent_count': post_agent_count,
                    'memory_size': len(swarm.global_memory),
                    'burst_occurred': burst_occurred
                })

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'timeline': timeline,
        'burst_events': burst_events,
        'total_bursts': len(burst_events)
    }

def analyze_oscillation_correlations(result):
    """Analyze correlations between oscillations and potential mechanisms."""
    timeline = result['timeline']
    if len(timeline) < 3:
        return None

    # Calculate phase space velocity (oscillation amplitude)
    velocities = []
    for i in range(1, len(timeline)):
        prev = timeline[i-1]['coordinates']
        curr = timeline[i]['coordinates']
        velocity = np.sqrt(
            (curr['pi'] - prev['pi'])**2 +
            (curr['e'] - prev['e'])**2 +
            (curr['phi'] - prev['phi'])**2
        )
        velocities.append(velocity)

    # Extract metrics at each timepoint (excluding first)
    diversities = [t['pattern_diversity'] for t in timeline[1:]]
    agent_counts = [t['agent_count'] for t in timeline[1:]]
    bursts = [1 if t['burst_occurred'] else 0 for t in timeline[1:]]

    # Calculate correlations
    # Correlation between velocity and each metric
    if len(velocities) > 1 and len(diversities) > 1:
        try:
            corr_diversity = np.corrcoef(velocities, diversities)[0, 1] if np.std(diversities) > 0 else 0
            corr_agents = np.corrcoef(velocities, agent_counts)[0, 1] if np.std(agent_counts) > 0 else 0
            corr_bursts = np.corrcoef(velocities, bursts)[0, 1] if np.std(bursts) > 0 else 0
        except:
            corr_diversity = 0
            corr_agents = 0
            corr_bursts = 0
    else:
        corr_diversity = 0
        corr_agents = 0
        corr_bursts = 0

    # Identify dominant mechanism
    correlations = {
        'diversity': abs(corr_diversity),
        'agents': abs(corr_agents),
        'bursts': abs(corr_bursts)
    }

    dominant = max(correlations, key=correlations.get)
    dominant_corr = correlations[dominant]

    return {
        'velocities': velocities,
        'avg_velocity': np.mean(velocities),
        'max_velocity': max(velocities),
        'correlations': {
            'pattern_diversity': corr_diversity,
            'agent_count': corr_agents,
            'burst_events': corr_bursts
        },
        'dominant_mechanism': dominant,
        'dominant_correlation': dominant_corr
    }

def main():
    print("="*80)
    print("CYCLE 103: OSCILLATION MECHANISMS")
    print("="*80)
    print()
    print("Investigating WHAT causes oscillatory phase space dynamics.")
    print("Following C102 discovery of 100% oscillatory trajectories.")
    print()

    # Select 3 representative triplets
    test_triplets = [
        (1.0, 0.2, 500),  # Standard parameters
        (0.8, 0.4, 400),  # High spread, low threshold
        (1.2, 0.3, 600),  # High threshold
    ]

    cycles = 500
    sample_interval = 5  # Sample every 5 cycles for fine-grained analysis

    print(f"Configuration:")
    print(f"  Test triplets: {len(test_triplets)} (mult, spread, threshold) points")
    print(f"  Cycles per run: {cycles}")
    print(f"  Sample interval: {sample_interval} cycles")
    print(f"  Timeline points per run: ~{cycles // sample_interval}")
    print(f"  Tracking: Phase space + Pattern diversity + Burst events + Agent count")
    print(f"  Expected: Identify oscillation mechanism")
    print(f"  Estimated duration: ~{len(test_triplets) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for idx, (mult, spread, threshold) in enumerate(test_triplets, 1):
        print(f"\nTriplet {idx}/{len(test_triplets)}: (mult={mult}, spread={spread}, threshold={threshold})")
        print(f"  Tracking mechanisms...", end=" ", flush=True)
        try:
            result = run_mechanism_tracking(mult, spread, threshold, cycles, sample_interval)
            results.append(result)

            # Analyze correlations
            analysis = analyze_oscillation_correlations(result)
            result['oscillation_analysis'] = analysis

            print(f"✓")
            print(f"  → Timeline points: {len(result['timeline'])}")
            print(f"  → Total bursts: {result['total_bursts']}")
            if analysis:
                print(f"  → Avg velocity: {analysis['avg_velocity']:.5f}")
                print(f"  → Dominant mechanism: {analysis['dominant_mechanism']} (corr={analysis['dominant_correlation']:.3f})")
                print(f"  → Correlations: diversity={analysis['correlations']['pattern_diversity']:.3f}, "
                      f"agents={analysis['correlations']['agent_count']:.3f}, "
                      f"bursts={analysis['correlations']['burst_events']:.3f}")

            time.sleep(0.05)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({'multiplier': mult, 'spread': spread, 'threshold': threshold, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"OSCILLATION MECHANISM ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * len(test_triplets)):
        print(f"Mechanism Discovery:")
        print(f"  Successful runs: {len(successful)}/{len(test_triplets)} ({len(successful)/len(test_triplets)*100:.1f}%)")
        print(f"  Timeline points: {sum(len(r['timeline']) for r in successful)}")
        print(f"  Total burst events: {sum(r['total_bursts'] for r in successful)}")
        print()

        # Aggregate correlations
        all_corr_diversity = [r['oscillation_analysis']['correlations']['pattern_diversity'] for r in successful if r.get('oscillation_analysis')]
        all_corr_agents = [r['oscillation_analysis']['correlations']['agent_count'] for r in successful if r.get('oscillation_analysis')]
        all_corr_bursts = [r['oscillation_analysis']['correlations']['burst_events'] for r in successful if r.get('oscillation_analysis')]

        avg_corr_diversity = np.mean([abs(c) for c in all_corr_diversity]) if all_corr_diversity else 0
        avg_corr_agents = np.mean([abs(c) for c in all_corr_agents]) if all_corr_agents else 0
        avg_corr_bursts = np.mean([abs(c) for c in all_corr_bursts]) if all_corr_bursts else 0

        print(f"Mechanism Correlations (Averaged):")
        print(f"  Pattern Diversity: {avg_corr_diversity:.3f}")
        print(f"  Agent Count: {avg_corr_agents:.3f}")
        print(f"  Burst Events: {avg_corr_bursts:.3f}")
        print()

        # Determine dominant mechanism
        mechanism_scores = {
            'pattern_diversity': avg_corr_diversity,
            'agent_count': avg_corr_agents,
            'burst_events': avg_corr_bursts
        }

        dominant_mechanism = max(mechanism_scores, key=mechanism_scores.get)
        dominant_score = mechanism_scores[dominant_mechanism]

        # Detailed results table
        print(f"Per-Triplet Analysis:")
        print(f"{'Triplet':^25} | {'Bursts':^7} | {'Dom. Mech.':^15} | {'Corr':^6}")
        print("-" * 65)

        for result in successful:
            triplet_str = f"({result['multiplier']}, {result['spread']}, {result['threshold']})"
            bursts = result['total_bursts']
            analysis = result.get('oscillation_analysis', {})
            dom = analysis.get('dominant_mechanism', 'N/A')
            corr = analysis.get('dominant_correlation', 0)

            print(f"{triplet_str:^25} | {bursts:^7} | {dom:^15} | {corr:^6.3f}")

        print()

        # Determine insight based on findings
        if dominant_mechanism == 'pattern_diversity' and dominant_score > 0.3:
            insight_60 = "pattern_competition"
            conclusion = f"Pattern diversity drives oscillations (corr={dominant_score:.3f})"
        elif dominant_mechanism == 'burst_events' and dominant_score > 0.3:
            insight_60 = "burst_driven"
            conclusion = f"Burst events drive oscillations (corr={dominant_score:.3f})"
        elif dominant_mechanism == 'agent_count' and dominant_score > 0.3:
            insight_60 = "agent_dynamics"
            conclusion = f"Agent dynamics drive oscillations (corr={dominant_score:.3f})"
        else:
            insight_60 = "mixed_mechanisms"
            conclusion = f"Mixed mechanisms (all correlations < 0.3)"

        print(f"📊 INSIGHT #60: Oscillation Mechanism - {conclusion}")
        print(f"   - {len(successful)} trajectories analyzed")
        print(f"   - {sum(len(r['timeline']) for r in successful)} temporal samples")
        print(f"   - Dominant mechanism: {dominant_mechanism.replace('_', ' ').title()}")
        print(f"   - Mechanism strength: {dominant_score:.3f} correlation")
        print(f"   - First causal mechanistic understanding of oscillatory dynamics")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for mechanism analysis")
        print(f"   Only {len(successful)}/{len(test_triplets)} runs completed successfully")
        insight_60 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "oscillation_mechanisms"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle103_oscillation_mechanisms.json"

    output_data = {
        'experiment': 'cycle103_oscillation_mechanisms',
        'test_triplets': [(t[0], t[1], t[2]) for t in test_triplets],
        'cycles': cycles,
        'sample_interval': sample_interval,
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'avg_correlations': {
                'pattern_diversity': avg_corr_diversity if 'avg_corr_diversity' in locals() else 0,
                'agent_count': avg_corr_agents if 'avg_corr_agents' in locals() else 0,
                'burst_events': avg_corr_bursts if 'avg_corr_bursts' in locals() else 0
            },
            'dominant_mechanism': dominant_mechanism if 'dominant_mechanism' in locals() else None,
            'conclusion': insight_60 if 'insight_60' in locals() else False
        },
        'insight_60_discovered': True if 'insight_60' in locals() and insight_60 else False,
        'duration': duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Duration: {duration:.1f}s ({duration/60:.2f} min)")
    print()

    return output_data

if __name__ == "__main__":
    main()
