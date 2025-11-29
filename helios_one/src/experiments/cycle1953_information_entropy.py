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

def get_all_base_positions(agent: FractalAgent, registry: Dict[str, List[FractalAgent]]) -> List[np.ndarray]:
    """Recursively retrieve positions of all base agents (depth 0)."""
    if agent.state.depth == 0:
        return [agent.state.position]
    
    positions = []
    constituents = registry.get(agent.agent_id, [])
    for child in constituents:
        # Constituents in registry might have outdated positions if we don't update them?
        # In current logic, constituents are 'frozen' inside cluster until decomposition.
        # They effectively exist at the cluster's position (conceptually).
        # OR we can say they exist at their last known position.
        # For entropy of the 'System', we should use the Cluster's position for all its constituents 
        # to reflect the physical reality that they are 'bound'. 
        # If we use dispersed positions, we miss the ordering effect of clustering.
        # So: All children take parent's position.
        positions.extend([agent.state.position] * get_base_constituents_count(child, registry))
        
    return positions

def get_base_constituents_count(agent: FractalAgent, registry: Dict[str, List[FractalAgent]]) -> int:
    if agent.state.depth == 0: return 1
    return sum(get_base_constituents_count(c, registry) for c in registry.get(agent.agent_id, []))

def calculate_entropy(positions: List[np.ndarray], grid_size: int = 10, world_size: float = 100.0) -> float:
    if not positions:
        return 0.0
        
    # 2D Histogram
    x = [p[0] for p in positions]
    y = [p[1] for p in positions]
    
    hist, _, _ = np.histogram2d(x, y, bins=grid_size, range=[[0, world_size], [0, world_size]])
    
    # Normalize to probability distribution
    prob = hist / np.sum(hist)
    
    # Filter zero probabilities for log
    prob = prob[prob > 0]
    
    # Shannon Entropy
    entropy = -np.sum(prob * np.log2(prob))
    
    return entropy

def run_experiment():
    print("MOG ONLINE: Cycle 1953 - Information Entropy", flush=True)
    
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
    
    # Calculate Max Entropy (Uniform Distribution)
    # For 10x10 grid, max entropy is log2(100) = 6.64 bits
    max_entropy = np.log2(100)
    print(f"Max Possible Entropy: {max_entropy:.2f} bits", flush=True)
    
    initial_positions = [a.state.position for a in agents]
    h_initial = calculate_entropy(initial_positions)
    print(f"Initial Entropy: {h_initial:.4f} bits", flush=True)
    
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
        
        # 4. Entropy Measurement
        # Get positions of all base agents (using cluster position for constituents)
        all_positions = []
        for agent in agents:
            # If agent is cluster, we add N copies of its position where N is number of constituents
            count = get_base_constituents_count(agent, cluster_registry)
            all_positions.extend([agent.state.position] * count)
            
        if not all_positions:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break
            
        h = calculate_entropy(all_positions)
        
        if cycle % 10 == 0 or cycle == CYCLES-1:
            print(f"Cycle {cycle}: H = {h:.4f} bits (Pop: {len(all_positions)})", flush=True)

    print(f"Final Entropy: {h:.4f} bits", flush=True)
    delta_h = h - h_initial
    print(f"Entropy Change: {delta_h:.4f} bits", flush=True)
    
    if delta_h < -0.5:
        print("ORDER EMERGED.", flush=True)
    else:
        print("NO SIGNIFICANT ORDER.", flush=True)

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
