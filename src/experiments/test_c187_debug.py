#!/usr/bin/env python3
"""
Debug test for C187 network structure experiment hang

Purpose: Identify where the infinite loop is occurring
"""

import sys
import time
import random
import numpy as np
import networkx as nx
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from transcendental_bridge import TranscendentalBridge

# Test parameters
SEED = 42
N_NODES = 100

print("=" * 80)
print("C187 HANG DEBUG TEST")
print("=" * 80)
print()

print("Step 1: Testing TranscendentalBridge initialization...")
start = time.time()
db_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/databases/test_debug")
db_path.mkdir(parents=True, exist_ok=True)
try:
    bridge = TranscendentalBridge(db_path)
    elapsed = time.time() - start
    print(f"✓ Bridge created successfully ({elapsed:.3f}s)")
except Exception as e:
    print(f"✗ Bridge creation FAILED: {e}")
    sys.exit(1)

print()
print("Step 2: Testing Scale-Free network generation...")
start = time.time()
try:
    G = nx.barabasi_albert_graph(n=N_NODES, m=2, seed=SEED)
    elapsed = time.time() - start
    print(f"✓ Scale-free network created ({elapsed:.3f}s)")
    print(f"  Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print(f"  Mean degree: {np.mean([d for n, d in G.degree()]):.2f}")
except Exception as e:
    print(f"✗ Network generation FAILED: {e}")
    sys.exit(1)

print()
print("Step 3: Testing Random network generation...")
start = time.time()
try:
    G = nx.erdos_renyi_graph(n=N_NODES, p=0.04, seed=SEED)
    elapsed = time.time() - start
    print(f"✓ Random network created ({elapsed:.3f}s)")
    print(f"  Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print(f"  Mean degree: {np.mean([d for n, d in G.degree()]):.2f}")
except Exception as e:
    print(f"✗ Network generation FAILED: {e}")
    sys.exit(1)

print()
print("Step 4: Testing Lattice network generation...")
start = time.time()
try:
    G = nx.grid_2d_graph(10, 10)
    mapping = {node: i for i, node in enumerate(G.nodes())}
    G = nx.relabel_nodes(G, mapping)
    elapsed = time.time() - start
    print(f"✓ Lattice network created ({elapsed:.3f}s)")
    print(f"  Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    degrees = [d for n, d in G.degree()]
    print(f"  Mean degree: {np.mean(degrees):.2f}")
    print(f"  Degree range: [{min(degrees)}, {max(degrees)}]")
except Exception as e:
    print(f"✗ Network generation FAILED: {e}")
    sys.exit(1)

print()
print("Step 5: Testing degree-weighted selection...")
start = time.time()
try:
    # Use scale-free network for testing
    G = nx.barabasi_albert_graph(n=N_NODES, m=2, seed=SEED)
    degrees = dict(G.degree())
    agent_ids = list(range(20))  # Simulate 20 agents

    # Filter agents in network
    valid_ids = [aid for aid in agent_ids if aid in degrees]
    agent_degrees = np.array([degrees[aid] for aid in valid_ids])

    # Degree-weighted selection
    probabilities = agent_degrees / agent_degrees.sum()
    np_random = np.random.RandomState(SEED)

    # Select 1000 times
    selections = []
    for _ in range(1000):
        selected_id = np_random.choice(valid_ids, p=probabilities)
        selections.append(selected_id)

    elapsed = time.time() - start
    print(f"✓ Degree-weighted selection completed ({elapsed:.3f}s)")
    print(f"  1000 selections in {elapsed*1000:.1f}ms")
except Exception as e:
    print(f"✗ Degree-weighted selection FAILED: {e}")
    sys.exit(1)

print()
print("Step 6: Testing single simulation cycle...")
start = time.time()
try:
    # Simple agent class
    from dataclasses import dataclass

    @dataclass
    class TestAgent:
        id: int
        energy: float = 50.0
        phase: float = 0.0
        depth: int = 0
        compositions: int = 0
        times_selected: int = 0
        total_energy_at_selection: float = 0.0

    # Create simple simulation
    agents = {i: TestAgent(i, energy=50.0, phase=random.uniform(0, 2*np.pi))
              for i in range(15)}
    network = nx.barabasi_albert_graph(n=100, m=2, seed=SEED)

    # Simulate spawn attempts
    F_SPAWN = 0.025
    n_agents = len(agents)
    n_spawn_attempts = np_random.poisson(F_SPAWN * n_agents)

    print(f"  Population: {n_agents}, Spawn attempts: {n_spawn_attempts}")

    # Do spawn attempts
    for attempt in range(n_spawn_attempts):
        # Select parent
        valid_ids = [aid for aid in agents.keys() if aid in degrees]
        if valid_ids:
            agent_degrees = np.array([degrees[aid] for aid in valid_ids])
            probs = agent_degrees / agent_degrees.sum()
            selected_id = np_random.choice(valid_ids, p=probs)

            # Update agent
            agents[selected_id].times_selected += 1

    elapsed = time.time() - start
    print(f"✓ Single cycle completed ({elapsed:.3f}s)")
except Exception as e:
    print(f"✗ Single cycle FAILED: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("ALL TESTS PASSED - No hang detected")
print("=" * 80)
print()
print("Conclusion: If all tests pass quickly, the hang is NOT in these components.")
print("Next: Check if experiment code has additional logic causing hang.")
