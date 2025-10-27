# Nested Resonance Memory (NRM) - Minimal Runnable Package

**Minimal self-contained implementation of the Nested Resonance Memory framework.**

## Overview

This package provides a lightweight, dependency-minimal implementation of NRM for demonstration and reproducibility. It runs a single experiment showing composition-decomposition dynamics.

## Features

- **Reality-grounded**: Uses actual system metrics (CPU, memory)
- **Minimal dependencies**: Only NumPy and psutil required
- **Fast execution**: ~30 seconds per experiment
- **Publication-ready**: Generates figures and JSON results

## Installation

```bash
# Install dependencies
pip install numpy psutil matplotlib

# Or use requirements.txt
pip install -r requirements.txt
```

## Quick Start

```bash
# Run minimal NRM experiment
python examples/run_minimal_experiment.py

# Output:
# - data/results_TIMESTAMP.json (experimental results)
# - data/population_dynamics.png (visualization)
```

## System Requirements

- Python 3.8+
- 50MB RAM
- Any OS (Linux, macOS, Windows)

## What This Demonstrates

1. **Fractal Agent System**: 100 agents with depth/resonance/energy states
2. **Composition-Decomposition Cycles**: Clustering → bursting dynamics
3. **Reality Grounding**: Agent energy coupled to actual system CPU/memory
4. **Pattern Emergence**: Self-organizing collective behavior

## Experiment Parameters

```python
{
    "population_size": 100,
    "cycles": 1000,
    "spawn_frequency": 0.02,
    "resonance_threshold": 0.80,
    "energy_threshold": 40,
    "composition_depth": 3
}
```

## Output Format

JSON results include:
- Population dynamics (N over time)
- Composition events (clustering occurrences)
- Decomposition events (burst occurrences)
- Energy statistics (mean, std, min, max)
- System metrics (CPU%, memory%)

## Validation

Expected behavior:
- Population stabilizes around 80-120 agents
- Composition events: 5-15 per 1000 cycles
- Decomposition events: 3-10 per 1000 cycles
- Energy variance: CV ≈ 8-12%

## Citation

```
Payopay, A. (2025). Nested Resonance Memory: Composition-Decomposition
Dynamics in Reality-Grounded Agent Systems. GitHub Repository:
https://github.com/mrdirno/nested-resonance-memory-archive
```

## License

GPL-3.0 - See LICENSE file

## Full Research Archive

Complete implementation with 11 papers, 545+ experiments, and full documentation:
https://github.com/mrdirno/nested-resonance-memory-archive

---

**Author**: Aldrin Payopay (aldrin.gdf@gmail.com)
**Version**: 1.0.0
**Date**: 2025-10-27
