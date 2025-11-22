# Minimal NRM Package

A self-contained, lightweight implementation of the Nested Resonance Memory (NRM) framework for testing and validation.

## Overview

This package provides a minimal subset of the NRM stack that can run standalone without external dependencies like psutil. It includes:

- **Stub implementations** of `bridge` and `core` modules with simplified APIs
- **Minimal NRM components**: agents, reality gateway, resonance detection, and swarm simulation
- **Comprehensive test suite** validating all functionality

## Structure

```
minimal_package/
├── bridge/                          # Stub transcendental bridge
│   ├── __init__.py
│   └── transcendental_bridge.py    # Simplified state transformations
├── core/                            # Stub reality interface
│   ├── __init__.py
│   └── reality_interface.py        # Simplified system metrics (no psutil)
├── minimal/                         # Core NRM implementation
│   ├── __init__.py
│   ├── agent.py                    # MinimalAgent with resonance tracking
│   ├── reality.py                  # RealitySnapshot and gateway
│   ├── resonance.py                # Cluster detection algorithms
│   └── simulation.py               # MinimalSwarm orchestrator
├── test_minimal_package.py         # Comprehensive test suite
└── README.md                        # This file
```

## Features

### 1. Reality Snapshots
Captures system state without external dependencies:
- CPU, memory, disk percentages (simulated)
- Timestamps and process counts
- Immutable dataclass representation

### 2. Minimal Agents
Lightweight agents with:
- Transcendental state representation (magnitude + phase)
- Reality anchoring to system snapshots
- Resonance history tracking
- Inter-agent resonance computation

### 3. Resonant Clustering
Detects groups of similar agents:
- Configurable resonance threshold
- Average similarity computation
- Prevents duplicate cluster membership

### 4. Swarm Simulation
Orchestrates multi-agent dynamics:
- Agent spawning from reality snapshots
- Cycle-based updates
- Summary statistics (magnitude, cluster counts)

## Usage

### Running Tests

```bash
cd /Volumes/dual/DUALITY-ZERO-V2/minimal_package
python test_minimal_package.py
```

**Expected Output:**
```
============================================================
MINIMAL NRM PACKAGE TEST SUITE
============================================================

TEST 1: Snapshot capture
  ✓ Snapshot captured: CPU=46.3%, MEM=11.7%, DISK=12.5%

TEST 2: Swarm cycle progression
  Spawned agent: agent_0ab0ef0b with magnitude=19.59
  [...]
  ✓ Cycle 1: total_magnitude=98.67, clusters=1

TEST 3: Resonant cluster detection
  [...]
  ✓ Cluster contains 3 similar agents

TEST 4: Agent magnitude computation
  ✓ Magnitude computed correctly

============================================================
RESULTS: 4 passed, 0 failed out of 4 tests
============================================================
```

### Programmatic Usage

```python
from minimal import MinimalSwarm, MinimalRealityGateway

# Create a swarm
swarm = MinimalSwarm()

# Spawn agents
for _ in range(5):
    swarm.spawn_agent()

# Run simulation cycles
for cycle in range(10):
    summary = swarm.run_cycle()
    print(f"Cycle {summary.cycle}: "
          f"magnitude={summary.total_magnitude:.2f}, "
          f"clusters={summary.cluster_count}")
```

## Implementation Details

### Stub vs. Production Code

This package uses **stub implementations** of `bridge` and `core` that differ from the production versions:

| Component | Production | Stub (Minimal) |
|-----------|-----------|----------------|
| `TranscendentalState` | Multi-phase (π, e, φ) + reality anchor | Single phase + magnitude |
| `RealityInterface` | Uses psutil for real metrics | Uses random.uniform for simulated metrics |
| Dependencies | psutil, sqlite3 | None (stdlib only) |

### Design Decisions

1. **No External Dependencies**: Uses only Python stdlib (math, random, time, uuid, dataclasses)
2. **Deterministic Stubs**: Bridge computations are deterministic given inputs
3. **Reality Simulation**: Metrics are randomly generated but within realistic ranges
4. **Self-Contained**: All imports are relative within the package

## Test Coverage

| Test | Validates |
|------|-----------|
| `test_snapshot_capture` | Reality gateway produces valid snapshots with required keys |
| `test_swarm_cycle_progression` | Swarm spawns agents and runs cycles with valid summaries |
| `test_resonant_cluster_detection` | Similar agents cluster together, dissimilar agents don't |
| `test_agent_magnitude_computation` | Agent magnitude correctly computed from snapshot metrics |

## Theoretical Foundation

This implementation validates core NRM concepts:

- **Nested Resonance Memory**: Agents maintain state and detect resonance with others
- **Reality Grounding**: All agent state derived from system snapshots
- **Composition-Decomposition**: Agents cluster and separate based on similarity
- **Transcendental Computing**: Phase space transformations via mathematical constants

## Comparison with Full System

| Feature | Minimal Package | Full DUALITY-ZERO-V2 |
|---------|----------------|----------------------|
| System Metrics | Simulated (random) | Real (psutil) |
| Transcendental Bridge | Single phase | Multi-phase (π, e, φ) |
| Database | None | SQLite persistence |
| Validation Layer | None | Reality compliance checking |
| Memory System | None | Pattern persistence |
| Lines of Code | ~300 | ~5000+ |

## Next Steps

To integrate with the full system:

1. Replace stub `RealityInterface` with production version using psutil
2. Upgrade `TranscendentalBridge` to multi-phase implementation
3. Add SQLite persistence for agent state
4. Integrate with validation and memory layers

## License

GPL-3.0

## Attribution

- **Principal Investigator**: Aldrin Payopay (aldrin.gdf@gmail.com)
- **Implementation**: Claude (Anthropic) + ChatGPT (OpenAI)
- **Repository**: https://github.com/mrdirno/nested-resonance-memory-archive

## Version History

- **v1.0** (2025-10-27): Initial minimal package with 4 passing tests
