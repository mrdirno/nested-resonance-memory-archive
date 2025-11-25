#!/usr/bin/env python3
"""
CYCLE 1940: SEMANTIC MASS

Determine the Critical Semantic Mass (N_LOGOS) required for a concept to survive.
Background: 1 LOGOS agent failed.
Test: 3, 5, 7, 10 LOGOS agents against constant 14 Noise agents.
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

def run_semantic_mass_test(seed, n_logos):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # 1. Initialize Background Noise
    for i in range(N_NOISE):
        reality.add_agent(FractalAgent(f"D0_Noise_{i}", 0, 1.0, depth=0), 0)

    # 2. Initialize Semantic Mass
    for i in range(n_logos):
        reality.add_agent(ConceptAgent(f"D0_LOGOS_{i}", 0, 1.5, semantic_tag="LOGOS"), 0)

    logos_history = []

    for cycle in range(CYCLES):
        # Count LOGOS
        all_agents = []
        for d in range(N_DEPTHS):
            all_agents.extend(reality.get_population_agents(d))
        
        logos_count = sum(1 for a in all_agents if getattr(a, 'semantic_tag', 'NULL') == "LOGOS")
        logos_history.append(logos_count)
        
        total_pop = len(all_agents)
        if total_pop >= 3000 or total_pop == 0: break

        # --- PHYSICS ENGINE ---
        
        # 1. Recharge
        for d in range(N_DEPTHS):
            for agent in reality.get_population_agents(d):
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)

        # 2. Reproduction (Strict Inheritance)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
                tag = getattr(agent, 'semantic_tag', "NULL")
                new_id = f"D0_{{cycle}}_{agent.agent_id[-4:]}"
                if tag != "NULL":
                    new_agent = ConceptAgent(new_id, 0, 0.5, semantic_tag=tag)
                else:
                    new_agent = FractalAgent(new_id, 0, 0.5, depth=0)
                reality.add_agent(new_agent, 0)
                agent.energy -= 0.3

        # 3. Composition (Strict Semantic Bonding)
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
                    new_e = (p1.energy + p2.energy) * 0.85
                    tag1 = getattr(p1, 'semantic_tag', "NULL")
                    tag2 = getattr(p2, 'semantic_tag', "NULL")
                    
                    # REINFORCEMENT LOGIC
                    new_tag = "NULL"
                    if tag1 == "LOGOS" and tag2 == "LOGOS":
                        new_tag = "LOGOS"
                    # Noise + Noise = Noise
                    # LOGOS + Noise = Noise (Dilution)

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

        # 4. Decomposition (Fragment Inheritance)
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

    final_pop = len(all_agents)
    final_logos = logos_history[-1]
    
    return {
        'initial': n_logos,
        'final': final_logos,
        'survival': final_logos > 0,
        'dominance': final_logos / final_pop if final_pop > 0 else 0
    }

def main():
    print(f"CYCLE 1940: Semantic Mass | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing Critical Semantic Mass against 14 Noise Agents.")
    print("=" * 80)

    test_cases = [1, 3, 5, 7, 10]
    seeds = [1940, 1941, 1942] # 3 runs per case for robustness

    print(f"\n{'Init LOGOS':>12} | {'Avg Final':>10} | {'Survival %':>10} | {'Dominance %':>12}")
    print("-" * 52)

    results = {}
    for n in test_cases:
        batch = [run_semantic_mass_test(s, n) for s in seeds]
        avg_final = np.mean([r['final'] for r in batch])
        survival_rate = np.mean([r['survival'] for r in batch]) * 100
        dominance = np.mean([r['dominance'] for r in batch]) * 100
        
        results[n] = (survival_rate, dominance)
        print(f"{n:>12} | {avg_final:>10.1f} | {survival_rate:>9.0f}% | {dominance:>11.1f}%")

    print(f"\n{'=' * 80}")
    print("ANALYSIS")
    print("=" * 80)

    critical_mass = next((n for n in test_cases if results[n][0] > 50), None)
    
    print(f"Critical Semantic Mass: {critical_mass if critical_mass else '> 10'}")
    
    if critical_mass:
        print(f"At N={critical_mass}, concepts survive and propagate.")
    else:
        print("Even N=10 is insufficient against N=14 Noise.")
        
    print("\nImplication: Concepts need to start with near-parity to Noise to survive.")

if __name__ == "__main__":
    main()
