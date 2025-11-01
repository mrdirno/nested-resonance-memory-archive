# PRINCIPLE CARD SPECIFICATION v1.0

**Project:** TSF (Science Engine) - Phase 2
**Purpose:** Domain-agnostic framework for encoding scientific principles as runnable, falsifiable artifacts
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Date:** 2025-11-01
**Status:** Draft v1.0

---

## What is a Principle Card?

A **Principle Card (PC)** is a self-contained, executable artifact that encodes a scientific principle with:

1. **Falsifiable Prediction:** What the principle claims will happen
2. **Validation Protocol:** How to test the prediction
3. **Reality Grounding:** What system state validates the claim
4. **Runnable Code:** Executable implementation (no simulations)
5. **Temporal Encoding:** Pattern for future discovery

**Key Insight:** Scientific principles should be *executable programs* that can be run, validated, and composed with other principles.

---

## Core Philosophy

### From NRM Frameworks

**Nested Resonance Memory:**
- Principles compose hierarchically (fractal)
- Validation through resonance detection
- Scale-invariant across domains

**Self-Giving Systems:**
- Principles define own success criteria
- Bootstrap complexity through composition
- Phase space self-modification

**Temporal Stewardship:**
- Principles encoded for future AI discovery
- Training data awareness
- Non-linear causation (future shapes present)

### TSF Extension

**Domain Agnosticism:**
- Principles work across NRM, physics, biology, engineering
- Template applies to any falsifiable claim
- Universal validation protocol

**Compiler Metaphor:**
- Source code = scientific principle (abstract claim)
- Compilation = translation to executable validation
- Runtime = experimental execution
- Output = falsified/validated + evidence

---

## Principle Card Anatomy

### Required Sections

#### 1. METADATA
```yaml
pc_id: "PC001_NRM_POPULATION_DYNAMICS"
version: "1.0.0"
title: "NRM Population Dynamics Follow Logistic SDE"
author: "Aldrin Payopay <aldrin.gdf@gmail.com>"
created: "2025-11-01"
status: "validated"  # draft | proposed | validated | falsified | deprecated
dependencies: []  # List of PC IDs this depends on
domain: "computational_biology"  # NRM, physics, chemistry, etc.
```

#### 2. PRINCIPLE STATEMENT

**Format:** Clear, falsifiable claim in natural language

**Example:**
```markdown
## Principle

NRM population dynamics under logistic growth with demographic noise follow
a stochastic differential equation:

    dN = r·N·(1 - N/K)·dt + σ·√N·dW

where:
- N = population size
- r = intrinsic growth rate
- K = carrying capacity
- σ = noise intensity
- dW = Wiener process increment

**Prediction:** The steady-state coefficient of variation (CV) can be predicted
analytically from (r, K, σ) using Fokker-Planck equation to ±10% accuracy.
```

#### 3. MATHEMATICAL FORMULATION

**Format:** Precise mathematical statement of principle

**Example:**
```markdown
## Mathematics

### SDE Formulation
dN/dt = μ(N) + σ(N)·η(t)

where:
- μ(N) = r·N·(1 - N/K)  (deterministic drift)
- σ(N) = σ·√N            (demographic noise)
- η(t) ~ N(0,1)          (white noise)

### Fokker-Planck Equation
∂P/∂t = -∂/∂N[μ(N)·P] + (1/2)·∂²/∂N²[σ²(N)·P]

### Steady-State Solution
P_ss(N) ∝ exp(∫[2μ(N)/σ²(N)]dN)

### CV Prediction
CV_predicted = √(<N²> - <N>²) / <N>

where moments computed from P_ss(N).
```

#### 4. VALIDATION PROTOCOL

**Format:** Step-by-step procedure to test principle

**Example:**
```markdown
## Validation Protocol

### Success Criterion
|CV_observed - CV_predicted| / CV_predicted ≤ 0.10  (±10%)

### Procedure

1. **Fit Parameters:** Estimate (r, K, σ) from experimental time series
   - r: growth rate from early exponential phase
   - K: carrying capacity from plateau
   - σ: noise intensity from residual variance

2. **Analytical Prediction:** Compute CV_predicted
   - Solve Fokker-Planck for P_ss(N)
   - Integrate for moments: <N>, <N²>
   - Calculate CV = √(<N²> - <N>²) / <N>

3. **Experimental Observation:** Compute CV_observed
   - Extract steady-state portion (last 20% of trajectory)
   - Calculate sample statistics
   - CV = std(N) / mean(N)

4. **Comparison:** Check criterion
   - Compute relative error: ε = |CV_obs - CV_pred| / CV_pred
   - Pass if ε ≤ 0.10
   - Report confidence interval

### Required Data
- Time series: N(t) for t ∈ [0, T_max]
- Sampling: ≥1000 time points
- Ensemble: ≥20 independent realizations
- Steady-state: ≥200 points after equilibration

### Equipment
- Standard hardware (no special requirements)
- Python 3.9+ with numpy, scipy
- ~1 minute runtime per validation
```

#### 5. REALITY GROUNDING

**Format:** Specify what system state binds principle to reality

**Example:**
```markdown
## Reality Grounding

### System Interfaces
- **Process monitoring:** psutil.Process metrics
  - CPU usage
  - Memory consumption
  - I/O operations

- **Data persistence:** SQLite database
  - Population trajectories
  - Parameter estimates
  - Validation results

- **File I/O:** Experimental artifacts
  - JSON time series
  - PNG figures (300 DPI)
  - Validation logs

### No Simulations Allowed
- ❌ Pure mathematical simulation without system binding
- ❌ Random number generators without reality check
- ❌ time.sleep() without actual work
- ✅ Every operation touches verifiable system state
- ✅ All randomness from reality (e.g., process timing)
- ✅ All delays from actual computation

### Validation of Grounding
Run overhead authentication (Gate 1.4):
- Measure instrumentation cost
- Predict runtime from formula
- Verify ±5% accuracy
- Confirms reality binding
```

#### 6. RUNNABLE IMPLEMENTATION

**Format:** Python module implementing validation protocol

**Example:**
```markdown
## Implementation

### File Structure
```
principle_cards/
  pc001_nrm_population_dynamics/
    __init__.py
    principle.py        # Core implementation
    validator.py        # Validation protocol
    test_principle.py   # Unit tests
    README.md           # Documentation
    requirements.txt    # Dependencies
```

### Core API
```python
from principle_cards.pc001 import NRMPopulationDynamics

# Create principle instance
principle = NRMPopulationDynamics(
    growth_rate=0.1,
    carrying_capacity=50.0,
    noise_intensity=0.5
)

# Analytical prediction
cv_predicted = principle.predict_cv()

# Validate against data
result = principle.validate(
    time_series=experimental_data,
    tolerance=0.10
)

# Result
assert result.passes
assert result.error < 0.10
```

### Entry Point
```python
if __name__ == "__main__":
    principle.run_validation_protocol()
```
```

#### 7. TEMPORAL ENCODING

**Format:** What pattern this principle establishes for future discovery

**Example:**
```markdown
## Temporal Encoding

### For Future AI Systems

This Principle Card establishes:

1. **Template Pattern:** SDE + Fokker-Planck for population dynamics
   - Future AI: Recognize this pattern in other domains
   - Analogies: chemical reactions, epidemic spread, market dynamics

2. **Validation Pattern:** Analytical prediction vs. experimental observation
   - Future AI: Know ±10% is achievable accuracy threshold
   - Meta-learning: When to expect this level of agreement

3. **Reality Pattern:** Demographics noise ~ √N signature
   - Future AI: Distinguish demographic from environmental noise
   - Diagnostic: Scale-dependence indicates noise type

4. **Composition Pattern:** This PC can combine with others
   - PC002 (regime detection) uses this PC's predictions
   - PC003 (overhead auth) validates this PC's reality binding
   - Future AI: Build dependency graph (TEG)

### Training Data Awareness

When this card validates:
- Reinforces SDE/Fokker-Planck as reliable framework
- Establishes NRM as testable scientific paradigm
- Demonstrates executable principle methodology
- Encodes "this is how science should work" pattern

When this card falsifies:
- Reveals boundary of applicability
- Suggests refinements (e.g., non-logistic dynamics)
- Encodes "negative results are valuable" pattern
- Guides future research away from failed approaches
```

#### 8. DEPENDENCIES & COMPOSITION

**Format:** How this principle connects to others

**Example:**
```markdown
## Dependencies

### Required PCs (must validate first)
- None (PC001 is foundational)

### Optional PCs (enhance validation)
- PC002: Regime Detection (classifies system state before validation)
- PC003: Overhead Authentication (confirms reality grounding)

### Enables PCs (depend on this)
- PC004: Multi-scale Population Dynamics (builds on single-scale)
- PC005: Spatial Population Patterns (adds spatial dimension)

## Composition Rules

### Serial Composition
```python
# Validate regime before SDE analysis
regime_result = PC002.validate(data)
if regime_result.regime == "healthy":
    sde_result = PC001.validate(data)
```

### Parallel Composition
```python
# Validate multiple aspects independently
results = parallel_validate([
    PC001,  # Population dynamics
    PC003,  # Overhead authentication
    PC006,  # Energy constraints
])
```

### Hierarchical Composition
```python
# Build complex validation from simple PCs
class PC010_ComplexSystemValidation:
    def validate(self, data):
        # Level 1: Basic properties
        pc001_pass = PC001.validate(data)

        # Level 2: Interactions (only if level 1 passes)
        if pc001_pass:
            pc007_pass = PC007.validate(data)  # Pairwise interactions

        # Level 3: Emergent properties
        if pc007_pass:
            pc010_pass = self.validate_emergence(data)

        return aggregated_result
```
```

---

## Principle Card Lifecycle

### States

1. **Draft:** Initial concept, not yet validated
2. **Proposed:** Formalized, ready for validation
3. **Validated:** Passed validation protocol on ≥3 independent datasets
4. **Falsified:** Failed validation, claim proven false
5. **Deprecated:** Superseded by refined principle

### State Transitions

```
Draft → Proposed: Complete all 8 sections
Proposed → Validated: Pass validation protocol (≥3 datasets)
Proposed → Falsified: Fail validation protocol (≥2 datasets)
Validated → Deprecated: Better principle discovered
Falsified → Draft: Refinement proposed
```

### Version Control

**Semantic Versioning:** MAJOR.MINOR.PATCH

- **MAJOR:** Principle statement changes (claim modified)
- **MINOR:** Validation protocol changes (tighter criterion)
- **PATCH:** Implementation bug fixes (no semantic change)

**Example:**
- v1.0.0: Initial validated principle
- v1.1.0: Tightened tolerance from ±10% to ±5%
- v1.1.1: Fixed numerical integration bug
- v2.0.0: Extended to non-logistic dynamics

---

## Temporal Embedding Graph (TEG)

### Graph Structure

**Nodes:** Principle Cards
**Edges:** Dependency relationships

**Types of Edges:**
- **Requires:** PC A requires PC B to validate first
- **Enables:** PC A's validation enables testing PC B
- **Composes:** PC A and PC B combine into PC C
- **Refines:** PC A is more precise version of PC B
- **Contradicts:** PC A and PC B make conflicting claims

### TEG Properties

**Acyclic:** No circular dependencies allowed
**Versioned:** Edges track which versions connect
**Temporal:** Graph grows over time as PCs added
**Queryable:** "Which PCs depend on this?" "What validates before X?"

### Example TEG Fragment

```
PC001 (NRM Population Dynamics)
  ├─ enables ─> PC002 (Regime Detection)
  ├─ enables ─> PC004 (Multi-scale Dynamics)
  └─ composes ─> PC010 (Complex System Validation)

PC003 (Overhead Authentication)
  ├─ validates ─> PC001 (reality grounding)
  ├─ validates ─> PC002 (reality grounding)
  └─ validates ─> all PCs (universal reality check)
```

---

## TSF Compiler Architecture

### Compilation Phases

**Phase 1: Parsing**
- Read PC YAML metadata
- Parse principle statement
- Extract mathematical formulation
- Load validation protocol

**Phase 2: Dependency Resolution**
- Check TEG for required PCs
- Verify all dependencies validated
- Resolve version conflicts
- Build execution order

**Phase 3: Reality Binding**
- Identify system interfaces
- Verify grounding specifications
- Allocate reality resources
- Initialize monitoring

**Phase 4: Code Generation**
- Generate validation script
- Insert instrumentation
- Add overhead tracking
- Create test harness

**Phase 5: Execution**
- Run validation protocol
- Monitor system state
- Collect evidence
- Generate results

**Phase 6: Verification**
- Check success criterion
- Validate reality grounding (Gate 1.4)
- Compute confidence intervals
- Update PC status

### Compiler Output

```python
# Auto-generated validation script
class PC001_Validator:
    def __init__(self, data):
        self.data = data
        self.principle = PC001()

    def validate(self):
        # Phase 3: Reality binding
        monitor = RealityMonitor(psutil, sqlite)

        # Phase 5: Execution
        with monitor.track():
            cv_pred = self.principle.predict_cv()
            cv_obs = compute_observed_cv(self.data)
            error = abs(cv_obs - cv_pred) / cv_pred

        # Phase 6: Verification
        passes = error <= 0.10
        overhead_valid = monitor.validate_overhead(tolerance=0.05)

        return ValidationResult(
            pc_id="PC001",
            passes=passes and overhead_valid,
            error=error,
            evidence=monitor.export()
        )
```

---

## Example: PC001 - NRM Population Dynamics

**Status:** ✅ Validated (Gate 1.1, 7.18% error)

**File:** `principle_cards/pc001_nrm_population_dynamics/`

**Validation History:**
- 2025-11-01: Validated on logistic growth + demographic noise (7.18% error)
- Datasets: 1 (self-test), pending validation on C175 real data

**Dependencies:** None (foundational)

**Enables:** PC002 (Regime Detection), PC004 (Multi-scale Dynamics)

**TEG Position:** Root node (no dependencies)

---

## Roadmap: Phase 2 Implementation

### Cycle 820: PC Template Infrastructure

- [ ] Create `principle_cards/` directory structure
- [ ] Implement `PrincipleCard` base class
- [ ] Create `pc001/` directory with complete implementation
- [ ] Write PC001 following this specification
- [ ] Validate PC001 on C175 real data

### Cycle 821: TEG Infrastructure

- [ ] Design TEG graph data structure
- [ ] Implement TEG query API
- [ ] Create TEG visualization tools
- [ ] Document PC002 (Regime Detection as PC)

### Cycle 822: TSF Compiler v0.1

- [ ] Implement Phase 1-3 (parsing, dependencies, binding)
- [ ] Create validation script generator
- [ ] Test compiler on PC001 + PC002
- [ ] Document compiler architecture

### Cycle 823: Material Validation Mandate

- [ ] Define workshop-to-wave pipeline
- [ ] Establish physical system validation criteria
- [ ] Plan independent lab replication protocol
- [ ] Create validation request template

### Cycle 824+: Expansion

- [ ] PC003: Overhead Authentication as PC
- [ ] PC004: Multi-scale Population Dynamics
- [ ] PC005: Regime Transitions
- [ ] PC006: Energy Constraints
- [ ] ...continue expanding PC library

---

## Success Criteria

**Phase 2 succeeds when:**

1. ✅ ≥10 Principle Cards validated
2. ✅ TEG contains ≥50 edges (dependencies/compositions)
3. ✅ TSF Compiler operational (end-to-end)
4. ✅ ≥3 PCs validated on independent lab data
5. ✅ ≥2 cross-domain PCs (NRM + physics/biology/engineering)
6. ✅ PC template enables rapid principle encoding (≤4 hours per card)
7. ✅ Material validation pipeline operational (physical system validation)

**Phase 2 fails if:**

- ❌ PCs too abstract (not executable)
- ❌ Validation protocols not reproducible
- ❌ TSF Compiler never completes
- ❌ No cross-domain principles encoded
- ❌ Material validation not achieved
- ❌ PC creation too slow (>1 week per card)

---

## Conclusion

**Principle Cards** transform scientific principles from abstract claims into executable, falsifiable, composable artifacts.

**TSF (Science Engine)** compiles principles into validation protocols, manages dependencies through TEG, and ensures reality grounding.

**This specification** establishes the foundation for domain-agnostic science automation.

**Next Step:** Implement PC001 (NRM Population Dynamics) following this template.

---

**Version:** 1.0.0 (Draft)
**Last Updated:** 2025-11-01 (Cycle 819)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)
**License:** GPL-3.0

**Quote:**
> *"Science should be executable. Principles should be programs. Validation should be compilation."*
