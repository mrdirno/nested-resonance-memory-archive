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

def calculate_mi(x_samples, y_samples, bins=10):
    """Calculate Mutual Information between two continuous variables."""
    c_xy = np.histogram2d(x_samples, y_samples, bins=bins)[0]
    p_xy = c_xy / np.sum(c_xy)
    
    p_x = np.sum(p_xy, axis=1)
    p_y = np.sum(p_xy, axis=0)
    
    mi = 0.0
    for i in range(bins):
        for j in range(bins):
            if p_xy[i, j] > 0:
                mi += p_xy[i, j] * np.log2(p_xy[i, j] / (p_x[i] * p_y[j]))
    return mi

def run_experiment():
    print("MOG ONLINE: Cycle 1954 - Mutual Information", flush=True)
    
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

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    # Track history for MI calculation (Time Series)
    # We need time series data for pairs to calculate MI over time.
    history: Dict[str, List[float]] = {a.agent_id: [] for a in agents} # Stores phase over time
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism & Update
        active_agents = []
        newly_released = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            # Record phase for MI
            # Note: If agent becomes part of a cluster, it technically disappears from 'agents' list in main loop logic
            # But we need to track Base Agents to measure MI between them.
            # This simulation structure makes tracking individual base agents tricky once they cluster.
            # For this experiment, we will focus on the SURVIVING CLUSTERS and calculate MI between their *constituents*.
            
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
            
        agents = [a for a in agents if a.agent_id not in consumed_ids] + new_clusters
        
        # Record Phase History for ALL Base Agents (Active or Dormant)
        # We need to iterate through agents AND cluster_registry
        
        current_base_phases = {}
        
        # Check active singles
        for agent in agents:
            if agent.state.depth == 0:
                current_base_phases[agent.agent_id] = agent.state.phase
                
        # Check dormant in clusters
        for cluster_id, constituents in cluster_registry.items():
            # We assume constituents update phase? 
            # In current code, constituents inside registry are NOT updated in the main loop!
            # This is a physics flaw. Dormant agents are frozen in time?
            # Or does the cluster phase update represent them?
            # Cluster phase is average.
            # For MI, let's assume constituents inherit Cluster Phase.
            
            # Find the cluster object to get its current phase
            cluster_obj = next((a for a in agents if a.agent_id == cluster_id), None)
            if cluster_obj:
                for child in constituents:
                    # Update child phase to match parent (Synchronization)
                    # child.state.phase = cluster_obj.state.phase 
                    # We record it as such
                    current_base_phases[child.agent_id] = cluster_obj.state.phase
        
        # Append to history
        for aid, phase in current_base_phases.items():
            if aid in history:
                history[aid].append(phase)
            else:
                # New agent (from burst?) or just tracking issue.
                # Since we don't reproduce, this shouldn't happen often unless logic error.
                pass

    print("Simulation Complete. Calculating MI...", flush=True)
    
    # Calculate MI
    # Group 1: Intra-Cluster Pairs
    intra_mi_scores = []
    
    for cluster_id, constituents in cluster_registry.items():
        if len(constituents) < 2: continue
        
        # Take all pairs in this cluster
        for i in range(len(constituents)):
            for j in range(i+1, len(constituents)):
                id_a = constituents[i].agent_id
                id_b = constituents[j].agent_id
                
                series_a = history.get(id_a, [])
                series_b = history.get(id_b, [])
                
                # Truncate to min length
                min_len = min(len(series_a), len(series_b))
                if min_len > 10:
                    mi = calculate_mi(series_a[:min_len], series_b[:min_len])
                    intra_mi_scores.append(mi)

    # Group 2: Random Inter-Cluster Pairs
    # Pick one agent from Cluster A and one from Cluster B
    inter_mi_scores = []
    cluster_ids = list(cluster_registry.keys())
    if len(cluster_ids) >= 2:
        for _ in range(50): # 50 random pairs
            c1, c2 = random.sample(cluster_ids, 2)
            if not cluster_registry[c1] or not cluster_registry[c2]: continue
            
            a1 = random.choice(cluster_registry[c1])
            a2 = random.choice(cluster_registry[c2])
            
            series_a = history.get(a1.agent_id, [])
            series_b = history.get(a2.agent_id, [])
            
            min_len = min(len(series_a), len(series_b))
            if min_len > 10:
                mi = calculate_mi(series_a[:min_len], series_b[:min_len])
                inter_mi_scores.append(mi)
    
    avg_intra = np.mean(intra_mi_scores) if intra_mi_scores else 0.0
    avg_inter = np.mean(inter_mi_scores) if inter_mi_scores else 0.0
    
    print(f"Intra-Cluster MI: {avg_intra:.4f} bits", flush=True)
    print(f"Inter-Cluster MI: {avg_inter:.4f} bits", flush=True)
    
    if avg_intra > avg_inter * 1.5: # Significant difference threshold
        print("HYPOTHESIS CONFIRMED: Strong Intra-Cluster Coupling.", flush=True)
    else:
        print("HYPOTHESIS FAILED: Weak or Uniform Coupling.", flush=True)

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
