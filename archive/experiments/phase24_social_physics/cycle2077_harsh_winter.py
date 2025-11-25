
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional, Set

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2076_cluster_eviction import GossipAgent, LedgerCompositionEngine, run_eviction_simulation

# --- SIMULATION WITH HARSH WINTER ---
def run_winter_simulation(eviction_enabled: bool) -> float:
    print(f"\n--- Simulation: Winter (Eviction {'Enabled' if eviction_enabled else 'Disabled'}) ---", flush=True)
    
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 200
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.03
    COST_SINGLE = 0.05 # HARSH WINTER: Singles die (-0.02 net)
    
    CONTRIBUTION_COST = 0.05
    SYNERGY_FACTOR = 3.0
    
    cluster_registry: Dict[str, List[GossipAgent]] = {}
    
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = GossipAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agent.strategy = "Cooperator" if i < N_AGENTS // 2 else "Defector"
        agents.append(agent)

    comp_engine = LedgerCompositionEngine(distance_threshold=DISTANCE_THRESHOLD, min_reputation=-0.1)
    
    fraction_cooperators = []
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Composition
        active_agents = [a for a in agents if a.state.depth == 0]
        candidates = active_agents 
        new_clusters = comp_engine.compose_all(candidates)
        
        consumed_ids = set()
        for cluster in new_clusters:
            constituents = []
            for child_id in cluster.state.children_ids:
                found = next((a for a in agents if a.agent_id == child_id), None)
                if found:
                    constituents.append(found)
                    consumed_ids.add(child_id)
            cluster_registry[cluster.agent_id] = constituents
            
        agents = [a for a in agents if a.agent_id not in consumed_ids] + new_clusters
        
        # 3. PGG, Memory, EVICTION
        active_agents = []
        newly_released = []

        for agent in agents:
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                if constituents:
                    pot = 0.0
                    contributors = []
                    defectors = []
                    
                    for child in constituents:
                        if child.strategy == "Cooperator":
                            pot += CONTRIBUTION_COST
                            child.state.energy -= CONTRIBUTION_COST
                            contributors.append(child)
                        else:
                            defectors.append(child)
                            
                    reward = 0.0
                    if pot > 0:
                        reward = (pot * SYNERGY_FACTOR) / len(constituents)
                        for child in constituents:
                            child.state.energy += reward
                    
                    # Record Interactions
                    for coop in contributors:
                        for defect in defectors:
                            coop.record_interaction(defect.agent_id, -1.0)
                        for other_coop in contributors:
                            if other_coop != coop:
                                coop.record_interaction(other_coop.agent_id, 0.5)

                    # EVICTION LOGIC
                    surviving_constituents = list(constituents) # Copy
                    
                    if eviction_enabled:
                        leavers = []
                        for child in constituents:
                            # Check if I want to stay
                            score = 0.0
                            for other in constituents:
                                if other != child:
                                    score += child.check_reputation(other.agent_id)
                            
                            if score < 0.0: # I hate this group
                                leavers.append(child)
                        
                        for leaver in leavers:
                            if leaver in surviving_constituents:
                                surviving_constituents.remove(leaver)
                                leaver.state.depth = 0 # Reset depth
                                newly_released.append(leaver)

                    # Update Cluster Energy
                    agent.state.energy = sum(c.state.energy for c in surviving_constituents)
                    cluster_registry[agent.agent_id] = surviving_constituents

            # Metabolism
            cost = COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                surviving = []
                for child in constituents:
                    child.update_energy(RECHARGE_RATE - cost)
                    if child.state.energy > 0:
                        surviving.append(child)
                
                cluster_registry[agent.agent_id] = surviving
                
                if not surviving:
                    pass 
                elif len(surviving) == 1:
                    for s in surviving:
                        s.state.depth = 0
                        newly_released.append(s)
                else:
                    active_agents.append(agent)
            else:
                if agent.state.energy > 0:
                    active_agents.append(agent)
        
        agents = active_agents + newly_released
        
        # Stats
        coop = 0; total = 0
        def count(agt):
            nonlocal coop, total
            if agt.state.depth == 0:
                total += 1
                if agt.strategy == "Cooperator": coop += 1
            else:
                for c in cluster_registry.get(agt.agent_id, []): count(c)
        for a in agents: count(a)
        
        if total > 0: fraction_cooperators.append(coop / total)
        else: 
            # print(f"Cycle {cycle}: Extinction")
            break
            
    final_frac = fraction_cooperators[-1] if fraction_cooperators else 0.0
    print(f"Final Cooperator Fraction: {final_frac:.2f}", flush=True)
    return final_frac

def run_experiment():
    print("MOG ONLINE: Cycle 2077 - The Harsh Winter", flush=True)
    
    frac_control = run_winter_simulation(eviction_enabled=False)
    frac_treatment = run_winter_simulation(eviction_enabled=True)
    
    if frac_treatment > frac_control:
        print(f"SUCCESS: Winter + Eviction favored Cooperation ({frac_treatment:.2f} vs {frac_control:.2f})", flush=True)
    else:
        print(f"FAILURE: Defectors still won ({frac_treatment:.2f} vs {frac_control:.2f})", flush=True)

if __name__ == "__main__":
    run_experiment()
