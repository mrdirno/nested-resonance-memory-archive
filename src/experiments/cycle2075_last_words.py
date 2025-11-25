
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional, Set

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2074_gossip_network import GossipAgent, LedgerCompositionEngine, run_gossip_simulation

# --- SIMULATION WITH LAST WORDS ---
def run_last_words_simulation(last_words_enabled: bool) -> float:
    print(f"\n--- Simulation: Last Words {'Enabled' if last_words_enabled else 'Disabled'} ---", flush=True)
    
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    GOSSIP_RADIUS = 30.0
    CYCLES = 200
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.03
    COST_SINGLE = 0.03
    
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

        # 2. GOSSIP PHASE (Standard)
        # Only Singles gossip
        singles = [a for a in agents if a.state.depth == 0 and isinstance(a, GossipAgent)]
        for i in range(len(singles)):
            for j in range(i + 1, len(singles)):
                a1 = singles[i]
                a2 = singles[j]
                dist = np.linalg.norm(a1.state.position - a2.state.position)
                if dist < GOSSIP_RADIUS:
                    a1.share_memory(a2)
                    a2.share_memory(a1)

        # 3. Composition
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
        
        # 4. PGG & Lifecycle
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

                    agent.state.energy = sum(c.state.energy for c in constituents)
            
            # Metabolism
            cost = COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                surviving_constituents = []
                dead_constituents = []
                
                for child in constituents:
                    child.update_energy(RECHARGE_RATE - cost)
                    if child.state.energy > 0:
                        surviving_constituents.append(child)
                    else:
                        dead_constituents.append(child)
                
                # LAST WORDS LOGIC
                if last_words_enabled and dead_constituents:
                    # Dying agents shout to nearby Singles
                    # Who are nearby? We need to check `singles` list calculated earlier (or re-calc)
                    # Optimization: Just grab current singles
                    current_singles = [a for a in active_agents if a.state.depth == 0 and isinstance(a, GossipAgent)]
                    # Wait, `active_agents` isn't fully populated yet. Use `agents` list filtered?
                    # Actually, `agents` list contains current state.
                    # Let's check against ALL agents (if they are GossipAgent)
                    
                    # Locate the cluster position (where the death is happening)
                    death_pos = agent.state.position
                    
                    potential_listeners = [a for a in agents if a.state.depth == 0 and isinstance(a, GossipAgent)]
                    
                    for listener in potential_listeners:
                        dist = np.linalg.norm(listener.state.position - death_pos)
                        if dist < GOSSIP_RADIUS:
                            for dying in dead_constituents:
                                listener.share_memory(dying) # Listener hears the dying words
                
                cluster_registry[agent.agent_id] = surviving_constituents
                
                if not surviving_constituents:
                    pass 
                elif len(surviving_constituents) == 1:
                    newly_released.extend(surviving_constituents)
                else:
                    active_agents.append(agent)
            else:
                if agent.state.energy > 0:
                    active_agents.append(agent)
                # Note: Singles dying don't have "Last Words" implemented here because they don't have
                # "Killers" inside them. They die of natural causes. 
                # Unless they interacted with someone? 
                # Singles don't interact. So they have no new info.
        
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
        else: break
            
    final_frac = fraction_cooperators[-1] if fraction_cooperators else 0.0
    print(f"Final Cooperator Fraction: {final_frac:.2f}", flush=True)
    return final_frac

def run_experiment():
    print("MOG ONLINE: Cycle 2075 - The Witness (Last Words)", flush=True)
    
    frac_control = run_last_words_simulation(last_words_enabled=False)
    frac_treatment = run_last_words_simulation(last_words_enabled=True)
    
    if frac_treatment > frac_control:
        print(f"SUCCESS: Last Words increased cooperation ({frac_treatment:.2f} vs {frac_control:.2f})", flush=True)
    else:
        print(f"FAILURE: Last Words did not help ({frac_treatment:.2f} vs {frac_control:.2f})", flush=True)

if __name__ == "__main__":
    run_experiment()
