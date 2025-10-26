#!/usr/bin/env python3
"""
Cycle 59: Fast Validation of Thermodynamic Law
Uses simplified cycle execution for faster results.
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine

print("="*80)
print("CYCLE 59: FAST VALIDATION OF THERMODYNAMIC LAW")
print("="*80)
print()

# Create swarm with modified burst threshold
workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
swarm = FractalSwarm(str(workspace))

# Replace with higher threshold
print("Patching burst_threshold: 500 → 750")
swarm.decomposition = DecompositionEngine(burst_threshold=750.0)
print(f"Confirmed: {swarm.decomposition.burst_threshold}")
print()

# Run cycles
cycles = 500
checkpoint_interval = 10
agent_counts = []

print(f"Running {cycles} cycles...")
start_time = time.time()

# Simplified reality metrics for spawning
reality_metrics = {
    'cpu_percent': 30.0,
    'memory_percent': 40.0,
    'disk_percent': 50.0
}

for cycle in range(1, cycles + 1):
    # Spawn agent if below limit
    if len(swarm.agents) < 10:
        swarm.spawn_agent(reality_metrics)

    # Evolve
    swarm.evolve_cycle(delta_time=1.0)

    # Checkpoint
    if cycle % checkpoint_interval == 0:
        agent_counts.append(len(swarm.agents))

        if cycle % 100 == 0:
            elapsed = time.time() - start_time
            states = sorted(set(agent_counts))
            print(f"  Cycle {cycle}/{cycles} - Agents: {len(swarm.agents)}, "
                  f"States: {states}, Time: {elapsed:.1f}s")

end_time = time.time()
duration = end_time - start_time

print(f"\n✅ Complete in {duration:.1f}s")
print()

# Analysis
print("="*80)
print("RESULTS")
print("="*80)

states = sorted(set(agent_counts))
state_counts = Counter(agent_counts)

print(f"\nStates observed: {states}")
print(f"Total unique states: {len(states)}")
print()

has_state_5 = 5 in states
has_state_6 = 6 in states

print("Key Findings:")
print(f"  State 5 appeared: {'✅ YES' if has_state_5 else '❌ NO'}")
print(f"  State 6 appeared: {'⚠️ YES' if has_state_6 else '✅ NO (as predicted)'}")
print()

print("State Frequencies:")
for state in sorted(states):
    count = state_counts[state]
    pct = 100 * count / len(agent_counts)
    print(f"  State {state}: {count}/{len(agent_counts)} ({pct:.1f}%)")
print()

# Validation
valid = has_state_5 and not has_state_6
if valid:
    print("🎉 HYPOTHESIS VALIDATED!")
    print("\nThermodynamic Law Confirmed:")
    print("  max_stable_agents = floor(burst_threshold / avg_agent_energy)")
    print("  burst_threshold=750 → max_stable=5 ✅")
elif has_state_5:
    print("⚠️ State 5 appeared but so did state 6")
    print(f"   Max observed: {max(states)}")
else:
    print("❌ State 5 did not appear")
    print("   Hypothesis needs revision")

print()
print("="*80)

# Save
results = {
    'burst_threshold': 750.0,
    'cycles': cycles,
    'agent_counts': agent_counts,
    'states': states,
    'state_frequencies': dict(state_counts),
    'validated': valid,
    'duration': duration
}

results_dir = Path(__file__).parent / "results" / "validation"
results_dir.mkdir(parents=True, exist_ok=True)
results_file = results_dir / "cycle59_fast_750.json"

with open(results_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved: {results_file}")
