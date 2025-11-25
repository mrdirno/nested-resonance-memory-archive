
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional, Set
from dataclasses import asdict

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2073_the_ledger import LedgerAgent, LedgerCompositionEngine, run_simulation as run_base_simulation

# --- GOSSIP AGENT ---
class GossipAgent(LedgerAgent):
    def share_memory(self, other_agent: 'GossipAgent'):
        # Simple Gossip: Additive Update
        # If I know X is bad, I tell you.
        for subject_id, score in self.memory.items():
            current = other_agent.memory.get(subject_id, 0.0)
            # Damping: Don't just double count everything infinitely. 
            # Only update if the new info pushes the score further? 
            # Or just add? Adding creates viral waves. Let's try Adding but capped.
            new_score = current + score
            new_score = max(-5.0, min(5.0, new_score)) # Cap
            other_agent.memory[subject_id] = new_score

# --- SIMULATION ---
def run_gossip_simulation(gossip_enabled: bool) -> float:
    print(f"\n--- Simulation: Gossip {'Enabled' if gossip_enabled else 'Disabled'} ---", flush=True)
    
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    GOSSIP_RADIUS = 30.0 # Can shout further than they can cluster? 
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

        # 2. GOSSIP PHASE
        if gossip_enabled:
            # Naive N^2 is fine for N=100
            for i in range(len(agents)):
                for j in range(i + 1, len(agents)):
                    a1 = agents[i]
                    a2 = agents[j]
                    # Only gossip if active (singles or clusters, doesn't matter, info travels)
                    # But conceptually, do clusters gossip with passing strangers? Yes.
                    dist = np.linalg.norm(a1.state.position - a2.state.position)
                    if dist < GOSSIP_RADIUS:
                        if isinstance(a1, GossipAgent) and isinstance(a2, GossipAgent):
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
        
        # 4. PGG & Memory Update
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
            
            # Metabolism & Lifecycle
            cost = COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                surviving = [c for c in constituents if (c.update_energy(RECHARGE_RATE - cost) or True) and c.state.energy > 0]
                cluster_registry[agent.agent_id] = surviving
                
                if not surviving: pass 
                elif len(surviving) == 1: newly_released.extend(surviving)
                else: active_agents.append(agent)
            else:
                if agent.state.energy > 0: active_agents.append(agent)
        
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
    print("MOG ONLINE: Cycle 2074 - The Reputation Network", flush=True)
    
    # Baseline (Memory only, no gossip - approx from C2073)
    # Actually run with Gossip=False is basically C2073
    frac_control = run_gossip_simulation(gossip_enabled=False)
    
    # Treatment
    frac_treatment = run_gossip_simulation(gossip_enabled=True)
    
    if frac_treatment > frac_control:
        print(f"SUCCESS: Gossip increased cooperation ({frac_treatment:.2f} vs {frac_control:.2f})", flush=True)
    else:
        print(f"FAILURE: Gossip did not help ({frac_treatment:.2f} vs {frac_control:.2f})", flush=True)

if __name__ == "__main__":
    run_experiment()
