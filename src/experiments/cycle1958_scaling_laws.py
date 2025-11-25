import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional, Set
from dataclasses import asdict
from scipy import stats

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

def get_base_constituents_count(agent: FractalAgent, registry: Dict[str, List[FractalAgent]]) -> int:
    if agent.state.depth == 0: return 1
    # Check if we have children in registry
    children = registry.get(agent.agent_id, [])
    if not children: return 1 # Fallback if registry missing (shouldn't happen with correct logic)
    
    count = 0
    for child in children:
        count += get_base_constituents_count(child, registry)
    return count

def run_experiment():
    print("MOG ONLINE: Cycle 1958 - Scaling Laws", flush=True)
    
    # Parameters (Scaled Up)
    N_AGENTS = 200
    WORLD_SIZE = 200.0 # Increased to maintain density
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 200
    VELOCITY_MAGNITUDE = 5.0
    
    # Starvation Regime
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
            
        agents = [a for a in agents if a.agent_id not in consumed_ids] + new_clusters
        
        if len(agents) == 0:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break

    # Analyze Cluster Sizes
    sizes = []
    for agent in agents:
        size = get_base_constituents_count(agent, cluster_registry)
        sizes.append(size)
        
    print(f"Final Active Entities: {len(agents)}", flush=True)
    print(f"Sizes: {sorted(sizes, reverse=True)}", flush=True)
    
    # Power Law Fit
    # P(x) ~ x^-alpha => log(P) ~ -alpha * log(x)
    
    # Histogram
    if len(sizes) > 5:
        size_counts = {}
        for s in sizes:
            size_counts[s] = size_counts.get(s, 0) + 1
            
        x = np.array(list(size_counts.keys()))
        y = np.array(list(size_counts.values()))
        
        # Log-Log Regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(np.log(x), np.log(y))
        alpha = -slope
        
        print(f"Power Law Alpha: {alpha:.4f}", flush=True)
        print(f"R-squared: {r_value**2:.4f}", flush=True)
        
        if r_value**2 > 0.8:
            print("CRITICALITY CONFIRMED (Scale-Free).", flush=True)
        else:
            print("DISTRIBUTION NOT POWER LAW.", flush=True)
    else:
        print("INSUFFICIENT DATA for Fit.", flush=True)

if __name__ == "__main__":
    run_experiment()