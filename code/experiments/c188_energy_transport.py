#!/usr/bin/env python3
"""
Cycle 188: Energy Transport Mechanism - Testing Topology Dependence

Purpose: Test if energy transport creates topology-dependent dynamics in NRM
Background: C187 showed topology-invariance (SF ≈ Random ≈ Lattice, all ~1.208).
            This experiment adds energy transport to test if hub accumulation creates effects.

Hypothesis: Energy transport enables topology effects:
            H3.1: Hubs accumulate energy → higher spawn rates (≥20% advantage)
            H3.2: Topology ranking emerges: Scale-Free > Random > Lattice
            H3.3: Energy inequality scales with degree variance (Gini)

Mechanism: Each cycle, agents donate fraction of energy to ALL neighbors
           - Hubs receive from many → accumulate energy → higher spawn capacity
           - Peripherals donate to few → lose energy → lower spawn capacity

Design:
    Three Topologies (same as C187):
    1. Scale-Free (Barabási-Albert): Power-law degree distribution
    2. Random (Erdős-Rényi): Poisson degree distribution
    3. Lattice (2D Grid): Uniform degree distribution

    Transport Rates: [0.0, 0.01, 0.03, 0.05, 0.10]
    - 0.0 = C187 baseline (no transport, topology-invariant)
    - 0.10 = strong transport (maximal hub effects)

    300 experiments: 3 topologies × 5 transport rates × 20 seeds

Expected Outcomes:
    transport=0.0: Hub/Peripheral = 1.0 (C187 baseline)
    transport=0.05: Hub/Peripheral ≥ 1.25 (strong hub advantage)
    transport=0.10: Hub/Peripheral ≥ 1.40 (very strong effect)

Parameters:
    cycles = 5000 (extended from C187's 3000)
    N = 100 nodes
    f_spawn = 2.5%
    seeds = 20 per condition (double C187's 10)

MOG Resonance: α = 0.78 (5 cross-domain analogies)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-10 (Cycle 1415)
License: GPL-3.0
"""

import sys
import json
import time
import random
import numpy as np
import networkx as nx
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from collections import defaultdict

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000  # Extended from C187's 3000
N_NODES = 100
MEAN_DEGREE = 4
F_SPAWN = 0.025
SEEDS = list(range(42, 62))  # 20 seeds (42-61)

# Transport rates to test (C188 primary parameter)
TRANSPORT_RATES = [0.0, 0.01, 0.03, 0.05, 0.10]

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

@dataclass
class NetworkMetrics:
    """Network-level metrics"""
    mean_degree: float
    degree_variance: float
    gini_energy: float  # NEW: Energy inequality
    hub_spawn_rate: float  # NEW: Top 10% degree spawn rate
    peripheral_spawn_rate: float  # NEW: Bottom 10% degree spawn rate
    degree_energy_correlation: float  # NEW: Pearson r(degree, energy)

class NetworkedPopulationWithTransport:
    """Population system with energy transport between neighbors"""

    def __init__(self, seed: int, topology: str, transport_rate: float, workspace_path: Path):
        self.seed = seed
        self.topology = topology
        self.transport_rate = transport_rate
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(workspace_path)

        # Generate network
        self.network = self._generate_network()

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.spawn_failures = 0

        # Time-series metrics (sample every 100 cycles)
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
                compositions=0
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

        # Gini = 2 * (sum of (i+1)*x_i) / (n * sum(x_i)) - (n+1)/n
        numerator = 2 * np.sum((np.arange(1, n+1)) * sorted_values)
        denominator = n * cumsum[-1] if cumsum[-1] > 0 else 1

        gini = (numerator / denominator) - (n + 1) / n
        return max(0.0, gini)  # Clamp to non-negative

    def _get_network_metrics(self) -> NetworkMetrics:
        """Calculate network-level metrics"""
        degrees = dict(self.network.degree())
        degree_values = [degrees[aid] for aid in self.agents.keys() if aid in degrees]

        mean_k = np.mean(degree_values) if degree_values else 0
        var_k = np.var(degree_values) if degree_values else 0

        # Energy inequality (Gini)
        energies = [agent.energy for agent in self.agents.values()]
        gini_energy = self._calculate_gini(energies)

        # Hub vs peripheral spawn rates
        # Hub = top 10% degree, Peripheral = bottom 10%
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

        # Degree-energy correlation
        agent_degrees = [degrees.get(aid, 0) for aid in self.agents.keys()]
        agent_energies = [self.agents[aid].energy for aid in self.agents.keys()]

        if len(agent_degrees) > 1 and np.std(agent_degrees) > 0 and np.std(agent_energies) > 0:
            degree_energy_corr = np.corrcoef(agent_degrees, agent_energies)[0, 1]
        else:
            degree_energy_corr = 0.0

        return NetworkMetrics(
            mean_degree=mean_k,
            degree_variance=var_k,
            gini_energy=gini_energy,
            hub_spawn_rate=hub_spawn_rate,
            peripheral_spawn_rate=peripheral_spawn_rate,
            degree_energy_correlation=degree_energy_corr
        )

    def _energy_transport(self):
        """
        Transport energy between neighbors
        Each agent donates (transport_rate * energy) divided equally among neighbors
        """
        if self.transport_rate == 0.0:
            return  # Skip transport if rate is 0 (C187 baseline)

        # Buffer for energy changes (avoid modifying during iteration)
        energy_delta = {aid: 0.0 for aid in self.agents.keys()}

        for agent_id, agent in self.agents.items():
            neighbors = list(self.network.neighbors(agent_id))
            if not neighbors:
                continue  # Isolated nodes don't transport

            # Donate energy equally to all neighbors
            donation_total = agent.energy * self.transport_rate
            donation_per_neighbor = donation_total / len(neighbors)

            for neighbor_id in neighbors:
                if neighbor_id in self.agents:
                    energy_delta[neighbor_id] += donation_per_neighbor
                    energy_delta[agent_id] -= donation_per_neighbor

        # Apply energy changes
        for agent_id, delta in energy_delta.items():
            self.agents[agent_id].energy += delta
            self.agents[agent_id].energy = max(0.0, min(E_MAX, self.agents[agent_id].energy))

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
        """Attempt to spawn new agent"""
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

        # Check energy threshold
        if parent.energy < E_THRESHOLD:
            self.spawn_failures += 1
            return

        # Spawn succeeds
        parent.energy -= E_COST
        parent.compositions += 1
        self.spawn_successes += 1

        # Create child
        phase_offset = self.random.uniform(-np.pi/4, np.pi/4)
        phase = (parent.phase + phase_offset) % (2 * np.pi)
        child = Agent(
            id=self.next_agent_id,
            energy=E_INITIAL,
            phase=phase,
            depth=parent.depth + 1,
            compositions=0
        )
        self.agents[self.next_agent_id] = child
        self.next_agent_id += 1

        # Add to network
        self.network.add_node(child.id)
        self.network.add_edge(parent.id, child.id)
        self.degree_cache[child.id] = 1
        self.degree_cache[parent.id] += 1

        parent_neighbors = list(self.network.neighbors(parent.id))
        if parent_neighbors:
            random_neighbor = self.random.choice(parent_neighbors)
            self.network.add_edge(child.id, random_neighbor)
            self.degree_cache[child.id] += 1
            self.degree_cache[random_neighbor] += 1

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

        # 2. Energy transport (NEW - C188 mechanism)
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
            'transport_rate': self.transport_rate,
            'cycles': CYCLES,
            'runtime_seconds': runtime,
            'final_population': len(self.agents),
            'spawn_attempts': self.spawn_attempts,
            'spawn_successes': self.spawn_successes,
            'spawn_rate': spawn_rate,
            'final_metrics': asdict(final_metrics),
            'history': self.history
        }


def run_experiment(topology: str, transport_rate: float, seed: int, workspace_path: Path) -> dict:
    """Run single experiment"""
    print(f"  Seed {seed}, topology={topology}, transport={transport_rate:.2f}...")

    system = NetworkedPopulationWithTransport(seed, topology, transport_rate, workspace_path)
    result = system.run()

    return result


def main():
    """Run C188 energy transport experiments"""
    print("="*80)
    print("CYCLE 188: ENERGY TRANSPORT MECHANISM")
    print("Testing topology dependence via hub accumulation")
    print("="*80)
    print()
    print(f"Topologies: {list(TOPOLOGIES.keys())}")
    print(f"Transport rates: {TRANSPORT_RATES}")
    print(f"Seeds per condition: {len(SEEDS)}")
    print(f"Total experiments: {len(TOPOLOGIES) * len(TRANSPORT_RATES) * len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print()

    # Setup database workspace (TranscendentalBridge expects directory, appends /bridge.db)
    workspace_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c188_workspace")
    workspace_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

    # Clear any existing bridge database in workspace
    bridge_db = workspace_path / "bridge.db"
    if bridge_db.exists():
        bridge_db.unlink()

    # Run all experiments
    results = []
    total_experiments = len(TOPOLOGIES) * len(TRANSPORT_RATES) * len(SEEDS)
    completed = 0
    start_time = time.time()

    for topology in TOPOLOGIES.keys():
        for transport_rate in TRANSPORT_RATES:
            print(f"\n{topology.upper()}, transport_rate={transport_rate:.2f}")

            for seed in SEEDS:
                result = run_experiment(topology, transport_rate, seed, workspace_path)
                results.append(result)

                completed += 1
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = (total_experiments - completed) / rate if rate > 0 else 0

                print(f"    [{completed}/{total_experiments}] "
                      f"Spawn rate: {result['spawn_rate']:.4f}, "
                      f"Gini: {result['final_metrics']['gini_energy']:.3f}, "
                      f"Hub/Periph: {result['final_metrics']['hub_spawn_rate']:.2f}/"
                      f"{result['final_metrics']['peripheral_spawn_rate']:.2f}, "
                      f"ETA: {remaining/60:.1f}min")

    # Save results
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c188_energy_transport.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        'experiment': 'C188_Energy_Transport',
        'description': 'Test if energy transport creates topology-dependent dynamics',
        'mog_resonance': 0.78,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'topologies': list(TOPOLOGIES.keys()),
            'transport_rates': TRANSPORT_RATES,
            'cycles': CYCLES,
            'n_nodes': N_NODES,
            'f_spawn': F_SPAWN,
            'seeds': SEEDS,
            'n_experiments': len(results)
        },
        'results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    total_time = time.time() - start_time
    print()
    print("="*80)
    print(f"C188 COMPLETE: {len(results)} experiments in {total_time/3600:.2f} hours")
    print(f"Results saved to: {output_path}")
    print("="*80)


if __name__ == '__main__':
    main()
