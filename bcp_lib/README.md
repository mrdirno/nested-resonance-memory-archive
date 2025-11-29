# BCP: Budget-Constrained Perception

A universal framework for attention allocation under resource constraints.

## The BCP Equation

```
V(a) = E[Gain(a)] - λ(B) × Cost(a) - γ × Complexity
```

Where:
- **V(a)**: Value of attending to action/item a
- **E[Gain(a)]**: Expected benefit if attended to
- **λ(B) = k / (ε + B)**: Metabolic pressure (inverse of budget)
- **Cost(a)**: Resource cost to attend
- **γ**: Complexity penalty coefficient

## Installation

```bash
pip install bcp-perception
```

Or install from source:

```bash
git clone https://github.com/mrdirno/nested-resonance-memory-archive.git
cd nested-resonance-memory-archive/bcp_lib
pip install -e .
```

For system monitoring features:

```bash
pip install bcp-perception[monitor]
```

## Quick Start

```python
from bcp import AttentionItem, BCPModel

# Create items with gain (benefit) and cost (effort)
items = [
    AttentionItem("Critical bug", gain=1.0, cost=0.3),
    AttentionItem("New feature", gain=0.7, cost=0.6),
    AttentionItem("Refactor", gain=0.5, cost=0.8),
    AttentionItem("Documentation", gain=0.4, cost=0.4),
]

# Create model and allocate with budget
model = BCPModel()
result = model.allocate(items, budget=1.0)

print(f"Phase: {result.phase.value}")
print(f"Attend to: {result.attended}")
print(f"Ignore: {result.ignored}")
```

Output:
```
Phase: scarcity
Attend to: ['Critical bug', 'New feature']
Ignore: ['Refactor', 'Documentation']
```

## Key Concepts

### Phase Transitions

BCP predicts three distinct phases based on resource availability:

| Phase | Budget Level | Behavior |
|-------|-------------|----------|
| **ABUNDANCE** | High (B > 2.0) | Attend to everything |
| **SCARCITY** | Moderate | Triage begins - ignore low-value items |
| **CRISIS** | Low (B < 0.5) | Focus on single highest-value item |

### Metabolic Pressure (λ)

Lambda controls cost sensitivity:
- **Low λ** (high budget): Costs matter less, attend broadly
- **High λ** (low budget): Costs dominate, strict triage

```python
model = BCPModel()

# High budget -> low lambda
print(model.compute_lambda(5.0))  # ~1.96

# Low budget -> high lambda
print(model.compute_lambda(0.5))  # ~16.67
```

### Domain Presets

Pre-configured scenarios validated across research:

```python
from bcp import DOMAIN_PRESETS, BCPModel

model = BCPModel()

# Available domains
domains = ["finance", "medical", "education", "diplomacy",
           "ecosystem", "software", "emergency", "moderation",
           "manufacturing"]

# Use a preset
items = DOMAIN_PRESETS["medical"]()
result = model.allocate(items, budget=0.5)
```

## Advanced Usage

### Budget Sweep

Analyze behavior across budget range:

```python
import numpy as np
from bcp import BCPModel, AttentionItem

def create_items():
    return [
        AttentionItem("A", gain=0.9, cost=0.3),
        AttentionItem("B", gain=0.7, cost=0.5),
        AttentionItem("C", gain=0.5, cost=0.4),
    ]

model = BCPModel()
budgets = np.linspace(0.1, 3.0, 30)
results = model.sweep_budgets(create_items, budgets)

# Find phase transition thresholds
triage_threshold, crisis_threshold = model.find_phase_thresholds(
    create_items, budgets
)
```

### Real-Time Monitoring

Monitor system resources with BCP-based triage:

```python
from bcp import BCPMonitor

monitor = BCPMonitor()

# Add monitoring tasks
monitor.add_task("cpu", gain=0.9, cost=0.1,
                 collector=lambda: get_cpu_usage())
monitor.add_task("memory", gain=0.8, cost=0.2,
                 collector=lambda: get_memory_usage())

# Sample with current budget
sample = monitor.sample(budget=1.0)
print(f"Attended: {sample.attended_tasks}")
print(f"Metrics: {sample.metrics}")
```

### Custom Model Parameters

```python
model = BCPModel(
    lambda_scale=10.0,      # Base metabolic pressure
    lambda_epsilon=0.1,     # Prevents division by zero
    gamma=0.1,              # Complexity penalty
    abundance_threshold=2.0, # Budget for ABUNDANCE phase
    crisis_threshold=0.5,   # Budget for CRISIS phase
)
```

## Research Background

BCP was developed through the DUALITY-ZERO research program, validated across 10 distinct domains:

1. **Finance** - Portfolio triage
2. **Medical** - Emergency triage
3. **Education** - Student attention allocation
4. **Diplomacy** - Negotiation focus
5. **Ecosystem** - Conservation priorities
6. **Software** - Bug triage
7. **Emergency** - Disaster response
8. **Moderation** - Content prioritization
9. **Manufacturing** - Quality control
10. **Systems** - Real-time monitoring

Key findings:
- **Universal phase transitions**: All domains show Abundance → Scarcity → Crisis
- **Binary decision rate**: 80% of allocation decisions are binary (attend/ignore)
- **Consistent thresholds**: 0.0% coefficient of variation across domains

## API Reference

### Classes

#### `AttentionItem(name, gain, cost)`
Represents an item that can receive attention.

- `name`: Identifier
- `gain`: Expected benefit (0.0 - 1.0)
- `cost`: Resource cost
- `compute_priority(lambda_, gamma, n_items)`: Calculate priority score

#### `BCPModel(lambda_scale, lambda_epsilon, gamma, abundance_threshold, crisis_threshold)`
The core BCP allocation model.

- `compute_lambda(budget)`: Calculate metabolic pressure
- `determine_phase(budget)`: Get current phase
- `allocate(items, budget)`: Perform attention allocation
- `sweep_budgets(items_fn, budget_range)`: Test across budgets
- `find_phase_thresholds(items_fn, budget_range)`: Find transition points

#### `BCPResult`
Result of allocation containing:

- `attended`: List of attended item names
- `ignored`: List of ignored item names
- `total_cost`: Resources consumed
- `phase`: Current Phase enum
- `lambda_`: Computed metabolic pressure
- `n_attended`, `n_ignored`, `attention_fraction`: Computed properties

#### `BCPMonitor`
Real-time monitoring with BCP triage.

- `add_task(name, gain, cost, collector)`: Register metric
- `remove_task(name)`: Unregister metric
- `sample(budget)`: Take single sample
- `run(budget_fn, interval, duration, callback)`: Continuous monitoring

### Enums

#### `Phase`
- `Phase.ABUNDANCE`: High budget, attend to everything
- `Phase.SCARCITY`: Moderate budget, triage active
- `Phase.CRISIS`: Low budget, focus on single item

## License

GPL-3.0

## Author

Aldrin Payopay <aldrin.gdf@gmail.com>

## Repository

https://github.com/mrdirno/nested-resonance-memory-archive
