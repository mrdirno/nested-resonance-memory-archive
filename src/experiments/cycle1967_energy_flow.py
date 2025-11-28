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

def plot_stacked_energy(single_energy, cluster_energy, width=60, height=20):
    """ASCII Stacked Area Chart."""
    if not single_energy: return
    
    total = [s + c for s, c in zip(single_energy, cluster_energy)]
    max_val = max(total) if total else 1.0
    
    print(f"Energy Flow (Single vs Cluster)")
    print(f"Max Energy: {max_val:.2f}")
    print("-" * (width + 2))
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    for col in range(width):
        idx = int(col / width * len(total))
        if idx >= len(total): idx = len(total) - 1
        
        s_val = single_energy[idx]
        c_val = cluster_energy[idx]
        
        s_height = int(s_val / max_val * height)
        c_height = int(c_val / max_val * height)
        
        # Draw Single (Bottom)
        for r in range(s_height):
            grid[height - 1 - r][col] = '.'
            
        # Draw Cluster (Top)
        for r in range(c_height):
            row = height - 1 - s_height - r
            if 0 <= row < height:
                grid[row][col] = '#'
                
    for row in grid:
        print("|" + "".join(row) + "|")
    print("-" * (width + 2))
    print("Legend: '.' = Single, '#' = Cluster")

def run_experiment():
    print("MOG ONLINE: Cycle 1967 - Energy Flow Visualization", flush=True)
    
    # Parameters
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    VELOCITY_MAGNITUDE = 5.0
    
    # Starvation Regime
    RECHARGE_RATE = 0.02
    COST_SINGLE = 0.10
    COST_CLUSTER = 0.02
    DECOMP_LOW_ENERGY = 0.2 
    DECOMP_HIGH_ENERGY = 4.0 
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}

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

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    single_energy_history = []
    cluster_energy_history = []
    
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
        willing_agents = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            willingness = min(1.0, 0.2 / (agent.state.energy + 0.01))
            if random.random() < willingness:
                willing_agents.append(agent)
            
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
        
        surviving_ids = set(a.agent_id for a in active_agents)
        compose_candidates = [a for a in willing_agents if a.agent_id in surviving_ids]
        
        # 3. Composition
        new_clusters = comp_engine.compose_all(compose_candidates)
        
        consumed_ids = set()
        for cluster in new_clusters:
            constituents = []
            for child_id in cluster.state.children_ids:
                found = next((a for a in agents if a.agent_id == child_id), None)
                if found:
                    constituents.append(found)
                    consumed_ids.add(child_id)
            cluster_registry[cluster.agent_id] = constituents
            
        agents = [a for a in active_agents if a.agent_id not in consumed_ids] + new_clusters + newly_released
        
        # 4. Energy Tracking
        e_single = sum(a.state.energy for a in agents if a.state.depth == 0)
        e_cluster = sum(a.state.energy for a in agents if a.state.depth > 0)
        
        single_energy_history.append(e_single)
        cluster_energy_history.append(e_cluster)
        
        if len(agents) == 0:
            break
            
    # Analysis
    plot_stacked_energy(single_energy_history, cluster_energy_history)
    
    final_single = single_energy_history[-1]
    final_cluster = cluster_energy_history[-1]
    total = final_single + final_cluster
    
    ratio = final_cluster / total if total > 0 else 0
    print(f"Final Cluster Energy Ratio: {ratio:.4f}", flush=True)
    
    if ratio > 0.8:
        print("HYPOTHESIS CONFIRMED: Clusters act as Energy Capacitors.", flush=True)
    else:
        print("HYPOTHESIS FAILED.", flush=True)

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
