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

def run_simulation(initial_energy: float) -> float:
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 50
    VELOCITY_MAGNITUDE = 5.0
    
    # Neutral Physics (No Starvation/Abundance bias for this test)
    RECHARGE_RATE = 0.00
    COST_SINGLE = 0.00
    COST_CLUSTER = 0.00
    DECOMP_LOW_ENERGY = -100.0 # Disable
    DECOMP_HIGH_ENERGY = 100.0 # Disable
    
    # Probabilistic Composition
    # P(Comp) = 1.0 / (Energy + epsilon)
    # We need to modify the Engine or the Agent to respect this.
    # For this experiment, we will filter candidates manually in the loop.
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}

    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=initial_energy,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    composition_events = 0
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Probabilistic Filter
        # Only agents that "want" to compose are passed to engine
        # Willingness = 1.0 / (Energy + 0.1)
        # Cap at 1.0
        
        willing_agents = []
        for agent in agents:
            willingness = min(1.0, 0.2 / (agent.state.energy + 0.01)) # Adjusted constant
            if random.random() < willingness:
                willing_agents.append(agent)
                
        # 3. Composition
        if len(willing_agents) >= 2:
            new_clusters = comp_engine.compose_all(willing_agents)
            composition_events += len(new_clusters)
            
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
        
        if len(agents) == 0:
            break

    rate = composition_events / CYCLES
    return rate

def run_experiment():
    print("MOG ONLINE: Cycle 1962 - Energy-Composition Probability", flush=True)
    
    energy_levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    results = []
    
    print("Sweeping Energy Levels...", flush=True)
    for e in energy_levels:
        rate = run_simulation(e)
        results.append(rate)
        print(f"Energy {e:.1f} -> Composition Rate {rate:.2f}", flush=True)
        
    # Check trend
    # Correlation coefficient
    corr = np.corrcoef(energy_levels, results)[0, 1]
    print(f"Correlation (Energy vs Rate): {corr:.4f}", flush=True)
    
    if corr < -0.8:
        print("HYPOTHESIS CONFIRMED: Strong Inverse Relationship.", flush=True)
    else:
        print("HYPOTHESIS FAILED.", flush=True)

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
