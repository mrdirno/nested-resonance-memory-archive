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

def calculate_autocorrelation(signal: List[float]) -> float:
    if len(signal) < 2: return 0.0
    # Lag-1 Autocorrelation
    return np.corrcoef(signal[:-1], signal[1:])[0, 1]

def run_experiment():
    print("MOG ONLINE: Cycle 1963 - Periodicity Analysis", flush=True)
    
    # Parameters
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 500
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
    
    pop_history = []
    cluster_history = []
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism & Willingness Filter
        active_agents = []
        newly_released = []
        
        # Filter for composition
        willing_agents = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            # Willingness Logic: 1 / (Energy + epsilon)
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
        
        # Note: We pass 'willing_agents' to compose, but update 'active_agents' list.
        # We must intersect willing_agents with active_agents (survivors).
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
        
        # Stats
        active_count = len(agents)
        dormant_count = sum(len(v) for v in cluster_registry.values())
        total_pop = active_count + dormant_count
        n_clusters = sum(1 for a in agents if a.state.depth > 0)
        
        pop_history.append(total_pop)
        cluster_history.append(n_clusters)
        
        if total_pop == 0:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break
            
    # Analysis
    lag1_pop = calculate_autocorrelation(pop_history)
    lag1_clus = calculate_autocorrelation(cluster_history)
    
    print(f"Final Population: {pop_history[-1]}", flush=True)
    print(f"Pop Autocorrelation (Lag-1): {lag1_pop:.4f}", flush=True)
    print(f"Cluster Autocorrelation (Lag-1): {lag1_clus:.4f}", flush=True)
    
    # Detect Oscillation via FFT
    fft_vals = np.fft.rfft(pop_history)
    power = np.abs(fft_vals)**2
    peak_idx = np.argmax(power[1:]) + 1
    peak_power = power[peak_idx]
    
    print(f"Dominant Freq: {peak_idx / len(pop_history):.4f}", flush=True)
    print(f"Peak Power: {peak_power:.2f}", flush=True)
    
    if peak_power > 1000: # Arbitrary threshold for "Strong Cycle"
        print("OSCILLATION CONFIRMED.", flush=True)
    else:
        print("NO STRONG OSCILLATION.", flush=True)

if __name__ == "__main__":
    run_experiment()