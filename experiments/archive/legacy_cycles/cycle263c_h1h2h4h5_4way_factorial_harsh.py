#!/usr/bin/env python3
"""
Cycle 263c: 4-Way Factorial Interaction - H1 × H2 × H4 × H5 (HARSH MODE)
(Energy Pooling × Reality Sources × Temporal Regulation × Energy Recovery)

Purpose: Test for emergent 4-way synergy (super-synergy) with HARSH parameters
         to force dependency on mechanisms.

Changes from C263b:
  - Baseline Recharge: 0.5 -> 0.0 (Agents die without H2/H1/H5)
  - Metabolic Rate: 0.2 (Maintained)
  - Reality Scale: 2.0 (Maintained)

Hypothesis: Control condition will collapse (population -> 0). 
            Full condition (H1+H2+H4+H5) will thrive (population > 0).
            This contrast will reveal the synergy.

Experimental Design:
  - 16 conditions (2^4 factorial)
  - Cycles: 3000 per condition
  - Paradigm: Mechanism validation (deterministic, n=1)

Mechanisms:
  - H1 (Pooling): Agents share energy within clusters
  - H2 (Reality): System metrics drive energy recharge
  - H4 (Memory): Recent compositions reduce selection probability (refractory period)
  - H5 (Recovery): Bonus energy after composition

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-18
Cycle: 1412
"""

import sys
import os
import json
import time
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set, Deque
from dataclasses import dataclass
from collections import defaultdict, deque

# Import from existing modules
sys.path.append(str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from code.bridge.transcendental_bridge import TranscendentalBridge
from code.fractal.agent import FractalAgent
from code.fractal.composition import CompositionEngine

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
CYCLES = 3000
INITIAL_POPULATION = 10
MAX_AGENTS = 50
DEPTH_LIMIT = 3

INITIAL_ENERGY = 50.0
METABOLIC_RATE = 0.2          # STRICTER: Was 0.1 (C263) -> 0.2 (C263b/c)
SPAWN_COST = 25.0             # STRICTER: Was 20.0 (C263) -> 25.0 (C263b/c)
SPAWN_THRESHOLD = 40.0        # STRICTER: Was 30.0 (C263) -> 40.0 (C263b/c)

# Mechanism Parameters
POOLING_SHARE_RATE = 0.1      # H1
REALITY_SCALE = 2.0           # STRICTER: Was 5.0 (C263) -> 2.0 (C263b/c)
TAU_MEMORY = 1000             # H4 (Memory window)
RECOVERY_BONUS = 15.0         # H5

RESULTS_FILE = Path(__file__).parent / "results" / "cycle263c_h1h2h4h5_4way_factorial_harsh_results.json"

@dataclass
class Condition:
    h1_pooling: bool
    h2_reality: bool
    h4_memory: bool
    h5_recovery: bool
    
    @property
    def name(self) -> str:
        parts = []
        if self.h1_pooling: parts.append("H1")
        if self.h2_reality: parts.append("H2")
        if self.h4_memory: parts.append("H4")
        if self.h5_recovery: parts.append("H5")
        return "×".join(parts) if parts else "OFF-OFF-OFF-OFF"

# -----------------------------------------------------------------------------
# H4: Memory Tracker
# -----------------------------------------------------------------------------
class MemoryTracker:
    """Track composition history for H4 (Memory-weighted selection)"""
    def __init__(self, tau_memory: float):
        self.tau_memory = tau_memory
        self.history: Dict[str, Deque[int]] = defaultdict(deque)

    def record_composition(self, agent_id: str, cycle: int):
        self.history[agent_id].append(cycle)

    def get_weight(self, agent_id: str, current_cycle: int) -> float:
        # Remove old events
        while self.history[agent_id] and (current_cycle - self.history[agent_id][0] > self.tau_memory):
            self.history[agent_id].popleft()
        
        n_recent = len(self.history[agent_id])
        # Exponential decay: more recent compositions -> lower probability
        return np.exp(-n_recent / 2.0)

# -----------------------------------------------------------------------------
# Simulation Logic
# -----------------------------------------------------------------------------
def run_condition(condition: Condition) -> Dict:
    """Run a single experimental condition."""
    print(f"Running {condition.name}...")
    
    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    composition_engine = CompositionEngine()  # Use defaults, bridge not needed for init
    memory_tracker = MemoryTracker(TAU_MEMORY) if condition.h4_memory else None
    
    # Initialize agents
    agents: List[FractalAgent] = []
    for i in range(INITIAL_POPULATION):
        agent = FractalAgent(
            agent_id=f"root_{i}",
            depth=0,
            energy=INITIAL_ENERGY,
            phase=bridge.reality_to_phase(reality.get_system_metrics()).pi_phase
        )
        # Initialize extra state for H4/H5 tracking if needed
        agent.compositions = 0 
        agents.append(agent)

    population_history = []
    
    start_time = time.time()
    
    for cycle in range(CYCLES):
        # 1. Update Reality & Agents
        metrics = reality.get_system_metrics()
        
        # H2: Reality Sources (if enabled)
        recharge_amount = 0.0
        if condition.h2_reality:
            cpu_factor = (100 - metrics.get('cpu_percent', 50)) / 100.0
            recharge_amount = cpu_factor * REALITY_SCALE
        
        # Evolve agents
        for agent in agents:
            # Manually update phase and energy to avoid FractalAgent.evolve() clamping to 1.0
            agent.update_phase(delta_t=1.0)
            agent.energy -= METABOLIC_RATE
            
            # Apply H2 recharge
            if condition.h2_reality:
                agent.energy = min(agent.energy + recharge_amount, 200.0)
            else:
                # HARSH MODE: No baseline recharge!
                # They must rely on initial energy or other mechanisms (if any apply, though H1/H5 are conditional)
                pass

        # 2. H1: Energy Pooling (if enabled)
        if condition.h1_pooling:
            clusters = composition_engine.detect_clusters(agents)
            for cluster_agents in clusters:
                if len(cluster_agents) > 1:
                    # Energy-conserving pooling: Move towards cluster average
                    avg_energy = sum(a.energy for a in cluster_agents) / len(cluster_agents)
                    for agent in cluster_agents:
                        # New Energy = (1 - Rate) * Own + Rate * Average
                        agent.energy = (1.0 - POOLING_SHARE_RATE) * agent.energy + POOLING_SHARE_RATE * avg_energy

        # 3. Spawning (Composition)
        # H4: Memory-weighted selection vs Random selection
        potential_parents = [a for a in agents if a.energy >= SPAWN_THRESHOLD and a.depth < DEPTH_LIMIT]
        
        if potential_parents and len(agents) < MAX_AGENTS:
            parent = None
            
            if condition.h4_memory:
                # H4: Weighted selection
                weights = [memory_tracker.get_weight(a.agent_id, cycle) for a in potential_parents]
                total_weight = sum(weights)
                if total_weight > 0:
                    probs = [w / total_weight for w in weights]
                    parent = np.random.choice(potential_parents, p=probs)
            else:
                # Baseline: Uniform random
                parent = random.choice(potential_parents)
            
            if parent:
                # Execute spawn
                parent.energy -= SPAWN_COST
                
                # H5: Energy Recovery (if enabled)
                if condition.h5_recovery:
                    parent.energy += RECOVERY_BONUS
                
                # H4: Record event
                if condition.h4_memory:
                    memory_tracker.record_composition(parent.agent_id, cycle)
                
                # Create child
                child_id = f"{parent.agent_id}_c{cycle}"
                child_phase = bridge.reality_to_phase(metrics).pi_phase
                child = FractalAgent(
                    agent_id=child_id,
                    depth=parent.depth + 1,
                    energy=INITIAL_ENERGY,
                    phase=child_phase
                )
                child.compositions = 0
                agents.append(child)

        # 4. Death (Energy depletion)
        agents = [a for a in agents if a.energy > 0]
        
        # Repopulate if extinct? 
        # In HARSH mode, we might want to allow extinction to prove the point.
        # But if we want to measure "mean population", extinction = 0.
        # Let's allow extinction. No rescue.
        
        population_history.append(len(agents))

    elapsed = time.time() - start_time
    mean_pop = np.mean(population_history)
    print(f"  Mean population: {mean_pop:.4f}")
    
    return {
        "condition": condition.name,
        "mean_population": mean_pop,
        "final_population": len(agents),
        "elapsed_time": elapsed,
        "flags": {
            "H1": condition.h1_pooling,
            "H2": condition.h2_reality,
            "H4": condition.h4_memory,
            "H5": condition.h5_recovery
        }
    }

# -----------------------------------------------------------------------------
# Analysis
# -----------------------------------------------------------------------------
def analyze_4way_synergy(results: List[Dict]):
    """Calculate 4-way interaction term."""
    print("\n" + "="*70)
    print("4-WAY SYNERGY ANALYSIS (HARSH)")
    print("="*70)
    
    # Map condition name to outcome (mean population)
    outcomes = {r['condition']: r['mean_population'] for r in results}
    
    # 4-way interaction formula (I_ABCD)
    # I_ABCD = (ABCD - ABC - ABD - ACD - BCD) + (AB + AC + AD + BC + BD + CD) - (A + B + C + D) + Baseline
    # Where terms are outcomes of conditions
    
    # Define terms
    baseline = outcomes.get("OFF-OFF-OFF-OFF", 0)
    
    # Main effects
    h1 = outcomes.get("H1", 0)
    h2 = outcomes.get("H2", 0)
    h4 = outcomes.get("H4", 0)
    h5 = outcomes.get("H5", 0)
    
    # 2-way
    h1h2 = outcomes.get("H1×H2", 0)
    h1h4 = outcomes.get("H1×H4", 0)
    h1h5 = outcomes.get("H1×H5", 0)
    h2h4 = outcomes.get("H2×H4", 0)
    h2h5 = outcomes.get("H2×H5", 0)
    h4h5 = outcomes.get("H4×H5", 0)
    
    # 3-way
    h1h2h4 = outcomes.get("H1×H2×H4", 0)
    h1h2h5 = outcomes.get("H1×H2×H5", 0)
    h1h4h5 = outcomes.get("H1×H4×H5", 0)
    h2h4h5 = outcomes.get("H2×H4×H5", 0)
    
    # 4-way
    full = outcomes.get("H1×H2×H4×H5", 0)
    
    # Calculate interaction
    interaction_4way = (full 
                        - (h1h2h4 + h1h2h5 + h1h4h5 + h2h4h5)
                        + (h1h2 + h1h4 + h1h5 + h2h4 + h2h5 + h4h5)
                        - (h1 + h2 + h4 + h5)
                        + baseline)
    
    print(f"4-way interaction (H1×H2×H4×H5): {interaction_4way:.4f}")
    
    if interaction_4way > 0.5:
        print("Classification: SUPER-SYNERGISTIC (Positive emergent interaction)")
    elif interaction_4way < -0.5:
        print("Classification: INTERFERENCE (Negative emergent interaction)")
    else:
        print("Classification: ADDITIVE (No significant 4-way interaction)")
        
    print(f"Observed Full: {full:.4f}")
    print(f"Observed Baseline: {baseline:.4f}")

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    print("="*70)
    print("CYCLE 263c: 4-WAY FACTORIAL - H1 × H2 × H4 × H5 (HARSH)")
    print("="*70)
    
    # Generate 16 conditions (Gray code order or binary count)
    conditions = []
    for i in range(16):
        h1 = bool(i & 1)
        h2 = bool(i & 2)
        h4 = bool(i & 4)
        h5 = bool(i & 8)
        conditions.append(Condition(h1, h2, h4, h5))
        
    # Sort by complexity (number of active flags)
    conditions.sort(key=lambda c: (c.h1_pooling + c.h2_reality + c.h4_memory + c.h5_recovery))
    
    results = []
    
    for i, cond in enumerate(conditions):
        print(f"\n[{i+1}/16] Condition: {cond.name}")
        result = run_condition(cond)
        results.append(result)
        
    analyze_4way_synergy(results)
    
    # Save results
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Atomic write pattern
    temp_file = RESULTS_FILE.with_suffix('.tmp')
    with open(temp_file, 'w') as f:
        json.dump(results, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    
    temp_file.replace(RESULTS_FILE)
    
    # Force filesystem sync
    if hasattr(os, 'sync'):
        os.sync()
        
    print(f"\nResults saved: {RESULTS_FILE}")

if __name__ == "__main__":
    sys.exit(main())
