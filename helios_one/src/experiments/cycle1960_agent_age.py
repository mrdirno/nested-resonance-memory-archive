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

def run_experiment():
    print("MOG ONLINE: Cycle 1960 - Agent Age", flush=True)
    
    # Parameters
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.02
    COST_SINGLE = 0.10
    COST_CLUSTER = 0.02
    DECOMP_LOW_ENERGY = 0.2 
    DECOMP_HIGH_ENERGY = 4.0 
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}
    birth_cycles: Dict[str, int] = {}

    # Initialize Population
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)
        birth_cycles[agent.agent_id] = 0

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism
        active_agents = []
        newly_released = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            decomposed = False
            if agent.state.depth > 0:
                if agent.state.energy < DECOMP_LOW_ENERGY or agent.state.energy > DECOMP_HIGH_ENERGY:
                    decomposed = True
                    constituents = cluster_registry.pop(agent.agent_id, [])
                    if constituents:
                        for child in constituents:
                            child.state.energy = agent.state.energy / len(constituents)
                            child.state.position = agent.state.position.copy()
                            child.move(np.random.rand(3) * 2.0 - 1.0)
                            newly_released.append(child)

            if not decomposed:
                if agent.is_alive(energy_threshold=0.0):
                    active_agents.append(agent)
        
        agents = active_agents + newly_released
        
        # 3. Composition
        new_clusters = comp_engine.compose_all(agents)
        consumed_ids = set()
        for cluster in new_clusters:
            constituents = []
            for child_id in cluster.state.children_ids:
                found = next((a for a in agents if a.agent_id == child_id), None)
                if found:
                    constituents.append(found)
                    consumed_ids.add(child_id)
            cluster_registry[cluster.agent_id] = constituents
            birth_cycles[cluster.agent_id] = cycle # Track cluster age
            
        agents = [a for a in agents if a.agent_id not in consumed_ids] + new_clusters
        
        if len(agents) == 0:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break

    # Analyze Age
    ages_clustered = []
    ages_single = []
    
    # We need to find Base Agents inside clusters and check their age
    # Base Agents were born at Cycle 0 (mostly).
    # If they are alive, Age = 100.
    
    # Iterate Cluster Registry
    for cluster_id, constituents in cluster_registry.items():
        for child in constituents:
            if child.state.depth == 0:
                age = CYCLES - birth_cycles.get(child.agent_id, 0)
                ages_clustered.append(age)
                
    # Iterate Active Agents (Singles)
    for agent in agents:
        if agent.state.depth == 0:
            age = CYCLES - birth_cycles.get(agent.agent_id, 0)
            ages_single.append(age)
            
    mean_cluster_age = np.mean(ages_clustered) if ages_clustered else 0.0
    mean_single_age = np.mean(ages_single) if ages_single else 0.0
    
    print(f"Mean Age (Clustered): {mean_cluster_age:.2f}", flush=True)
    print(f"Mean Age (Single): {mean_single_age:.2f}", flush=True)
    print(f"Total Survivors: {len(ages_clustered) + len(ages_single)}", flush=True)
    
    if mean_cluster_age > mean_single_age:
        print("HYPOTHESIS CONFIRMED: Clusters enable longevity.", flush=True)
    else:
        print("HYPOTHESIS FAILED.", flush=True)

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
