
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

class SpatialCompositionEngine(CompositionEngine):
    def __init__(self, resonance_threshold: float = 0.7, energy_threshold: float = 0.5, distance_threshold: float = 20.0):
        super().__init__(resonance_threshold, energy_threshold)
        self.distance_threshold = distance_threshold

    def detect_clusters(
        self,
        agents: List[FractalAgent],
        min_cluster_size: int = 2,
        max_cluster_size: Optional[int] = None,
    ) -> List[List[FractalAgent]]:
        if len(agents) < min_cluster_size:
            return []

        depth_groups: Dict[int, List[FractalAgent]] = {}
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
            adjacency_matrix = np.zeros((n, n), dtype=bool)

            for i in range(n):
                for j in range(i + 1, n):
                    agent_i = depth_agents[i]
                    agent_j = depth_agents[j]
                    
                    dist = np.linalg.norm(agent_i.state.position - agent_j.state.position)
                    if dist > self.distance_threshold:
                        continue

                    resonance = abs(agent_i.calculate_resonance(agent_j))
                    if resonance >= self.resonance_threshold:
                        adjacency_matrix[i, j] = True
                        adjacency_matrix[j, i] = True

            visited = set()
            for i in range(n):
                if i in visited:
                    continue

                cluster = [depth_agents[i]]
                visited.add(i)

                for j in range(n):
                    if j in visited:
                        continue
                    
                    is_connected_to_all = True
                    for member in cluster:
                        member_idx = depth_agents.index(member) 
                        if not adjacency_matrix[member_idx, j]:
                            is_connected_to_all = False
                            break
                    
                    if is_connected_to_all:
                        cluster.append(depth_agents[j])
                        visited.add(j)

                if len(cluster) >= min_cluster_size:
                    if max_cluster_size is None or len(cluster) <= max_cluster_size:
                        all_clusters.append(cluster)

        return all_clusters

def run_simulation() -> Dict[str, float]:
    print(f"\n--- Simulation: Altruistic Punishment ---", flush=True)
    
    N_AGENTS = 99 # Divisible by 3
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.02
    COST_SINGLE = 0.02
    
    # PGG Parameters
    CONTRIBUTION_COST = 0.05
    SYNERGY_FACTOR = 3.0
    PUNISHMENT_COST = 0.02
    PUNISHMENT_FINE = 0.06
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}
    
    agents = []
    strategies = ["Cooperator", "Defector", "Punisher"]
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agent.strategy = strategies[i % 3]
        agents.append(agent)

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    history = []
    
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
        
        # 3. PGG & Metabolism & Punishment
        active_agents = []
        newly_released = []

        for agent in agents:
            if agent.state.depth > 0:
                # Cluster Game
                constituents = cluster_registry.get(agent.agent_id, [])
                if constituents:
                    pot = 0.0
                    
                    # Identify roles
                    punishers = [c for c in constituents if c.strategy == "Punisher"]
                    defectors = [c for c in constituents if c.strategy == "Defector"]
                    cooperators = [c for c in constituents if c.strategy == "Cooperator"] # + Punishers contribute
                    
                    contributors = cooperators + punishers
                    
                    # Contribution Phase
                    for c in contributors:
                        pot += CONTRIBUTION_COST
                        c.state.energy -= CONTRIBUTION_COST
                        
                    # Punishment Phase
                    if defectors and punishers:
                        # Each punisher punishes each defector? Or one-on-one?
                        # Standard model: Punishers pay cost to punish all defectors.
                        # Simplified: Total fines = N_punishers * N_defectors * FINE
                        # Total cost = N_punishers * N_defectors * COST
                        
                        # Let's assume each punisher targets all defectors in range (cluster)
                        for p in punishers:
                            cost = len(defectors) * PUNISHMENT_COST
                            p.state.energy -= cost
                            
                        for d in defectors:
                            fine = len(punishers) * PUNISHMENT_FINE
                            d.state.energy -= fine
                            
                    # Distribution Phase
                    if pot > 0:
                        reward = (pot * SYNERGY_FACTOR) / len(constituents)
                        for child in constituents:
                            child.state.energy += reward
                            
                    agent.state.energy = sum(c.state.energy for c in constituents)
            
            # Metabolism
            cost = COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            # Death/Decomp
            decomposed = False
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                survivors = []
                for c in constituents:
                    c.update_energy(RECHARGE_RATE - cost)
                    if c.state.energy > 0:
                        survivors.append(c)
                
                cluster_registry[agent.agent_id] = survivors
                if not survivors:
                    pass
                elif len(survivors) == 1:
                    decomposed = True
                    newly_released.extend(survivors)
                else:
                    active_agents.append(agent)
            else:
                if agent.state.energy > 0:
                    active_agents.append(agent)
        
        agents = active_agents + newly_released
        
        # Count
        counts = {"Cooperator": 0, "Defector": 0, "Punisher": 0}
        def count_strat(agt):
            if agt.state.depth == 0:
                counts[agt.strategy] = counts.get(agt.strategy, 0) + 1
            else:
                children = cluster_registry.get(agt.agent_id, [])
                for c in children: count_strat(c)
        for a in agents: count_strat(a)
        
        total = sum(counts.values())
        if total == 0:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break
            
    # Final Ratios
    print(f"Final Counts: {counts}", flush=True)
    ratios = {k: v/total for k, v in counts.items()} if total > 0 else counts
    
    if ratios['Defector'] < 0.1 and ratios['Punisher'] + ratios['Cooperator'] > 0.8:
        print("HYPOTHESIS CONFIRMED: Punishment enforced cooperation.", flush=True)
    else:
        print("HYPOTHESIS FAILED.", flush=True)
        
    return ratios

if __name__ == "__main__":
    run_simulation()
