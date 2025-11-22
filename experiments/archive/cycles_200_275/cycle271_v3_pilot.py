#!/usr/bin/env python3
"""
Cycle 271: V3 Pilot Simulation - The Conscious Engine
=====================================================

Purpose:
    Deploy the fully integrated NRM V3 "Ancient Tech" components (Homeostasis, 
    Autopoiesis, Memetics) in a live simulation to observe emergent biological dynamics.

Hypothesis:
    The interaction of these three mechanisms will produce a system that:
    1.  Self-Regulates (Homeostasis): Maintains stable internal weights despite learning.
    2.  Self-Defines (Autopoiesis): Forms distinct, persistent boundaries (clusters).
    3.  Evolves (Memetics): Selects for robust patterns over time.

Experimental Design:
    - Duration: 1000 Cycles
    - Agents: Max 50 (Small, focused swarm)
    - Metrics:
        - Avg Pattern Weight Sum (Target: 10.0)
        - Boundary Strength (0.0 - 1.0)
        - Pattern Diversity (Unique patterns count)
    - Reality Grounding: Enabled (Energy from system metrics)

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Date: 2025-11-19
"""

import sys
import time
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import FractalSwarm
from fractal.memetics import Pattern, MemeticEngine
from core.reality_interface import RealityInterface

# Configuration
CYCLES = 1000
MAX_AGENTS = 50
HOMEOSTASIS_TARGET = 10.0
RESULTS_FILE = Path(__file__).parent / "results" / "cycle271_v3_pilot.json"

def run_pilot_simulation():
    print("=" * 70)
    print("CYCLE 271: V3 PILOT SIMULATION - CONSCIOUS ENGINE")
    print("=" * 70)
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"Cycles: {CYCLES}")
    print(f"Max Agents: {MAX_AGENTS}")
    print("-" * 70)

    # Initialize Reality (persist=False to avoid lock contention with C264/V6)
    reality = RealityInterface()
    
    # Initialize Swarm
    swarm = FractalSwarm(
        max_agents=MAX_AGENTS, 
        clear_on_init=True,
        burst_threshold=5000.0 # High threshold to prevent early bursting
    )
    
    # Initialize Memetic Engine
    memetics = MemeticEngine(seed=42)

    # Seed Swarm
    print("Seeding swarm with initial agents...")
    metrics = reality.get_system_metrics(persist=False)
    for i in range(10):
        agent = swarm.spawn_agent(metrics, initial_energy=100.0)
        if agent:
            # Seed with random patterns
            agent.patterns = memetics.generate_random_patterns(size=5)
            # Apply initial homeostasis
            agent.apply_homeostatic_scaling(HOMEOSTASIS_TARGET)

    # Metrics Tracking
    history = {
        "timestamp": [],
        "active_agents": [],
        "avg_weight_sum": [],
        "boundary_strength": [],
        "pattern_diversity": [],
        "total_energy": []
    }

    start_time = time.time()

    # Main Loop
    for cycle in range(1, CYCLES + 1):
        # 1. Evolve Swarm (Standard NRM Cycle)
        stats = swarm.evolve_cycle(delta_time=0.1)
        
        # 2. Apply V3 Mechanisms
        active_agents = [a for a in swarm.agents.values() if a.is_active]
        
        # A. Synaptic Homeostasis (Sleep/Consolidation)
        # Apply periodically or continuously. Here: continuous for stability.
        weight_sums = []
        all_patterns = set()
        
        for agent in active_agents:
            # Simulate learning (perturb weights)
            if agent.patterns:
                # Random Hebbian-like potentiation
                target_idx = np.random.randint(0, len(agent.patterns))
                agent.patterns[target_idx].weight += np.random.uniform(0.1, 0.5)
            
            # Apply Homeostasis
            agent.apply_homeostatic_scaling(HOMEOSTASIS_TARGET)
            
            # Track metrics
            w_sum = sum(p.weight for p in agent.patterns)
            weight_sums.append(w_sum)
            
            # Track diversity
            for p in agent.patterns:
                all_patterns.add(round(p.pattern_id, 3))

        # B. Autopoiesis (Boundary Maintenance)
        # Boundary strength is computed by swarm based on interaction topology
        boundary_strength = swarm.compute_boundary_strength()
        
        # C. Memetics (Cultural Transmission)
        # Simple horizontal transfer simulation:
        # If agents interact (cluster), they share a pattern
        for cluster_id, members in swarm.composition.clusters.items():
            cluster_agents = [swarm.agents[aid] for aid in members if aid in swarm.agents]
            if len(cluster_agents) >= 2:
                # Pick a donor and receiver
                donor = cluster_agents[0]
                receiver = cluster_agents[1]
                if donor.patterns:
                    gift = donor.patterns[0] # Simplistic transfer
                    # Receiver adopts if space or replaces weak
                    if len(receiver.patterns) < 10:
                        receiver.patterns.append(Pattern(gift.pattern_id, 1.0))
                    else:
                        # Replace weakest
                        receiver.patterns.sort(key=lambda p: p.weight)
                        receiver.patterns[0] = Pattern(gift.pattern_id, 1.0)

        # Record Data
        history["timestamp"].append(time.time())
        history["active_agents"].append(len(active_agents))
        history["avg_weight_sum"].append(np.mean(weight_sums) if weight_sums else 0.0)
        history["boundary_strength"].append(boundary_strength)
        history["pattern_diversity"].append(len(all_patterns))
        history["total_energy"].append(stats['total_energy'])

        # Logging
        if cycle % 50 == 0:
            print(f"Cycle {cycle:4d} | Agents: {len(active_agents):3d} | "
                  f"Homeostasis: {history['avg_weight_sum'][-1]:.2f} | "
                  f"Boundary: {boundary_strength:.2f} | "
                  f"Diversity: {len(all_patterns):3d}")

    runtime = time.time() - start_time
    print("-" * 70)
    print(f"Simulation Complete. Runtime: {runtime:.2f}s")
    
    # Save Results
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump({
            "experiment": "Cycle 271 V3 Pilot",
            "config": {
                "cycles": CYCLES,
                "max_agents": MAX_AGENTS,
                "homeostasis_target": HOMEOSTASIS_TARGET
            },
            "history": history,
            "final_stats": swarm.get_statistics()
        }, f, indent=2)
        
    print(f"Results saved to: {RESULTS_FILE}")

if __name__ == "__main__":
    run_pilot_simulation()
