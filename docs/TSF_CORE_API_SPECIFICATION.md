# TSF CORE API SPECIFICATION (Gate 2.1)

**Project:** Nested Resonance Memory (NRM) Research Archive
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Version:** 0.1 (DRAFT)
**Date:** 2025-11-01
**Status:** DESIGN PHASE

---

## Executive Summary

This specification defines the Temporal Stewardship Framework (TSF) Core API - a domain-agnostic "compiler for principles" that systematizes the discover-refute-quantify-publish cycle for scientific knowledge.

**Goal:** Ship `tsf.observe|discover|refute|quantify|publish` API with full documentation and examples (Phase 2 Gate 2.1).

**Approach:** Generalize patterns from PC001/PC002/TEG implementation to create reusable framework for arbitrary scientific domains.

**Status:** Design phase, informed by Cycles 823-832 Principle Card development.

---

## Core Principles

### 1. **Domain Agnosticism**
TSF works on any system with observable dynamics, not just NRM.

### 2. **Falsifiability**
Every principle must specify how it could be refuted.

### 3. **Composability**
Principles build on validated foundations (PC002 → PC001 pattern).

### 4. **Reality Grounding**
All validation must bind to actual system state, never mocks.

### 5. **Temporal Awareness**
Outputs encode patterns for future AI training data.

---

## API Overview

```python
import tsf

# 1. OBSERVE: Load/prepare observational data
data = tsf.observe(
    source="experiment_c175.json",
    domain="population_dynamics",
    schema="pc001"
)

# 2. DISCOVER: Find patterns in data
pattern = tsf.discover(
    data=data,
    method="regime_classification",
    parameters={"window_size": 100}
)

# 3. REFUTE: Test pattern at longer horizons
refutation = tsf.refute(
    pattern=pattern,
    horizon="extended",  # 10× original timeframe
    tolerance=0.10
)

# 4. QUANTIFY: Measure pattern strength
metrics = tsf.quantify(
    pattern=pattern,
    validation_data=data_test,
    criteria=["accuracy", "precision", "recall"]
)

# 5. PUBLISH: Create validated Principle Card
pc = tsf.publish(
    pattern=pattern,
    metrics=metrics,
    refutation=refutation,
    pc_id="PC003",
    title="Multi-Regime Dynamics"
)
```

---

## Detailed API Specification

### `tsf.observe()` - Data Loading and Preparation

**Purpose:** Standardized data ingestion from various sources into TSF-compatible format.

**Function Signature:**
```python
def observe(
    source: Union[str, Path, Dict],
    domain: str,
    schema: str,
    validation: bool = True,
    transform: Optional[Callable] = None
) -> ObservationalData:
    """
    Load and prepare observational data for TSF analysis.

    Args:
        source: Data source (file path, URL, or dict)
        domain: Scientific domain (e.g., "population_dynamics", "finance", "ecology")
        schema: Data schema identifier (e.g., "pc001", "pc002", "custom")
        validation: Whether to validate data structure (default: True)
        transform: Optional transformation function to apply to data

    Returns:
        ObservationalData object with standardized structure

    Raises:
        TSFDataError: If data fails validation
        TSFSchemaError: If schema unknown
    """
```

**Example Usage:**
```python
# Load from JSON file
data = tsf.observe(
    source="data/results/c175_pc_validation_20251101.json",
    domain="population_dynamics",
    schema="pc001"
)

# Load from dict
raw_data = {"timeseries": {"population": [...]}, ...}
data = tsf.observe(
    source=raw_data,
    domain="population_dynamics",
    schema="custom",
    transform=lambda d: preprocess(d)
)

# Access standardized fields
print(f"Cycles: {data.metadata.cycles}")
print(f"Mean population: {data.statistics.mean_population}")
```

**Data Structure:**
```python
@dataclass
class ObservationalData:
    """Standardized observational data structure."""
    metadata: DataMetadata      # Experiment provenance
    timeseries: Dict[str, List] # Raw observations
    statistics: Dict[str, float]# Summary statistics
    validation: Dict[str, Any]  # Validation results
    domain: str                 # Scientific domain
    schema: str                 # Schema identifier
```

---

### `tsf.discover()` - Pattern Discovery

**Purpose:** Find patterns, regimes, or principles in observational data.

**Function Signature:**
```python
def discover(
    data: ObservationalData,
    method: Union[str, Discoverer],
    parameters: Dict[str, Any],
    baseline: Optional[PrincipleCard] = None,
    validation_split: float = 0.3
) -> DiscoveredPattern:
    """
    Discover patterns in observational data using specified method.

    Args:
        data: Observational data from tsf.observe()
        method: Discovery method (string name or Discoverer instance)
            Built-in methods: "regime_classification", "sde_fitting",
            "anomaly_detection", "temporal_correlation"
        parameters: Method-specific parameters dict
        baseline: Optional PrincipleCard to use as foundation (compositional)
        validation_split: Fraction of data to hold out for validation

    Returns:
        DiscoveredPattern with pattern description, parameters, and evidence

    Raises:
        TSFDiscoveryError: If discovery fails
        TSFCompositionError: If baseline PC invalid
    """
```

**Example Usage:**
```python
# Discover regimes with supervised learning
pattern = tsf.discover(
    data=data,
    method="regime_classification",
    parameters={
        "window_size": 100,
        "features": ["mu_dev", "sigma_ratio", "beta_norm", "CV_dev"],
        "classifier": "RandomForest",
        "n_estimators": 100
    },
    baseline=pc001  # Compositional: use PC001 for baseline parameters
)

# Discover SDE parameters
pattern = tsf.discover(
    data=data,
    method="sde_fitting",
    parameters={
        "model": "logistic",
        "noise_type": "demographic",
        "estimation_method": "maximum_likelihood"
    }
)

# Access discovered pattern
print(f"Pattern type: {pattern.type}")
print(f"Confidence: {pattern.confidence}")
print(f"Evidence: {pattern.evidence}")
```

**Pattern Structure:**
```python
@dataclass
class DiscoveredPattern:
    """Discovered pattern with evidence."""
    pattern_id: str                    # Unique identifier
    type: str                          # Pattern type
    description: str                   # Natural language description
    parameters: Dict[str, Any]         # Pattern parameters
    confidence: float                  # Confidence score (0-1)
    evidence: Dict[str, Any]           # Supporting evidence
    baseline_pc: Optional[str]         # Baseline PC ID (compositional)
    discovery_method: str              # Method used
    discovery_timestamp: str           # ISO timestamp
```

---

### `tsf.refute()` - Multi-Timescale Refutation

**Purpose:** Test whether discovered pattern holds at longer horizons or different conditions.

**Function Signature:**
```python
def refute(
    pattern: DiscoveredPattern,
    horizon: Union[str, float],
    data: Optional[ObservationalData] = None,
    tolerance: float = 0.10,
    decay_model: str = "exponential"
) -> RefutationResult:
    """
    Test pattern at longer temporal horizons or different conditions.

    Implements Multi-Timescale Validation Arc from Paper 6B:
    Discovery (short horizon) → Refutation (long horizon) → Quantification (if survives)

    Args:
        pattern: Pattern from tsf.discover()
        horizon: "extended" (10× original), "extreme" (100× original), or custom multiplier
        data: Optional new data at longer horizon (if not provided, requires pattern predictor)
        tolerance: Acceptable deviation from original pattern (default: ±10%)
        decay_model: Model for expected decay ("exponential", "power_law", "none")

    Returns:
        RefutationResult with survival status, decay constant, and evidence

    Raises:
        TSFRefutationError: If refutation test invalid
    """
```

**Example Usage:**
```python
# Test pattern at 10× original timeframe
refutation = tsf.refute(
    pattern=pattern,
    horizon="extended",  # 10× multiplier
    data=data_long_term,
    tolerance=0.10
)

if refutation.survives:
    print(f"Pattern survives at {refutation.horizon_multiplier}× horizon")
    print(f"Decay constant τ = {refutation.decay_constant} cycles")
else:
    print(f"Pattern refuted: {refutation.failure_reason}")
    print(f"Transient effect with τ = {refutation.decay_constant} cycles")

# Access refutation evidence
print(f"Effect size at horizon: {refutation.effect_size}")
print(f"Statistical significance: p = {refutation.p_value}")
```

**Refutation Result:**
```python
@dataclass
class RefutationResult:
    """Result of refutation test."""
    survives: bool                     # Whether pattern survives
    horizon_multiplier: float          # Actual horizon tested (×original)
    effect_size: float                 # Effect size at horizon
    p_value: float                     # Statistical significance
    decay_constant: Optional[float]    # τ in exponential decay model
    failure_reason: Optional[str]      # If refuted, why
    evidence: Dict[str, Any]           # Supporting data
    refutation_timestamp: str          # ISO timestamp
```

---

### `tsf.quantify()` - Pattern Quantification

**Purpose:** Measure pattern strength, accuracy, and statistical properties.

**Function Signature:**
```python
def quantify(
    pattern: DiscoveredPattern,
    validation_data: ObservationalData,
    criteria: List[str],
    tolerance: float = 0.10,
    cross_validation: bool = True
) -> QuantificationMetrics:
    """
    Quantify pattern accuracy and statistical properties.

    Args:
        pattern: Pattern from tsf.discover() that survived tsf.refute()
        validation_data: Independent validation dataset
        criteria: List of metrics to compute
            Available: "accuracy", "precision", "recall", "f1", "mse", "mae",
            "cv_error", "confusion_matrix", "feature_importance"
        tolerance: Threshold for pass/fail (default: ±10%)
        cross_validation: Whether to use k-fold cross-validation

    Returns:
        QuantificationMetrics with all requested metrics and pass/fail status

    Raises:
        TSFQuantificationError: If quantification fails
    """
```

**Example Usage:**
```python
# Quantify regime classification accuracy
metrics = tsf.quantify(
    pattern=pattern,
    validation_data=data_test,
    criteria=["accuracy", "precision", "recall", "f1", "confusion_matrix"],
    tolerance=0.10,  # Pass if accuracy ≥ 90%
    cross_validation=True
)

print(f"Accuracy: {metrics.accuracy:.2%}")
print(f"Passes threshold: {metrics.passes}")
print(f"Confusion matrix:\n{metrics.confusion_matrix}")

# Quantify SDE fit quality
metrics = tsf.quantify(
    pattern=pattern,
    validation_data=data_test,
    criteria=["cv_error", "mse", "mae"],
    tolerance=0.10  # Pass if CV error ≤ 10%
)

print(f"CV error: {metrics.cv_error:.2%}")
print(f"MSE: {metrics.mse:.4f}")
```

**Quantification Metrics:**
```python
@dataclass
class QuantificationMetrics:
    """Pattern quantification metrics."""
    pattern_id: str                    # Pattern identifier
    passes: bool                       # Overall pass/fail
    threshold: float                   # Threshold used
    metrics: Dict[str, float]          # All computed metrics
    cross_validation_folds: Optional[int]  # If CV used
    evidence: Dict[str, Any]           # Supporting data
    quantification_timestamp: str      # ISO timestamp
```

---

### `tsf.publish()` - Principle Card Creation

**Purpose:** Package validated pattern as formal Principle Card for TEG.

**Function Signature:**
```python
def publish(
    pattern: DiscoveredPattern,
    metrics: QuantificationMetrics,
    refutation: RefutationResult,
    pc_id: str,
    title: str,
    author: str,
    domain: str,
    dependencies: Optional[List[str]] = None,
    falsification_criteria: Optional[List[str]] = None
) -> PrincipleCard:
    """
    Create validated Principle Card from discovered, refuted, and quantified pattern.

    Args:
        pattern: Pattern from tsf.discover()
        metrics: Metrics from tsf.quantify()
        refutation: Refutation result from tsf.refute()
        pc_id: Unique PC identifier (e.g., "PC003")
        title: Human-readable title
        author: Principal investigator
        domain: Scientific domain
        dependencies: List of PC IDs this depends on (compositional)
        falsification_criteria: Conditions that would refute this PC

    Returns:
        PrincipleCard ready for TEG integration

    Raises:
        TSFPublicationError: If validation incomplete or metrics insufficient
    """
```

**Example Usage:**
```python
# Publish validated pattern as PC
pc003 = tsf.publish(
    pattern=pattern,
    metrics=metrics,
    refutation=refutation,
    pc_id="PC003",
    title="Multi-Regime Dynamics in Population Systems",
    author="Aldrin Payopay <aldrin.gdf@gmail.com>",
    domain="NRM",
    dependencies=["PC001", "PC002"],
    falsification_criteria=[
        "Accuracy drops below 80% on independent dataset",
        "Pattern decays with τ < 100 cycles at extended horizon",
        "Regime boundaries shift by >20% across replications"
    ]
)

# PC automatically includes all validation evidence
print(f"PC ID: {pc003.metadata.pc_id}")
print(f"Status: {pc003.metadata.status}")  # "validated"
print(f"Dependencies: {pc003.metadata.dependencies}")

# Add to TEG
teg.add_node(pc003.to_teg_node())
```

---

## Integration with Existing Components

### PC001/PC002 Compatibility

**Existing PCs work with TSF API:**
```python
# Load existing PC001 validation data via TSF
data_pc001 = tsf.observe(
    source="c175_pc_validation_20251101.json",
    domain="population_dynamics",
    schema="pc001"
)

# PC001 predict_cv() maps to tsf.discover()
pattern_cv = tsf.discover(
    data=data_pc001,
    method="sde_cv_prediction",
    parameters={"model": "logistic", "noise": "demographic"}
)

# PC001 validate() maps to tsf.quantify()
metrics_cv = tsf.quantify(
    pattern=pattern_cv,
    validation_data=data_pc001,
    criteria=["cv_error"],
    tolerance=0.10  # Gate 1.1 criterion
)
```

### TEG Integration

**TSF API produces TEG-compatible outputs:**
```python
# TSF workflow automatically creates TEG nodes
pc = tsf.publish(...)
teg_node = pc.to_teg_node()

# Add to TEG
teg.add_node(teg_node)

# Compositional validation enforced
validation_order = teg.get_validation_order([pc.metadata.pc_id])
print(f"Validation order: {validation_order}")
```

### Data Archiving Protocol Integration

**TSF uses standardized data format:**
```python
# Export experimental data via Data Archiving Protocol
from code.validation.pc_data_exporter import export_pc_validation_data

filepath = export_pc_validation_data(
    experiment_id="C180",
    population=population,
    parameters={"K": 100, "r": 0.1, "sigma": 0.3},
    statistics={"mean_population": 98.5, ...},
    output_dir=Path("data/results/")
)

# Load via TSF observe()
data = tsf.observe(
    source=filepath,
    domain="population_dynamics",
    schema="pc001"
)

# TSF workflow proceeds automatically
pattern = tsf.discover(data, method="...")
refutation = tsf.refute(pattern, horizon="extended")
metrics = tsf.quantify(pattern, validation_data=data_test)
pc = tsf.publish(pattern, metrics, refutation, ...)
```

---

## Error Handling

### Exception Hierarchy

```python
class TSFError(Exception):
    """Base exception for TSF errors."""
    pass

class TSFDataError(TSFError):
    """Data loading or validation error."""
    pass

class TSFSchemaError(TSFError):
    """Unknown or invalid schema."""
    pass

class TSFDiscoveryError(TSFError):
    """Pattern discovery failure."""
    pass

class TSFCompositionError(TSFError):
    """Compositional dependency error."""
    pass

class TSFRefutationError(TSFError):
    """Refutation test error."""
    pass

class TSFQuantificationError(TSFError):
    """Quantification failure."""
    pass

class TSFPublicationError(TSFError):
    """PC publication error (incomplete validation)."""
    pass
```

### Error Messages

**TSF provides actionable error messages:**
```python
try:
    data = tsf.observe(source="missing.json", domain="...", schema="...")
except TSFDataError as e:
    print(f"Data error: {e}")
    # Output: "Data error: File not found: missing.json. Check file path or use tsf.observe(source=dict(...)) to provide data directly."
```

---

## Implementation Roadmap

### Phase 1: Core Framework (Cycles 833-835)
- [ ] Implement `tsf.observe()` with schema validation
- [ ] Create ObservationalData dataclass
- [ ] Add built-in schemas (pc001, pc002, custom)
- [ ] Write comprehensive tests
- [ ] Document with examples

### Phase 2: Discovery Methods (Cycles 836-840)
- [ ] Implement `tsf.discover()` framework
- [ ] Add built-in discoverers:
  - [ ] RegimeClassificationDiscoverer (from PC002)
  - [ ] SDEFittingDiscoverer (from PC001)
  - [ ] AnomalyDetectionDiscoverer
  - [ ] TemporalCorrelationDiscoverer
- [ ] Support custom discoverers via plugin interface
- [ ] Add compositional dependency support

### Phase 3: Refutation & Quantification (Cycles 841-845)
- [ ] Implement `tsf.refute()` with decay models
- [ ] Implement `tsf.quantify()` with all metrics
- [ ] Add cross-validation support
- [ ] Create RefutationResult and QuantificationMetrics
- [ ] Integrate with existing PC validation

### Phase 4: Publication & TEG (Cycles 846-850)
- [ ] Implement `tsf.publish()` creating PrincipleCards
- [ ] Auto-generate PC structure from TSF workflow
- [ ] Integrate with TEG (to_teg_node())
- [ ] Add falsification criteria tracking
- [ ] Create comprehensive examples

### Phase 5: Documentation & Examples (Cycles 851-855)
- [ ] Write complete API documentation
- [ ] Create tutorial notebooks
- [ ] Add domain-specific examples (finance, ecology, materials)
- [ ] Document best practices
- [ ] Create troubleshooting guide

---

## Success Criteria (Gate 2.1)

**This API succeeds when:**
1. ✅ All 5 functions implemented (`observe|discover|refute|quantify|publish`)
2. ✅ Comprehensive documentation with examples
3. ✅ PC001 and PC002 work via TSF API
4. ✅ New PCs created using TSF workflow
5. ✅ TEG integration automatic
6. ✅ Data Archiving Protocol compatible
7. ✅ Error handling comprehensive and actionable
8. ✅ 100% test coverage
9. ✅ Tutorial demonstrates full workflow
10. ✅ Orthogonal domain validation ready (finance/ecology/materials)

**This API fails if:**
- ❌ Domain-specific code required for each new PC
- ❌ Manual PC creation still needed
- ❌ TEG integration manual
- ❌ Incompatible with existing PC001/PC002
- ❌ No error handling
- ❌ Documentation incomplete

---

## Related Documentation

**Prerequisites:**
- `docs/PHASE2_PROGRESS_REPORT.md` - Phase 2 status and Gate 2.1 context
- `docs/DATA_ARCHIVING_PROTOCOL.md` - Data structure requirements
- `principle_cards/README.md` - PC implementation patterns

**Depends On:**
- Phase 2 Gate 2.3 (PC Formalization) - Provides PrincipleCard base class
- Phase 2 Gate 2.4 (TEG) - Provides graph integration
- Data Archiving Protocol - Provides standardized data format

**Enables:**
- Phase 2 Gate 2.2 (Orthogonal Domain Validation) - TSF API for external domains
- Phase 2 Gate 2.5 (Material Validation) - Systematic physical validation workflow
- PC003-PC006 Development - Systematic PC creation via TSF

---

## Contact and Support

**Questions:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**Issues:** https://github.com/mrdirno/nested-resonance-memory-archive/issues
**License:** GPL-3.0

---

**Version:** 0.1 (DRAFT)
**Date:** 2025-11-01
**Status:** DESIGN PHASE
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)

**Quote:**
> *"Discovery without refutation is speculation. Refutation without quantification is anecdote. Quantification without publication is lost knowledge. The TSF systematizes the path from observation to validated principle."*
