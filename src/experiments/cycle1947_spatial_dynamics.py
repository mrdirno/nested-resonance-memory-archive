
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional
from dataclasses import asdict

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

class SpatialCompositionEngine(CompositionEngine):
    """
    Extension of CompositionEngine that enforces spatial constraints.
    Agents must be within 'distance_threshold' to be considered for clustering.
    """
    def __init__(self, resonance_threshold: float = 0.7, energy_threshold: float = 0.5, distance_threshold: float = 20.0):
        super().__init__(resonance_threshold, energy_threshold)
        self.distance_threshold = distance_threshold

    def detect_clusters(
        self,
        agents: List[FractalAgent],
        min_cluster_size: int = 2,
        max_cluster_size: Optional[int] = None,
    ) -> List[List[FractalAgent]]:
        """
        Detect potential clusters via resonance AND spatial proximity.
        """
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
                    
                    # 1. Spatial Check
                    dist = np.linalg.norm(agent_i.state.position - agent_j.state.position)
                    if dist > self.distance_threshold:
                        continue

                    # 2. Resonance Check
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
    print("MOG ONLINE: Cycle 1947 - Spatial Dynamics Check (Movement)")
    
    # Parameters
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    RECHARGE_RATE = 0.05
    METABOLIC_COST = 0.01
    VELOCITY_MAGNITUDE = 5.0 # High speed to test scattering
    
    # Initialize Population
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0 # 2D plane
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    print(f"Initialized {len(agents)} agents in {WORLD_SIZE}x{WORLD_SIZE} world.")
    print(f"Distance Threshold: {DISTANCE_THRESHOLD}")
    print(f"Velocity: {VELOCITY_MAGNITUDE}")

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    for cycle in range(CYCLES):
        # 1. Movement (Random Walk + Wrap)
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism & Recharge
        active_agents = []
        for agent in agents:
            agent.evolve(delta_time=1.0)
            agent.update_energy(RECHARGE_RATE)
            
            if agent.is_alive():
                active_agents.append(agent)
        
        agents = active_agents
        
        # 3. Composition
        new_clusters = comp_engine.compose_all(agents)
        
        clustered_ids = set()
        for cluster in new_clusters:
            for child_id in cluster.state.children_ids:
                clustered_ids.add(child_id)
        
        surviving_agents = [a for a in agents if a.agent_id not in clustered_ids]
        agents = surviving_agents + new_clusters
        
        # 4. Decomposition
        next_gen = []
        for agent in agents:
            if agent.state.energy > 4.0:
                # Simplified: Pass through for baseline check
                pass
            next_gen.append(agent)
        
        agents = next_gen
        
        n_count = len(agents)
        
        if n_count == 0:
            print(f"EXTINCTION at Cycle {cycle}")
            break
            
    # Final Stats
    print(f"Final Population: {len(agents)}")
    if len(agents) > 0:
        print("SURVIVAL CONFIRMED.")
    else:
        print("EXTINCTION CONFIRMED.")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
