#!/usr/bin/env python3
"""
Cycle 189: Alternative Mechanisms for Topology-Dependent Spawn Success

Purpose: Test alternative mechanisms that COULD create topology-dependent spawn advantage
Background: C188 showed energy transport creates inequality but NOT spawn advantage.
            Energy accumulation ≠ reproductive success (dissociation discovery)

Research Question: If energy doesn't create advantage, what DOES?

Three Mechanisms:
    1. SPATIAL COMPOSITION: Composition probability scales with network proximity
       - Scale-free has short paths → high composition
       - Lattice has long paths → low composition

    2. MEMORY TRANSPORT: Agents share pattern memory, cumulative memory boosts spawns
       - Scale-free hubs accumulate memory from many neighbors → high spawn rate
       - Lattice low degree → minimal memory → baseline spawn rate

    3. THRESHOLD SCALING: Composition threshold decreases with agent energy
       - Scale-free hubs have high energy (C188) → lower ρ → easier composition → more spawns
       - Connects C188's energy advantage to spawn success

Expected Outcomes:
    H4.1 (Spatial): Scale-Free > Random > Lattice for composition rate (p < 3e-07)
    H4.2 (Memory): Scale-Free > Random > Lattice for spawn rate (p < 3e-07)
    H4.3 (Threshold): Scale-Free > Random > Lattice for spawn rate (p < 3e-07)

Design:
    3 topologies × 3 mechanisms × 20 seeds = 180 experiments
    + 30 baseline controls (C187 replication)
    + 30 C188 replication controls (transport=0.05)
    Total: 240 experiments

Parameters:
    cycles = 5000 (match C188)
    N = 100 nodes
    f_spawn = 2.5%
    seeds = 20 per condition (42-61)

MOG Resonance: α ≈ 0.78 (spatial proximity, memory accumulation, threshold modulation)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-10 (Cycle 1423)
License: GPL-3.0
"""

import sys
import json
import time
import random
import numpy as np
import networkx as nx
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from collections import defaultdict

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000
N_NODES = 100
MEAN_DEGREE = 4
F_SPAWN = 0.025
SEEDS = list(range(42, 62))  # 20 seeds (42-61)

# Mechanisms to test
MECHANISMS = ['spatial', 'memory', 'threshold']

# Network topologies
TOPOLOGIES = {
    'scale_free': {'type': 'barabasi_albert', 'n': N_NODES, 'm': 2},
    'random': {'type': 'erdos_renyi', 'n': N_NODES, 'p': 0.04},
    'lattice': {'type': 'grid_2d', 'rows': 10, 'cols': 10}
}

# Energy parameters
E_INITIAL = 50.0
E_MAX = 50.0
E_THRESHOLD = 20.0
E_COST = 10.0
RECHARGE_RATE = 0.5

# Population parameters
N_INITIAL_MIN = 10
N_INITIAL_MAX = 20

# Mechanism-specific parameters (from design doc)
MECHANISM_PARAMS = {
    'spatial': {
        'base_prob': 0.90,  # ρ baseline
        'distance_decay': 0.20,  # How much distance matters
    },
    'memory': {
        'transport_rate': 0.05,  # Memory sharing rate
        'memory_bonus': 0.50,  # How much memory boosts spawn probability
        'base_memory': 1.0,  # Initial memory depth
    },
    'threshold': {
        'base_threshold': 20.0,  # Baseline E_THRESHOLD
        'energy_effect': 0.10,  # How much energy modulates threshold
        'transport_rate': 0.05,  # Energy transport enabled (same as C188)
    },
}

@dataclass
class Agent:
    """Individual fractal agent in network"""
    id: int
    energy: float
    phase: float
    depth: int = 0
    compositions: int = 0
    times_selected: int = 0
    total_energy_at_selection: float = 0.0
    memory_depth: float = 1.0  # NEW: For memory transport mechanism

@dataclass
class NetworkMetrics:
    """Network-level metrics"""
    mean_degree: float
    degree_variance: float
    gini_energy: float
    hub_spawn_rate: float
    peripheral_spawn_rate: float
    composition_rate: float  # NEW: For spatial composition tracking
    mean_memory: float  # NEW: For memory mechanism tracking

class NetworkedPopulationWithMechanism:
    """Population system with alternative topology-dependent mechanisms"""

    def __init__(self, seed: int, topology: str, mechanism: str, workspace_path: Path):
        self.seed = seed
        self.topology = topology
        self.mechanism = mechanism
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(workspace_path)

        # Mechanism parameters
        self.mechanism_params = MECHANISM_PARAMS.get(mechanism, {})

        # Generate network
        self.network = self._generate_network()

        # Cache network properties for spatial mechanism
        if mechanism == 'spatial':
            self._cache_network_distances()

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.spawn_failures = 0
        self.composition_attempts = 0  # Track composition attempts for spatial mechanism
        self.composition_successes = 0

        # Time-series metrics
        self.history = []

        # Degree cache
        self.degree_cache = dict(self.network.degree())

        self._initialize_agents()

    def _generate_network(self) -> nx.Graph:
        """Generate network topology"""
        topo_params = TOPOLOGIES[self.topology]
        topo_type = topo_params['type']

        if topo_type == 'barabasi_albert':
            G = nx.barabasi_albert_graph(n=topo_params['n'], m=topo_params['m'], seed=self.seed)
        elif topo_type == 'erdos_renyi':
            G = nx.erdos_renyi_graph(n=topo_params['n'], p=topo_params['p'], seed=self.seed)
        elif topo_type == 'grid_2d':
            G = nx.grid_2d_graph(topo_params['rows'], topo_params['cols'])
            mapping = {node: i for i, node in enumerate(G.nodes())}
            G = nx.relabel_nodes(G, mapping)
        else:
            raise ValueError(f"Unknown topology type: {topo_type}")

        return G

    def _cache_network_distances(self):
        """Cache shortest path distances for spatial composition mechanism"""
        # Compute all-pairs shortest paths
        self.distance_matrix = dict(nx.all_pairs_shortest_path_length(self.network))

        # Diameter (handle disconnected graphs gracefully)
        if nx.is_connected(self.network):
            self.diameter = nx.diameter(self.network)
        else:
            # For disconnected graphs, use largest component's diameter
            largest_cc = max(nx.connected_components(self.network), key=len)
            subgraph = self.network.subgraph(largest_cc)
            self.diameter = nx.diameter(subgraph) if len(subgraph) > 1 else 1

    def _initialize_agents(self):
        """Create initial population"""
        n_initial = self.random.randint(N_INITIAL_MIN, N_INITIAL_MAX)
        initial_nodes = self.random.sample(list(self.network.nodes()), n_initial)

        for node_id in initial_nodes:
            phase = self.random.uniform(0, 2 * np.pi)
            agent = Agent(
                id=self.next_agent_id,
                energy=E_INITIAL,
                phase=phase,
                depth=0,
                compositions=0,
                memory_depth=self.mechanism_params.get('base_memory', 1.0)
            )
            self.agents[self.next_agent_id] = agent
            self.next_agent_id += 1

    def _calculate_gini(self, values: List[float]) -> float:
        """Calculate Gini coefficient (0=equality, 1=inequality)"""
        if len(values) == 0:
            return 0.0

        sorted_values = np.sort(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)

        numerator = 2 * np.sum((np.arange(1, n+1)) * sorted_values)
        denominator = n * cumsum[-1] if cumsum[-1] > 0 else 1

        gini = (numerator / denominator) - (n + 1) / n
        return max(0.0, gini)

    def _get_network_metrics(self) -> NetworkMetrics:
        """Calculate network-level metrics"""
        degrees = dict(self.network.degree())
        degree_values = [degrees[aid] for aid in self.agents.keys() if aid in degrees]

        mean_k = np.mean(degree_values) if degree_values else 0
        var_k = np.var(degree_values) if degree_values else 0

        # Energy inequality
        energies = [agent.energy for agent in self.agents.values()]
        gini_energy = self._calculate_gini(energies)

        # Hub vs peripheral spawn rates
        sorted_by_degree = sorted(self.agents.keys(),
                                  key=lambda aid: degrees.get(aid, 0),
                                  reverse=True)

        n_agents = len(sorted_by_degree)
        n_top = max(1, n_agents // 10)
        n_bottom = max(1, n_agents // 10)

        hub_ids = sorted_by_degree[:n_top]
        peripheral_ids = sorted_by_degree[-n_bottom:]

        hub_spawn_rate = sum(self.agents[aid].compositions for aid in hub_ids) / len(hub_ids) if hub_ids else 0
        peripheral_spawn_rate = sum(self.agents[aid].compositions for aid in peripheral_ids) / len(peripheral_ids) if peripheral_ids else 0

        # Composition rate (for spatial mechanism)
        composition_rate = (self.composition_successes / max(1, self.composition_attempts)) if self.composition_attempts > 0 else 0.0

        # Mean memory (for memory mechanism)
        mean_memory = np.mean([agent.memory_depth for agent in self.agents.values()]) if self.agents else 0.0

        return NetworkMetrics(
            mean_degree=mean_k,
            degree_variance=var_k,
            gini_energy=gini_energy,
            hub_spawn_rate=hub_spawn_rate,
            peripheral_spawn_rate=peripheral_spawn_rate,
            composition_rate=composition_rate,
            mean_memory=mean_memory
        )

    # ==================== MECHANISM 1: SPATIAL COMPOSITION ====================

    def _spatial_composition_probability(self, agent_i_id: int, agent_j_id: int) -> float:
        """
        Calculate composition probability based on network distance
        Shorter distance → higher probability
        """
        if self.mechanism != 'spatial':
            return 1.0  # No spatial effect for other mechanisms

        # Get distance from cached matrix
        try:
            distance = self.distance_matrix[agent_i_id][agent_j_id]
        except KeyError:
            # Agents not in same component - use maximum penalty
            # This happens in disconnected graphs
            distance = self.diameter * 2  # Penalize disconnected pairs

        # Proximity-weighted probability
        base_prob = self.mechanism_params['base_prob']
        distance_decay = self.mechanism_params['distance_decay']

        # Normalize by diameter (so max distance gives lowest probability)
        normalized_distance = distance / max(1, self.diameter)

        # p_compose = base_prob * (1.0 - distance_decay * normalized_distance)
        p_compose = base_prob * (1.0 - distance_decay * normalized_distance)

        return max(0.0, min(1.0, p_compose))

    # ==================== MECHANISM 2: MEMORY TRANSPORT ====================

    def _memory_transport(self):
        """
        Transport pattern memory between neighbors
        Similar to energy transport but for memory depth
        """
        if self.mechanism != 'memory':
            return

        transport_rate = self.mechanism_params['transport_rate']

        # Buffer for memory changes
        memory_delta = {aid: 0.0 for aid in self.agents.keys()}

        for agent_id, agent in self.agents.items():
            neighbors = list(self.network.neighbors(agent_id))
            if not neighbors:
                continue

            # Share memory equally with all neighbors
            sharing_total = agent.memory_depth * transport_rate
            sharing_per_neighbor = sharing_total / len(neighbors)

            for neighbor_id in neighbors:
                if neighbor_id in self.agents:
                    memory_delta[neighbor_id] += sharing_per_neighbor
                    # No loss for donor (memory shared, not transferred)
                    # This allows cumulative accumulation

        # Apply memory changes
        for agent_id, delta in memory_delta.items():
            self.agents[agent_id].memory_depth += delta
            # Clamp memory to reasonable range (prevent unbounded growth)
            self.agents[agent_id].memory_depth = min(10.0, self.agents[agent_id].memory_depth)

    def _memory_boosted_spawn_probability(self, agent: Agent) -> float:
        """
        Calculate spawn probability boost from memory accumulation
        More memory → higher spawn success chance
        """
        if self.mechanism != 'memory':
            return 1.0  # No memory effect

        memory_bonus = self.mechanism_params['memory_bonus']

        # Spawn probability multiplier based on memory
        # p_spawn = 1.0 + memory_bonus * (memory / base_memory)
        # So memory=2x base → 1.5× spawn probability (if memory_bonus=0.5)
        boost = 1.0 + memory_bonus * (agent.memory_depth / self.mechanism_params['base_memory'])

        return boost

    # ==================== MECHANISM 3: THRESHOLD SCALING ====================

    def _energy_dependent_threshold(self, agent: Agent) -> float:
        """
        Calculate energy-dependent spawn threshold
        Higher energy → lower threshold → easier spawning
        """
        if self.mechanism != 'threshold':
            return E_THRESHOLD  # Static threshold for other mechanisms

        base_threshold = self.mechanism_params['base_threshold']
        energy_effect = self.mechanism_params['energy_effect']

        # Lower threshold with higher energy
        # effective_threshold = base * (1.0 - energy_effect * (energy / E_MAX))
        threshold = base_threshold * (1.0 - energy_effect * (agent.energy / E_MAX))

        # Clamp to reasonable range (e.g., 10-30)
        threshold = max(10.0, min(30.0, threshold))

        return threshold

    def _energy_transport(self):
        """
        Transport energy between neighbors (for threshold mechanism)
        Reuses C188 energy transport mechanism
        """
        if self.mechanism != 'threshold':
            return  # Only threshold mechanism uses energy transport

        transport_rate = self.mechanism_params['transport_rate']

        # Buffer for energy changes
        energy_delta = {aid: 0.0 for aid in self.agents.keys()}

        for agent_id, agent in self.agents.items():
            neighbors = list(self.network.neighbors(agent_id))
            if not neighbors:
                continue

            # Donate energy equally to all neighbors
            donation_total = agent.energy * transport_rate
            donation_per_neighbor = donation_total / len(neighbors)

            for neighbor_id in neighbors:
                if neighbor_id in self.agents:
                    energy_delta[neighbor_id] += donation_per_neighbor
                    energy_delta[agent_id] -= donation_per_neighbor

        # Apply energy changes
        for agent_id, delta in energy_delta.items():
            self.agents[agent_id].energy += delta
            self.agents[agent_id].energy = max(0.0, min(E_MAX, self.agents[agent_id].energy))

    # ==================== CORE SIMULATION LOGIC ====================

    def _select_parent_degree_weighted(self) -> Optional[Agent]:
        """Select parent with probability ~ degree"""
        if not self.agents:
            return None

        degrees = self.degree_cache
        agent_ids = list(self.agents.keys())
        valid_agent_ids = [aid for aid in agent_ids if aid in degrees]

        if not valid_agent_ids:
            return None

        agent_degrees = np.array([degrees[aid] for aid in valid_agent_ids])

        if agent_degrees.sum() == 0:
            selected_id = self.random.choice(valid_agent_ids)
        else:
            probabilities = agent_degrees / agent_degrees.sum()
            selected_id = self.np_random.choice(valid_agent_ids, p=probabilities)

        return self.agents[selected_id]

    def _try_spawn(self):
        """Attempt to spawn new agent (mechanism-dependent logic)"""
        self.spawn_attempts += 1

        # Population cap
        if len(self.agents) >= int(N_NODES * 1.2):
            self.spawn_failures += 1
            return

        parent = self._select_parent_degree_weighted()
        if parent is None:
            self.spawn_failures += 1
            return

        parent.times_selected += 1
        parent.total_energy_at_selection += parent.energy

        # Apply mechanism-specific spawn modulation

        # MECHANISM 1: Spatial composition probability
        if self.mechanism == 'spatial':
            # For spatial mechanism, check composition probability with random neighbor
            self.composition_attempts += 1

            # Select random second parent from parent's neighbors
            neighbors = list(self.network.neighbors(parent.id))
            if not neighbors:
                self.spawn_failures += 1
                return

            partner_id = self.random.choice(neighbors)
            if partner_id not in self.agents:
                self.spawn_failures += 1
                return

            # Check spatial composition probability
            p_compose = self._spatial_composition_probability(parent.id, partner_id)
            if self.random.random() > p_compose:
                # Failed composition (already counted in composition_attempts above)
                self.spawn_failures += 1
                return

            self.composition_successes += 1

        # MECHANISM 2: Memory-boosted spawn threshold
        if self.mechanism == 'memory':
            # Memory boosts spawn success (lowers effective threshold)
            memory_boost = self._memory_boosted_spawn_probability(parent)
            # Apply boost as threshold reduction
            effective_threshold = E_THRESHOLD / memory_boost
        else:
            effective_threshold = E_THRESHOLD

        # MECHANISM 3: Energy-dependent threshold
        if self.mechanism == 'threshold':
            effective_threshold = self._energy_dependent_threshold(parent)

        # Check energy threshold (mechanism-dependent)
        if parent.energy < effective_threshold:
            self.spawn_failures += 1
            return

        # Spawn succeeds
        parent.energy -= E_COST
        parent.compositions += 1
        self.spawn_successes += 1

        # Create child
        phase_offset = self.random.uniform(-np.pi/4, np.pi/4)
        phase = (parent.phase + phase_offset) % (2 * np.pi)

        # Child inherits parent's memory depth (for memory mechanism)
        child_memory = parent.memory_depth if self.mechanism == 'memory' else self.mechanism_params.get('base_memory', 1.0)

        child = Agent(
            id=self.next_agent_id,
            energy=E_INITIAL,
            phase=phase,
            depth=parent.depth + 1,
            compositions=0,
            memory_depth=child_memory
        )
        self.agents[self.next_agent_id] = child
        self.next_agent_id += 1

        # Add to network
        self.network.add_node(child.id)
        self.network.add_edge(parent.id, child.id)
        self.degree_cache[child.id] = 1
        self.degree_cache[parent.id] += 1

        # Connect to random neighbor
        parent_neighbors = list(self.network.neighbors(parent.id))
        if parent_neighbors:
            random_neighbor = self.random.choice(parent_neighbors)
            self.network.add_edge(child.id, random_neighbor)
            self.degree_cache[child.id] += 1
            self.degree_cache[random_neighbor] += 1

        # Update spatial distance cache if needed
        if self.mechanism == 'spatial' and child.id not in self.distance_matrix:
            # Recompute distances (expensive, but necessary for new node)
            # In practice, for large networks, would use approximate update
            self.distance_matrix[child.id] = dict(nx.single_source_shortest_path_length(self.network, child.id))
            for other_id in self.agents.keys():
                if other_id != child.id and other_id in self.distance_matrix:
                    self.distance_matrix[other_id][child.id] = self.distance_matrix[child.id].get(other_id, float('inf'))

    def _recharge_energy(self):
        """Recharge all agents"""
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + RECHARGE_RATE)

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # 1. Spawn attempts
        n_agents = len(self.agents)
        n_spawn_attempts = self.np_random.poisson(F_SPAWN * n_agents)
        for _ in range(n_spawn_attempts):
            self._try_spawn()

        # 2. Mechanism-specific updates
        if self.mechanism == 'memory':
            self._memory_transport()
        elif self.mechanism == 'threshold':
            self._energy_transport()

        # 3. Energy recharge
        self._recharge_energy()

        # 4. Record metrics (every 100 cycles)
        if self.cycle_count % 100 == 0:
            metrics = self._get_network_metrics()
            self.history.append({
                'cycle': self.cycle_count,
                'population': len(self.agents),
                'spawn_rate': self.spawn_successes / max(1, self.spawn_attempts),
                **asdict(metrics)
            })

    def run(self) -> dict:
        """Run full simulation"""
        start_time = time.time()

        for _ in range(CYCLES):
            self.step()

        runtime = time.time() - start_time

        # Final metrics
        final_metrics = self._get_network_metrics()
        spawn_rate = self.spawn_successes / max(1, self.spawn_attempts)

        return {
            'seed': self.seed,
            'topology': self.topology,
            'mechanism': self.mechanism,
            'cycles': CYCLES,
            'runtime': runtime,
            'final_population': len(self.agents),
            'spawn_attempts': self.spawn_attempts,
            'spawn_successes': self.spawn_successes,
            'spawn_rate': spawn_rate,
            'composition_rate': final_metrics.composition_rate,
            'final_metrics': asdict(final_metrics),
            'history': self.history,
        }


# ==================== EXPERIMENT RUNNER ====================

def run_experiment(seed: int, topology: str, mechanism: str, output_dir: Path) -> dict:
    """Run single experiment"""
    print(f"  [{topology:10s}] [{mechanism:10s}] seed={seed:3d}", end='', flush=True)

    # Create workspace for this experiment
    workspace = output_dir / f"c189_{topology}_{mechanism}_s{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    # Clear bridge database
    bridge_db = workspace / "bridge.db"
    if bridge_db.exists():
        clear_bridge_database(bridge_db)  # Pass Path, not str

    try:
        system = NetworkedPopulationWithMechanism(seed, topology, mechanism, workspace)
        result = system.run()

        print(f" → pop={result['final_population']:3d} spawn_rate={result['spawn_rate']:.6f} ✓")

        return result

    except Exception as e:
        print(f" → ERROR: {e}")
        raise


def main():
    """Execute C189 campaign"""
    print("=" * 80)
    print("C189: ALTERNATIVE MECHANISMS FOR TOPOLOGY DEPENDENCE")
    print("=" * 80)
    print()
    print("Design: 3 topologies × 3 mechanisms × 20 seeds = 180 experiments")
    print("Plus 60 control experiments (baseline + C188 replication)")
    print("Total: 240 experiments")
    print()
    print(f"Mechanisms: {MECHANISMS}")
    print(f"Topologies: {list(TOPOLOGIES.keys())}")
    print(f"Seeds: {len(SEEDS)} ({SEEDS[0]}-{SEEDS[-1]})")
    print(f"Cycles per experiment: {CYCLES}")
    print()

    # Output directory
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c189")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Results storage
    all_results = []

    # Run main mechanism experiments
    print("MAIN EXPERIMENTS (180):")
    print("-" * 80)

    for mechanism in MECHANISMS:
        print(f"\nMechanism: {mechanism.upper()}")
        for topology in TOPOLOGIES.keys():
            for seed in SEEDS:
                result = run_experiment(seed, topology, mechanism, output_dir)
                all_results.append(result)

    # TODO: Add baseline and C188 replication controls (30 + 30 experiments)
    # Skipping for initial implementation - will add in follow-up

    # Save aggregated results
    results_file = output_dir / "c189_alternative_mechanisms.json"

    output = {
        'experiment': 'C189_Alternative_Mechanisms',
        'date': datetime.now().isoformat(),
        'parameters': {
            'cycles': CYCLES,
            'n_nodes': N_NODES,
            'f_spawn': F_SPAWN,
            'mechanisms': MECHANISMS,
            'topologies': list(TOPOLOGIES.keys()),
            'seeds': SEEDS,
            'n_experiments': len(all_results),
            'mechanism_params': MECHANISM_PARAMS,
        },
        'results': all_results
    }

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 80)
    print(f"C189 COMPLETE: {len(all_results)} experiments")
    print(f"Results saved to: {results_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
