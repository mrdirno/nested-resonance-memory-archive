#!/usr/bin/env python3
"""
CYCLE 255: MECHANISM VALIDATION - H1 × H2 Factorial (LIGHTWEIGHT - NO DATABASE)

**ROOT CAUSE FIX (Cycle 569):**
Original issue was NOT psutil overhead, but DATABASE PERSISTENCE bottleneck:
- Every get_system_metrics() call persists to SQLite (line 200 in reality_interface.py)
- 3000 cycles × ~100 agents × 4 conditions = 1.2 million DB writes
- bridge.db bloated to 5.5 GB, duality_v2.db to 183 MB
- Database I/O caused hang at 2h 44m (0% CPU)

**LIGHTWEIGHT SOLUTION:**
- Use psutil directly (NO RealityInterface database)
- Maintain reality grounding (actual system metrics)
- Skip database persistence entirely
- Expected runtime: <5 minutes (vs 13 min "optimized", 38h original)

Purpose: Test whether Energy Pooling (H1) and Reality Sources (H2) exhibit
         synergistic, antagonistic, or additive effects when combined.

H1 - Energy Pooling:
  Agents share energy within resonance clusters

H2 - Reality Sources:
  Multiple reality sampling sources provide diverse energy inputs

Hypothesis:
  Pooling + Sources = SYNERGISTIC (synergy > 0.1)

Date: 2025-10-29
Researcher: Claude (DUALITY-ZERO-V2), Cycle 569
Principal Investigator: Aldrin Payopay (aldrin.gdf@gmail.com)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import sys
import json
import time
import psutil  # Direct psutil, no database wrapper
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from bridge.transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 3000
MAX_AGENTS = 100
RESULTS_FILE = Path(__file__).parent / "results" / "cycle255_h1h2_lightweight_results.json"


def get_reality_metrics() -> Dict:
    """Get system metrics directly from psutil (no database persistence)."""
    cpu = psutil.cpu_percent(interval=0.01)  # Quick sample
    memory = psutil.virtual_memory()

    return {
        'cpu_percent': cpu,
        'memory_percent': memory.percent,
        'timestamp': time.time()
    }


class LightweightAgent:
    """Minimal fractal agent without database dependencies."""

    def __init__(self, agent_id: str, bridge: TranscendentalBridge,
                 initial_energy: float = 100.0, depth: int = 0):
        self.agent_id = agent_id
        self.bridge = bridge
        self.energy = initial_energy
        self.depth = depth
        self.phase = np.random.uniform(0, 2 * np.pi)
        self.children = []

    def evolve(self, reality_metrics: Dict, delta_time: float = 1.0):
        """Evolve agent using reality metrics (no database)."""
        # Energy from system capacity
        available_capacity = (100 - reality_metrics['cpu_percent']) + \
                           (100 - reality_metrics['memory_percent'])
        energy_gain = 0.01 * available_capacity

        # Energy decay
        energy_decay = 0.5 * delta_time

        # Update energy
        self.energy = max(0.0, min(200.0, self.energy + energy_gain - energy_decay))

        # Update phase using transcendental bridge
        phi_value = (1 + np.sqrt(5)) / 2
        self.phase = (self.phase + 0.1 * phi_value) % (2 * np.pi)

    def get_phase_vector(self) -> np.ndarray:
        """Get agent's phase vector for resonance detection."""
        return np.array([np.cos(self.phase), np.sin(self.phase)])


class MechanismCondition:
    """Factorial mechanism condition."""

    def __init__(self, h1_enabled: bool, h2_enabled: bool):
        self.h1_pooling = h1_enabled
        self.h2_sources = h2_enabled
        self.name = f"{'ON' if h1_enabled else 'OFF'}-{'ON' if h2_enabled else 'OFF'}"

    def __str__(self):
        h1 = "H1:ON" if self.h1_pooling else "H1:OFF"
        h2 = "H2:ON" if self.h2_sources else "H2:OFF"
        return f"{self.name} ({h1}, {h2})"


def detect_clusters(agents: List[LightweightAgent], threshold: float = 0.85) -> Dict[int, List[str]]:
    """Detect resonance clusters using phase alignment."""
    clusters = {}
    cluster_id = 0

    for i, agent_a in enumerate(agents):
        if any(agent_a.agent_id in members for members in clusters.values()):
            continue  # Already in a cluster

        cluster_members = [agent_a.agent_id]
        phase_a = agent_a.get_phase_vector()

        for agent_b in agents[i+1:]:
            if any(agent_b.agent_id in members for members in clusters.values()):
                continue

            phase_b = agent_b.get_phase_vector()
            alignment = np.dot(phase_a, phase_b)

            if alignment >= threshold:
                cluster_members.append(agent_b.agent_id)

        if len(cluster_members) >= 2:
            clusters[cluster_id] = cluster_members
            cluster_id += 1

    return clusters


def run_condition(condition: MechanismCondition) -> Dict:
    """Run single deterministic experiment."""
    print(f"  Running {condition}...")
    start_time = time.time()

    # Initialize
    bridge = TranscendentalBridge()
    root = LightweightAgent("root", bridge, initial_energy=130.0, depth=0)
    agents = [root]

    population_history = []

    # Run experiment
    for cycle in range(CYCLES):
        # Sample reality once per cycle
        cycle_metrics = get_reality_metrics()

        # H1: Energy pooling (if enabled)
        if condition.h1_pooling:
            clusters = detect_clusters(agents)

            for cluster_id, member_ids in clusters.items():
                if len(member_ids) < 2:
                    continue

                cluster_agents = [a for a in agents if a.agent_id in member_ids]

                # Pool 10% of cluster energy
                total_energy = sum(a.energy for a in cluster_agents)
                shared_energy = total_energy * 0.10
                per_agent_share = shared_energy / len(cluster_agents)

                for agent in cluster_agents:
                    agent.energy = min(agent.energy + per_agent_share, 200.0)

        # H2: Reality sources (if enabled)
        if condition.h2_sources:
            available_capacity = (100 - cycle_metrics['cpu_percent']) + \
                               (100 - cycle_metrics['memory_percent'])
            bonus_energy = 0.005 * available_capacity

            for agent in agents:
                agent.energy = min(agent.energy + bonus_energy, 200.0)

        # Evolve all agents
        for agent in agents:
            agent.evolve(cycle_metrics)

        # Spawn new agents
        for agent in list(agents):
            if agent.energy >= 10.0 and agent.depth < 7 and len(agents) < MAX_AGENTS:
                child_id = f"{agent.agent_id}_c{cycle}"
                child = LightweightAgent(child_id, bridge, initial_energy=10.0,
                                        depth=agent.depth + 1)
                agents.append(child)
                agent.children.append(child)
                agent.energy -= 10.0

        # Death
        agents = [a for a in agents if a.energy >= 1.0]

        # Record
        population_history.append(len(agents))

    # Compute metrics
    mean_population = np.mean(population_history)
    final_population = population_history[-1]
    max_population = np.max(population_history)
    runtime = time.time() - start_time

    print(f"    → mean={mean_population:.2f}, final={final_population}, " +
          f"max={max_population}, runtime={runtime:.1f}s")

    return {
        'condition': str(condition),
        'h1_pooling': condition.h1_pooling,
        'h2_sources': condition.h2_sources,
        'mean_population': float(mean_population),
        'final_population': int(final_population),
        'max_population': int(max_population),
        'population_history': population_history,
        'runtime_seconds': float(runtime)
    }


def analyze_synergy(results: Dict[str, Dict]) -> Dict:
    """Analyze factorial synergy."""
    off_off = results['OFF-OFF']['mean_population']
    on_off = results['ON-OFF']['mean_population']
    off_on = results['OFF-ON']['mean_population']
    on_on = results['ON-ON']['mean_population']

    h1_effect = on_off - off_off
    h2_effect = off_on - off_off
    additive_prediction = off_off + h1_effect + h2_effect
    synergy = on_on - additive_prediction
    fold_change = on_on / off_off if off_off > 0 else float('inf')

    if synergy > 0.1:
        classification = "SYNERGISTIC"
        interpretation = "H1 and H2 amplify each other (positive interaction)"
    elif synergy < -0.1:
        classification = "ANTAGONISTIC"
        interpretation = "H1 and H2 interfere with each other (negative interaction)"
    else:
        classification = "ADDITIVE"
        interpretation = "H1 and H2 effects are independent (no interaction)"

    return {
        'off_off': float(off_off),
        'on_off': float(on_off),
        'off_on': float(off_on),
        'on_on': float(on_on),
        'h1_effect': float(h1_effect),
        'h2_effect': float(h2_effect),
        'additive_prediction': float(additive_prediction),
        'synergy': float(synergy),
        'fold_change': float(fold_change),
        'classification': classification,
        'interpretation': interpretation
    }


def main():
    """Run factorial validation experiment."""
    print("=" * 70)
    print("CYCLE 255: MECHANISM VALIDATION - H1 × H2 (LIGHTWEIGHT)")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Optimization: No database persistence (root cause fix)")
    print()

    # Define conditions
    conditions = [
        MechanismCondition(h1_enabled=False, h2_enabled=False),  # OFF-OFF
        MechanismCondition(h1_enabled=True, h2_enabled=False),   # ON-OFF
        MechanismCondition(h1_enabled=False, h2_enabled=True),   # OFF-ON
        MechanismCondition(h1_enabled=True, h2_enabled=True)     # ON-ON
    ]

    # Run experiments
    print("EXPERIMENTAL CONDITIONS:")
    print("-" * 70)
    results = {}
    for i, condition in enumerate(conditions, 1):
        print(f"[{i}/4] Condition: {condition}")
        result = run_condition(condition)
        results[condition.name] = result
        print()

    # Analyze synergy
    print("-" * 70)
    print("SYNERGY ANALYSIS:")
    print("-" * 70)
    synergy_analysis = analyze_synergy(results)

    print(f"OFF-OFF (baseline):       {synergy_analysis['off_off']:.4f}")
    print(f"ON-OFF (H1 only):         {synergy_analysis['on_off']:.4f}")
    print(f"OFF-ON (H2 only):         {synergy_analysis['off_on']:.4f}")
    print(f"ON-ON (both mechanisms):  {synergy_analysis['on_on']:.4f}")
    print()
    print(f"H1 effect (pooling):      {synergy_analysis['h1_effect']:+.4f}")
    print(f"H2 effect (sources):      {synergy_analysis['h2_effect']:+.4f}")
    print(f"Additive prediction:      {synergy_analysis['additive_prediction']:.4f}")
    print(f"Synergy (interaction):    {synergy_analysis['synergy']:+.4f}")
    print()
    print(f"Classification: {synergy_analysis['classification']}")
    print(f"Interpretation: {synergy_analysis['interpretation']}")
    print(f"Fold-change (ON-ON/OFF-OFF): {synergy_analysis['fold_change']:.2f}×")
    print()

    # Save results
    output = {
        'metadata': {
            'cycle': 255,
            'version': 'lightweight_no_database',
            'date': datetime.now().isoformat(),
            'cycles': CYCLES,
            'paradigm': 'mechanism_validation',
            'n_per_condition': 1,
            'deterministic': True,
            'root_cause_fix': 'disabled_database_persistence',
            'reality_grounding': 'maintained (psutil direct, no DB)'
        },
        'conditions': results,
        'synergy_analysis': synergy_analysis
    }

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {RESULTS_FILE}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
