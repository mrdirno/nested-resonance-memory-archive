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

def calculate_order_parameter(phases: List[float]) -> float:
    if not phases:
        return 0.0
    # Kuramoto Order Parameter: R = |(1/N) * sum(e^(i*theta))|
    complex_phases = np.exp(1j * np.array(phases))
    z = np.mean(complex_phases)
    return np.abs(z)

def run_experiment():
    print("MOG ONLINE: Cycle 1955 - Spectral Analysis", flush=True)
    
    # Parameters
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 200 # Increased for FFT resolution
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
    
    order_history = []
    
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
        
        # 4. Order Parameter Calculation
        # Collect phases of all Base Agents
        base_phases = []
        for agent in agents:
            if agent.state.depth == 0:
                base_phases.append(agent.state.phase)
            else:
                # Cluster: Add phase N times (assuming perfect sync inside)
                count = len(cluster_registry.get(agent.agent_id, []))
                base_phases.extend([agent.state.phase] * count)
        
        r = calculate_order_parameter(base_phases)
        order_history.append(r)
        
        if len(base_phases) == 0:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break

    # FFT Analysis
    fft_vals = np.fft.rfft(order_history)
    fft_freqs = np.fft.rfftfreq(len(order_history))
    power_spectrum = np.abs(fft_vals)**2
    
    # Find dominant frequency (ignore DC component at index 0)
    if len(power_spectrum) > 1:
        peak_idx = np.argmax(power_spectrum[1:]) + 1
        peak_freq = fft_freqs[peak_idx]
        peak_power = power_spectrum[peak_idx]
        
        print(f"Dominant Frequency: {peak_freq:.4f} cycles^-1", flush=True)
        print(f"Peak Power: {peak_power:.2f}", flush=True)
        print(f"Period: {1.0/peak_freq:.2f} cycles", flush=True)
        
        # Check for 1/f noise (Pink Noise) -> Complexity
        # Or Peak -> Limit Cycle
        
        if peak_power > 5.0: # Arbitrary significance
            print("OSCILLATION DETECTED (Limit Cycle).", flush=True)
        else:
            print("NOISY DYNAMICS (No clear rhythm).", flush=True)
    else:
        print("INSUFFICIENT DATA for Spectral Analysis.", flush=True)

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
