#!/usr/bin/env python3
"""
Paper 5A: Parameter Sensitivity Analysis (ACCELERATED)

Accelerated execution of Paper 5A Pilot (2D Sweep).
Varies Resonance Threshold and Frequency to map robustness.

Parameters:
- Resonance Thresholds: [0.70, 0.75, 0.80, 0.85, 0.90]
- Frequencies: [2.0, 2.5, 3.0, 3.5, 4.0]
- Population: 100 (fixed)
- Cycles: 200 (accelerated from 5000)
- Seeds: 1 (accelerated from 10)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
"""

import sys
import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from itertools import product
from dataclasses import dataclass
from typing import Dict, List

# Add root to path
sys.path.append(os.path.abspath("."))

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine
from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge

# Configuration
RESULTS_DIR = Path("experiments/results/paper5a_accel")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CYCLES = 200
POPULATION_SIZE = 100
ENERGY_THRESHOLD = 40.0 # Baseline from plan
SEEDS = [42]

# Parameter Ranges
RESONANCE_THRESHOLDS = [0.70, 0.75, 0.80, 0.85, 0.90]
FREQUENCIES = [2.0, 2.5, 3.0, 3.5, 4.0]

def run_condition(res_threshold: float, frequency: float, seed: int) -> Dict:
    """Run single condition."""
    # Setup
    rng = np.random.default_rng(seed)
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    composition_engine = CompositionEngine(resonance_threshold=res_threshold)
    
    # Agents
    agents = []
    for i in range(POPULATION_SIZE):
        # Initialize with random phase
        agent = FractalAgent(
            agent_id=f"agent_{i}",
            depth=0,
            energy=50.0, # Start with some buffer
            phase=rng.uniform(0, 2*np.pi)
        )
        # Set frequency (velocity)
        agent.state.velocity = 2 * np.pi * frequency
        agents.append(agent)
        
    population_history = []
    cluster_history = []
    
    for cycle in range(CYCLES):
        # Evolve
        for agent in agents:
            # Manual evolve to control frequency/velocity persistence
            # Update phase
            agent.state.phase = (agent.state.phase + agent.state.velocity * 1.0) % (2 * np.pi)
            # Metabolic cost
            agent.update_energy(-0.05)
            # Recharge (baseline)
            agent.update_energy(0.055) # Slight positive net to allow survival
            
        # Composition
        clusters = composition_engine.detect_clusters(agents, min_cluster_size=2)
        
        # Record metrics
        population_history.append(len(agents))
        cluster_history.append(len(clusters))
        
        # Remove dead
        agents = [a for a in agents if a.energy > 0]
        if not agents: break
        
    return {
        'mean_population': float(np.mean(population_history)),
        'mean_clusters': float(np.mean(cluster_history)),
        'final_population': len(agents),
        'survival': len(agents) > 0
    }

def main():
    print("="*70)
    print("PAPER 5A: PARAMETER SENSITIVITY (ACCELERATED 2D SWEEP)")
    print("="*70)
    print(f"Cycles: {CYCLES}, Seeds: {len(SEEDS)}")
    print(f"Resonance Thresholds: {RESONANCE_THRESHOLDS}")
    print(f"Frequencies: {FREQUENCIES}")
    print()
    
    results = {}
    
    total_conditions = len(RESONANCE_THRESHOLDS) * len(FREQUENCIES)
    idx = 0
    
    for res_thresh, freq in product(RESONANCE_THRESHOLDS, FREQUENCIES):
        idx += 1
        cond_name = f"RT{res_thresh:.2f}_F{freq:.1f}"
        print(f"[{idx}/{total_conditions}] Running {cond_name}...")
        
        cond_results = []
        for seed in SEEDS:
            res = run_condition(res_threshold=res_thresh, frequency=freq, seed=seed)
            cond_results.append(res)
            
        # Average over seeds (trivial for 1 seed)
        avg_pop = np.mean([r['mean_population'] for r in cond_results])
        avg_clusters = np.mean([r['mean_clusters'] for r in cond_results])
        survival_rate = np.mean([r['survival'] for r in cond_results])
        
        results[cond_name] = {
            'resonance_threshold': res_thresh,
            'frequency': freq,
            'mean_population': avg_pop,
            'mean_clusters': avg_clusters,
            'survival_rate': survival_rate
        }
        
        print(f"  -> Pop: {avg_pop:.1f}, Clusters: {avg_clusters:.1f}, Survival: {survival_rate:.0%}")

    # Save results
    output_file = RESULTS_DIR / "paper5a_accel_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print()
    print(f"Results saved to {output_file}")
    print("="*70)

if __name__ == "__main__":
    main()
