#!/usr/bin/env python3
"""
CYCLE 1943: THE FIRST SENTENCE (SYNTAX)

Test if distinct concepts can combine into a higher-order semantic structure.
Seeds: "SUBJECT" (Tag: SUB) and "VERB" (Tag: VRB).
Rule: SUB + VRB = SENTENCE (Tag: SNT).
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

# Supercritical Parameters
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

def run_syntax_test(seed):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # 1. Initialize Background Noise
    for i in range(N_NOISE):
        reality.add_agent(FractalAgent(f"D0_Noise_{i}", 0, 1.0, depth=0), 0)

    # 2. Initialize Grammar Seeds
    # 2 Subjects, 2 Verbs to increase odds
    for i in range(2):
        reality.add_agent(ConceptAgent(f"D0_SUB_{i}", 0, 1.5, semantic_tag="SUB"), 0)
        reality.add_agent(ConceptAgent(f"D0_VRB_{i}", 0, 1.5, semantic_tag="VRB"), 0)

    snt_history = []

    for cycle in range(CYCLES):
        # Count Sentences (D1+)
        snt_count = 0
        all_agents = []
        for d in range(N_DEPTHS):
            all_agents.extend(reality.get_population_agents(d))
            
        snt_count = sum(1 for a in all_agents if getattr(a, 'semantic_tag', 'NULL') == "SNT")
        snt_history.append(snt_count)
        
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
                new_id = f"D0_{{cycle}}_{agent.agent_id[-4:]}"
                if tag != "NULL":
                    new_agent = ConceptAgent(new_id, 0, 0.5, semantic_tag=tag)
                else:
                    new_agent = FractalAgent(new_id, 0, 0.5, depth=0)
                reality.add_agent(new_agent, 0)
                agent.energy -= 0.3

        # 3. Composition (SYNTAX)
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
                    
                    # SYNTAX RULES
                    # 1. Homogeneous Reinforcement (SUB+SUB->SUB, VRB+VRB->VRB)
                    if tag1 == tag2 and tag1 != "NULL":
                        bond_allowed = True
                        new_tag = tag1
                    # 2. Heterogeneous Synthesis (SUB+VRB -> SNT)
                    elif (tag1 == "SUB" and tag2 == "VRB") or (tag1 == "VRB" and tag2 == "SUB"):
                        bond_allowed = True
                        new_tag = "SNT"
                    
                    # Note: Assortative Mating (Segregation) is still active.
                    # Noise cannot bond with Concepts.
                    
                    if bond_allowed:
                        new_e = (p1.energy + p2.energy) * 0.85
                        reality.remove_agent(p1.agent_id, d)
                        reality.remove_agent(p2.agent_id, d)
                        
                        new_id = f"D{{d+1}}_{cycle}"
                        child = ConceptAgent(new_id, d+1, new_e, semantic_tag=new_tag)
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
                    
                    # Decomposing a Sentence returns its parts?
                    # Simplified: Returns two random parts (SUB/VRB) or clones of SNT?
                    # For now: Returns clones of current tag to maintain mass.
                    
                    for j in range(2):
                        new_id = f"D{{d-1}}_{cycle}_{j}"
                        frag = ConceptAgent(new_id, d-1, ce, semantic_tag=tag)
                        reality.add_agent(frag, d-1)
                    reality.remove_agent(agent.agent_id, d)

        # 5. Metabolism
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    return max(snt_history)

def main():
    print(f"CYCLE 1943: The First Sentence | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing Semantic Synthesis: SUB + VRB -> SNT")
    print("=" * 80)

    seeds = list(range(1943001, 1943051)) # 50 seeds
    
    successes = 0
    for s in seeds:
        peak_snt = run_syntax_test(s)
        if peak_snt > 0:
            successes += 1
            
    rate = (successes / len(seeds)) * 100
    
    print(f"\nRESULTS (N={len(seeds)}):")
    print(f"  Syntax Emergence Rate: {rate:.1f}%")
    
    print(f"\n{'=' * 80}")
    print("ANALYSIS")
    print("=" * 80)
    
    if rate > 0:
        print("The system successfully combined distinct concepts into a higher-order structure.")
        print("We have achieved rudimentary grammar.")
    else:
        print("No sentences formed. The resonance barrier might be too high for hetero-bonding.")

if __name__ == "__main__":
    main()
