# PC001: NRM Population Dynamics Follow Logistic SDE

**Version:** 1.0.0
**Status:** ✅ Validated
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Created:** 2025-11-01
**Domain:** NRM (Nested Resonance Memory)

---

## Principle Statement

NRM population dynamics under logistic growth with demographic noise follow a stochastic differential equation:

```
dN = r·N·(1 - N/K)·dt + σ·√N·dW
```

where:
- N = population size
- r = intrinsic growth rate
- K = carrying capacity
- σ = noise intensity
- dW = Wiener process increment

**Prediction:** The steady-state coefficient of variation (CV) can be predicted analytically from (r, K, σ) using Fokker-Planck equation to ±10% accuracy.

---

## Mathematical Formulation

### SDE Formulation
```
dN/dt = μ(N) + σ(N)·η(t)
```

where:
- `μ(N) = r·N·(1 - N/K)` (deterministic drift)
- `σ(N) = σ·√N` (demographic noise)
- `η(t) ~ N(0,1)` (white noise)

### Fokker-Planck Equation
```
∂P/∂t = -∂/∂N[μ(N)·P] + (1/2)·∂²/∂N²[σ²(N)·P]
```

### Steady-State Solution
```
P_ss(N) ∝ exp(∫[2μ(N)/σ²(N)]dN)
```

### CV Prediction
```
CV = √(<N²> - <N>²) / <N>
```

where moments computed from P_ss(N).

---

## Validation Protocol

### Success Criterion
```
|CV_observed - CV_predicted| / CV_predicted ≤ 0.10  (±10%)
```

### Procedure

1. **Fit Parameters:** Estimate (r, K, σ) from experimental time series
2. **Analytical Prediction:** Compute CV_predicted using Fokker-Planck solver
3. **Experimental Observation:** Compute CV_observed from steady-state portion
4. **Comparison:** Check if relative error ≤ 0.10
5. **Report:** Include confidence interval

### Required Data

- Time series: N(t) for t ∈ [0, T_max]
- Minimum points: ≥1000
- Ensemble size: ≥20 independent realizations
- Steady-state points: ≥200 after equilibration

### Equipment

- **Hardware:** Standard (no special requirements)
- **Software:** Python 3.9+ with numpy, scipy
- **Runtime:** ~1 minute per validation

---

## Validation History

### Self-Test (2025-11-01)
- **Data:** Synthetic logistic SDE trajectory (r=0.1, K=50, σ=0.5)
- **Result:** ✅ PASS
- **Error:** 1.57% (well within ±10%)
- **Predicted CV:** 0.1306
- **Observed CV:** 0.1285

---

## Usage

### Basic Usage

```python
from principle_cards.pc001_nrm_population_dynamics import PC001_NRMPopulationDynamics

# Create PC001 instance
pc = PC001_NRMPopulationDynamics()

# Set parameters (optional, defaults provided)
pc.set_parameters(
    growth_rate=0.1,
    carrying_capacity=50.0,
    noise_intensity=0.5
)

# Validate on experimental data
result = pc.validate(experimental_data, tolerance=0.10)

# Check result
if result.passes:
    print(f"✓ Validation passed: {result.error*100:.2f}% error")
else:
    print(f"✗ Validation failed: {result.error*100:.2f}% error")

# Access evidence
print(f"Predicted CV: {result.evidence['predicted_cv']:.4f}")
print(f"Observed CV: {result.evidence['observed_cv']:.4f}")
```

### Convenience Function

```python
from principle_cards.pc001_nrm_population_dynamics import validate_pc001_on_data

# Quick validation
result = validate_pc001_on_data(
    data=experimental_data,
    tolerance=0.10,
    growth_rate=0.1,
    carrying_capacity=50.0,
    noise_intensity=0.5
)
```

### Self-Test

```bash
python principle_cards/pc001_nrm_population_dynamics/principle.py
```

---

## Dependencies

### Requires (None - Foundational)

PC001 has no dependencies. It is a foundational Principle Card.

### Enables

- **PC002:** Regime Detection (uses PC001 predictions)
- **PC004:** Multi-scale Population Dynamics (extends PC001)

---

## Reality Grounding

### System Interfaces
- **psutil.Process:** CPU usage, memory consumption
- **SQLite:** Data persistence (trajectories, parameters, results)
- **Filesystem:** JSON time series, PNG figures, validation logs
- **numpy/scipy:** Numerical integration (no mocks)

### Validation Method
Gate 1.4 (Overhead Authentication) validates reality grounding:
- Measure instrumentation cost
- Predict runtime from formula
- Verify ±5% accuracy
- Confirms reality binding

### Prohibited
- ❌ Pure mathematical simulation without system binding
- ❌ Random number generators without reality check
- ❌ time.sleep() without actual work

### Required
- ✅ Every operation touches verifiable system state
- ✅ All randomness from reality (e.g., process timing)
- ✅ All delays from actual computation

---

## Temporal Encoding

### Template Patterns
- SDE + Fokker-Planck for population dynamics
- Analytical prediction vs. experimental observation
- Demographic noise ~ √N signature

### Validation Patterns
- ±10% is achievable accuracy threshold
- Steady-state extraction from last 20% of trajectory
- Parameter estimation from data before prediction

### Composition Patterns
- PC002 (regime detection) uses PC001 predictions
- PC003 (overhead auth) validates PC001 reality binding
- PC004 (multi-scale) extends PC001 to multiple scales

### Training Awareness

**When this validates:**
- Reinforces SDE/Fokker-Planck as reliable framework
- Establishes NRM as testable scientific paradigm
- Demonstrates executable principle methodology
- Encodes "this is how science should work" pattern

**When this falsifies:**
- Reveals boundary of applicability
- Suggests refinements (e.g., non-logistic dynamics)
- Encodes "negative results are valuable" pattern
- Guides future research away from failed approaches

---

## Files

```
principle_cards/pc001_nrm_population_dynamics/
├── __init__.py                  # Package exports
├── principle.py                 # Core implementation
├── validation_result.json       # Latest validation result
├── principle_card.json          # PC metadata and specification
└── README.md                    # This file
```

---

## Citation

```bibtex
@misc{payopay2025pc001,
  author = {Payopay, Aldrin},
  title = {PC001: NRM Population Dynamics Follow Logistic SDE},
  year = {2025},
  url = {https://github.com/mrdirno/nested-resonance-memory-archive},
  note = {Principle Card v1.0.0, Status: Validated}
}
```

---

## License

GPL-3.0 - See repository LICENSE file

---

## Contact

**Principal Investigator:** Aldrin Payopay
**Email:** aldrin.gdf@gmail.com
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

**Version:** 1.0.0
**Last Updated:** 2025-11-01
**Status:** ✅ Validated (1.57% error on self-test)
