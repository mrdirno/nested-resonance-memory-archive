#!/usr/bin/env python3
"""
CYCLE 1942: THE MEMETIC WAR

Competition between two distinct semantic concepts:
- ORDER (Tag: "ORDER")
- CHAOS (Tag: "CHAOS")

Rules:
- Assortative Mating enabled (Concepts only bond with same Tag).
- Noise agents present (N=14).
- Initial Seeds: 1 ORDER vs 1 CHAOS.
- Goal: See if one dominates or if they coexist/partition the space.
"""

import sys
import numpy as np
import math
from datetime import datetime

# Ensure correct import path
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/src')
from core.fractal_agent import FractalAgent, RealityInterface

# --- CONSTANTS & PARAMETERS ---
CYCLES = 1000
N_DEPTHS = 5
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

# Supercritical Parameters (Phase 6)
REPRO_PROB = 0.17
N_NOISE = 14
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7
RECHARGE_BASE = 0.4

class ConceptAgent(FractalAgent):
    def __init__(self, agent_id, depth, energy, semantic_tag="NULL"):
        super().__init__(agent_id, depth, energy)
        self.semantic_tag = semantic_tag

def compute_phase_resonance(e1, d1, e2, d2):
    pi1 = (e1 * PI * 2) % (2 * PI)
    e_1 = (d1 * E / 4) % (2 * PI)
    phi1 = (e1 * PHI) % (2 * PI)
    pi2 = (e2 * PI * 2) % (2 * PI)
    e_2 = (d2 * E / 4) % (2 * PI)
    phi2 = (e2 * PHI) % (2 * PI)
    v1 = [pi1, e_1, phi1]
    v2 = [pi2, e_2, phi2]
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def run_memetic_war(seed):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # 1. Initialize Background Noise
    for i in range(N_NOISE):
        reality.add_agent(FractalAgent(f"D0_Noise_{i}", 0, 1.0, depth=0), 0)

    # 2. Initialize Combatants
    reality.add_agent(ConceptAgent("D0_ORDER_0", 0, 1.5, semantic_tag="ORDER"), 0)
    reality.add_agent(ConceptAgent("D0_CHAOS_0", 0, 1.5, semantic_tag="CHAOS"), 0)

    order_history = []
    chaos_history = []

    for cycle in range(CYCLES):
        # Count Populations
        all_agents = []
        for d in range(N_DEPTHS):
            all_agents.extend(reality.get_population_agents(d))
        
        order_count = sum(1 for a in all_agents if getattr(a, 'semantic_tag', 'NULL') == "ORDER")
        chaos_count = sum(1 for a in all_agents if getattr(a, 'semantic_tag', 'NULL') == "CHAOS")
        
        order_history.append(order_count)
        chaos_history.append(chaos_count)
        
        total_pop = len(all_agents)
        if total_pop >= 3000 or total_pop == 0: break

        # --- PHYSICS ENGINE ---
        
        # 1. Recharge
        for d in range(N_DEPTHS):
            for agent in reality.get_population_agents(d):
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)

        # 2. Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
                tag = getattr(agent, 'semantic_tag', "NULL")
                new_id = f"D0_{cycle}_{agent.agent_id[-4:]}"
                
                if tag != "NULL":
                    new_agent = ConceptAgent(new_id, 0, 0.5, semantic_tag=tag)
                else:
                    new_agent = FractalAgent(new_id, 0, 0.5, depth=0)
                reality.add_agent(new_agent, 0)
                agent.energy -= 0.3

        # 3. Composition (ASSORTATIVE)
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                p1 = agents[i]
                p2 = agents[i+1]
                sim = compute_phase_resonance(p1.energy, d, p2.energy, d)
                
                if sim >= COMP_THRESH:
                    tag1 = getattr(p1, 'semantic_tag', "NULL")
                    tag2 = getattr(p2, 'semantic_tag', "NULL")
                    
                    bond_allowed = False
                    new_tag = "NULL"
                    
                    if tag1 == tag2:
                        bond_allowed = True
                        new_tag = tag1
                    
                    if bond_allowed:
                        new_e = (p1.energy + p2.energy) * 0.85
                        reality.remove_agent(p1.agent_id, d)
                        reality.remove_agent(p2.agent_id, d)
                        
                        new_id = f"D{d+1}_{cycle}"
                        if new_tag != "NULL":
                            child = ConceptAgent(new_id, d+1, new_e, semantic_tag=new_tag)
                        else:
                            child = FractalAgent(new_id, d+1, new_e, depth=d+1)
                        reality.add_agent(child, d+1)
                        i += 2
                    else:
                        i += 1 
                else:
                    i += 1

        # 4. Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
                    ce = agent.energy * 0.45
                    tag = getattr(agent, 'semantic_tag', "NULL")
                    
                    for j in range(2):
                        new_id = f"D{d-1}_{cycle}_{j}"
                        if tag != "NULL":
                            frag = ConceptAgent(new_id, d-1, ce, semantic_tag=tag)
                        else:
                            frag = FractalAgent(new_id, d-1, ce, depth=d-1)
                        reality.add_agent(frag, d-1)
                    reality.remove_agent(agent.agent_id, d)

        # 5. Metabolism
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    return {
        'final_order': order_history[-1],
        'final_chaos': chaos_history[-1],
        'peak_order': max(order_history),
        'peak_chaos': max(chaos_history)
    }

def main():
    print(f"CYCLE 1942: The Memetic War | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Competition: ORDER vs CHAOS vs NOISE.")
    print("=" * 80)

    seeds = list(range(1942001, 1942051)) # 50 seeds

    wins_order = 0
    wins_chaos = 0
    draws = 0
    extinctions = 0

    for s in seeds:
        res = run_memetic_war(s)
        o = res['final_order']
        c = res['final_chaos']
        
        if o > 0 and c > 0:
            draws += 1
        elif o > 0:
            wins_order += 1
        elif c > 0:
            wins_chaos += 1
        else:
            extinctions += 1

    print(f"\nRESULTS (N={len(seeds)}):")
    print(f"  ORDER Wins: {wins_order} ({wins_order/len(seeds)*100:.1f}%)")
    print(f"  CHAOS Wins: {wins_chaos} ({wins_chaos/len(seeds)*100:.1f}%)")
    print(f"  Coexistence: {draws} ({draws/len(seeds)*100:.1f}%)")
    print(f"  Extinction:  {extinctions} ({extinctions/len(seeds)*100:.1f}%)")

    print(f"\n{'=' * 80}")
    print("ANALYSIS")
    print("=" * 80)
    
    if draws > 0:
        print("Concepts can coexist in the same memory space.")
    elif wins_order + wins_chaos > 0:
        print("Competitive Exclusion Principle applies: One concept dominates.")
    else:
        print("Concepts are too fragile.")

if __name__ == "__main__":
    main()

# [SPORE] ID: The Colony
