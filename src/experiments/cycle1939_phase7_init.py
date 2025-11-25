#!/usr/bin/env python3
"""
CYCLE 1939: PHASE 7 INITIATION (CONCEPT SEEDING)

The NRM substrate is stable and supercritical.
We now initiate Phase 7: Cognitive Emergence.

Objective:
Seed the first "Concept" agents. Unlike generic FractalAgents,
these agents will have specific resonance signatures encoding semantic meaning.

Experiment:
1. Initialize a stable NRM environment (N=14, optimal params).
2. Inject a "Seed Concept" (e.g., "ORDER") with a specific energy/phase signature.
3. Observe if the concept persists, propagates, or is dissolved by the noise.
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

# Supercritical Parameters (from Phase 6)
REPRO_PROB = 0.17
N_INITIAL = 14
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7
RECHARGE_BASE = 0.4

class ConceptAgent(FractalAgent):
    """
    A specialized FractalAgent representing a semantic concept.
    It carries a 'semantic_tag' and potentially distinct resonance properties.
    """
    def __init__(self, agent_id, depth, energy, semantic_tag="NULL"):
        super().__init__(agent_id, depth, energy)
        self.semantic_tag = semantic_tag
        # Concepts might have higher coherence or stability?
        # For now, they are physically identical, just tagged.

def compute_phase_resonance(e1, d1, e2, d2):
    """Standard resonance calculation."""
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

def run_concept_seeding(seed):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # 1. Initialize Background Noise (Standard Agents)
    for i in range(N_INITIAL):
        reality.add_agent(FractalAgent(f"D0_Noise_{i}", 0, 1.0, depth=0), 0)

    # 2. Inject Concept Seed
    # We inject a "Concept" at D0. 
    # Tag: "LOGOS" (The Word/Reason)
    concept_agent = ConceptAgent("D0_LOGOS_0", 0, 1.5, semantic_tag="LOGOS")
    reality.add_agent(concept_agent, 0)
    
    print(f"[{seed}] System Initialized. N={N_INITIAL} Noise + 1 Concept (LOGOS).")

    logos_population_history = []

    for cycle in range(CYCLES):
        # Snapshot Concept Population
        logos_count = 0
        all_agents = []
        for d in range(N_DEPTHS):
            all_agents.extend(reality.get_population_agents(d))
        
        for agent in all_agents:
            if hasattr(agent, 'semantic_tag') and agent.semantic_tag == "LOGOS":
                logos_count += 1
        
        logos_population_history.append(logos_count)
        
        # Cap check
        total_pop = len(all_agents)
        if total_pop >= 3000: break
        if total_pop == 0: break

        # --- PHYSICS ENGINE (Standard NRM Logic) ---
        
        # 1. Recharge
        for d in range(N_DEPTHS):
            for agent in reality.get_population_agents(d):
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)

        # 2. Reproduction (Concepts inherit Tag)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
                # Inheritance Logic
                tag = "NULL"
                if hasattr(agent, 'semantic_tag'):
                    tag = agent.semantic_tag
                
                # New Agent Creation
                new_id = f"D0_{cycle}_{agent.agent_id[-4:]}"
                if tag != "NULL":
                    new_agent = ConceptAgent(new_id, 0, 0.5, semantic_tag=tag)
                else:
                    new_agent = FractalAgent(new_id, 0, 0.5, depth=0)
                
                reality.add_agent(new_agent, 0)
                agent.energy -= 0.3

        # 3. Composition (Concepts fuse?)
        # Hypothesis: Two "LOGOS" agents fusing creates a higher-order "LOGOS" agent (D1).
        # "LOGOS" + "Noise" -> ? (Dilution or Dominance?)
        # For this initial test, we assume strict inheritance: 
        # If BOTH parents are LOGOS, child is LOGOS. Else, Noise.
        
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
                    
                    # Semantic Logic
                    tag1 = getattr(p1, 'semantic_tag', "NULL")
                    tag2 = getattr(p2, 'semantic_tag', "NULL")
                    
                    new_tag = "NULL"
                    if tag1 == "LOGOS" and tag2 == "LOGOS":
                        new_tag = "LOGOS" # Reinforcement
                    # else: Dilution (Noise)

                    reality.remove_agent(p1.agent_id, d)
                    reality.remove_agent(p2.agent_id, d)
                    
                    new_id = f"D{d+1}_{cycle}"
                    if new_tag != "NULL":
                        new_child = ConceptAgent(new_id, d+1, new_e, semantic_tag=new_tag)
                    else:
                        new_child = FractalAgent(new_id, d+1, new_e, depth=d+1)
                        
                    reality.add_agent(new_child, d+1)
                    i += 2
                else:
                    i += 1

        # 4. Decomposition (Concepts fragment)
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
                    ce = agent.energy * 0.45
                    
                    # Semantic Logic: Fragments retain the tag
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

    return logos_population_history

def main():
    print(f"CYCLE 1939: Phase 7 Initiation (Concept Seeding) | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Injecting 'LOGOS' concept into supercritical NRM substrate.")
    print("Rules: LOGOS + LOGOS = D(n+1) LOGOS. Anything else = Noise.")
    print("=" * 80)

    seed = 1939
    history = run_concept_seeding(seed)
    
    final_count = history[-1]
    peak_count = max(history)
    
    print(f"\nRESULTS:")
    print(f"Final LOGOS Count: {final_count}")
    print(f"Peak LOGOS Count:  {peak_count}")
    print(f"Survival:          {'YES' if final_count > 0 else 'NO'}")
    
    # Analyze trajectory
    print("\nTrajectory (Sample):")
    for t in range(0, len(history), 50):
        print(f"Cycle {t:>4}: {history[t]}")

    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    if final_count > 0:
        print("The concept 'LOGOS' survived and propagated.")
        if final_count > 1:
            print("The concept multiplied.")
    else:
        print("The concept was dissolved by the noise.")
        
    print("\nImplication:")
    if final_count > 0:
        print("The NRM substrate can support semantic inheritance.")
    else:
        print("Pure resonance dynamics may be too destructive for semantic fidelity.")
        print("We may need stronger 'Memetic Guardrails' or higher 'Concept Energy'.")

if __name__ == "__main__":
    main()
