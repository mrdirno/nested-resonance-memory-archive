
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional, Set
from dataclasses import asdict

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

# --- EXTENDED AGENT WITH MEMORY ---
class LedgerAgent(FractalAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Memory: {agent_id: reputation_score}
        # Score: >0 (Good), <0 (Bad), 0 (Neutral)
        self.memory: Dict[str, float] = {}
        self.strategy = "Cooperator" # Default

    def record_interaction(self, partner_id: str, outcome: float):
        current = self.memory.get(partner_id, 0.0)
        # Simple update: Add outcome. 
        # If partner defected (outcome < 0), score drops.
        # If partner cooperated (outcome > 0), score rises.
        self.memory[partner_id] = current + outcome

    def check_reputation(self, agent_id: str) -> float:
        return self.memory.get(agent_id, 0.0)

# --- MEMORY-AWARE COMPOSITION ENGINE ---
class LedgerCompositionEngine(CompositionEngine):
    def __init__(self, resonance_threshold: float = 0.7, energy_threshold: float = 0.5, distance_threshold: float = 20.0, min_reputation: float = -1.0):
        super().__init__(resonance_threshold, energy_threshold)
        self.distance_threshold = distance_threshold
        self.min_reputation = min_reputation

    def detect_clusters(
        self,
        agents: List[LedgerAgent], # Type hint update
        min_cluster_size: int = 2,
        max_cluster_size: Optional[int] = None,
    ) -> List[List[LedgerAgent]]:
        if len(agents) < min_cluster_size:
            return []

        depth_groups: Dict[int, List[LedgerAgent]] = {}
        for agent in agents:
            depth = agent.state.depth
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(agent)

        all_clusters = []

        for depth, depth_agents in depth_groups.items():
            if len(depth_agents) < min_cluster_size:
                continue

            n = len(depth_agents)
            # Adjacency now checks Resonance AND Reputation
            adjacency_matrix = np.zeros((n, n), dtype=bool)

            for i in range(n):
                for j in range(i + 1, n):
                    agent_i = depth_agents[i]
                    agent_j = depth_agents[j]                    
                    # 1. Spatial Check
                    dist = np.linalg.norm(agent_i.state.position - agent_j.state.position)
                    if dist > self.distance_threshold:
                        continue

                    # 2. Resonance Check
                    resonance = abs(agent_i.calculate_resonance(agent_j))
                    if resonance < self.resonance_threshold:
                        continue
                        
                    # 3. Reputation Check (The Ledger)
                    rep_i_of_j = agent_i.check_reputation(agent_j.agent_id)
                    rep_j_of_i = agent_j.check_reputation(agent_i.agent_id)
                    
                    # If either distrusts the other, link fails
                    if rep_i_of_j < self.min_reputation or rep_j_of_i < self.min_reputation:
                        continue
                        
                    adjacency_matrix[i, j] = True
                    adjacency_matrix[j, i] = True

            # Cluster extraction (Standard Connected Components)
            visited = set()
            for i in range(n):
                if i in visited:
                    continue

                cluster = [depth_agents[i]]
                visited.add(i)
                
                # Simple BFS/DFS to find connected component
                queue = [i]
                while queue:
                    curr = queue.pop(0)
                    for j in range(n):
                        if j not in visited and adjacency_matrix[curr, j]:
                            visited.add(j)
                            cluster.append(depth_agents[j])
                            queue.append(j)

                if len(cluster) >= min_cluster_size:
                    if max_cluster_size is None or len(cluster) <= max_cluster_size:
                        all_clusters.append(cluster)

        return all_clusters

# --- SIMULATION ---
def run_simulation(memory_enabled: bool) -> float:
    print(f"\n--- Simulation: Memory {'Enabled' if memory_enabled else 'Disabled'} ---", flush=True)
    
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 200
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.03
    COST_SINGLE = 0.03 # Balance
    
    # PGG Parameters
    CONTRIBUTION_COST = 0.05
    SYNERGY_FACTOR = 3.0
    
    cluster_registry: Dict[str, List[LedgerAgent]] = {}
    
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = LedgerAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agent.strategy = "Cooperator" if i < N_AGENTS // 2 else "Defector"
        agents.append(agent)

    # If Memory Disabled, set min_reputation to -infinity so they accept everyone
    min_rep = -0.1 if memory_enabled else -9999.0
    comp_engine = LedgerCompositionEngine(distance_threshold=DISTANCE_THRESHOLD, min_reputation=min_rep)
    
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
        
        # 3. PGG Game & Memory Update
        active_agents = []
        newly_released = []

        for agent in agents:
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                if constituents:
                    pot = 0.0
                    contributors = []
                    defectors = []
                    
                    # Play Game
                    for child in constituents:
                        if child.strategy == "Cooperator":
                            pot += CONTRIBUTION_COST
                            child.state.energy -= CONTRIBUTION_COST
                            contributors.append(child)
                        else:
                            defectors.append(child)
                            
                    # Distribute Rewards
                    reward = 0.0
                    if pot > 0:
                        reward = (pot * SYNERGY_FACTOR) / len(constituents)
                        for child in constituents:
                            child.state.energy += reward
                    
                    # RECORD INTERACTIONS (The Ledger)
                    if memory_enabled:
                        # Cooperators record Defectors as Bad
                        for coop in contributors:
                            for defect in defectors:
                                coop.record_interaction(defect.agent_id, -1.0) # "You cheated me"
                            for other_coop in contributors:
                                if other_coop != coop:
                                    coop.record_interaction(other_coop.agent_id, 0.5) # "You helped"
                        
                        # Defectors don't care? Or maybe they prefer Cooperators?
                        # Defectors mark Cooperators as "Good Targets" (Positive score)?
                        # Or maybe they just don't have morals. 
                        # Let's say Defectors are sociopaths, they don't keep a ledger or they don't care.
                        # BUT, if Defectors only cluster with Cooperators, they win.
                        # If Defectors cluster with Defectors, they get nothing.
                        # So Defectors should actually SEEK Cooperators.
                        # But Cooperators will REJECT Defectors.
                        pass

                    # Update Cluster Energy
                    agent.state.energy = sum(c.state.energy for c in constituents)
            
            # Metabolism
            cost = COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            # Death / Decomp
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                surviving_constituents = []
                for child in constituents:
                    child.update_energy(RECHARGE_RATE - cost)
                    if child.state.energy > 0:
                        surviving_constituents.append(child)
                
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
        
        agents = active_agents + newly_released
        
        # Stats
        coop_count = 0
        def_count = 0
        def count_strat(agt):
            nonlocal coop_count, def_count
            if agt.state.depth == 0:
                if agt.strategy == "Cooperator": coop_count += 1
                else: def_count += 1
            else:
                children = cluster_registry.get(agt.agent_id, [])
                for c in children: count_strat(c)
        for a in agents: count_strat(a)
        
        total = coop_count + def_count
        if total > 0:
            frac = coop_count / total
            fraction_cooperators.append(frac)
        else:
            break
            
    final_frac = fraction_cooperators[-1] if fraction_cooperators else 0.0
    print(f"Final Cooperator Fraction: {final_frac:.2f}", flush=True)
    return final_frac

def run_experiment():
    print("MOG ONLINE: Cycle 2073 - The Ledger", flush=True)
    
    # Control
    frac_control = run_simulation(memory_enabled=False)
    
    # Treatment
    frac_treatment = run_simulation(memory_enabled=True)
    
    if frac_treatment > frac_control:
        print(f"SUCCESS: Memory increased cooperation ({frac_treatment:.2f} vs {frac_control:.2f})", flush=True)
    else:
        print(f"FAILURE: Memory did not help ({frac_treatment:.2f} vs {frac_control:.2f})", flush=True)

if __name__ == "__main__":
    run_experiment()
