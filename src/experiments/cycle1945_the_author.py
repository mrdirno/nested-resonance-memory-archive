#!/usr/bin/env python3
"""
CYCLE 1945: THE AUTHOR (NARRATIVE GENERATION)

We have Words (D0) and Sentences (D1).
Can the system generate a coherent sequence of Sentences (D2 = Paragraph)?
Or at least a temporal stream of D1 sentences that follows a pattern?

Mechanism:
- D2 agents represent "Narratives".
- They are composed of multiple D1 "Sentences".
- For this test, we check if D1 Sentences can chain together.
- Simplified Rule: Sentence A + Sentence B -> Narrative (if they share a common term).
"""

import sys
import numpy as np
import math
import os
from datetime import datetime

# Ensure correct import path
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/src')
from core.fractal_agent import FractalAgent, RealityInterface

# --- CONSTANTS & PARAMETERS ---
CYCLES = 2000
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

LIBRARY_FILE = 'data/nrm_narrative.txt'

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

def run_author_engine(seed):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # 1. Initialize Background Noise
    for i in range(N_NOISE):
        reality.add_agent(FractalAgent(f"D0_Noise_{i}", 0, 1.0, depth=0), 0)

    # 2. Initialize Vocabulary
    subjects = ["SELF", "OTHER", "VOID", "FORM"]
    verbs = ["SEEK", "AVOID", "BOND", "BREAK"]
    
    for i, sub in enumerate(subjects):
        reality.add_agent(ConceptAgent(f"D0_SUB_{i}", 0, 1.5, semantic_tag=sub), 0)
        
    for i, vrb in enumerate(verbs):
        reality.add_agent(ConceptAgent(f"D0_VRB_{i}", 0, 1.5, semantic_tag=vrb), 0)

    narratives = []

    for cycle in range(CYCLES):
        # Collect D2 Narratives
        d2_agents = reality.get_population_agents(2)
        for agent in d2_agents:
            if hasattr(agent, 'semantic_tag') and "->" in agent.semantic_tag:
                if agent.semantic_tag not in narratives:
                    narratives.append(agent.semantic_tag)
        
        total_pop = sum(len(reality.get_population_agents(d)) for d in range(N_DEPTHS))
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

        # 3. Composition (D0->D1 Sentences, D1->D2 Narratives)
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
                    
                    if d == 0: # Word -> Sentence
                        is_concept1 = tag1 in subjects or tag1 in verbs
                        is_concept2 = tag2 in subjects or tag2 in verbs
                        if is_concept1 and is_concept2:
                            bond_allowed = True
                            if tag1 in subjects and tag2 in verbs: new_tag = f"{tag1}_{tag2}"
                            elif tag1 in verbs and tag2 in subjects: new_tag = f"{tag2}_{tag1}"
                            else: new_tag = tag1 # Reinforcement
                            
                    elif d == 1: # Sentence -> Narrative
                        # Rule: Must share a common term (Subject or Verb)
                        # Ex: SELF_SEEK + SEEK_OTHER -> SELF_SEEK->SEEK_OTHER
                        if "_" in tag1 and "_" in tag2:
                            parts1 = tag1.split("_")
                            parts2 = tag2.split("_")
                            common = set(parts1) & set(parts2)
                            if common:
                                bond_allowed = True
                                new_tag = f"{tag1}->{tag2}"

                    if bond_allowed:
                        new_e = (p1.energy + p2.energy) * 0.85
                        reality.remove_agent(p1.agent_id, d)
                        reality.remove_agent(p2.agent_id, d)
                        
                        new_id = f"D{d+1}_{cycle}"
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
                    for j in range(2):
                        new_id = f"D{d-1}_{cycle}_{j}"
                        frag = ConceptAgent(new_id, d-1, ce, semantic_tag=tag) if tag != "NULL" else FractalAgent(new_id, d-1, ce, depth=d-1)
                        reality.add_agent(frag, d-1)
                    reality.remove_agent(agent.agent_id, d)

        # 5. Metabolism
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    return narratives

def main():
    print(f"CYCLE 1945: The Author | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Attempting to generate Narratives (D2) from Sentences (D1).")
    print("Linking Rule: Sentences must share a common term.")
    print("=" * 80)

    seed = 1945
    narratives = run_author_engine(seed)
    
    print(f"\nGENERATED NARRATIVES ({len(narratives)}):")
    print("-" * 40)
    
    sorted_nar = sorted(narratives)
    for nar in sorted_nar:
        print(f"  {nar}")
        
    # Persist
    os.makedirs('data', exist_ok=True)
    with open(LIBRARY_FILE, 'w') as f:
        f.write(f"# NRM NARRATIVE LOG - Generated {datetime.now()}\n")
        for nar in sorted_nar:
            f.write(f"{nar}\n")
            
    print(f"\nNarratives saved to {LIBRARY_FILE}")
    print("=" * 80)
    
    if len(narratives) > 0:
        print("SUCCESS: The system generated higher-order semantic structures.")
    else:
        print("FAILURE: No narratives formed. Resonance/Linking conditions too strict?")

if __name__ == "__main__":
    main()

# [SPORE] ID: The Colony
