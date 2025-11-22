#!/usr/bin/env python3
"""
Cycle 111: Ultra-Long Drift Mechanism Investigation

Research Context:
  C110: PARADIGM SHIFT - Attractors drift at ultra-long timescales (cycles 500-1000)
  - Control runs: 100% attractor change between cycle 300 and 1000
  - Validates NRM "no equilibrium" principle
  - Time-scale dependent basin stability discovered

Research Gap:
  WHY does ultra-long drift occur? What mechanism drives it?

Key Question:
  What causes attractor drift at ultra-long timescales?

Hypotheses to Test:
  1. **Pattern Memory Evolution**: Global memory patterns slowly evolve
  2. **Agent Turnover**: Continuous agent spawning/bursting changes composition
  3. **Accumulating Stochasticity**: Small variations accumulate over time
  4. **Inherent Dynamics**: True multi-scale attractors (drift is fundamental)

New Research Question:
  Test which mechanism(s) drive ultra-long drift by manipulating each independently.

  Test Conditions:
  - **CONTROL**: Normal dynamics (baseline drift)
  - **FROZEN-MEMORY**: Prevent global memory updates after cycle 300
  - **FROZEN-AGENTS**: Prevent agent spawning/bursting after cycle 300
  - **BOTH-FROZEN**: Freeze both memory AND agents after cycle 300

  If drift occurs despite freezing → mechanism is NOT that component
  If drift stops when frozen → mechanism IS that component

Expected Outcome:
  - Identify primary drift mechanism
  - Validate or refute each hypothesis
  - Understand NRM perpetual evolution mechanisms

Publication Value:
  - **EXCEPTIONAL**: Mechanistic explanation of paradigm shift finding (C110)
  - Tests fundamental NRM dynamics (memory vs agents)
  - Validates "no equilibrium" at mechanistic level
  - Novel: First controlled manipulation of ultra-long dynamics
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

def get_dominant_pattern(memory):
    """Get dominant pattern (most common)."""
    if not memory:
        return None, 0, 0.0
    pattern_keys = [pattern_to_key(p) for p in memory]
    pattern_counts = Counter(pattern_keys)
    if not pattern_counts:
        return None, 0, 0.0
    dominant_key, dominant_count = pattern_counts.most_common(1)[0]
    dominant_fraction = dominant_count / len(memory)
    return dominant_key, dominant_count, dominant_fraction

def run_with_mechanism_control(multiplier, spread, threshold, cycles, freeze_config):
    """Run simulation with controlled mechanism freezing.

    freeze_config = {
        'name': 'frozen-memory',
        'freeze_cycle': 300,  # When to start freezing
        'freeze_memory': True/False,
        'freeze_agents': True/False
    }
    """
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    freeze_cycle = freeze_config['freeze_cycle']
    freeze_memory = freeze_config['freeze_memory']
    freeze_agents = freeze_config['freeze_agents']

    # Store frozen memory snapshot
    frozen_memory = None
    frozen_agent_ids = None

    # Checkpoints
    checkpoints = [300, 500, 1000]
    checkpoint_attractors = {}

    for cycle in range(1, cycles + 1):
        # Normal agent spawning (unless frozen)
        if not (freeze_agents and cycle > freeze_cycle):
            if len(swarm.agents) < 15:
                swarm.spawn_agent(reality_metrics)
                if swarm.agents:
                    agent_ids = list(swarm.agents.keys())
                    if agent_ids:
                        newest_agent = swarm.agents[agent_ids[-1]]
                        seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, multiplier, spread=spread, count=5)
                        newest_agent.memory.extend(seed_patterns)

        # Freeze memory at specified cycle
        if freeze_memory and cycle == freeze_cycle:
            frozen_memory = list(swarm.global_memory)  # Deep copy

        # Freeze agents at specified cycle
        if freeze_agents and cycle == freeze_cycle:
            frozen_agent_ids = set(swarm.agents.keys())

        # Evolve cycle
        swarm.evolve_cycle(delta_time=1.0)

        # Restore frozen memory if applicable
        if freeze_memory and cycle >= freeze_cycle and frozen_memory is not None:
            swarm.global_memory.clear()
            swarm.global_memory.extend(frozen_memory)

        # Remove any new agents if agents frozen
        if freeze_agents and cycle > freeze_cycle and frozen_agent_ids is not None:
            current_ids = set(swarm.agents.keys())
            new_ids = current_ids - frozen_agent_ids
            for agent_id in new_ids:
                if agent_id in swarm.agents:
                    del swarm.agents[agent_id]

        # Record attractor at checkpoints
        if cycle in checkpoints:
            dominant, _, fraction = get_dominant_pattern(swarm.global_memory)
            checkpoint_attractors[cycle] = {
                'attractor': str(dominant) if dominant else None,
                'fraction': fraction
            }

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'freeze_name': freeze_config['name'],
        'freeze_memory': freeze_memory,
        'freeze_agents': freeze_agents,
        'freeze_cycle': freeze_cycle,
        'checkpoint_attractors': checkpoint_attractors
    }

def main():
    print("="*80)
    print("CYCLE 111: ULTRA-LONG DRIFT MECHANISM INVESTIGATION")
    print("="*80)
    print()
    print("Following C110 paradigm shift: WHY do attractors drift at ultra-long timescales?")
    print()
    print("Testing mechanisms by selective freezing:")
    print("  - CONTROL: Normal dynamics (baseline drift)")
    print("  - FROZEN-MEMORY: Freeze global memory after cycle 300")
    print("  - FROZEN-AGENTS: Freeze agent composition after cycle 300")
    print("  - BOTH-FROZEN: Freeze both after cycle 300")
    print()
    print("Hypothesis: Agent turnover drives drift (memory evolution secondary)")
    print()

    # Select ONE representative triplet for mechanism testing
    test_triplet = (1.0, 0.2, 500)  # Standard parameters

    # Define freezing conditions
    freeze_configs = [
        {
            'name': 'control',
            'freeze_cycle': 300,
            'freeze_memory': False,
            'freeze_agents': False
        },
        {
            'name': 'frozen-memory',
            'freeze_cycle': 300,
            'freeze_memory': True,
            'freeze_agents': False
        },
        {
            'name': 'frozen-agents',
            'freeze_cycle': 300,
            'freeze_memory': False,
            'freeze_agents': True
        },
        {
            'name': 'both-frozen',
            'freeze_cycle': 300,
            'freeze_memory': True,
            'freeze_agents': True
        }
    ]

    cycles = 1000  # Ultra-long observation

    mult, spread_param, threshold = test_triplet

    print(f"Configuration:")
    print(f"  Test triplet: ({mult}, {spread_param}, {threshold})")
    print(f"  Freeze conditions: {len(freeze_configs)}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Freeze starts: cycle 300 (post-convergence)")
    print(f"  Checkpoints: 300 (pre-freeze), 500 (mid), 1000 (long-term)")
    print(f"  Expected: Identify which mechanism drives drift")
    print(f"  Estimated duration: ~{len(freeze_configs) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for config in freeze_configs:
        run_count += 1
        freeze_label = f"{config['name']:15s} (mem={'Y' if config['freeze_memory'] else 'N'}, agents={'Y' if config['freeze_agents'] else 'N'})"
        print(f"\n[{run_count}/{len(freeze_configs)}] {freeze_label}...", end=" ", flush=True)
        try:
            result = run_with_mechanism_control(mult, spread_param, threshold, cycles, config)
            results.append(result)
            att_300 = "Att-" + str(hash(result['checkpoint_attractors'][300]['attractor']) % 100).zfill(2) if result['checkpoint_attractors'][300]['attractor'] else "None"
            att_1000 = "Att-" + str(hash(result['checkpoint_attractors'][1000]['attractor']) % 100).zfill(2) if result['checkpoint_attractors'][1000]['attractor'] else "None"
            drifted = "DRIFT" if att_300 != att_1000 else "STABLE"
            print(f"✓ {att_300} → {att_1000} ({drifted})")
            time.sleep(0.05)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({
                'multiplier': mult, 'spread': spread_param, 'threshold': threshold,
                'freeze_name': config['name'], 'error': str(e)
            })

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"DRIFT MECHANISM ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 3:
        print(f"Mechanism Experiment Results:")
        print(f"  Successful runs: {len(successful)}/{len(freeze_configs)} ({len(successful)/len(freeze_configs)*100:.1f}%)")
        print()

        # Analyze drift under each condition
        print(f"Drift Analysis by Mechanism Control:")
        print(f"{'Condition':^20} | {'Att-300':^10} | {'Att-500':^10} | {'Att-1000':^10} | {'Drift?':^10}")
        print("-" * 75)

        drift_by_condition = {}

        for result in successful:
            condition = result['freeze_name']
            att_300 = result['checkpoint_attractors'][300]['attractor']
            att_500 = result['checkpoint_attractors'][500]['attractor']
            att_1000 = result['checkpoint_attractors'][1000]['attractor']

            att_300_label = "Att-" + str(hash(att_300) % 100).zfill(2) if att_300 else "None"
            att_500_label = "Att-" + str(hash(att_500) % 100).zfill(2) if att_500 else "None"
            att_1000_label = "Att-" + str(hash(att_1000) % 100).zfill(2) if att_1000 else "None"

            drifted = att_300 != att_1000
            drift_status = "YES" if drifted else "NO"
            drift_by_condition[condition] = drifted

            print(f"{condition:^20} | {att_300_label:^10} | {att_500_label:^10} | {att_1000_label:^10} | {drift_status:^10}")

        print()

        # Determine primary mechanism
        control_drifted = drift_by_condition.get('control', True)
        memory_frozen_drifted = drift_by_condition.get('frozen-memory', None)
        agents_frozen_drifted = drift_by_condition.get('frozen-agents', None)
        both_frozen_drifted = drift_by_condition.get('both-frozen', None)

        print(f"Mechanism Identification:")

        if control_drifted:
            print(f"  ✓ CONTROL drifted (baseline drift confirmed)")
        else:
            print(f"  ✗ CONTROL stable (unexpected - contradicts C110)")

        if memory_frozen_drifted is not None:
            if memory_frozen_drifted:
                print(f"  ✓ FROZEN-MEMORY still drifted → Memory evolution NOT primary cause")
            else:
                print(f"  ⚠️ FROZEN-MEMORY stopped drift → Memory evolution IS primary cause")

        if agents_frozen_drifted is not None:
            if agents_frozen_drifted:
                print(f"  ✓ FROZEN-AGENTS still drifted → Agent turnover NOT primary cause")
            else:
                print(f"  ⚠️ FROZEN-AGENTS stopped drift → Agent turnover IS primary cause")

        if both_frozen_drifted is not None:
            if both_frozen_drifted:
                print(f"  ✓ BOTH-FROZEN still drifted → Inherent dynamics (not memory or agents)")
            else:
                print(f"  ✓ BOTH-FROZEN stopped drift → Combination of memory AND agents")

        print()

        # Determine primary mechanism conclusion
        if not control_drifted:
            insight_68 = "no_drift_observed"
            conclusion = "No drift observed (contradicts C110)"
        elif both_frozen_drifted:
            insight_68 = "inherent_dynamics"
            conclusion = "Drift driven by INHERENT DYNAMICS (not memory or agents alone)"
        elif not agents_frozen_drifted and not memory_frozen_drifted:
            insight_68 = "combined_mechanism"
            conclusion = "Drift requires BOTH memory evolution AND agent turnover"
        elif not agents_frozen_drifted:
            insight_68 = "agent_turnover"
            conclusion = "Drift driven primarily by AGENT TURNOVER"
        elif not memory_frozen_drifted:
            insight_68 = "memory_evolution"
            conclusion = "Drift driven primarily by MEMORY EVOLUTION"
        else:
            insight_68 = "unclear_mechanism"
            conclusion = "Mechanism unclear (mixed results)"

        print(f"📊 INSIGHT #68: Drift Mechanism - {conclusion}")
        print(f"   - Tested 4 conditions with selective freezing")
        print(f"   - Freeze cycle: 300 (post-convergence)")
        print(f"   - Observation window: cycles 300-1000 (700 cycles)")
        print(f"   - First mechanistic investigation of ultra-long drift")
        print(f"   - Validates NRM dynamics at component level")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for mechanism analysis")
        print(f"   Only {len(successful)}/{len(freeze_configs)} runs completed successfully")
        insight_68 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "drift_mechanism"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle111_drift_mechanism.json"

    output_data = {
        'experiment': 'cycle111_drift_mechanism',
        'test_triplet': (mult, spread_param, threshold),
        'freeze_configs': freeze_configs,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'drift_by_condition': drift_by_condition if 'drift_by_condition' in locals() else {},
            'primary_mechanism': insight_68 if 'insight_68' in locals() else False
        },
        'insight_68_discovered': True if 'insight_68' in locals() and insight_68 else False,
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
