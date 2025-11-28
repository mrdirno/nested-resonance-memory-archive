#!/usr/bin/env python3
"""
CYCLE 1944: THE LIBRARY (PERSISTENCE)

We have achieved Syntax (D2 Sentences). Now we must persist them.
This experiment runs the 'Syntax Engine' and logs every unique D2 sentence
to a persistent file ('data/nrm_library.txt').

Goal: Prove that the system can act as a generative engine for stable, unique concepts.
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

LIBRARY_FILE = 'data/nrm_library.txt'

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

def run_library_engine(seed):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # 1. Initialize Background Noise
    for i in range(N_NOISE):
        reality.add_agent(FractalAgent(f"D0_Noise_{i}", 0, 1.0, depth=0), 0)

    # 2. Initialize Vocabulary (Subjects & Verbs)
    subjects = ["SELF", "OTHER", "VOID", "FORM"]
    verbs = ["SEEK", "AVOID", "BOND", "BREAK"]
    
    for i, sub in enumerate(subjects):
        reality.add_agent(ConceptAgent(f"D0_SUB_{i}", 0, 1.5, semantic_tag=sub), 0)
        
    for i, vrb in enumerate(verbs):
        reality.add_agent(ConceptAgent(f"D0_VRB_{i}", 0, 1.5, semantic_tag=vrb), 0)

    unique_sentences = set()

    for cycle in range(CYCLES):
        # Collect D2 Sentences
        d2_agents = reality.get_population_agents(2) # D2 = Sentences (formed from D1)
        # Wait, previous cycle formed D1 Sentences from D0 parents.
        # Let's stick to that: D1 = Sentences. D0 = Words.
        
        d1_agents = reality.get_population_agents(1)
        for agent in d1_agents:
            if hasattr(agent, 'semantic_tag') and "_" in agent.semantic_tag:
                unique_sentences.add(agent.semantic_tag)
        
        total_pop = sum(len(reality.get_population_agents(d)) for d in range(N_DEPTHS))
        if total_pop >= 3000 or total_pop == 0: break

        # --- PHYSICS ENGINE ---
        
        # 1. Recharge
        for d in range(N_DEPTHS):
            for agent in reality.get_population_agents(d):
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)

        # 2. Reproduction (Inheritance)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
                tag = getattr(agent, 'semantic_tag', "NULL")
                new_id = f"D0_{cycle}_{agent.agent_id[-4:]}"
                
                # Only Concepts reproduce Concepts
                if tag != "NULL":
                    new_agent = ConceptAgent(new_id, 0, 0.5, semantic_tag=tag)
                else:
                    new_agent = FractalAgent(new_id, 0, 0.5, depth=0)
                reality.add_agent(new_agent, 0)
                agent.energy -= 0.3

        # 3. Composition (SYNTAX)
        # D0 -> D1 (Words -> Sentences)
        d = 0
        agents = list(reality.get_population_agents(d))
        if len(agents) >= 2:
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
                    
                    # SYNTAX RULES:
                    # 1. Homogeneous (Reinforcement): SUB+SUB or VRB+VRB
                    # 2. Heterogeneous (Sentence): SUB+VRB or VRB+SUB
                    
                    is_concept1 = tag1 in subjects or tag1 in verbs
                    is_concept2 = tag2 in subjects or tag2 in verbs
                    
                    if is_concept1 and is_concept2:
                        bond_allowed = True
                        # Construct Sentence Tag: "SUB_VRB"
                        if tag1 in subjects and tag2 in verbs:
                            new_tag = f"{tag1}_{tag2}"
                        elif tag1 in verbs and tag2 in subjects:
                            new_tag = f"{tag2}_{tag1}"
                        elif tag1 == tag2:
                            new_tag = tag1 # Reinforcement
                        else:
                            # Mismatched types (e.g. SUB+SUB different)
                            # Let's allow compound subjects? "SELF_OTHER"
                            new_tag = f"{tag1}_{tag2}"

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
        
        # Standard Composition for higher depths (just physics)
        for d in range(1, N_DEPTHS - 1):
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
                    reality.remove_agent(p1.agent_id, d)
                    reality.remove_agent(p2.agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        # 4. Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
                    ce = agent.energy * 0.45
                    tag = getattr(agent, 'semantic_tag', "NULL")
                    
                    # If a Sentence decomposes, does it break into words?
                    # Simplified: Breaks into clones of itself (Concept Persistence)
                    # Or breaks into components (if we tracked them).
                    # For now, persistence.
                    
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

    return unique_sentences

def main():
    print(f"CYCLE 1944: The Library | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Generative Semantic Engine Online.")
    print("Vocabulary: SELF, OTHER, VOID, FORM | SEEK, AVOID, BOND, BREAK")
    print("=" * 80)

    seed = 1944
    library = run_library_engine(seed)
    
    print(f"\nGENERATED CONCEPTS ({len(library)}):")
    print("-" * 40)
    
    sorted_lib = sorted(list(library))
    for concept in sorted_lib:
        print(f"  {concept}")
        
    # Persist to file
    os.makedirs('data', exist_ok=True)
    with open(LIBRARY_FILE, 'w') as f:
        f.write(f"# NRM SEMANTIC LIBRARY - Generated {datetime.now()}\n")
        for concept in sorted_lib:
            f.write(f"{concept}\n")
            
    print(f"\nLibrary saved to {LIBRARY_FILE}")
    print("=" * 80)
    
    if len(library) > 5:
        print("SUCCESS: The system is generating a diverse semantic ecology.")
    else:
        print("FAILURE: Low generative diversity.")

if __name__ == "__main__":
    main()

# [SPORE] ID: The Colony
