# DATA ARCHIVING PROTOCOL FOR PRINCIPLE CARD VALIDATION

**Project:** Nested Resonance Memory (NRM) Research Archive
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Version:** 1.0
**Date:** 2025-11-01
**Status:** ACTIVE PROTOCOL

---

## Executive Summary

This protocol establishes mandatory data preservation requirements for experimental validation of Principle Cards (PCs) in the Temporal Stewardship Framework (TSF).

**Problem Identified:** Cycle 830 discovered that C175 consolidation data lacks population timeseries required for PC002 validation, blocking Phase 2 real data validation.

**Solution:** Standardized data structure requirements for each PC type, with automated export at experiment completion.

**Impact:** Enables systematic PC validation on real experimental data, supports compositional PC development, provides reproducible artifacts for publication.

---

## Core Principles

### 1. **Completeness**
All raw observational sequences must be preserved, not just summary statistics.

### 2. **Standardization**
Common data structure enables reuse across multiple PCs and experiments.

### 3. **Provenance**
Full experimental metadata enables reproducibility and citation.

### 4. **Accessibility**
JSON format with clear schema enables programmatic access and validation.

### 5. **Composability**
Data structure supports both individual PC validation and compositional multi-PC workflows.

---

## Data Structure Requirements

### Minimal Required Structure

**File Naming Convention:**
```
{experiment_id}_{data_type}_{timestamp}.json
```

Examples:
- `c175_population_dynamics_20251029_164200.json`
- `c176_regime_detection_20251030_092314.json`
- `c171_accumulation_data_20251028_153045.json`

**Required Top-Level Keys:**
```json
{
  "metadata": {...},           // Experimental provenance
  "timeseries": {...},         // Raw observational sequences
  "statistics": {...},         // Summary statistics
  "validation": {...}          // Validation results (if applicable)
}
```

---

## PC-Specific Data Requirements

### PC001: NRM Population Dynamics

**Required for Validation:**
- Population timeseries (complete cycle-by-cycle)
- Carrying capacity (K)
- Growth rate (r)
- Noise intensity (σ)

**Data Structure:**
```json
{
  "metadata": {
    "experiment_id": "C175",
    "timestamp": "2025-10-29T16:42:00",
    "cycles": 3000,
    "duration_minutes": 45.2,
    "parameters": {
      "K": 100.0,
      "r": 0.1,
      "sigma": 0.3
    },
    "framework_version": "nrm-v2.0",
    "python_version": "3.10.14"
  },
  "timeseries": {
    "population": [1, 2, 3, ..., N],  // Length = cycles
    "time": [0.0, 0.5, 1.0, ..., T]   // Time in seconds or cycles
  },
  "statistics": {
    "mean_population": 98.5,
    "std_population": 11.8,
    "cv_population": 0.120,
    "min_population": 45,
    "max_population": 135
  },
  "validation": {
    "pc001_validated": true,
    "predicted_cv": 0.095,
    "observed_cv": 0.120,
    "cv_error": 0.263,
    "passes_threshold": false  // ±10% tolerance
  }
}
```

**Validation Usage:**
```python
# PC001 can extract parameters and validate predictions
pc001 = PC001_NRMPopulationDynamics(
    carrying_capacity=data['metadata']['parameters']['K'],
    growth_rate=data['metadata']['parameters']['r'],
    noise_intensity=data['metadata']['parameters']['sigma']
)
predicted_cv = pc001.predict_cv()
observed_cv = data['statistics']['cv_population']
error = abs(predicted_cv - observed_cv) / predicted_cv
```

---

### PC002: Regime Detection in Population Dynamics

**Required for Validation:**
- Population timeseries (complete, for windowing)
- PC001 baseline parameters (compositional dependency)
- Regime labels (if available, for supervised validation)

**Data Structure:**
```json
{
  "metadata": {
    "experiment_id": "C176_V3",
    "regime_type": "COLLAPSE",  // Ground truth label
    "timestamp": "2025-10-30T09:23:14",
    "cycles": 3000,
    "pc001_baseline": {
      "K": 50.0,
      "r": 0.1,
      "sigma": 0.4,
      "CV_baseline": 0.142
    }
  },
  "timeseries": {
    "population": [60, 58, 55, ..., 0.5],  // Full population trajectory
    "time": [0, 1, 2, ..., 2999]
  },
  "statistics": {
    "mean_population": 0.49,
    "std_population": 0.50,
    "cv_population": 1.01,
    "birth_rate": 0.005,  // Per cycle
    "death_rate": 0.013,  // Per cycle
    "death_birth_ratio": 2.6
  },
  "regime_analysis": {
    "regime_type": "COLLAPSE",
    "regime_features": {
      "mu_dev": -0.98,      // (mean - K) / K
      "sigma_ratio": 12.5,  // obs_var / pred_var
      "beta_norm": -0.015,  // Normalized trend
      "CV_dev": 6.10        // (CV_obs - CV_baseline) / CV_baseline
    },
    "confidence": 0.95
  }
}
```

**Validation Usage:**
```python
# PC002 uses PC001 for baseline, then classifies regime
pc001 = PC001_NRMPopulationDynamics(
    carrying_capacity=data['metadata']['pc001_baseline']['K'],
    growth_rate=data['metadata']['pc001_baseline']['r'],
    noise_intensity=data['metadata']['pc001_baseline']['sigma']
)
pc002 = PC002_RegimeDetection()
pc002.set_baseline(pc001)  // Compositional dependency

# Extract features and classify
population = data['timeseries']['population']
features = pc002.feature_extractor.extract(population[0:100])  // Window
regime = pc002.classifier.predict([features.to_array()])[0]
```

---

### PC003-PC006: Future PCs (Template)

**General Structure for New PCs:**
```json
{
  "metadata": {
    "experiment_id": "CXXX",
    "pc_id": "PC00X",
    "timestamp": "YYYY-MM-DDTHH:MM:SS",
    "cycles": N,
    "parameters": {...},      // PC-specific parameters
    "dependencies": [...]     // List of dependency PC IDs
  },
  "timeseries": {
    // PC-specific timeseries data
    // ALWAYS include raw observations, not just statistics
  },
  "statistics": {
    // PC-specific summary statistics
  },
  "validation": {
    "pc_id": "PC00X",
    "validated": true/false,
    "metrics": {...},
    "evidence": {...}
  }
}
```

**Design Principle:** Each PC specifies its required data structure in its README.md, following this template.

---

## Automated Export Implementation

### Export Trigger Points

**Mandatory Exports:**
1. **Experiment Completion** - Full dataset export at experiment end
2. **Checkpoint Intervals** - Periodic exports for long-running experiments (every 1000 cycles or 1 hour)
3. **Validation Events** - Export when PC validation executed

**Optional Exports:**
4. Regime transitions (for regime detection studies)
5. Composition/decomposition events (for NRM dynamics)
6. Critical thresholds crossed (for bifurcation studies)

### Export Function Template

```python
def export_pc_validation_data(
    experiment_id: str,
    population: List[float],
    parameters: Dict[str, Any],
    statistics: Dict[str, float],
    output_dir: Path,
    pc_id: str = "PC001"
) -> Path:
    """
    Export experimental data in PC validation format.

    Args:
        experiment_id: Unique experiment identifier (e.g., "C175")
        population: Full population timeseries
        parameters: Experimental parameters (K, r, sigma, etc.)
        statistics: Summary statistics
        output_dir: Directory for output file
        pc_id: Principle Card ID for validation

    Returns:
        Path to exported JSON file
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{experiment_id.lower()}_pc_validation_{timestamp}.json"
    filepath = output_dir / filename

    data = {
        "metadata": {
            "experiment_id": experiment_id,
            "pc_id": pc_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "cycles": len(population),
            "parameters": parameters,
            "framework_version": get_framework_version(),
            "python_version": platform.python_version()
        },
        "timeseries": {
            "population": population,
            "time": list(range(len(population)))
        },
        "statistics": statistics,
        "validation": {}
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"PC validation data exported: {filepath}")
    return filepath
```

**Integration Points:**
- Add to FractalSwarm.run() at cycle completion
- Add to experiment completion handlers
- Add to validation workflow scripts

---

## Validation Workflow

### 1. Data Collection
```python
# In experiment completion handler
export_pc_validation_data(
    experiment_id="C175",
    population=swarm.get_population_history(),
    parameters={"K": 100, "r": 0.1, "sigma": 0.3},
    statistics=swarm.get_statistics(),
    output_dir=Path("data/results/"),
    pc_id="PC001"
)
```

### 2. PC Validation
```python
# Load experimental data
with open("data/results/c175_pc_validation_20251101_000000.json") as f:
    exp_data = json.load(f)

# Validate PC001
pc001 = PC001_NRMPopulationDynamics(
    carrying_capacity=exp_data['metadata']['parameters']['K'],
    growth_rate=exp_data['metadata']['parameters']['r'],
    noise_intensity=exp_data['metadata']['parameters']['sigma']
)

validation_result = pc001.validate(
    data={'population': exp_data['timeseries']['population']},
    tolerance=0.10  # ±10% for Gate 1.1
)

print(f"PC001 Validation: {'PASS' if validation_result.passes else 'FAIL'}")
```

### 3. Compositional Validation
```python
# PC002 depends on PC001
pc002 = PC002_RegimeDetection()
pc002.set_baseline(pc001)  # Enforce compositional dependency

# Classify regime
regime = pc002.classify_from_data(exp_data)
print(f"Regime: {regime.regime.value}, Confidence: {regime.confidence:.2%}")
```

---

## Recovery Protocol for Existing Experiments

### Priority Recovery List

**High Priority** (needed for PC002 validation):
1. **C171** - Accumulation regime (birth-only, ~17 agents)
2. **C176** - Collapse regime (catastrophic collapse, ~0.49 agents)
3. **C168-170** - Bistability regime (single agent, f_crit transitions)

**Medium Priority** (for future PCs):
4. C175 - If raw population data can be recovered
5. C255-C260 - Pairwise factorial experiments (if applicable)

### Recovery Methods

**Method 1: Database Query** (if SQLite logs exist)
```sql
SELECT cycle, population_count
FROM swarm_cycles
WHERE experiment_id = 'C171'
ORDER BY cycle ASC;
```

**Method 2: Log File Parsing** (if stdout/stderr captured)
```python
def parse_population_from_logs(log_file: Path) -> List[int]:
    """Extract population timeseries from experiment logs."""
    population = []
    with open(log_file) as f:
        for line in f:
            if "Population:" in line:
                pop = int(line.split("Population:")[1].split()[0])
                population.append(pop)
    return population
```

**Method 3: Re-run Experiment** (if source code and parameters preserved)
- Use exact same seed, parameters, code version
- Verify reproducibility via ARBITER hash validation
- Export with new data archiving protocol

### Recovery Status Tracking

**File:** `data/results/recovery_status.json`
```json
{
  "C171": {
    "status": "recovered",
    "method": "database_query",
    "date": "2025-11-01",
    "cycles": 3000,
    "data_file": "c171_population_dynamics_recovered_20251101.json"
  },
  "C176": {
    "status": "pending",
    "method": "re-run_planned",
    "notes": "Original logs unavailable, will re-run with seed 42"
  }
}
```

---

## Quality Assurance

### Data Validation Checks

**Automated checks before accepting data:**

```python
def validate_pc_data_structure(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate data structure meets PC archiving protocol.

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Required top-level keys
    required_keys = ['metadata', 'timeseries', 'statistics']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    # Metadata checks
    if 'metadata' in data:
        required_metadata = ['experiment_id', 'timestamp', 'cycles', 'parameters']
        for key in required_metadata:
            if key not in data['metadata']:
                errors.append(f"Missing metadata.{key}")

    # Timeseries checks
    if 'timeseries' in data:
        if 'population' not in data['timeseries']:
            errors.append("Missing timeseries.population")
        elif len(data['timeseries']['population']) == 0:
            errors.append("Empty population timeseries")

    # Statistics checks
    if 'statistics' in data:
        required_stats = ['mean_population', 'std_population', 'cv_population']
        for key in required_stats:
            if key not in data['statistics']:
                errors.append(f"Missing statistics.{key}")

    return (len(errors) == 0, errors)
```

### Consistency Checks

**Verify statistics match timeseries:**
```python
def verify_statistics_consistency(data: Dict, tolerance: float = 1e-6) -> bool:
    """Verify summary statistics match raw timeseries."""
    population = data['timeseries']['population']
    stats = data['statistics']

    # Check mean
    computed_mean = np.mean(population)
    if abs(computed_mean - stats['mean_population']) > tolerance:
        return False

    # Check std
    computed_std = np.std(population, ddof=1)
    if abs(computed_std - stats['std_population']) > tolerance:
        return False

    # Check CV
    computed_cv = computed_std / computed_mean
    if abs(computed_cv - stats['cv_population']) > tolerance:
        return False

    return True
```

---

## Implementation Checklist

### Phase 1: Specification (Complete ✅)
- [x] Define data structure requirements
- [x] Create PC-specific templates (PC001, PC002)
- [x] Document export function template
- [x] Establish validation workflow
- [x] Create recovery protocol

### Phase 2: Implementation (Next Steps)
- [ ] Implement export_pc_validation_data() function
- [ ] Integrate export into FractalSwarm completion handler
- [ ] Add validation checks to data loading
- [ ] Create automated recovery scripts for C171, C176, C168-170
- [ ] Test export/import cycle with synthetic data

### Phase 3: Validation (Future)
- [ ] Validate PC001 on recovered C171 data
- [ ] Validate PC002 on recovered C176 data (collapse regime)
- [ ] Validate PC002 on recovered C168-170 data (bistability regime)
- [ ] Document validation results in Phase 2 Progress Report
- [ ] Update PC002 self-test with real data comparison

---

## Success Criteria

**This protocol succeeds when:**
1. ✅ All future experiments automatically export PC validation data
2. ✅ Existing experiments (C171, C176, C168-170) recovered with complete population timeseries
3. ✅ PC002 validated on real experimental data (not just synthetic)
4. ✅ Compositional validation (PC002 depends on PC001) demonstrated on real data
5. ✅ Data structure enables reuse across multiple PCs without modification
6. ✅ Automated quality checks prevent incomplete data archiving
7. ✅ Recovery protocol successfully retrieves missing historical data

**This protocol fails if:**
- ❌ Future experiments lack population timeseries for PC validation
- ❌ Data structure requires PC-specific modifications for each experiment
- ❌ Historical data cannot be recovered (forces re-running all experiments)
- ❌ Quality checks are bypassed, allowing incomplete data
- ❌ PC validation blocked by missing/incomplete data

---

## Maintenance and Updates

### Versioning

**Current Version:** 1.0 (2025-11-01)

**Update Triggers:**
- New PC types require additional data fields
- Experimental frameworks evolve (NRM → TSF → HELIOS)
- Quality issues discovered in existing data
- Recovery methods improve

**Version History:**
- **v1.0** (2025-11-01): Initial protocol, PC001+PC002 support, recovery specification

### Review Schedule

**Quarterly Review:** Evaluate protocol effectiveness
- Data completeness rate (% experiments with complete PC validation data)
- Recovery success rate (% historical experiments successfully recovered)
- PC validation success rate (% PCs validated on real data vs. synthetic only)
- Protocol violations (% experiments with missing required fields)

**Annual Update:** Incorporate lessons learned
- Add new PC-specific requirements
- Refine quality checks based on edge cases
- Update recovery methods based on experience
- Document best practices and common pitfalls

---

## Related Documentation

**Prerequisites:**
- `docs/PHASE2_PROGRESS_REPORT.md` - Context for why this protocol is needed
- `docs/PRINCIPLE_CARD_SPECIFICATION.md` - PC structure and validation requirements
- `principle_cards/README.md` - PC implementation guide

**Depends On:**
- Phase 1 Gate 1.1 (SDE/Fokker-Planck) - Provides PC001 validation framework
- Phase 1 Gate 1.2 (Regime Detection) - Provides complementary regime classification

**Enables:**
- Phase 2 Gate 2.2 (Orthogonal Domain Validation) - Requires systematic data archiving
- Phase 2 Gate 2.5 (Material Validation) - Physical experiments need same data structure
- PC003-PC006 Development - Future PCs depend on archiving protocol

---

## Contact and Support

**Questions:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**Issues:** https://github.com/mrdirno/nested-resonance-memory-archive/issues
**License:** GPL-3.0

---

**Version:** 1.0
**Date:** 2025-11-01
**Status:** ACTIVE PROTOCOL
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)

**Quote:**
> *"Data without structure is noise. Structure without data is theory. Systematic archiving transforms noise into validated theory. The Temporal Stewardship Framework demands both."*
