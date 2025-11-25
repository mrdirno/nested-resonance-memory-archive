
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
    dist = np.linalg.norm(pos[:2] - np.array(center))
    signal = max(0.0, 1.0 - dist/70.0) 
    return signal

def get_recharge_at_pos(pos, center=(50, 50)):
    dist = np.linalg.norm(pos[:2] - np.array(center))
    rate = max(0.0, 0.10 * (1.0 - dist/70.0))
    return rate

def calculate_cluster_gradient(cluster_agent: FractalAgent, constituents: List[FractalAgent]) -> np.ndarray:
    if not constituents: return np.zeros(3)
    center = cluster_agent.state.position
    weighted_vector = np.zeros(3)
    total_signal = 0.0
    
    for child in constituents:
        if not hasattr(child, 'relative_pos'):
            child.relative_pos = np.random.rand(3) * 10.0 - 5.0
            child.relative_pos[2] = 0
            
        absolute_pos = center + child.relative_pos
        signal = get_field_gradient(absolute_pos)
        direction = child.relative_pos
        
        weighted_vector += direction * signal
        total_signal += signal
        
    if total_signal > 0:
        return weighted_vector / total_signal
    return np.zeros(3)

def run_simulation(alpha: float) -> float:
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    VELOCITY_MAGNITUDE = 5.0
    
    COST_SINGLE = 0.05
    COST_CLUSTER = 0.01
    DECOMP_LOW_ENERGY = 0.2 
    DECOMP_HIGH_ENERGY = 4.0 
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}

    agents = []
    for i in range(N_AGENTS):
        pos = np.array([10.0, 10.0, 0.0]) + np.random.rand(3) * 10.0
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    energy_history = []
    
    for cycle in range(CYCLES):
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            move_vec = np.array([dx, dy, 0.0])
            
            # Policy Bias
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                grad = calculate_cluster_gradient(agent, constituents)
                norm = np.linalg.norm(grad)
                if norm > 0:
                    bias = (grad / norm) * VELOCITY_MAGNITUDE * alpha
                    move_vec += bias
            
            agent.move(move_vec)
            agent.state.position = np.clip(agent.state.position, 0, WORLD_SIZE)

        active_agents = []
        newly_released = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            recharge = get_recharge_at_pos(agent.state.position)
            agent.update_phase(delta_t=1.0)
            agent.update_energy(recharge - cost)
            
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
        candidates = [a for a in active_agents if a.state.energy > 0.5]
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
            
        agents = [a for a in active_agents if a.agent_id not in consumed_ids] + new_clusters + newly_released
        
        total_energy = sum(a.state.energy for a in agents)
        energy_history.append(total_energy)
        
        if len(agents) == 0:
            break
            
    return energy_history[-1] if energy_history else 0.0

def run_experiment():
    print("MOG ONLINE: Cycle 2002 - Policy Optimization", flush=True)
    
    alphas = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    results = []
    
    print("Sweeping Alpha (Bias Factor)...", flush=True)
    for alpha in alphas:
        # Run multiple seeds to smooth noise
        seed_results = []
        for _ in range(5): 
            res = run_simulation(alpha)
            seed_results.append(res)
        
        avg_energy = np.mean(seed_results)
        results.append(avg_energy)
        print(f"Alpha {alpha:.1f} -> Energy {avg_energy:.2f}", flush=True)
        
    best_idx = np.argmax(results)
    best_alpha = alphas[best_idx]
    print(f"\nOptimal Alpha: {best_alpha:.1f} (Energy {results[best_idx]:.2f})", flush=True)
    
    if 0.0 < best_alpha < 1.0:
        print("HYPOTHESIS CONFIRMED: Balance is required.", flush=True)
    elif best_alpha == 0.0:
        print("HYPOTHESIS FAILED: Random Walk is optimal.", flush=True)
    else:
        print("HYPOTHESIS FAILED: Greedy is optimal.", flush=True)

if __name__ == "__main__":
    run_experiment()
