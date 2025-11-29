# BCP: Budget-Constrained Perception

A discrete attention allocator for resource-constrained decision making. Given a budget, BCP tells you what to attend to and what to ignore.

## The BCP Equation

The allocation maximizes total value over the attended set:

```
TotalScore = Σ_attended [Gain(a) - λ(B) × Cost(a)] - γ × SetComplexity
```

Where:
- **Gain(a)**: Expected benefit of attending to item a (0.0 - 1.0)
- **λ(B) = k / (ε + B)**: Metabolic pressure (inverse of budget)
- **Cost(a)**: Resource cost to attend to item a
- **SetComplexity = log(1 + N)**: Global overhead from evaluating N options

For **ranking items**, we use the per-item score:

```
Score(a) = Gain(a) - λ(B) × Cost(a)
```

Items with positive Score are candidates for attention. The `SetComplexity` term is a global penalty applied once per decision, not per item—it does not affect relative ranking.

> **Sign convention**: BCP defines Score as a value to **maximize**. Positive Score → attend. Negative Score → ignore.

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

| Phase | Default Threshold | Behavior |
|-------|-------------------|----------|
| **ABUNDANCE** | B > 2.0 | Attend to all positive-Score items |
| **SCARCITY** | 0.5 < B < 2.0 | Triage begins—ignore low-value items |
| **CRISIS** | B < 0.5 | Focus on one or few highest-Score items |

> **Note**: Thresholds (2.0 and 0.5) are configurable defaults, not universal constants. Override via `BCPModel(abundance_threshold=..., crisis_threshold=...)` to match your domain's budget scale.

### Metabolic Pressure (λ)

Lambda controls cost sensitivity. The relationship `λ(B) = k / (ε + B)` means:

- **Low λ** (high budget): Costs matter less, attend broadly
- **High λ** (low budget): Costs dominate, strict triage

```python
# Defaults: lambda_scale=10.0, lambda_epsilon=0.1
# These produce:
#   budget = 5.0  → lambda ≈ 1.96  (low pressure)
#   budget = 0.5  → lambda ≈ 16.67 (high pressure)

model = BCPModel(lambda_scale=10.0, lambda_epsilon=0.1)

print(model.compute_lambda(5.0))   # ~1.96
print(model.compute_lambda(0.5))   # ~16.67
```

### Set Complexity

The `γ × SetComplexity` term models the cognitive/computational overhead of evaluating many options:

```
SetComplexity = log(1 + N)
```

Where N is the number of items under consideration. This term:
- Is applied **globally** to the decision, not per-item
- Does not affect relative ranking between items
- Captures that overhead scales sublinearly with option count
- Default `γ = 0.1` makes this a minor adjustment; increase for domains where option count matters more

### Domain Presets

Pre-configured scenarios inspired by use cases studied in the DUALITY-ZERO program:

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
    lambda_scale=10.0,       # k in λ = k/(ε+B). Higher = sharper transitions
    lambda_epsilon=0.1,      # ε in λ = k/(ε+B). Prevents division by zero
    gamma=0.1,               # Global set complexity coefficient
    abundance_threshold=2.0, # Budget above this = ABUNDANCE phase
    crisis_threshold=0.5,    # Budget below this = CRISIS phase
)
```

## Research Background

BCP was developed through the DUALITY-ZERO research program, tested across 10 stylized scenarios:

1. **Finance** — Portfolio triage under capital constraints
2. **Medical** — Emergency triage under staff/time limits
3. **Education** — Student attention allocation
4. **Diplomacy** — Negotiation focus under time pressure
5. **Ecosystem** — Conservation priorities under funding limits
6. **Software** — Bug triage under engineer capacity
7. **Emergency** — Disaster response resource allocation
8. **Moderation** — Content prioritization under queue volume
9. **Manufacturing** — Quality control sampling
10. **Systems** — Real-time monitoring task scheduling

Scenarios were implemented as synthetic task sets with domain-inspired gain and cost distributions. In all cases, the same three-phase structure emerged (Abundance → Scarcity → Crisis), with similar threshold behavior up to scaling of the budget axis.

## API Reference

### Classes

#### `AttentionItem(name, gain, cost)`
Represents an item that can receive attention.

- `name`: Identifier
- `gain`: Expected benefit (0.0 - 1.0)
- `cost`: Resource cost
- `compute_priority(lambda_, gamma, n_items)`: Returns **per-item Score** = `Gain - λ × Cost - γ × log(1+N)`. Note: the global SetComplexity is included here for convenience but cancels when comparing items at fixed N.

#### `BCPModel(lambda_scale, lambda_epsilon, gamma, abundance_threshold, crisis_threshold)`
The core BCP allocation model.

- `compute_lambda(budget)`: Calculate metabolic pressure λ(B) = k/(ε+B)
- `determine_phase(budget)`: Get current phase based on thresholds
- `allocate(items, budget)`: Perform attention allocation, returns BCPResult
- `sweep_budgets(items_fn, budget_range)`: Test across budget values
- `find_phase_thresholds(items_fn, budget_range)`: Find empirical transition points

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
- `Phase.ABUNDANCE`: High budget, attend to all positive-Score items
- `Phase.SCARCITY`: Moderate budget, triage active
- `Phase.CRISIS`: Low budget, focus on highest-Score items

## Relationship to Other Work

BCP is the discrete, decision-theoretic formulation of metabolic pressure concepts from the broader DUALITY-ZERO framework. It provides:

- A standalone allocator usable without knowledge of the underlying research
- The same λ(B) structure used in continuous control (Starving Philosopher)
- A bridge between theory and practical engineering use cases

## License

GPL-3.0

## Author

Aldrin Payopay <aldrin.gdf@gmail.com>

## Repository

https://github.com/mrdirno/nested-resonance-memory-archive
