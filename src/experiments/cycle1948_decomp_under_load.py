
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
    print("MOG ONLINE: Cycle 1948 - Decomposition Under Load")
    
    # Parameters
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    RECHARGE_RATE = 0.05
    METABOLIC_COST = 0.01
    VELOCITY_MAGNITUDE = 5.0
    
    # Thresholds
    DECOMP_LOW_ENERGY = 0.2  # Starvation -> Dissolve
    DECOMP_HIGH_ENERGY = 4.0 # Burst -> Dissolve
    
    # Registry to hold "dormant" constituents inside clusters
    # Map Cluster ID -> List[FractalAgent]
    cluster_registry: Dict[str, List[FractalAgent]] = {}

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

    print(f"Initialized {len(agents)} agents.")
    print(f"Decomp Thresholds: <{DECOMP_LOW_ENERGY} (Starve), >{DECOMP_HIGH_ENERGY} (Burst)")

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism & Recharge
        active_agents = []
        # List for decomposition products
        newly_released = []

        for agent in agents:
            # Flat metabolic cost (Cluster advantage: pays same as single agent)
            agent.evolve(delta_time=1.0) 
            agent.update_energy(RECHARGE_RATE)
            
            # DECOMPOSITION CHECK
            decomposed = False
            if agent.state.depth > 0:
                # It is a cluster
                if agent.state.energy < DECOMP_LOW_ENERGY or agent.state.energy > DECOMP_HIGH_ENERGY:
                    decomposed = True
                    # Dissolve!
                    # Retrieve constituents
                    constituents = cluster_registry.pop(agent.agent_id, [])
                    
                    # Distribute remaining energy to constituents?
                    # If bursting (>4.0), they get rich.
                    # If starving (<0.2), they get scraps.
                    
                    if constituents:
                        energy_share = agent.state.energy / len(constituents)
                        for child in constituents:
                            child.state.energy = energy_share
                            child.state.position = agent.state.position.copy() # Released at cluster location
                            # Give them a random kick so they don't instantly re-compose
                            child.move(np.random.rand(3) * 2.0 - 1.0)
                            newly_released.append(child)
                    
                    # print(f"Cycle {cycle}: Cluster {agent.agent_id[:6]} decomposed (E={agent.state.energy:.2f}) into {len(constituents)} agents.")

            if not decomposed:
                if agent.is_alive():
                    active_agents.append(agent)
                else:
                    # Base agent died
                    pass
        
        agents = active_agents + newly_released
        
        # 3. Composition
        new_clusters = comp_engine.compose_all(agents)
        
        # Process new clusters
        clustered_ids = set()
        for cluster in new_clusters:
            # Store constituents in registry
            constituents = []
            for child_id in cluster.state.children_ids:
                # Find the agent object
                # We need to iterate agents to find matches. Inefficient but fine for N=50.
                found = next((a for a in agents if a.agent_id == child_id), None)
                if found:
                    constituents.append(found)
                    clustered_ids.add(child_id)
            
            cluster_registry[cluster.agent_id] = constituents
        
        surviving_agents = [a for a in agents if a.agent_id not in clustered_ids]
        agents = surviving_agents + new_clusters
        
        n_count = len(agents)
        total_pop = n_count + sum(len(v) for v in cluster_registry.values()) # Count constituents inside clusters too

        if n_count == 0:
            print(f"EXTINCTION at Cycle {cycle}")
            break
            
    # Final Stats
    active_count = len(agents)
    dormant_count = sum(len(v) for v in cluster_registry.values())
    print(f"Final Active Agents: {active_count}")
    print(f"Dormant in Clusters: {dormant_count}")
    print(f"Total Biomass: {active_count + dormant_count}")
    
    if active_count > 0:
        print("SURVIVAL CONFIRMED.")
    else:
        print("EXTINCTION CONFIRMED.")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
