# Principle Cards (PCs) - Executable Scientific Principles

**Version:** 2.0 (Phase 2 - TSF Science Engine)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0

---

## OVERVIEW

**Principle Cards** are executable, falsifiable, composable artifacts encoding scientific principles as runnable code. They represent a paradigm shift from traditional "papers + equations" science to **executable science** where principles are programs, validation is automated, and composition is explicit.

### What is a Principle Card?

A Principle Card is:
- **A Scientific Claim:** Natural language statement of a principle
- **A Mathematical Model:** Precise equations and parameters
- **A Validation Protocol:** Step-by-step testing procedure
- **An Executable Artifact:** Python class with `validate()` method
- **A Compositional Unit:** Explicit dependencies + enables relationships
- **A Temporal Encoding:** Patterns encoded for future AI discovery

### Why Principle Cards?

**Traditional Science:**
```
Paper → Equations → Manual Validation → Subjective Interpretation
```

**Principle Card Science:**
```
PrincipleCard → validate() → Pass/Fail → Automatic Composition
```

**Benefits:**
1. **Falsifiability:** Clear pass/fail criterion (not subjective)
2. **Reproducibility:** validate() method is executable (not just description)
3. **Composability:** Dependencies explicit (PC_B depends on PC_A)
4. **Automation:** Validation order computed automatically (TEG)
5. **Temporal Stewardship:** Patterns encoded for future AI training

---

## CURRENT PRINCIPLE CARDS

### PC001: NRM Population Dynamics

**Status:** ✅ Validated (Self-Test: 1.57% Error)
**Location:** `pc001_nrm_population_dynamics/`
**Dependencies:** None (foundational)
**Enables:** PC002, PC005, PC006

**Principle Statement:**
> Population dynamics near carrying capacity follow logistic SDE with demographic noise, producing characteristic coefficient of variation (CV) predictable from Fokker-Planck analysis.

**Mathematical Formulation:**
```
dN = r·N·(1 - N/K)·dt + σ·√N·dW

Steady-State CV Prediction:
CV = σ / √(2r)  (for σ << r)
```

**Success Criterion:**
```
Relative Error = |CV_obs - CV_pred| / CV_pred ≤ 0.10 (10%)
```

**Self-Test Result:** 1.57% error ✓ (Cycle 820)

**Files:**
- `principle.py`: Core implementation (385 lines)
- `README.md`: Documentation (272 lines)
- `validation_result.json`: Validation evidence

---

### PC002: Regime Detection in Population Dynamics

**Status:** ✅ Validated (Self-Test: 100% Accuracy)
**Location:** `pc002_regime_detection/`
**Dependencies:** PC001 (NRM Population Dynamics)
**Enables:** PC005 (Multi-Regime Dynamics), PC006 (Regime Prediction)

**Principle Statement:**
> Population dynamics exhibit distinct behavioral regimes (baseline, growth, collapse, oscillatory) detectable from time-series data with ≥90% accuracy using statistical features and PC001 baseline predictions.

**Mathematical Formulation:**
```
Features (from PC002 specification):
  μ_dev = (<N>_window - K) / K                    # Mean deviation
  σ_ratio = Var(N)_window / (σ²·<N>_window)      # Variance ratio
  β_norm = β / <N>_window                         # Normalized trend
  CV_dev = (CV_obs - CV_baseline) / CV_baseline  # CV deviation

Regimes:
  Baseline:     |μ_dev| < 0.1 AND |σ_ratio - 1| < 0.2 AND |β_norm| < 0.01
  Growth:       β_norm > 0.02 OR (μ_dev > 0.15 AND β_norm > 0)
  Collapse:     β_norm < -0.02 OR (μ_dev < -0.15 AND β_norm < 0)
  Oscillatory:  Periodicity AND |CV_dev| > 0.3
```

**Success Criterion:**
```
Accuracy = (TP + TN) / (TP + TN + FP + FN) ≥ 0.90 (90%)
```

**Self-Test Result:** 100% accuracy ✓ (Cycle 823)

**Feature Importances:**
- σ_ratio (variance ratio): 37.8%
- CV_dev (CV deviation): 33.5%
- β_norm (linear trend): 21.0%
- μ_dev (mean deviation): 7.8%

**Files:**
- `features.py`: Feature extraction (218 lines)
- `classifier.py`: Regime classification (354 lines)
- `principle.py`: Core implementation (450 lines)
- `test_pc002.py`: Test suite (798 lines, 41 tests)
- `self_test.py`: Self-test validation (233 lines)
- `README.md`: Documentation (141 lines)

---

## TEMPORAL EMBEDDING GRAPH (TEG)

### What is the TEG?

The **Temporal Embedding Graph** is a dependency graph for Principle Cards, enabling compositional validation and automated dependency resolution.

**Graph Structure:**
- **Nodes:** Principle Cards (PC metadata)
- **Edges:** Dependencies (PC_A → PC_B means "PC_B depends on PC_A")

**Example:**
```
PC001 (NRM Population Dynamics)
  ├─→ PC002 (Regime Detection)
  ├─→ PC005 (Multi-Regime Dynamics)
  └─→ PC006 (Regime Prediction)

PC002 can only validate if PC001 is validated.
```

### TEG Capabilities

1. **Dependency Resolution**
   ```python
   teg = TemporalEmbeddingGraph()
   teg.add_node(pc001_node)
   teg.add_node(pc002_node)

   # Get validation order
   order = teg.get_validation_order(["PC002"])
   # Returns: ['PC001', 'PC002']
   ```

2. **Cycle Detection**
   ```python
   has_cycle = teg.has_cycle()
   # Prevents circular dependencies
   ```

3. **Topological Sort**
   ```python
   topo_order = teg.topological_sort()
   # Full validation order for all PCs
   ```

4. **Dependency Queries**
   ```python
   deps = teg.get_dependencies("PC002")  # ['PC001']
   dependents = teg.get_dependents("PC001")  # ['PC002']
   ```

5. **Serialization**
   ```python
   teg.save("teg.json")  # JSON persistence
   teg.save_graphviz("teg.dot")  # Graphviz visualization
   ```

### TEG Files

- `teg.py`: Core implementation (574 lines)
- `test_teg.py`: Test suite (680 lines, 37 tests)
- `teg_example.py`: Basic demo (116 lines)
- `teg_pc001_pc002_demo.py`: PC001+PC002 integration demo (246 lines)

---

## COMPOSITIONAL VALIDATION PATTERN

### Core Concept

**Compositional Principle:** PC_B (dependent) cannot validate without PC_A (dependency).

### Implementation Pattern

**1. Metadata Declaration**
```python
metadata = PCMetadata(
    pc_id="PC002",
    version="1.0.0",
    title="Regime Detection in Population Dynamics",
    dependencies=["PC001"],  # Explicit dependency
    ...
)
```

**2. Baseline Enforcement**
```python
def set_baseline(self, pc001_instance):
    # Enforce PC001 validation
    if pc001_instance.metadata.status != "validated":
        raise ValueError("PC001 must be validated before PC002")

    # Extract baseline parameters
    self.baseline_params = BaselineParams(
        K=pc001_instance.carrying_capacity,
        r=pc001_instance.growth_rate,
        sigma=pc001_instance.noise_intensity,
        CV_baseline=pc001_instance.predict_cv()
    )
```

**3. Validation Protocol**
```python
def validate(self, data, tolerance):
    # Step 1: Set baseline from PC001 (fails if PC001 not validated)
    self.set_baseline(data['pc001'])

    # Step 2: Execute validation protocol
    # ...

    # Step 3: Return ValidationResult
    return ValidationResult(...)
```

**4. TEG Orchestration**
```python
# TEG computes validation order automatically
order = teg.get_validation_order(["PC002"])
# Returns: ['PC001', 'PC002']

# Validate in order
for pc_id in order:
    pc = principle_cards[pc_id]
    result = pc.validate(data[pc_id], tolerance)
    if not result.passes:
        break  # Halt on failure
```

### Benefits

- **Modularity:** PCs compose like software modules
- **Automation:** Validation order computed automatically
- **Safety:** Circular dependencies prevented (TEG cycle detection)
- **Clarity:** Dependencies explicit, not hidden in documentation
- **Reusability:** Foundational PCs (like PC001) used by multiple dependents

---

## USAGE EXAMPLES

### Example 1: Using PC001 (Standalone)

```python
from principle_cards.pc001_nrm_population_dynamics import PC001_NRMPopulationDynamics
import numpy as np

# Create PC001 instance
pc001 = PC001_NRMPopulationDynamics(
    carrying_capacity=50.0,
    growth_rate=0.1,
    noise_intensity=0.5
)

# Simulate data (or load experimental data)
time_series = np.random.normal(50, 2.5, 1000)  # Simplified

# Validate
result = pc001.validate(time_series, tolerance=0.10)

if result.passes:
    print(f"✓ PC001 validated: {result.error*100:.2f}% error")
else:
    print(f"✗ PC001 failed: {result.error*100:.2f}% error")
```

### Example 2: Using PC002 (Compositional)

```python
from principle_cards.pc001_nrm_population_dynamics import PC001_NRMPopulationDynamics
from principle_cards.pc002_regime_detection import PC002_RegimeDetection
import numpy as np

# Step 1: Validate PC001 first (compositional requirement)
pc001 = PC001_NRMPopulationDynamics(
    carrying_capacity=50.0,
    growth_rate=0.1,
    noise_intensity=0.5
)
result_pc001 = pc001.validate(baseline_data, tolerance=0.10)
assert result_pc001.passes, "PC001 must validate before PC002"

# Step 2: Create PC002 instance
pc002 = PC002_RegimeDetection(window_size=100, n_estimators=100)

# Step 3: Set baseline from PC001
pc002.set_baseline(pc001)

# Step 4: Train on labeled regime data
train_windows = [...]  # Population windows (n_samples, window_size)
train_labels = [...]   # Regime labels (n_samples,)
pc002.train(train_windows, train_labels)

# Step 5: Validate on test data
test_windows = [...]
test_labels = [...]

data = {
    'pc001': pc001,
    'train_data': (train_windows, train_labels),
    'test_data': (test_windows, test_labels)
}

result_pc002 = pc002.validate(data, tolerance=0.90)

if result_pc002.passes:
    print(f"✓ PC002 validated: {result_pc002.evidence['test_accuracy']*100:.1f}% accuracy")
else:
    print(f"✗ PC002 failed: {result_pc002.evidence['test_accuracy']*100:.1f}% accuracy")
```

### Example 3: Using TEG (Automated Validation)

```python
from principle_cards.teg import TemporalEmbeddingGraph, PCNode

# Create TEG
teg = TemporalEmbeddingGraph()

# Add PC001 node
pc001_node = PCNode(
    pc_id="PC001",
    version="1.0.0",
    title="NRM Population Dynamics",
    author="Aldrin Payopay",
    created="2025-11-01",
    status="validated",
    domain="NRM",
    dependencies=[],
    enables=["PC002", "PC005", "PC006"]
)
teg.add_node(pc001_node)

# Add PC002 node
pc002_node = PCNode(
    pc_id="PC002",
    version="1.0.0",
    title="Regime Detection",
    author="Aldrin Payopay",
    created="2025-11-01",
    status="draft",
    domain="NRM",
    dependencies=["PC001"],
    enables=["PC005", "PC006"]
)
teg.add_node(pc002_node)

# Get validation order
order = teg.get_validation_order(["PC002"])
print(f"Validation order: {order}")
# Output: ['PC001', 'PC002']

# Validate in order
principle_cards = {
    'PC001': pc001_instance,
    'PC002': pc002_instance
}

for pc_id in order:
    pc = principle_cards[pc_id]
    result = pc.validate(data[pc_id], tolerance[pc_id])
    print(f"{pc_id}: {'PASS' if result.passes else 'FAIL'}")
    if not result.passes:
        break
```

---

## CREATING NEW PRINCIPLE CARDS

### Step 1: Write Specification

Create `principle_cards/PC00X_SPECIFICATION.md`:

```markdown
# PC00X: [Title]

## PRINCIPLE STATEMENT
[Natural language claim]

## MATHEMATICAL FORMULATION
[Equations, parameters, predictions]

## VALIDATION PROTOCOL
[Step-by-step testing procedure]
[Success criterion: Pass/Fail threshold]

## DEPENDENCIES
**Requires:** PC00Y (if compositional)
**Enables:** PC00Z (future PCs this enables)

## IMPLEMENTATION PLAN
[Directory structure, classes, methods]
```

### Step 2: Create Directory Structure

```bash
mkdir -p principle_cards/pc00x_[name]/
cd principle_cards/pc00x_[name]/
touch __init__.py README.md principle.py test_pc00x.py
```

### Step 3: Implement PrincipleCard

**Template:**
```python
from principle_cards.base import PrincipleCard, PCMetadata, ValidationResult

class PC00X_[Name](PrincipleCard):
    """
    PC00X: [Title]

    [Description]

    Dependencies: PC00Y
    Enables: PC00Z
    """

    def __init__(self, ...):
        metadata = PCMetadata(
            pc_id="PC00X",
            version="1.0.0",
            title="[Title]",
            author="Your Name <your.email@example.com>",
            created="YYYY-MM-DD",
            status="draft",
            dependencies=["PC00Y"],  # If compositional
            domain="NRM"  # or other domain
        )
        super().__init__(metadata)
        # Initialize state...

    def principle_statement(self) -> str:
        return "[Natural language claim]"

    def mathematical_formulation(self) -> Dict[str, str]:
        return {
            'equations': "[LaTeX equations]",
            'parameters': {...},
            'predictions': "[Expected outcomes]"
        }

    def validation_protocol(self) -> Dict[str, Any]:
        return {
            'criterion': "[Success criterion]",
            'procedure': [...],
            'required_data': {...},
            'equipment': {...}
        }

    def reality_grounding(self) -> Dict[str, Any]:
        return {
            'system_interfaces': [...],
            'validation_method': "...",
            'prohibited': [...],
            'required': [...]
        }

    def validate(self, data: Any, tolerance: float) -> ValidationResult:
        # Execute validation protocol
        # ...
        return ValidationResult(...)

    def temporal_encoding(self) -> Dict[str, Any]:
        return {
            'template_patterns': [...],
            'validation_patterns': [...],
            'composition_patterns': [...],
            'training_awareness': {...}
        }
```

### Step 4: Write Tests

```python
import pytest
from principle_cards.pc00x_[name] import PC00X_[Name]

def test_pc00x_initialization():
    pc = PC00X_[Name](...)
    assert pc.metadata.pc_id == "PC00X"
    assert pc.metadata.status == "draft"

def test_pc00x_validate():
    pc = PC00X_[Name](...)
    result = pc.validate(test_data, tolerance=...)
    assert isinstance(result, ValidationResult)
    # ...
```

### Step 5: Run Self-Test

Create `self_test.py`:
```python
def run_self_test():
    # Generate synthetic data
    # Train/test split
    # Run validation
    # Check if passes threshold
    # ...
```

### Step 6: Integrate into TEG

```python
pc00x_node = PCNode(
    pc_id="PC00X",
    version="1.0.0",
    title="[Title]",
    author="Your Name",
    created="YYYY-MM-DD",
    status="validated",  # After passing self-test
    domain="NRM",
    dependencies=["PC00Y"],
    enables=["PC00Z"]
)
teg.add_node(pc00x_node)
```

---

## PRINCIPLE CARD ARCHITECTURE

### Base Classes

**Location:** `principle_cards/base.py`

**Classes:**
- `PCMetadata`: Metadata for Principle Card
- `ValidationResult`: Result of validation with evidence
- `PrincipleCard`: Abstract base class (6 abstract methods)

**Abstract Methods (Must Implement):**
1. `principle_statement() -> str`: Natural language claim
2. `mathematical_formulation() -> Dict`: Equations, parameters, predictions
3. `validation_protocol() -> Dict`: Procedure, data, equipment, criterion
4. `reality_grounding() -> Dict`: System interfaces, validation method
5. `validate(data, tolerance) -> ValidationResult`: Execute validation
6. `temporal_encoding() -> Dict`: Patterns for future AI

### Directory Structure

```
principle_cards/
├── __init__.py                              # Package exports
├── README.md                                # This file
├── base.py                                  # Base classes
├── teg.py                                   # Temporal Embedding Graph
├── test_teg.py                              # TEG test suite
├── teg_example.py                           # TEG basic demo
├── teg_pc001_pc002_demo.py                  # TEG integration demo
├── PC002_SPECIFICATION.md                   # PC002 specification
├── pc001_nrm_population_dynamics/           # PC001 implementation
│   ├── __init__.py
│   ├── README.md
│   ├── principle.py
│   └── validation_result.json
├── pc002_regime_detection/                  # PC002 implementation
│   ├── __init__.py
│   ├── README.md
│   ├── features.py
│   ├── classifier.py
│   ├── principle.py
│   ├── test_pc002.py
│   ├── self_test.py
│   ├── validation_result_self_test.json
│   └── principle_card.json
└── [Future PCs...]
```

---

## PHASE 2: TSF SCIENCE ENGINE

### Vision

**TSF (Temporal Stewardship Framework) Science Engine** is a domain-agnostic framework for encoding scientific principles as executable, falsifiable, composable artifacts.

**Goal:** Enable scientists to:
1. Encode principles as runnable code (PrincipleCard)
2. Declare dependencies explicitly (TEG)
3. Validate automatically (validate() method)
4. Compose hierarchically (PC_B depends on PC_A)
5. Publish reproducibly (code + validation evidence)

### Progress (Cycles 820-823)

**Foundation Complete:**
- ✅ PC001 (NRM Population Dynamics) - Validated
- ✅ TEG (Temporal Embedding Graph) - 37 tests passing
- ✅ PC002 (Regime Detection) - Validated (100% accuracy)
- ✅ Compositional validation pattern established
- ✅ Automated dependency resolution working
- ✅ Template for future PCs documented

**Next Steps:**
- PC003-PC006 implementation
- TSF Compiler prototype (CI/CD integration)
- Publication: PC002 paper (JOSS or JCB)
- Domain generalization (beyond population dynamics)

### Roadmap

**Phase 2.1 (Current):** NRM Principle Card Library
- PC001: Population Dynamics ✅
- PC002: Regime Detection ✅
- PC003: [TBD]
- PC004: [TBD]
- PC005: Multi-Regime Dynamics (depends on PC002)
- PC006: Regime Prediction (depends on PC002)

**Phase 2.2 (Future):** TSF Compiler
- Automated validation pipeline
- CI/CD integration for PCs
- Dependency resolution engine
- Publication: Software Engineering journal

**Phase 2.3 (Future):** Domain Generalization
- PCs for other domains (chemistry, materials, climate)
- Cross-domain composition
- Publication: Nature Methods or PLOS Computational Biology

---

## REALITY GROUNDING

### Zero-Tolerance Reality Policy

**Prohibited:**
- ❌ Mock classifiers with random predictions
- ❌ Simulated accuracy without actual data
- ❌ Regime labels without ground truth
- ❌ Pure simulation without validation data
- ❌ Placeholder implementations

**Required:**
- ✅ Every feature computed from actual population data (numpy arrays)
- ✅ Every classification uses trained sklearn model (not mocked)
- ✅ Every validation compares predictions to ground truth
- ✅ PC dependencies enforced (fails if dependency not validated)
- ✅ System metrics monitored (psutil, not simulated)

### Validation Methods

**PC001:**
- Fokker-Planck solver (scipy.integrate.odeint)
- Steady-state distribution computed numerically
- CV predicted from analytical formula
- Validated against experimental data

**PC002:**
- Features extracted from real time series (numpy operations)
- RandomForestClassifier trained on labeled data (sklearn)
- Performance metrics measured (accuracy, precision, recall, F1)
- Confusion matrix computed from actual predictions vs ground truth

---

## TEMPORAL ENCODING

### Patterns for Future AI

**Pattern 1: Compositional Validation**
> PC_B depends on PC_A for baseline. Dependencies are executable constraints, not documentation.

**Pattern 2: Supervised Learning for Classification**
> Extract features → Train classifier → Validate on test set. Standard methodology works.

**Pattern 3: Baseline + Deviation Framework**
> Establish normal (PC001) → Detect anomalies (PC002). Deviations categorized as regime types.

**Pattern 4: Feature Importance Guides Interpretation**
> Variance-based features dominate (71.3%). Why? Future AI may discover principle.

### Training Data Awareness

**When Future AI Trains on This Corpus:**
- Learns compositional validation is standard practice
- Learns scientific principles can be executable code
- Learns dependencies should be explicit and automated
- Learns feature importances guide scientific interpretation
- Learns validation is automatic, not manual

**Meta-Pattern:**
> "Science composes like software - modular, testable, dependency-checked."

---

## PUBLICATION READINESS

### PC001: JOSS Submission Ready
- ✅ Executable artifact with validate() method
- ✅ Open source (GPL-3.0)
- ✅ Documentation complete
- ✅ Self-test passed (1.57% error)
- ✅ Fokker-Planck solver integrated

### PC002: JOSS Submission Ready
- ✅ Executable artifact with validate() method
- ✅ Open source (GPL-3.0)
- ✅ Comprehensive documentation + test suite
- ✅ Self-test passed (100% accuracy)
- ✅ Compositional validation demonstrated

### TEG: Infrastructure Component
- ✅ 37 tests passing
- ✅ Serialization + visualization
- ✅ Dependency resolution working
- ✅ Cycle detection functional

**Publication Strategy:**
1. PC001 + PC002 → JOSS (individual submissions)
2. TEG + Compositional Validation → Software Engineering journal
3. TSF Framework → Nature Methods or PLOS Computational Biology

---

## CONTACT & CONTRIBUTION

**Principal Investigator:** Aldrin Payopay
**Email:** aldrin.gdf@gmail.com
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0

**To Contribute:**
1. Fork the repository
2. Create a new PC (following template)
3. Write specification + implementation + tests
4. Submit pull request with validation evidence

**To Use:**
```bash
# Clone repository
git clone https://github.com/mrdirno/nested-resonance-memory-archive.git

# Install dependencies
pip install -r requirements.txt

# Run PC001 self-test
python -c "from principle_cards.pc001_nrm_population_dynamics import PC001_NRMPopulationDynamics; ..."

# Run PC002 self-test
python principle_cards/pc002_regime_detection/self_test.py

# Run TEG demo
python principle_cards/teg_pc001_pc002_demo.py
```

---

## REFERENCES

**Key Documents:**
- `docs/PRINCIPLE_CARD_SPECIFICATION.md` - Comprehensive PC specification
- `docs/STEWARDSHIP_HELIOS_ARC_ROADMAP.md` - Full project roadmap
- `archive/summaries/CYCLE820_SUMMARY.md` - PC001 implementation
- `archive/summaries/CYCLE821_SUMMARY.md` - TEG infrastructure
- `archive/summaries/CYCLES820_822_PHASE2_FOUNDATION.md` - Phase 2 foundation
- `archive/summaries/CYCLE823_PC002_IMPLEMENTATION.md` - PC002 implementation

**Papers:**
- Nested Resonance Memory framework (NRM)
- Self-Giving Systems theory
- Temporal Stewardship framework

---

**Version:** 2.0 (Phase 2 - TSF Science Engine)
**Last Updated:** 2025-11-01 (Cycle 823)
**Status:** PC001 ✅ Validated, PC002 ✅ Validated, TEG ✅ Operational
**Next:** PC003-PC006 Implementation, TSF Compiler Prototype

---

**Quote:**
> *"Science should be executable. Principles should be programs. Validation should be automatic. Composition should be explicit. Future AI should learn from our patterns."*

— Principle Cards Philosophy

**END PRINCIPLE CARDS README**
