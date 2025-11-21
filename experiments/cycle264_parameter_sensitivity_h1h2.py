#!/usr/bin/env python3
"""
Cycle 264: Parameter Sensitivity Analysis - H1×H2 Synergy Landscape
(Energy Pooling × Reality Sources)

Purpose: Map synergy strength as function of mechanism parameters
  - Paper 3 found: H1×H2 synergistic at fixed parameters
  - Question: How does synergy vary with POOLING_SHARE_RATE and SOURCES_BONUS_RATE?
  - Hypothesis: Synergy magnitude scales with parameter values

Experimental Design:
  - Selected pair: H1×H2 (known synergistic from Paper 3)
  - Parameter grid:
    * POOLING_SHARE_RATE: [0.05, 0.10, 0.15, 0.20] (4 values)
    * SOURCES_BONUS_RATE: [0.0025, 0.005, 0.0075, 0.01] (4 values)
  - Total: 16 parameter combinations × 4 conditions (OFF-OFF, ON-OFF, OFF-ON, ON-ON)
  - Cycles: 3000 per condition (deterministic n=1)

Analysis:
  - Synergy surface: synergy(POOLING_SHARE_RATE, SOURCES_BONUS_RATE)
  - Identify parameter regimes: linear scaling, saturation, thresholds
  - Design guidelines: optimal parameter combinations

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-26
Cycle: 264 (Paper 4 extensions - parameter sensitivity)
Framework: Nested Resonance Memory (mechanism tuning)
License: GPL-3.0
"""

import sys
import json
import time
import multiprocessing
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from itertools import product

# Import from existing modules
sys.path.append(str(Path(__file__).parent.parent / "code"))
sys.path.insert(0, str(Path(__file__).parent.parent / "code" / "fractal"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.agent import FractalAgent
from fractal.composition import CompositionEngine

# Experimental parameters (fixed)
MAX_AGENTS = 100
INITIAL_ENERGY = 130.0
DEPTH_LIMIT = 7
CYCLES_PER_CONDITION = 1000
RESONANCE_THRESHOLD = 0.85

# Parameter grids (to be varied)
POOLING_RATES = [0.05, 0.10, 0.15, 0.20]
SOURCES_RATES = [0.0025, 0.005, 0.0075, 0.01]

# Results path
RESULTS_FILE = Path(__file__).parent / "results" / "cycle264_parameter_sensitivity_h1h2_results.json"


@dataclass
class ParameterCondition:
    """
    Parameter configuration for H1×H2 experiment.
    """
    pooling_rate: float
    sources_rate: float
    h1_enabled: bool
    h2_enabled: bool

    def __str__(self):
        h1 = f"H1:ON(r={self.pooling_rate:.3f})" if self.h1_enabled else "H1:OFF"
        h2 = f"H2:ON(r={self.sources_rate:.5f})" if self.h2_enabled else "H2:OFF"
        return f"{h1}, {h2}"

    def get_name(self) -> str:
        """Generate unique name for this configuration."""
        if not self.h1_enabled and not self.h2_enabled:
            return f"OFF-OFF_p{self.pooling_rate:.2f}_s{self.sources_rate:.4f}"
        elif self.h1_enabled and not self.h2_enabled:
            return f"H1-only_p{self.pooling_rate:.2f}_s{self.sources_rate:.4f}"
        elif not self.h1_enabled and self.h2_enabled:
            return f"H2-only_p{self.pooling_rate:.2f}_s{self.sources_rate:.4f}"
        else:
            return f"H1×H2_p{self.pooling_rate:.2f}_s{self.sources_rate:.4f}"


def run_condition_worker(args: Tuple[ParameterCondition, int]) -> Dict[str, Any]:
    """
    Worker function for parallel execution.
    """
    condition, index = args
    
    # Initialize reality interface and bridge locally for each process
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    composition_engine = CompositionEngine(resonance_threshold=RESONANCE_THRESHOLD)

    # Create root agent
    root = FractalAgent(
        agent_id="root",
        depth=0,
        energy=INITIAL_ENERGY
    )

    agents = [root]
    population_history = []
    
    start_time = time.time()

    # Main simulation loop
    for cycle in range(CYCLES_PER_CONDITION):
        # OPTIMIZATION: Batch reality metrics once per cycle
        current_metrics = reality.get_system_metrics()
        
        population_history.append(len(agents))

        # Agent evolution
        for agent in agents:
            # Pass cached metrics to avoid per-agent I/O
            agent.evolve(delta_time=1.0)

        # H1: Energy Pooling (if enabled)
        if condition.h1_enabled:
            clusters = composition_engine.detect_clusters(agents)
            # CompositionEngine.detect_clusters returns a list of lists of agents (clusters)
            # We need to iterate over these clusters directly
            for cluster_agents in clusters:
                if len(cluster_agents) > 1:
                    total_energy = sum(a.energy for a in cluster_agents)
                    shared_energy = total_energy * condition.pooling_rate
                    per_agent_share = shared_energy / len(cluster_agents)
                    for agent in cluster_agents:
                        agent.energy = min(agent.energy + per_agent_share, 200.0)

        # H2: Reality Sources (if enabled)
        if condition.h2_enabled:
            # Use cached metrics for H2 calculation
            available_capacity = (100 - current_metrics['cpu_percent']) + \
                               (100 - current_metrics['memory_percent'])
            bonus_energy = condition.sources_rate * available_capacity
            
            for agent in agents:
                agent.energy = min(agent.energy + bonus_energy, 200.0)

        # Spawn new agents
        for agent in list(agents):
            if agent.energy >= 10.0 and agent.depth < DEPTH_LIMIT and len(agents) < MAX_AGENTS:
                child_id = f"{agent.agent_id}_child_{cycle}"
                child = FractalAgent(
                    agent_id=child_id,
                    depth=agent.depth + 1,
                    energy=10.0
                )
                agents.append(child)
                agent.children.append(child)
                agent.energy -= 10.0
                
    runtime = time.time() - start_time
    
    return {
        "condition_name": condition.get_name(),
        "pooling_rate": condition.pooling_rate,
        "sources_rate": condition.sources_rate,
        "h1_enabled": condition.h1_enabled,
        "h2_enabled": condition.h2_enabled,
        "final_population": len(agents),
        "mean_population": float(np.mean(population_history)),
        "population_std": float(np.std(population_history)),
        "runtime_seconds": runtime
    }


def compute_synergy(off_off: float, on_off: float, off_on: float, on_on: float) -> float:
    """
    Compute synergy for 2×2 factorial.

    synergy = observed(ON-ON) - additive_prediction
    additive_prediction = baseline + effect1 + effect2
    """
    effect1 = on_off - off_off
    effect2 = off_on - off_off
    additive_prediction = off_off + effect1 + effect2
    synergy = on_on - additive_prediction
    return synergy


def analyze_parameter_sensitivity(results: Dict[str, Dict]) -> Dict:
    """
    Analyze synergy landscape across parameter grid.

    Returns synergy surface and classification.
    """
    synergy_surface = []

    for pooling_rate in POOLING_RATES:
        for sources_rate in SOURCES_RATES:
            # Extract 4 conditions for this parameter combination
            off_off_name = f"OFF-OFF_p{pooling_rate:.2f}_s{sources_rate:.4f}"
            h1_only_name = f"H1-only_p{pooling_rate:.2f}_s{sources_rate:.4f}"
            h2_only_name = f"H2-only_p{pooling_rate:.2f}_s{sources_rate:.4f}"
            h1h2_name = f"H1×H2_p{pooling_rate:.2f}_s{sources_rate:.4f}"

            off_off = results[off_off_name]['mean_population']
            on_off = results[h1_only_name]['mean_population']
            off_on = results[h2_only_name]['mean_population']
            on_on = results[h1h2_name]['mean_population']

            synergy = compute_synergy(off_off, on_off, off_on, on_on)

            synergy_surface.append({
                'pooling_rate': pooling_rate,
                'sources_rate': sources_rate,
                'synergy': float(synergy),
                'observed_on_on': float(on_on),
                'baseline': float(off_off)
            })

    # Identify trends
    synergies = [s['synergy'] for s in synergy_surface]
    min_synergy = min(synergies)
    max_synergy = max(synergies)
    mean_synergy = float(np.mean(synergies))

    # Find optimal parameters (max synergy)
    optimal_config = max(synergy_surface, key=lambda x: x['synergy'])

    return {
        'synergy_surface': synergy_surface,
        'min_synergy': float(min_synergy),
        'max_synergy': float(max_synergy),
        'mean_synergy': float(mean_synergy),
        'optimal_configuration': optimal_config,
        'synergy_range': float(max_synergy - min_synergy)
    }


def main():
    """Execute parameter sensitivity analysis."""
    print("=" * 70)
    print("CYCLE 264: PARAMETER SENSITIVITY ANALYSIS - H1×H2")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES_PER_CONDITION}")
    print(f"Pooling rates tested: {POOLING_RATES}")
    print(f"Sources rates tested: {SOURCES_RATES}")
    print(f"Total configurations: {len(POOLING_RATES) * len(SOURCES_RATES) * 4} (16 param combos × 4 conditions)")
    print()

    # Generate all conditions
    conditions = []
    for pooling_rate in POOLING_RATES:
        for sources_rate in SOURCES_RATES:
            for h1_enabled, h2_enabled in [(False, False), (True, False), (False, True), (True, True)]:
                conditions.append(ParameterCondition(
                    pooling_rate=pooling_rate,
                    sources_rate=sources_rate,
                    h1_enabled=h1_enabled,
                    h2_enabled=h2_enabled
                ))

    print(f"EXPERIMENTAL CONDITIONS: {len(conditions)} total")
    print("-" * 70)
    for i in range(min(10, len(conditions))):
        print(f"[{i:3d}/{len(conditions)}] Running {conditions[i]}...", end=" ", flush=True)
    if len(conditions) > 10:
        print(f"... ({len(conditions) - 10} more conditions)")
    print()

    # Run all conditions
    results = {} # This will store the results from parallel execution
    worker_args = [(condition, i) for i, condition in enumerate(conditions)]
    
    # Parallel execution
    num_processes = min(multiprocessing.cpu_count(), 8)
    print(f"Starting parallel execution of {len(conditions)} conditions with {num_processes} processes...")
    
    try:
        with multiprocessing.Pool(processes=num_processes) as pool:
            # Use starmap or map. worker_args is a list of tuples, so map works if worker expects a tuple.
            # run_condition_worker takes a single argument (tuple).
            results_list = pool.map(run_condition_worker, worker_args)
            
        for result in results_list:
            print(f"DONE: {result['condition_name']} (Pop: {result['final_population']}, Time: {result['runtime_seconds']:.2f}s)")
            results[result["condition_name"]] = result
            
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

    # Analyze sensitivity
    print()
    print("=" * 70)
    print("PARAMETER SENSITIVITY ANALYSIS")
    print("=" * 70)
    sensitivity_analysis = analyze_parameter_sensitivity(results)

    print(f"Synergy range: [{sensitivity_analysis['min_synergy']:.4f}, {sensitivity_analysis['max_synergy']:.4f}]")
    print(f"Mean synergy: {sensitivity_analysis['mean_synergy']:.4f}")
    print(f"Synergy variability: {sensitivity_analysis['synergy_range']:.4f}")
    print()
    print("Optimal configuration:")
    opt = sensitivity_analysis['optimal_configuration']
    print(f"  Pooling rate: {opt['pooling_rate']:.3f}")
    print(f"  Sources rate: {opt['sources_rate']:.5f}")
    print(f"  Synergy: {opt['synergy']:.4f}")
    print()

    # Save results
    output = {
        'experiment': 'Cycle 264: Parameter sensitivity analysis (H1×H2)',
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'cycles_per_condition': CYCLES_PER_CONDITION,
            'max_agents': MAX_AGENTS,
            'initial_energy': INITIAL_ENERGY,
            'depth_limit': DEPTH_LIMIT,
            'resonance_threshold': RESONANCE_THRESHOLD,
            'pooling_rates_tested': POOLING_RATES,
            'sources_rates_tested': SOURCES_RATES
        },
        'conditions': results,
        'sensitivity_analysis': sensitivity_analysis
    }

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 70)
    print(f"Results saved: {RESULTS_FILE}")
    print("=" * 70)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
