
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

def get_field_gradient(pos, center=(50, 50)):
    """Fake sensory input: Energy is higher near center."""
    dist = np.linalg.norm(pos[:2] - np.array(center))
    # Signal = 1.0 at center, 0.0 at edge (assuming radius 50)
    signal = max(0.0, 1.0 - dist/70.0) 
    return signal

def calculate_cluster_gradient(cluster_agent: FractalAgent, constituents: List[FractalAgent]) -> np.ndarray:
    """
    Determine gradient direction based on constituent sensor data.
    Vector sum of (Constituent Position - Cluster Center) weighted by Signal.
    """
    if not constituents: return np.zeros(3)
    
    center = cluster_agent.state.position
    weighted_vector = np.zeros(3)
    total_signal = 0.0
    
    for child in constituents:
        # Child Position (Conceptually, they are at 'center' in current physics, 
        # but for this test we need them to have spatial extent.
        # Let's assume they have a 'relative_position' or we use their last known position.
        # In C1967 we just used cluster position.
        # To TEST sensing, we must give them distinct positions.
        
        # Hack: Assign random relative offsets for this test to simulate a 'body'.
        # In a real physics engine, they would maintain relative structure.
        if not hasattr(child, 'relative_pos'):
            child.relative_pos = np.random.rand(3) * 10.0 - 5.0 # +/- 5.0 radius
            child.relative_pos[2] = 0
            
        absolute_pos = center + child.relative_pos
        signal = get_field_gradient(absolute_pos)
        
        # Vector pointing from Center to Child
        direction = child.relative_pos
        
        # We want to move TOWARDS the signal.
        # If child has HIGH signal, we should move towards child?
        # Yes. 
        weighted_vector += direction * signal
        total_signal += signal
        
    if total_signal > 0:
        return weighted_vector / total_signal
    return np.zeros(3)

def run_experiment():
    print("MOG ONLINE: Cycle 2000 - Emergent Sensing", flush=True)
    
    # Create a Cluster
    cluster = FractalAgent(agent_id="Cluster_1", depth=1, position=np.array([20.0, 20.0, 0.0]))
    constituents = []
    for i in range(10):
        c = FractalAgent(agent_id=f"c_{i}", depth=0)
        c.relative_pos = np.random.rand(3) * 10.0 - 5.0 # Body shape
        c.relative_pos[2] = 0
        constituents.append(c)
        
    print(f"Cluster Created at {cluster.state.position} with 10 sensors.", flush=True)
    
    # Target is at (50, 50)
    # Cluster is at (20, 20)
    # Gradient should point roughly (1, 1)
    
    perceived_gradient = calculate_cluster_gradient(cluster, constituents)
    
    # Normalize
    norm = np.linalg.norm(perceived_gradient)
    if norm > 0:
        direction = perceived_gradient / norm
    else:
        direction = np.zeros(3)
        
    print(f"Perceived Gradient Vector: {direction}", flush=True)
    
    # Check alignment with true direction
    true_vector = np.array([50.0, 50.0, 0.0]) - cluster.state.position
    true_dir = true_vector / np.linalg.norm(true_vector)
    
    dot_product = np.dot(direction, true_dir)
    print(f"Alignment (Dot Product): {dot_product:.4f}", flush=True)
    
    if dot_product > 0.5:
        print("SUCCESS: Cluster sensed the gradient correctly.", flush=True)
    else:
        print("FAILURE: Cluster is blind or confused.", flush=True)

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
