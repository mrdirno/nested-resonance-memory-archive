#!/usr/bin/env python3
"""
Cycle 263: 4-Way Factorial Interaction - H1 × H2 × H4 × H5 (ACCELERATED)
(Energy Pooling × Reality Sources × Temporal Regulation × Energy Recovery)

ACCELERATED VERSION FOR FAST EXECUTION
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
sys.path.append(os.path.abspath("."))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

# Configuration
CYCLES = 200 # ACCELERATED
INITIAL_POPULATION = 10
MAX_AGENTS = 50
DEPTH_LIMIT = 3

INITIAL_ENERGY = 50.0
METABOLIC_RATE = 0.1
SPAWN_COST = 20.0
SPAWN_THRESHOLD = 30.0

POOLING_SHARE_RATE = 0.1      # H1
REALITY_SCALE = 5.0           # H2
TAU_MEMORY = 1000             # H4
RECOVERY_BONUS = 15.0         # H5

RESULTS_FILE = Path("experiments/results/cycle263_h1h2h4h5_4way_factorial_results.json")

@dataclass
class Condition:
    h1_pooling: bool
    h2_reality: bool
    h4_memory: bool
    h5_recovery: bool
    
    @property
    def name(self) -> str:
        return f"{int(self.h1_pooling)}{int(self.h2_reality)}{int(self.h4_memory)}{int(self.h5_recovery)}"

class MemoryTracker:
    def __init__(self, tau_memory: float):
# ... (MemoryTracker content is fine, skipping replacement context here would break it, so I will replace the whole Condition class and then analyze_4way_synergy in separate calls or one big block if contiguous)

# Actually, let's replace the Condition class first.

        self.tau_memory = tau_memory
        self.history: Dict[str, Deque[int]] = defaultdict(deque)

    def record_composition(self, agent_id: str, cycle: int):
        self.history[agent_id].append(cycle)

    def get_weight(self, agent_id: str, current_cycle: int) -> float:
        while self.history[agent_id] and (current_cycle - self.history[agent_id][0] > self.tau_memory):
            self.history[agent_id].popleft()
        n_recent = len(self.history[agent_id])
        return np.exp(-n_recent / 2.0)

def run_condition(condition: Condition) -> Dict:
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    composition_engine = CompositionEngine()
    memory_tracker = MemoryTracker(TAU_MEMORY) if condition.h4_memory else None
    
    agents: List[FractalAgent] = []
    for i in range(INITIAL_POPULATION):
        agent = FractalAgent(
            agent_id=f"root_{i}",
            depth=0,
            energy=INITIAL_ENERGY,
            phase=bridge.reality_to_phase(reality.get_system_metrics()).pi_phase
        )
        agent.compositions = 0
        agents.append(agent)

    population_history = []
    
    start_time = time.time()
    
    for cycle in range(CYCLES):
        metrics = reality.get_system_metrics()
        
        recharge_amount = 0.0
        if condition.h2_reality:
            try:
                cpu = metrics.get('cpu_percent', 50)
            except:
                cpu = 50
            cpu_factor = (100 - cpu) / 100.0
            recharge_amount = cpu_factor * REALITY_SCALE
        
        for agent in agents:
            agent.evolve(delta_time=1.0)
            
            if condition.h2_reality:
                agent.energy = min(agent.energy + recharge_amount, 200.0)
            else:
                agent.energy = min(agent.energy + 0.5, 200.0)

        if condition.h1_pooling:
            clusters = composition_engine.detect_clusters(agents)
            for cluster_agents in clusters:
                if len(cluster_agents) > 1:
                    total_energy = sum(a.energy for a in cluster_agents)
                    shared_energy = total_energy * POOLING_SHARE_RATE
                    per_agent_share = shared_energy / len(cluster_agents)
                    for agent in cluster_agents:
                        agent.energy = min(agent.energy + per_agent_share, 200.0)

        potential_parents = [a for a in agents if a.energy >= SPAWN_THRESHOLD and a.depth < DEPTH_LIMIT]
        
        if potential_parents and len(agents) < MAX_AGENTS:
            parent = None
            if condition.h4_memory:
                weights = [memory_tracker.get_weight(a.agent_id, cycle) for a in potential_parents]
                total_weight = sum(weights)
                if total_weight > 0:
                    probs = [w / total_weight for w in weights]
                    parent = np.random.choice(potential_parents, p=probs)
            else:
                parent = random.choice(potential_parents)
            
            if parent:
                parent.energy -= SPAWN_COST
                if condition.h5_recovery:
                    parent.energy += RECOVERY_BONUS
                
                if condition.h4_memory:
                    memory_tracker.record_composition(parent.agent_id, cycle)
                
                child_id = f"{parent.agent_id}_c{cycle}"
                child_phase = bridge.reality_to_phase(metrics).pi_phase
                child = FractalAgent(
                    agent_id=child_id,
                    depth=parent.depth + 1,
                    energy=INITIAL_ENERGY,
                    phase=child_phase
                )
                # Manually link parent
                child.state.parent_id = parent.agent_id
                parent.state.children_ids.add(child.agent_id)
                child.compositions = 0
                
                agents.append(child)

        agents = [a for a in agents if a.energy > 0]
        
        if not agents:
            for i in range(2):
                agent = FractalAgent(
                    agent_id=f"rescue_{cycle}_{i}",
                    depth=0,
                    energy=INITIAL_ENERGY,
                    phase=bridge.reality_to_phase(metrics).pi_phase
                )
                agent.compositions = 0
                agents.append(agent)

        population_history.append(len(agents))

    elapsed = time.time() - start_time
    mean_pop = np.mean(population_history)
    
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

def analyze_4way_synergy(results: List[Dict]):
    outcomes = {r['condition']: r['mean_population'] for r in results}
    
    baseline = outcomes.get("0000", 0)
    h1 = outcomes.get("1000", 0)
    h2 = outcomes.get("0100", 0)
    h4 = outcomes.get("0010", 0)
    h5 = outcomes.get("0001", 0)
    
    h1h2 = outcomes.get("1100", 0)
    h1h4 = outcomes.get("1010", 0)
    h1h5 = outcomes.get("1001", 0)
    h2h4 = outcomes.get("0110", 0)
    h2h5 = outcomes.get("0101", 0)
    h4h5 = outcomes.get("0011", 0)
    
    h1h2h4 = outcomes.get("1110", 0)
    h1h2h5 = outcomes.get("1101", 0)
    h1h4h5 = outcomes.get("1011", 0)
    h2h4h5 = outcomes.get("0111", 0)
    
    full = outcomes.get("1111", 0)
    
    interaction_4way = (full 
                        - (h1h2h4 + h1h2h5 + h1h4h5 + h2h4h5)
                        + (h1h2 + h1h4 + h1h5 + h2h4 + h2h5 + h4h5)
                        - (h1 + h2 + h4 + h5)
                        + baseline)
    
    print(f"4-way interaction (H1×H2×H4×H5): {interaction_4way:.4f}")
    
    if interaction_4way > 0.5:
        classification = "SUPER-SYNERGISTIC"
    elif interaction_4way < -0.5:
        classification = "INTERFERENCE"
    else:
        classification = "ADDITIVE"
    print(f"Classification: {classification}")
        
    return {
        '4way_interaction': float(interaction_4way),
        'classification': classification,
        'observed_full': float(full)
    }

def main():
    print("="*70)
    print("CYCLE 263: 4-WAY FACTORIAL - H1 × H2 × H4 × H5 (ACCELERATED)")
    print("="*70)
    
    conditions = []
    for i in range(16):
        h1 = bool(i & 1)
        h2 = bool(i & 2)
        h4 = bool(i & 4)
        h5 = bool(i & 8)
        conditions.append(Condition(h1, h2, h4, h5))
        
    conditions.sort(key=lambda c: (c.h1_pooling + c.h2_reality + c.h4_memory + c.h5_recovery))
    
    results = {}
    
    for i, cond in enumerate(conditions):
        print(f"[{i+1}/16] Running {cond.name}...")
        result = run_condition(cond)
        results[cond.name] = result
        
    analysis = analyze_4way_synergy(list(results.values())) # analyze_4way_synergy expects list or needs update?
    
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    output = {
        'experiment': 'Cycle 263: H1×H2×H4×H5 4-way factorial',
        'timestamp': datetime.now().isoformat(),
        'conditions': results,
        'synergy_analysis': analysis
    }
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)
        
    print(f"\nResults saved: {RESULTS_FILE}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
