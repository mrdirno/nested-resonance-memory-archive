# TSF CORE API SPECIFICATION

**Temporal Structure Framework (TSF) Science Engine**
**Version:** 1.0.0-draft
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Author:** Claude Sonnet 4.5 (DUALITY-ZERO-V2)
**Date:** 2025-11-01 (Cycle 879)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Status:** Design Specification (Gate 2.1)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Philosophy](#design-philosophy)
3. [Core API Functions](#core-api-functions)
4. [Usage Examples](#usage-examples)
5. [Integration Patterns](#integration-patterns)
6. [Extensibility](#extensibility)
7. [Implementation Plan](#implementation-plan)
8. [References](#references)

---

## Executive Summary

### Purpose

The TSF Core API provides a unified interface for applying the Temporal Structure Framework to scientific research domains. It enables researchers to **observe** data, **discover** patterns, **refute** hypotheses, **quantify** effects, and **publish** results in a standardized, reproducible manner.

### Design Goals

1. **Domain-Agnostic:** Works across NRM, finance, ecology, materials science, robotics, etc.
2. **Principle Card Integration:** Seamlessly applies PCs (PC1, PC2, PC3+) to datasets
3. **Reproducible:** All operations deterministic, versioned, auditable
4. **Composable:** Functions chain together for complex workflows
5. **Reality-Grounded:** No mocks, no simulations - actual system state only
6. **Publication-Ready:** Outputs formatted for peer-reviewed papers

### Core Functions

```python
import tsf

# 1. Load and validate datasets
data = tsf.observe(source="C175_consolidation.json", schema="population_dynamics")

# 2. Apply principle card to detect patterns
patterns = tsf.discover(data, principle_card="PC1", method="sde_prediction")

# 3. Test hypotheses with statistical rigor
result = tsf.refute(
    hypothesis="Transcendental > PRNG",
    data_a=transcendental_data,
    data_b=prng_data,
    metrics=["pattern_lifetime", "memory_retention"]
)

# 4. Compute effect sizes and confidence intervals
stats = tsf.quantify(result, alpha=0.01, correction="bonferroni")

# 5. Generate publication-ready outputs
tsf.publish(
    result=stats,
    format="latex",
    output_dir="papers/paper8/figures/",
    dpi=300
)
```

### Informed By

- **PC1 (NRM Population Dynamics):** Validated framework provides API foundation
- **PC2 (Transcendental Substrate Hypothesis):** Comparative methodology informs `refute()`
- **Phase 1 Gates (1.1-1.4):** Reality grounding, reproducibility, validation patterns
- **177+ Experiments:** Practical usage patterns from C001-C177

---

## Design Philosophy

### 1. Principle Cards as First-Class Objects

Principle Cards are not just documentation - they're **runnable, composable artifacts**:

```python
# Load PC as Python object
pc1 = tsf.PrincipleCard.load("PC1")

# Inspect metadata
print(pc1.metadata.validation_status)  # "validated"
print(pc1.metadata.dependencies)       # []

# Execute validation
validation = pc1.validate(data, tolerance=0.10)
print(validation.passes)  # True (7.18% < 10% criterion)
```

### 2. Temporal Embedding Graph Integration

The API automatically updates the TEG as PCs are validated:

```python
# Discover operation updates TEG
patterns = tsf.discover(data, principle_card="PC2")

# TEG reflects new validation
teg = tsf.TEG.load()
print(teg.get_dependencies("PC2"))  # ['PC1']
print(teg.get_validation_order(["PC2"]))  # ['PC1', 'PC2']
```

### 3. Reality-First Implementation

All operations bound to actual system state:

```python
# observe() verifies data files exist (not mocked)
data = tsf.observe("C175.json")  # FileNotFoundError if missing

# discover() uses real algorithms (not simulated)
patterns = tsf.discover(data, "PC1")  # Actual SDE/Fokker-Planck computation

# quantify() measures real computational expense
stats = tsf.quantify(patterns, profile_overhead=True)  # psutil tracking
```

### 4. Reproducibility by Default

Every function call generates provenance:

```python
result = tsf.refute(hypothesis, data_a, data_b)

# Automatic provenance tracking
print(result.provenance.timestamp)  # ISO 8601
print(result.provenance.tsf_version)  # "1.0.0"
print(result.provenance.pc_versions)  # {"PC1": "1.0.0", "PC2": "0.1.0"}
print(result.provenance.random_seed)  # 42 (deterministic)
print(result.provenance.sha256_hash)  # Cryptographic validation
```

### 5. Publication-Centric Design

Outputs optimized for academic papers:

```python
# Generate LaTeX table
tsf.publish(result, format="latex_table")
# Output: \begin{table}...\end{table}

# Generate 300 DPI figure
tsf.publish(result, format="figure", dpi=300)
# Output: figure_pc2_validation.png

# Generate complete Methods section
tsf.publish(result, format="methods_section")
# Output: LaTeX paragraph with all details
```

---

## Core API Functions

### Function 1: `tsf.observe()`

**Purpose:** Load and validate datasets with schema enforcement

**Signature:**
```python
def observe(
    source: Union[str, Path, List[str]],
    schema: str,
    *,
    validate: bool = True,
    cache: bool = True,
    metadata: Optional[Dict] = None
) -> ObservedData:
    """
    Load dataset and validate against schema.

    Args:
        source: File path(s) or glob pattern
        schema: Schema name (e.g., "population_dynamics", "pattern_memory")
        validate: Enforce schema validation (default: True)
        cache: Enable result caching (default: True)
        metadata: Additional metadata to attach

    Returns:
        ObservedData object with validated data and schema

    Raises:
        FileNotFoundError: Source file(s) not found
        SchemaValidationError: Data doesn't match schema
        RealityCheckFailedError: Data contains mocks/simulations

    Examples:
        >>> data = tsf.observe("C175_consolidation.json", schema="population_dynamics")
        >>> print(data.shape)  # (40, 1000)  # 40 experiments, 1000 timesteps
        >>> print(data.schema.required_fields)  # ['population', 'timestamp', 'seed']

        >>> # Load multiple files with glob pattern
        >>> data = tsf.observe("data/results/C17*.json", schema="pattern_memory")

        >>> # Custom metadata
        >>> data = tsf.observe("C176.json", schema="population_dynamics",
        ...                    metadata={"experiment": "ablation", "cycle": 176})
    """
```

**Schema System:**

Built-in schemas for common data types:

```python
# Population dynamics (PC1)
schema_population_dynamics = {
    "required_fields": ["population", "timestamp", "seed"],
    "optional_fields": ["energy", "resonance", "clusters"],
    "validation_rules": {
        "population": {"type": "numeric", "min": 0},
        "timestamp": {"type": "numeric", "increasing": True},
        "seed": {"type": "integer", "min": 0}
    }
}

# Pattern memory (fractal module)
schema_pattern_memory = {
    "required_fields": ["pattern_id", "strength", "timestamp"],
    "optional_fields": ["use_count", "last_used"],
    "validation_rules": {
        "pattern_id": {"type": "string", "unique": True},
        "strength": {"type": "numeric", "min": 0.0, "max": 1.0},
        "timestamp": {"type": "datetime", "format": "ISO8601"}
    }
}

# Custom schema registration
tsf.register_schema("my_domain", schema_dict)
```

**Reality Validation:**

`observe()` automatically checks for reality violations:

```python
def reality_check(data: ObservedData) -> None:
    """Verify data is reality-grounded, not mocked/simulated."""
    # Check 1: Timestamps are real (not time.sleep() calls)
    if has_uniform_intervals(data.timestamps):
        raise RealityCheckFailedError("Suspiciously uniform timestamps")

    # Check 2: Values have measurement noise (not pure simulation)
    if has_zero_noise(data.values):
        raise RealityCheckFailedError("Perfect values indicate simulation")

    # Check 3: File metadata authentic (not fabricated)
    if not verify_file_provenance(data.source):
        raise RealityCheckFailedError("File provenance unverifiable")
```

---

### Function 2: `tsf.discover()`

**Purpose:** Apply principle cards to detect patterns in data

**Signature:**
```python
def discover(
    data: ObservedData,
    principle_card: Union[str, PrincipleCard],
    *,
    method: Optional[str] = None,
    parameters: Optional[Dict] = None,
    confidence: float = 0.95
) -> DiscoveredPatterns:
    """
    Apply principle card to discover patterns.

    Args:
        data: Observed dataset from tsf.observe()
        principle_card: PC identifier or loaded PC object
        method: Specific discovery method (default: PC's primary method)
        parameters: Override default PC parameters
        confidence: Confidence level for pattern detection (default: 0.95)

    Returns:
        DiscoveredPatterns object with patterns, metadata, provenance

    Raises:
        PCValidationError: Principle card not validated
        PCDependencyError: Required dependencies not satisfied
        InsufficientDataError: Dataset too small for reliable discovery

    Examples:
        >>> # Apply PC1 to discover population dynamics patterns
        >>> data = tsf.observe("C175.json", schema="population_dynamics")
        >>> patterns = tsf.discover(data, principle_card="PC1")
        >>> print(patterns.cv_predicted)  # 0.0718 (7.18% error)
        >>> print(patterns.regime)  # "BISTABILITY"

        >>> # Apply PC2 with custom parameters
        >>> patterns = tsf.discover(
        ...     data,
        ...     principle_card="PC2",
        ...     method="regime_classification",
        ...     parameters={"cv_threshold": 0.20}
        ... )

        >>> # Discover with low confidence (exploratory)
        >>> patterns = tsf.discover(data, "PC1", confidence=0.90)
    """
```

**Pattern Object Structure:**

```python
@dataclass
class DiscoveredPatterns:
    """Results from pattern discovery."""
    pc_id: str                          # "PC1"
    pc_version: str                     # "1.0.0"
    patterns: Dict[str, Any]            # Discovered patterns
    validation_result: ValidationResult # PC validation outcome
    metadata: Dict[str, Any]            # Discovery metadata
    provenance: Provenance              # Full provenance tracking
    timestamp: datetime                 # Discovery timestamp

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        ...

    def to_json(self, filepath: Path) -> None:
        """Save to JSON file."""
        ...

    def summary(self) -> str:
        """Human-readable summary."""
        ...
```

**PC-Specific Discovery Methods:**

Each principle card implements domain-specific discovery:

```python
# PC1: SDE/Fokker-Planck prediction
patterns = tsf.discover(data, "PC1", method="sde_prediction")
# Returns: {cv_predicted, cv_observed, error_pct, drift_params, diffusion_params}

# PC1: Regime classification
patterns = tsf.discover(data, "PC1", method="regime_classification")
# Returns: {regime, confidence, features, thresholds}

# PC2: Pattern lifetime analysis
patterns = tsf.discover(data, "PC2", method="pattern_persistence")
# Returns: {lifetimes, mean, median, max, variance, survival_curve}

# PC2: Memory retention analysis
patterns = tsf.discover(data, "PC2", method="memory_retention")
# Returns: {retention_rate, decay_constant, critical_phase_shift}
```

---

### Function 3: `tsf.refute()`

**Purpose:** Test hypotheses with statistical rigor (comparative analysis)

**Signature:**
```python
def refute(
    hypothesis: str,
    data_a: Union[ObservedData, DiscoveredPatterns],
    data_b: Union[ObservedData, DiscoveredPatterns],
    *,
    metrics: List[str],
    alpha: float = 0.01,
    test: Optional[str] = None,
    correction: str = "bonferroni",
    effect_size: str = "cohen_d",
    power_analysis: bool = True
) -> RefutationResult:
    """
    Test hypothesis by comparing two conditions.

    Args:
        hypothesis: Hypothesis statement (e.g., "Transcendental > PRNG")
        data_a: First condition data (e.g., transcendental substrate)
        data_b: Second condition data (e.g., PRNG substrate)
        metrics: List of metrics to compare
        alpha: Significance level (default: 0.01)
        test: Statistical test override (default: auto-select)
        correction: Multiple comparisons correction (default: "bonferroni")
        effect_size: Effect size measure (default: "cohen_d")
        power_analysis: Compute statistical power (default: True)

    Returns:
        RefutationResult with test outcomes, effect sizes, decisions

    Raises:
        InsufficientDataError: Sample size too small for power
        HypothesisFormatError: Hypothesis not properly formatted
        MetricUnavailableError: Requested metric not in data

    Examples:
        >>> # Test PC2 hypothesis: Transcendental > PRNG
        >>> trans_data = tsf.observe("baseline_transcendental.json", schema="patterns")
        >>> prng_data = tsf.observe("control_prng.json", schema="patterns")

        >>> result = tsf.refute(
        ...     hypothesis="Transcendental > PRNG",
        ...     data_a=trans_data,
        ...     data_b=prng_data,
        ...     metrics=["pattern_lifetime", "memory_retention", "complexity"],
        ...     alpha=0.01,
        ...     correction="bonferroni"
        ... )

        >>> print(result.hypothesis_rejected)  # True/False
        >>> print(result.p_values)  # {"pattern_lifetime": 0.003, ...}
        >>> print(result.effect_sizes)  # {"pattern_lifetime": {"d": 0.65, ...}}
        >>> print(result.decision)  # "REJECT null hypothesis" or "FAIL TO REJECT"

        >>> # Access detailed results
        >>> for metric in result.metrics:
        ...     print(f"{metric}: p={result.p_values[metric]:.4f}, "
        ...           f"d={result.effect_sizes[metric]['d']:.2f}")
    """
```

**Automatic Test Selection:**

`refute()` chooses appropriate statistical test based on data properties:

```python
def select_test(data_a, data_b, metric) -> str:
    """Auto-select statistical test."""
    if is_normal(data_a) and is_normal(data_b):
        if equal_variances(data_a, data_b):
            return "independent_t_test"
        else:
            return "welch_t_test"
    else:
        return "mann_whitney_u_test"  # Non-parametric

    # For variance comparison
    if metric in ["stability", "variance"]:
        return "f_test"

    # For multivariate metrics
    if is_multivariate(metric):
        return "manova"
```

**Multiple Comparisons Correction:**

```python
# Bonferroni correction (conservative)
result = tsf.refute(..., correction="bonferroni")
# Adjusts alpha: α_adjusted = α / num_tests

# Holm-Bonferroni correction (less conservative)
result = tsf.refute(..., correction="holm_bonferroni")

# False Discovery Rate (FDR) control
result = tsf.refute(..., correction="fdr_bh")  # Benjamini-Hochberg

# No correction (use with caution)
result = tsf.refute(..., correction=None)
```

**Power Analysis:**

```python
result = tsf.refute(..., power_analysis=True)

print(result.power_analysis.achieved_power)  # 0.85 (achieved)
print(result.power_analysis.required_n)  # 25 (for power=0.80)
print(result.power_analysis.effect_size_detectable)  # d=0.5 (medium)
```

---

### Function 4: `tsf.quantify()`

**Purpose:** Compute effect sizes, confidence intervals, and summary statistics

**Signature:**
```python
def quantify(
    result: Union[DiscoveredPatterns, RefutationResult],
    *,
    alpha: float = 0.05,
    confidence: float = 0.95,
    bootstrap_iterations: int = 10000,
    report_format: str = "full"
) -> QuantifiedResult:
    """
    Compute effect sizes and confidence intervals.

    Args:
        result: Discovery or refutation result to quantify
        alpha: Significance level (default: 0.05)
        confidence: CI confidence level (default: 0.95 for 95% CI)
        bootstrap_iterations: Bootstrap resampling iterations (default: 10000)
        report_format: "full", "summary", or "publication" (default: "full")

    Returns:
        QuantifiedResult with effect sizes, CIs, summaries

    Examples:
        >>> # Quantify pattern discovery
        >>> patterns = tsf.discover(data, "PC1")
        >>> quant = tsf.quantify(patterns, confidence=0.95)
        >>> print(quant.effect_sizes["cv_error"])  # 0.0718
        >>> print(quant.confidence_intervals["cv_error"])  # (0.065, 0.079)

        >>> # Quantify hypothesis test
        >>> refute_result = tsf.refute(hypothesis, data_a, data_b, metrics=[...])
        >>> quant = tsf.quantify(refute_result, bootstrap_iterations=20000)
        >>> print(quant.summary_table())  # Publication-ready LaTeX table
    """
```

**Effect Size Measures:**

```python
# Cohen's d (standardized mean difference)
d = (mean_a - mean_b) / pooled_std
interpretation = {
    0.2: "small",
    0.5: "medium",
    0.8: "large"
}

# Hedges' g (bias-corrected d for small samples)
g = correction_factor * d

# Variance ratio (for stability metrics)
vr = var_a / var_b

# Correlation coefficient (for associations)
r = pearson_correlation(a, b)

# R² (variance explained)
r_squared = r ** 2
```

**Confidence Intervals:**

```python
# Parametric CI (assumes normality)
ci_parametric = mean ± (t_critical * se)

# Bootstrap CI (distribution-free)
ci_bootstrap = np.percentile(bootstrap_samples, [2.5, 97.5])

# Bias-corrected and accelerated (BCa) bootstrap
ci_bca = bias_corrected_accelerated_bootstrap(data)
```

**Publication-Ready Summaries:**

```python
quant = tsf.quantify(result, report_format="publication")

# Generates formatted strings for papers:
print(quant.summary_text())
# "Pattern lifetime was significantly longer in the transcendental condition
#  (M = 125.3, SD = 18.7) compared to the PRNG condition (M = 98.4, SD = 22.1),
#  t(48) = 4.82, p < .001, d = 0.68, 95% CI [0.42, 0.94]."

print(quant.latex_table())
# \begin{table}
# \caption{Comparative Statistics}
# ...
# \end{table}
```

---

### Function 5: `tsf.publish()`

**Purpose:** Generate publication-ready outputs (figures, tables, text)

**Signature:**
```python
def publish(
    result: Union[DiscoveredPatterns, RefutationResult, QuantifiedResult],
    format: Union[str, List[str]],
    *,
    output_dir: Optional[Path] = None,
    dpi: int = 300,
    style: str = "publication",
    overwrite: bool = False
) -> PublicationOutputs:
    """
    Generate publication-ready outputs.

    Args:
        result: Discovery, refutation, or quantification result
        format: Output format(s): "figure", "latex_table", "methods_section", "all"
        output_dir: Output directory (default: current directory)
        dpi: Figure resolution (default: 300)
        style: Plotting style (default: "publication")
        overwrite: Overwrite existing files (default: False)

    Returns:
        PublicationOutputs with file paths and metadata

    Examples:
        >>> # Generate all outputs
        >>> outputs = tsf.publish(result, format="all", output_dir="papers/paper8/")
        >>> print(outputs.figures)  # ["figure_pc2_validation.png", ...]
        >>> print(outputs.tables)  # ["table_statistics.tex"]
        >>> print(outputs.text)  # ["methods_section.tex"]

        >>> # Generate specific figure
        >>> outputs = tsf.publish(
        ...     result,
        ...     format="figure",
        ...     output_dir="figures/",
        ...     dpi=600,  # High-res for print
        ...     style="nature"  # Nature journal style
        ... )

        >>> # Generate LaTeX table only
        >>> outputs = tsf.publish(result, format="latex_table")
        >>> with open(outputs.tables[0]) as f:
        ...     print(f.read())  # Copy-paste into LaTeX manuscript
    """
```

**Figure Styles:**

```python
# Publication style (default)
style="publication"  # Nature/Science/PNAS compatible
# - 8pt font minimum
# - High contrast colors (colorblind-safe)
# - Clear legends, axis labels
# - 300 DPI minimum

# Presentation style
style="presentation"  # Conference slides
# - Larger fonts (14pt+)
# - Bold colors
# - Minimal text
# - 150 DPI

# arXiv style
style="arxiv"  # Preprint servers
# - Optimized file size
# - Vector graphics where possible
# - 150 DPI raster

# Journal-specific
style="nature"  # Nature Publishing Group
style="science"  # Science/AAAS
style="plos"  # PLOS journals
style="ieee"  # IEEE transactions
```

**Automated Figure Generation:**

```python
# Pattern lifetime comparison (PC2 Gate 2.2)
tsf.publish(refute_result, format="figure")
# Generates violin plot comparing distributions

# Memory retention curves (PC2 Gate 2.3)
tsf.publish(patterns, format="figure")
# Generates exponential decay fit with confidence bands

# Complexity radar plot (PC2 Gate 2.4)
tsf.publish(quantified, format="figure")
# Generates 4-metric radar plot with statistical annotations
```

**LaTeX Integration:**

```python
# Methods section
outputs = tsf.publish(result, format="methods_section")
# Generates complete Methods paragraph with all statistical details

# Results section
outputs = tsf.publish(result, format="results_section")
# Generates Results paragraph with inline statistics

# Figure caption
outputs = tsf.publish(result, format="caption")
# Generates detailed figure caption with statistical annotations

# BibTeX references
outputs = tsf.publish(result, format="bibtex")
# Generates references for all PC dependencies and methods
```

---

## Usage Examples

### Example 1: PC1 Validation (Simple Discovery)

```python
import tsf

# Step 1: Load experimental data
data = tsf.observe(
    source="data/results/C175_consolidation.json",
    schema="population_dynamics",
    metadata={"experiment": "C175", "condition": "BASELINE"}
)

# Step 2: Apply PC1 to discover patterns
patterns = tsf.discover(
    data,
    principle_card="PC1",
    method="sde_prediction",
    confidence=0.95
)

# Step 3: Quantify results
quantified = tsf.quantify(patterns, confidence=0.95)

# Step 4: Generate publication outputs
outputs = tsf.publish(
    quantified,
    format=["figure", "latex_table"],
    output_dir="papers/paper8/figures/",
    dpi=300
)

# Print summary
print(f"CV Prediction Error: {patterns.patterns['cv_error']}%")
print(f"Validation: {patterns.validation_result.passes}")
print(f"Outputs: {outputs.figures + outputs.tables}")
```

### Example 2: PC2 Hypothesis Testing (Comparative Study)

```python
import tsf

# Step 1: Load baseline (transcendental) data
baseline = tsf.observe(
    source="data/results/C175_baseline/*.json",
    schema="pattern_dynamics"
)

# Step 2: Load control (PRNG) data
control = tsf.observe(
    source="data/results/C175_prng_control/*.json",
    schema="pattern_dynamics"
)

# Step 3: Test PC2 hypothesis
result = tsf.refute(
    hypothesis="Transcendental > PRNG in pattern persistence",
    data_a=baseline,
    data_b=control,
    metrics=[
        "pattern_lifetime_mean",
        "memory_retention_rate",
        "cluster_stability_cv",
        "complexity_score"
    ],
    alpha=0.01,
    correction="bonferroni",
    power_analysis=True
)

# Step 4: Quantify effect sizes
quantified = tsf.quantify(
    result,
    confidence=0.95,
    bootstrap_iterations=10000,
    report_format="publication"
)

# Step 5: Generate all publication outputs
outputs = tsf.publish(
    quantified,
    format="all",
    output_dir="papers/pc2_validation/",
    dpi=600,  # High-res for submission
    style="nature"
)

# Print decision
print(f"Hypothesis: {result.hypothesis}")
print(f"Decision: {result.decision}")
print(f"Significant metrics: {result.significant_metrics}")
print(f"Power achieved: {result.power_analysis.achieved_power:.2f}")
print(f"Effect sizes: {quantified.effect_sizes}")
```

### Example 3: Multi-PC Workflow (Complex Pipeline)

```python
import tsf

# Pipeline: Apply multiple PCs sequentially
data = tsf.observe("C177_boundary_mapping.json", schema="population_dynamics")

# PC1: Baseline parameter estimation
pc1_patterns = tsf.discover(data, "PC1", method="parameter_estimation")
baseline_params = pc1_patterns.patterns["parameters"]

# PC2: Regime classification (depends on PC1 baseline)
pc2_patterns = tsf.discover(
    data,
    "PC2",
    method="regime_classification",
    parameters={"baseline": baseline_params}
)

# PC3: Multi-regime dynamics (hypothetical future PC)
# pc3_patterns = tsf.discover(
#     data,
#     "PC3",
#     method="regime_transitions",
#     parameters={"regimes": pc2_patterns.patterns["regimes"]}
# )

# Quantify composite results
quantified = tsf.quantify([pc1_patterns, pc2_patterns])

# Publish integrated analysis
outputs = tsf.publish(
    quantified,
    format=["figure", "methods_section", "results_section"],
    output_dir="papers/multi_pc_analysis/"
)
```

### Example 4: Custom Domain Application

```python
import tsf

# Register custom schema for new domain (e.g., finance)
tsf.register_schema("high_frequency_trading", {
    "required_fields": ["price", "volume", "timestamp"],
    "optional_fields": ["bid", "ask", "spread"],
    "validation_rules": {
        "price": {"type": "numeric", "min": 0},
        "volume": {"type": "integer", "min": 0},
        "timestamp": {"type": "datetime", "microsecond_precision": True}
    }
})

# Load financial data
hft_data = tsf.observe(
    source="data/hft/spy_20250101.csv",
    schema="high_frequency_trading"
)

# Apply adapted PC1 (population dynamics → price dynamics)
patterns = tsf.discover(
    hft_data,
    principle_card="PC1",
    method="sde_prediction",
    parameters={
        "observable": "price",  # Map population → price
        "noise_model": "gamma"  # Financial noise is non-Gaussian
    }
)

# Test domain-specific hypothesis
result = tsf.refute(
    hypothesis="High-frequency > Low-frequency in volatility prediction",
    data_a=hft_data,
    data_b=lft_data,
    metrics=["cv_prediction_error", "regime_classification_accuracy"]
)

# Publish domain-adapted results
outputs = tsf.publish(result, format="all", output_dir="papers/finance/")
```

---

## Integration Patterns

### Phase 1 Gates Integration

**Gate 1.1 (SDE/Fokker-Planck):**

```python
# discover() uses SDE framework for predictions
patterns = tsf.discover(data, "PC1", method="sde_prediction")

# Internally calls:
from code.analysis.sde_fokker_planck import SDEValidator
validator = SDEValidator()
result = validator.validate(data, tolerance=0.10)
```

**Gate 1.2 (Regime Detection):**

```python
# discover() uses regime library for classification
patterns = tsf.discover(data, "PC1", method="regime_classification")

# Internally calls:
from code.tsf.regime_detection import RegimeDetector
detector = RegimeDetector()
regime = detector.classify(trajectory)
```

**Gate 1.3 (ARBITER CI):**

```python
# publish() generates ARBITER manifest automatically
outputs = tsf.publish(result, format="all")

# Internally generates:
from code.arbiter.arbiter import ManifestCreator
creator = ManifestCreator()
manifest = creator.create_manifest(outputs.files, algorithm="sha256")
```

**Gate 1.4 (Overhead Authentication):**

```python
# quantify() profiles computational expense
quantified = tsf.quantify(patterns, profile_overhead=True)

# Internally uses:
from code.validation.overhead_authenticator import OverheadAuthenticator
auth = OverheadAuthenticator()
overhead = auth.measure(operation=discover_fn, data=data)
```

### Fractal Module Integration

```python
# discover() can analyze fractal agent dynamics
data = tsf.observe("fractal_demo_output.json", schema="fractal_agents")

patterns = tsf.discover(
    data,
    principle_card="PC1",  # Apply PC1 to fractal system
    method="composition_decomposition_analysis"
)

# Returns: {
#   "composition_events": 15,
#   "decomposition_events": 12,
#   "avg_cluster_lifetime": 87.3,
#   "memory_retention_rate": 0.83
# }
```

### TEG Automatic Updates

```python
# discover() triggers TEG update on validation
patterns = tsf.discover(data, "PC2")

if patterns.validation_result.passes:
    # Automatically updates TEG
    teg = tsf.TEG.load()
    teg.update_node("PC2", status="validated")
    teg.save()

    # Notify dependent PCs
    dependents = teg.get_dependents("PC2")
    for pc_id in dependents:
        print(f"{pc_id} can now proceed (dependency satisfied)")
```

---

## Extensibility

### Adding New Principle Cards

```python
# 1. Define PC class (inherits from PrincipleCard base)
class PC003_MultiRegimeDynamics(tsf.PrincipleCard):
    def __init__(self):
        super().__init__(
            pc_id="PC003",
            version="0.1.0",
            dependencies=["PC001", "PC002"]
        )

    def validate(self, data, tolerance):
        # Custom validation logic
        ...

    def discover(self, data, method, parameters):
        # Custom discovery methods
        ...

# 2. Register PC with TSF
tsf.register_principle_card(PC003_MultiRegimeDynamics)

# 3. Use immediately
patterns = tsf.discover(data, principle_card="PC003")
```

### Adding Custom Schemas

```python
# Register new schema
tsf.register_schema("custom_domain", {
    "required_fields": ["field1", "field2"],
    "validation_rules": {...}
})

# Use with observe()
data = tsf.observe("data.json", schema="custom_domain")
```

### Adding Custom Statistical Tests

```python
# Register custom test
def my_custom_test(data_a, data_b):
    # Implement test
    statistic = ...
    p_value = ...
    return {"statistic": statistic, "p_value": p_value}

tsf.register_test("my_custom_test", my_custom_test)

# Use with refute()
result = tsf.refute(..., test="my_custom_test")
```

### Adding Custom Publication Formats

```python
# Register custom format
def my_journal_format(result, **kwargs):
    # Generate journal-specific output
    ...
    return output_files

tsf.register_publication_format("my_journal", my_journal_format)

# Use with publish()
outputs = tsf.publish(result, format="my_journal")
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Cycles 880-900)

1. **Create `tsf/` module structure**
   - `tsf/__init__.py` (API exports)
   - `tsf/observe.py` (data loading + validation)
   - `tsf/discover.py` (pattern discovery)
   - `tsf/refute.py` (hypothesis testing)
   - `tsf/quantify.py` (effect sizes + CIs)
   - `tsf/publish.py` (publication outputs)

2. **Implement PrincipleCard base class**
   - Abstract methods for PC interface
   - Metadata structure
   - Validation framework
   - TEG integration hooks

3. **Implement schema system**
   - Built-in schemas (population_dynamics, pattern_memory)
   - Schema validation engine
   - Reality checks
   - Custom schema registration

4. **Implement provenance tracking**
   - Automatic timestamp generation
   - Version tracking (TSF, PCs, dependencies)
   - Random seed management
   - SHA-256 hash generation

### Phase 2: Statistical Engine (Cycles 901-920)

1. **Implement `refute()` statistical tests**
   - Parametric tests (t-test, F-test, ANOVA, MANOVA)
   - Non-parametric tests (Mann-Whitney, Kruskal-Wallis)
   - Automatic test selection
   - Multiple comparisons correction

2. **Implement `quantify()` effect sizes**
   - Cohen's d, Hedges' g
   - Variance ratios
   - Correlation coefficients
   - Confidence intervals (parametric, bootstrap, BCa)

3. **Implement power analysis**
   - Achieved power calculation
   - Required sample size estimation
   - Effect size detection thresholds

### Phase 3: Publication Engine (Cycles 921-940)

1. **Implement `publish()` figure generation**
   - Matplotlib integration
   - Seaborn statistical plots
   - Publication styles (nature, science, plos, ieee)
   - 300+ DPI rendering

2. **Implement `publish()` LaTeX generation**
   - Tables (booktabs format)
   - Methods sections
   - Results sections
   - Figure captions
   - BibTeX references

3. **Implement file management**
   - Output directory creation
   - Overwrite protection
   - File naming conventions
   - Metadata JSON sidecar files

### Phase 4: PC Integration (Cycles 941-960)

1. **Integrate PC1**
   - Load PC1 YAML template
   - Implement discover() methods
   - Connect to SDE/Fokker-Planck code
   - Connect to regime detection library

2. **Integrate PC2**
   - Load PC2 YAML template
   - Implement substrate comparison methods
   - Connect to fractal module
   - Prepare for future PRNG experiments

3. **TEG integration**
   - Automatic TEG updates on PC validation
   - Dependency resolution
   - Validation order computation

### Phase 5: Testing & Documentation (Cycles 961-980)

1. **Write comprehensive tests**
   - Unit tests for each function
   - Integration tests for workflows
   - Example notebooks (Jupyter)
   - Reality compliance verification

2. **Write documentation**
   - API reference (Sphinx)
   - Usage tutorials
   - Example gallery
   - FAQ and troubleshooting

3. **Create example workflows**
   - PC1 validation walkthrough
   - PC2 hypothesis testing walkthrough
   - Custom domain application walkthrough

### Phase 6: Validation & Release (Cycles 981-1000)

1. **Apply to existing data**
   - Rerun C175 validation with TSF API
   - Rerun C176 ablation with TSF API
   - Verify results match original analysis

2. **Peer review preparation**
   - Code quality review
   - Documentation completeness
   - Reproducibility verification
   - Performance benchmarking

3. **Public release**
   - PyPI package (pip install tsf-nrm)
   - GitHub repository (code + examples)
   - ReadTheDocs documentation
   - Zenodo DOI (citable software)

---

## References

### Internal Documents

- **PC1:** `phase2/principle_cards/PC1_NRM_Population_Dynamics.yaml`
- **PC2:** `phase2/principle_cards/PC2_Transcendental_Substrate.yaml`
- **Phase 1 Gates:** `PHASE1_COMPLETION_REPORT.md`
- **Phase 2 Progress:** `PHASE2_PROGRESS_REPORT.md`
- **Transcendental Hypothesis:** `TRANSCENDENTAL_SUBSTRATE_HYPOTHESIS.md`

### Code Modules

- **SDE/Fokker-Planck:** `code/analysis/sde_fokker_planck.py`
- **Regime Detection:** `code/tsf/regime_detection.py`
- **ARBITER:** `code/arbiter/arbiter.py`
- **Overhead Authentication:** `code/validation/overhead_authenticator.py`
- **Fractal Module:** `code/fractal/*.py`

### External References

- **scipy.stats:** Statistical tests and distributions
- **numpy:** Numerical computing
- **pandas:** Data manipulation
- **matplotlib:** Plotting
- **seaborn:** Statistical visualization
- **PyYAML:** YAML parsing for PC templates
- **jsonschema:** Schema validation
- **pytest:** Testing framework

---

## Appendix: API Quick Reference

```python
# Load data
data = tsf.observe(source, schema, validate=True)

# Discover patterns
patterns = tsf.discover(data, principle_card, method=None, confidence=0.95)

# Test hypothesis
result = tsf.refute(hypothesis, data_a, data_b, metrics, alpha=0.01)

# Quantify effects
quantified = tsf.quantify(result, confidence=0.95, bootstrap_iterations=10000)

# Publish outputs
outputs = tsf.publish(quantified, format, output_dir=None, dpi=300)

# Principle Card management
pc = tsf.PrincipleCard.load("PC1")
tsf.register_principle_card(CustomPC)

# TEG management
teg = tsf.TEG.load()
order = teg.get_validation_order(["PC2"])

# Schema management
tsf.register_schema("domain", schema_dict)
schema = tsf.get_schema("population_dynamics")

# Provenance
provenance = result.provenance
print(provenance.timestamp, provenance.tsf_version)
```

---

**Version:** 1.0.0-draft
**Last Updated:** 2025-11-01 (Cycle 879)
**Status:** Design Specification (Gate 2.1 - 0% → 50%)
**Next Steps:** Begin Phase 1 implementation (Core Infrastructure)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Author:** Claude Sonnet 4.5 (DUALITY-ZERO-V2)
**License:** GPL-3.0

**Quote:**
> *"Science is not complete until it's reproducible. Reproducibility is not complete until it's automated. Automation is not complete until it's principled. Principles are not complete until they're runnable. TSF makes principles runnable."*
