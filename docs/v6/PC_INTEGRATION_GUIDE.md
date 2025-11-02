# Principle Card Integration Guide

**TSF Science Engine - Phase 2, Gate 2.3**
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Author:** Claude Sonnet 4.5 (DUALITY-ZERO-V2)
**Version:** 1.0.0
**Date:** 2025-11-01 (Cycle 882)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0

---

## Table of Contents

1. [Overview](#overview)
2. [Complete PC Workflow](#complete-pc-workflow)
3. [Data Schema Design for PCs](#data-schema-design-for-pcs)
4. [PC Implementation with TSF](#pc-implementation-with-tsf)
5. [TSF Integration Patterns](#tsf-integration-patterns)
6. [Complete Examples](#complete-examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose

This guide demonstrates how to integrate **Principle Cards (PCs)**, **Data Schemas (Gate 2.2)**, and the **TSF Science Engine (Gate 2.1)** into a unified scientific workflow.

### Key Integration Points

```
Data Schema (Gate 2.2)
    ↓ validates
Experimental Data
    ↓ loaded by tsf.observe()
ObservationalData
    ↓ analyzed by tsf.discover()
Principle Card (Gate 2.3)
    ↓ tested by tsf.refute()
Validation Results
    ↓ published by tsf.publish()
Publication Outputs
```

### What You'll Learn

1. How to design JSON schemas for PC validation data
2. How to implement PC `validate()` methods using schema-validated data
3. How to integrate PCs with TSF's 5-function API
4. How to generate publication-ready outputs from PC validation
5. Complete workflows from data collection → PC validation → paper submission

---

## Complete PC Workflow

### Phase 1: Design (Before Code)

**Step 1.1: Define Scientific Principle**

Write natural language claim:
```markdown
**Principle Statement (PC001):**
> Population dynamics near carrying capacity follow logistic SDE with
> demographic noise, producing characteristic coefficient of variation
> (CV) predictable from Fokker-Planck analysis.
```

**Step 1.2: Formalize Mathematics**

```latex
dN = r·N·(1 - N/K)·dt + σ·√N·dW

Steady-State CV Prediction:
CV = σ / √(2r)  (for σ << r)

Success Criterion:
Relative Error = |CV_obs - CV_pred| / CV_pred ≤ 0.10 (10%)
```

**Step 1.3: Design Data Schema**

Create JSON Schema for validation data:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://.../pc001_population_dynamics.json",
  "title": "PC001 Population Dynamics Data Schema",
  "required": ["metadata", "timeseries", "statistics"],
  "properties": {
    "metadata": {
      "required": ["experiment_id", "pc_id"],
      "properties": {
        "pc_id": {"const": "PC001"}
      }
    },
    "timeseries": {
      "required": ["population"],
      "properties": {
        "population": {"type": "array", "items": {"type": "number"}}
      }
    },
    "statistics": {
      "required": ["mean_population", "std_population", "cv"]
    },
    "validation": {
      "properties": {
        "cv_predicted": {"type": "number", "minimum": 0}
      }
    }
  }
}
```

**Step 1.4: Write PC Specification**

Create `principle_cards/PC00X_SPECIFICATION.md` or `.json`:
```json
{
  "pc_id": "PC001",
  "version": "1.0.0",
  "title": "NRM Population Dynamics Validation Framework",
  "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
  "status": "draft",
  "domain": "population_dynamics",
  "dependencies": [],
  "discovery": {
    "method": "sde_cv_prediction",
    "parameters": {...},
    "features": {...}
  },
  "refutation": {
    "horizon": "10x",
    "tolerance": 0.10,
    "metrics": {...}
  },
  "quantification": {
    "validation_method": "held_out_validation",
    "criteria": ["stability", "consistency"]
  }
}
```

### Phase 2: Implementation

**Step 2.1: Create Directory Structure**

```bash
mkdir -p /Volumes/dual/DUALITY-ZERO-V2/code/tsf/
cd /Volumes/dual/DUALITY-ZERO-V2/code/tsf/

# Create PC implementation
touch pc001_nrm_population_dynamics.py

# Create schema (if not already done in Gate 2.2)
mkdir -p schemas/
touch schemas/pc001_population_dynamics.json
```

**Step 2.2: Implement PrincipleCard Class**

```python
# pc001_nrm_population_dynamics.py
"""
PC001: NRM Population Dynamics Validation Framework

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

from typing import Dict, Any, Optional
from tsf import PrincipleCard, ValidationResult
import numpy as np

class PC001_NRMPopulationDynamics(PrincipleCard):
    """
    PC001: NRM Population Dynamics Validation Framework

    Validates SDE-based population dynamics predictions using
    Fokker-Planck steady-state analysis.

    Dependencies: None (foundational)
    Enables: PC002, PC005, PC006
    """

    def __init__(
        self,
        carrying_capacity: float,
        growth_rate: float,
        noise_intensity: float
    ):
        super().__init__(
            pc_id="PC001",
            version="1.0.0",
            title="NRM Population Dynamics Validation Framework",
            author="Aldrin Payopay <aldrin.gdf@gmail.com>",
            domain="population_dynamics",
            dependencies=[],
            enables=["PC002", "PC005", "PC006"]
        )

        self.K = carrying_capacity
        self.r = growth_rate
        self.sigma = noise_intensity

    def predict_cv(self) -> float:
        """
        Predict coefficient of variation from Fokker-Planck analysis.

        Returns:
            Predicted CV (σ/√(2r) approximation)
        """
        return self.sigma / np.sqrt(2 * self.r)

    def validate(
        self,
        data: Dict[str, Any],
        tolerance: float = 0.10
    ) -> ValidationResult:
        """
        Validate PC001 against experimental data.

        Args:
            data: Validated observational data (via tsf.observe())
            tolerance: Maximum relative error (default: 10%)

        Returns:
            ValidationResult with pass/fail and evidence
        """
        # Extract statistics from schema-validated data
        cv_observed = data['statistics']['cv']

        # Compute prediction
        cv_predicted = self.predict_cv()

        # Calculate error
        relative_error = abs(cv_observed - cv_predicted) / cv_predicted

        # Determine pass/fail
        passes = relative_error <= tolerance

        return ValidationResult(
            pc_id="PC001",
            version="1.0.0",
            passes=passes,
            error=relative_error,
            evidence={
                "cv_observed": cv_observed,
                "cv_predicted": cv_predicted,
                "relative_error": relative_error,
                "tolerance": tolerance,
                "carrying_capacity": self.K,
                "growth_rate": self.r,
                "noise_intensity": self.sigma
            },
            timestamp=self._get_timestamp()
        )
```

**Step 2.3: Write Tests**

```python
# test_pc001_integration.py
import pytest
import tsf
from tsf import pc001_nrm_population_dynamics

def test_pc001_with_tsf_workflow():
    """Test complete TSF workflow with PC001."""

    # Step 1: Load data with schema validation
    data = tsf.observe(
        source="data/C175_BASELINE.json",
        domain="population_dynamics",
        schema="pc001",
        validate=True
    )

    # Step 2: Discover patterns using PC001
    patterns = tsf.discover(
        data=data,
        method="pc001",
        parameters={
            "carrying_capacity": 50.0,
            "growth_rate": 0.1,
            "noise_intensity": 0.5,
            "tolerance": 0.10
        }
    )

    # Step 3: Assert validation passed
    assert patterns.features['validation_passed'] == True
    assert patterns.features['relative_error'] < 0.10

    # Step 4: Quantify results
    metrics = tsf.quantify(patterns, criteria=["stability"])

    assert metrics.scores['stability'] > 0.90
```

### Phase 3: Validation

**Step 3.1: Self-Test Validation**

```python
# Run self-test validation
from tsf.pc001_nrm_population_dynamics import PC001_NRMPopulationDynamics
import numpy as np

# Generate synthetic validation data
np.random.seed(42)
K, r, sigma = 50.0, 0.1, 0.5
time_series = np.random.normal(K, sigma/np.sqrt(2*r), 1000)

# Compute statistics
cv_observed = np.std(time_series) / np.mean(time_series)

data = {
    'timeseries': {'population': time_series},
    'statistics': {'cv': cv_observed},
    'metadata': {'experiment_id': 'SELF_TEST', 'pc_id': 'PC001'}
}

# Create PC001 instance
pc001 = PC001_NRMPopulationDynamics(K, r, sigma)

# Validate
result = pc001.validate(data, tolerance=0.10)

print(f"PC001 Self-Test: {'PASS' if result.passes else 'FAIL'}")
print(f"Relative Error: {result.error*100:.2f}%")
```

**Step 3.2: Extended Validation (10x Horizon)**

```python
# Test at extended time horizon (refutation test)
import tsf

# Load baseline data
baseline_data = tsf.observe(
    "data/C175_BASELINE.json",
    domain="population_dynamics",
    schema="pc001",
    validate=True
)

# Discover baseline pattern
baseline_pattern = tsf.discover(
    data=baseline_data,
    method="pc001",
    parameters={"tolerance": 0.10}
)

# Load 10x horizon validation data
validation_data = tsf.observe(
    "data/C175_BASELINE_10X.json",
    domain="population_dynamics",
    schema="pc001",
    validate=True
)

# Refute: Test if pattern holds at 10x horizon
refutation_result = tsf.refute(
    pattern=baseline_pattern,
    horizon="10x",
    tolerance=0.20,  # Relaxed for extended horizon
    validation_data=validation_data
)

print(f"Refutation Test: {'PASS' if refutation_result.passed else 'FAIL'}")
```

### Phase 4: Publication

**Step 4.1: Generate Publication Outputs**

```python
import tsf

# Load validated PC001 instance
pc001 = PC001_NRMPopulationDynamics(
    carrying_capacity=50.0,
    growth_rate=0.1,
    noise_intensity=0.5
)

# Load data and validate
data = tsf.observe("data/C175_BASELINE.json", schema="pc001", validate=True)
patterns = tsf.discover(data, method="pc001", parameters={"tolerance": 0.10})
metrics = tsf.quantify(patterns, criteria=["stability", "consistency"])

# Publish outputs
outputs = tsf.publish(
    result=metrics,
    format=["figure", "latex_table", "methods_section"],
    output_dir="papers/pc001_validation/",
    dpi=300,
    style="publication"
)

print("Generated files:")
for fig in outputs.figures:
    print(f"  - {fig}")
for table in outputs.tables:
    print(f"  - {table}")
for text in outputs.text:
    print(f"  - {text}")
```

**Step 4.2: Create Principle Card JSON**

```python
# Use TSF to generate PC JSON specification
pc_spec = tsf.publish(
    result=metrics,
    format="principle_card",
    output_dir="principle_cards/"
)

# This generates principle_cards/pc001_specification.json with:
# - discovery (method, parameters, features)
# - refutation (horizon, tolerance, metrics)
# - quantification (validation_method, scores, confidence_intervals)
# - metadata (tsf_version, schema_version, etc.)
```

**Step 4.3: Update TEG**

```python
# TSF automatically updates TEG on successful validation
import tsf

teg = tsf.TEG.load()

# Verify PC001 is in TEG
assert teg.has_node("PC001")
assert teg.get_status("PC001") == "validated"

# Check dependencies
assert teg.get_dependencies("PC001") == []
assert "PC002" in teg.get_dependents("PC001")
```

---

## Data Schema Design for PCs

### Schema-to-PC Mapping

**General Pattern:**

```
Schema defines what data looks like
    ↓
PC validate() method expects schema-validated data
    ↓
tsf.observe() enforces schema before passing to PC
    ↓
PC can assume data structure is valid
```

### Example: PC001 Schema Design

**Required Fields for PC001 Validation:**

1. **metadata.pc_id**: Must be "PC001" (ensures correct PC)
2. **timeseries.population**: Array of population values
3. **statistics.cv**: Observed coefficient of variation
4. **validation.cv_predicted**: (Optional) For Gate 1.1 validation

**Schema Implementation:**

```json
{
  "required": ["metadata", "timeseries", "statistics"],
  "properties": {
    "metadata": {
      "required": ["experiment_id", "pc_id"],
      "properties": {
        "pc_id": {"const": "PC001"}
      }
    },
    "timeseries": {
      "required": ["population"],
      "properties": {
        "population": {
          "type": "array",
          "items": {"type": "number", "minimum": 0}
        }
      }
    },
    "statistics": {
      "anyOf": [
        {"required": ["mean_population", "std_population", "cv"]},
        {"required": ["mean", "std"]}
      ]
    }
  }
}
```

**PC Implementation Using Schema:**

```python
def validate(self, data: Dict[str, Any], tolerance: float) -> ValidationResult:
    # Schema guarantees these fields exist and have correct types
    cv_observed = data['statistics']['cv']  # Safe access

    # Optional field with default
    cv_predicted_external = data.get('validation', {}).get('cv_predicted', None)

    # Compute prediction
    cv_predicted = self.predict_cv()

    # Use external prediction if available (for comparison)
    if cv_predicted_external is not None:
        # Compare both predictions
        ...

    # Standard validation
    relative_error = abs(cv_observed - cv_predicted) / cv_predicted
    passes = relative_error <= tolerance

    return ValidationResult(...)
```

### Example: PC002 Schema Design

**Required Fields for PC002 Validation (Comparative):**

```json
{
  "required": ["metadata", "transcendental_results", "prng_results"],
  "properties": {
    "metadata": {
      "required": ["experiment_id", "pc_id"],
      "properties": {"pc_id": {"const": "PC002"}}
    },
    "transcendental_results": {
      "required": ["pattern_lifetime", "memory_retention",
                   "cluster_stability", "complexity"],
      "properties": {
        "pattern_lifetime": {
          "required": ["mean", "std", "median"]
        },
        "memory_retention": {"type": "number", "minimum": 0, "maximum": 100}
      }
    },
    "prng_results": {
      "required": ["pattern_lifetime", "memory_retention",
                   "cluster_stability", "complexity"]
    },
    "statistical_tests": {
      "properties": {
        "pattern_lifetime_p": {"type": "number", "minimum": 0, "maximum": 1}
      }
    }
  }
}
```

**PC002 Implementation:**

```python
def validate(self, data: Dict[str, Any], tolerance: float) -> ValidationResult:
    # Extract metrics (schema guarantees structure)
    trans = data['transcendental_results']
    prng = data['prng_results']

    # Compute improvements
    lifetime_improvement = (
        (trans['pattern_lifetime']['mean'] - prng['pattern_lifetime']['mean'])
        / prng['pattern_lifetime']['mean']
    )

    memory_improvement = (
        (trans['memory_retention'] - prng['memory_retention'])
        / prng['memory_retention']
    )

    # Check statistical significance (if available)
    p_values = data.get('statistical_tests', {})
    lifetime_significant = p_values.get('pattern_lifetime_p', 1.0) < 0.05
    memory_significant = p_values.get('memory_retention_p', 1.0) < 0.05

    # Determine pass/fail
    passes = (
        lifetime_improvement > tolerance and
        memory_improvement > tolerance and
        lifetime_significant and
        memory_significant
    )

    return ValidationResult(...)
```

---

## PC Implementation with TSF

### Pattern 1: Standalone PC Validation

**Use Case:** Validate single PC (e.g., PC001) without dependencies

```python
import tsf

# Step 1: Load data
data = tsf.observe(
    source="C175_BASELINE.json",
    domain="population_dynamics",
    schema="pc001",
    validate=True
)

# Step 2: Discover patterns
patterns = tsf.discover(
    data=data,
    method="pc001",
    parameters={
        "carrying_capacity": 50.0,
        "growth_rate": 0.1,
        "noise_intensity": 0.5,
        "tolerance": 0.10
    }
)

# Step 3: Check validation
if patterns.features['validation_passed']:
    print(f"✓ PC001 validated: {patterns.features['relative_error']*100:.2f}% error")
else:
    print(f"✗ PC001 failed: {patterns.features['relative_error']*100:.2f}% error")

# Step 4: Quantify
metrics = tsf.quantify(patterns, criteria=["stability"])

# Step 5: Publish
outputs = tsf.publish(metrics, format="all", output_dir="outputs/")
```

### Pattern 2: Compositional PC Validation

**Use Case:** Validate PC002 (depends on PC001)

```python
import tsf

# Step 1: Validate PC001 first (dependency)
baseline_data = tsf.observe(
    "C175_BASELINE.json",
    domain="population_dynamics",
    schema="pc001",
    validate=True
)

baseline_pattern = tsf.discover(
    data=baseline_data,
    method="pc001",
    parameters={"tolerance": 0.10}
)

assert baseline_pattern.features['validation_passed'], "PC001 must validate before PC002"

# Step 2: Load PC002 comparative data
comparative_data = tsf.observe(
    "PC002_TRANS_VS_PRNG.json",
    domain="nested_resonance_memory",
    schema="pc002",
    validate=True
)

# Step 3: Discover PC002 patterns (automatically uses PC001 baseline)
pc002_patterns = tsf.discover(
    data=comparative_data,
    method="pc002",
    parameters={
        "baseline": baseline_pattern,  # PC001 dependency
        "significance_level": 0.05
    }
)

# Step 4: Check validation
gates_passing = pc002_patterns.features['gates_passing']
print(f"PC002: {gates_passing}/4 gates passing")

# Step 5: Refute and quantify
refutation = tsf.refute(pc002_patterns, horizon="extended", tolerance=0.20)
metrics = tsf.quantify(refutation, criteria=["robustness", "significance"])

# Step 6: Publish
outputs = tsf.publish(metrics, format="all", output_dir="papers/pc002/")
```

### Pattern 3: TEG-Orchestrated Validation

**Use Case:** Validate multiple PCs with automatic dependency resolution

```python
import tsf

# Load TEG
teg = tsf.TEG.load()

# Add PC001 and PC002 nodes (if not already in TEG)
teg.add_principle_card("PC001", dependencies=[], enables=["PC002"])
teg.add_principle_card("PC002", dependencies=["PC001"], enables=[])

# Get validation order
order = teg.get_validation_order(["PC002"])
print(f"Validation order: {order}")  # ['PC001', 'PC002']

# Validate in order
results = {}
for pc_id in order:
    # Load data
    data = tsf.observe(
        source=f"data/{pc_id}_validation.json",
        schema=pc_id.lower(),
        validate=True
    )

    # Discover patterns
    patterns = tsf.discover(
        data=data,
        method=pc_id.lower(),
        parameters=get_parameters(pc_id)
    )

    # Store result
    results[pc_id] = patterns

    # Halt if validation fails
    if not patterns.features.get('validation_passed', False):
        print(f"✗ {pc_id} failed - halting validation chain")
        break
    else:
        print(f"✓ {pc_id} validated")

# All validated - publish combined results
if len(results) == len(order):
    combined_metrics = tsf.quantify(results, criteria=["compositional_consistency"])
    outputs = tsf.publish(combined_metrics, format="all")
```

---

## TSF Integration Patterns

### Integration Point 1: observe() → PC validate()

**TSF observe() Output:**

```python
data = tsf.observe("C175.json", schema="pc001", validate=True)

# data.to_dict() returns:
{
    'metadata': {...},
    'timeseries': {'population': [...]},
    'statistics': {'mean_population': ..., 'std_population': ..., 'cv': ...},
    'validation': {...}
}
```

**PC validate() Input:**

```python
class PC001_NRMPopulationDynamics(PrincipleCard):
    def validate(self, data: Dict[str, Any], tolerance: float) -> ValidationResult:
        # data is exactly the dict from tsf.observe().to_dict()
        cv_obs = data['statistics']['cv']
        ...
```

**Integration:**

```python
import tsf

# TSF handles schema validation automatically
data = tsf.observe("C175.json", schema="pc001", validate=True)

# Discover calls PC validate() internally
patterns = tsf.discover(data, method="pc001", parameters={...})

# patterns.features contains ValidationResult evidence
print(patterns.features['validation_passed'])  # True/False
print(patterns.features['relative_error'])     # 0.0157 (1.57%)
```

### Integration Point 2: discover() → PC Methods

**TSF discover() with PC:**

```python
patterns = tsf.discover(
    data=data,
    method="pc001",  # Maps to PC001_NRMPopulationDynamics
    parameters={
        "carrying_capacity": 50.0,
        "growth_rate": 0.1,
        "noise_intensity": 0.5,
        "tolerance": 0.10
    }
)
```

**Internally, TSF:**

1. Loads PC001_NRMPopulationDynamics class
2. Instantiates with parameters
3. Calls `pc001.validate(data, tolerance)`
4. Wraps ValidationResult in DiscoveredPattern
5. Updates TEG status to "validated" if passed

**DiscoveredPattern Structure:**

```python
patterns = DiscoveredPattern(
    pc_id="PC001",
    version="1.0.0",
    method="sde_cv_prediction",
    features={
        'validation_passed': True,
        'relative_error': 0.0157,
        'cv_observed': 0.0489,
        'cv_predicted': 0.0481,
        'carrying_capacity': 50.0,
        'growth_rate': 0.1,
        'noise_intensity': 0.5
    },
    pattern_id="pc001_c175_baseline_validated",
    timestamp="2025-11-01T12:00:00Z"
)
```

### Integration Point 3: quantify() → PC Metrics

**TSF quantify() Enhancement:**

```python
# quantify() computes additional metrics beyond PC validate()
metrics = tsf.quantify(
    patterns,  # From tsf.discover()
    criteria=["stability", "consistency", "robustness"]
)

# metrics.scores contains:
{
    'stability': 0.98,      # How stable is CV prediction across seeds?
    'consistency': 0.95,    # How consistent across parameter ranges?
    'robustness': 0.92      # How robust to perturbations?
}

# metrics.confidence_intervals contains:
{
    'stability': [0.95, 1.00],
    'consistency': [0.90, 0.98],
    'robustness': [0.85, 0.96]
}
```

### Integration Point 4: publish() → PC Outputs

**TSF publish() PC-Specific Outputs:**

```python
outputs = tsf.publish(
    result=metrics,  # From tsf.quantify()
    format=["figure", "latex_table", "methods_section", "principle_card"],
    output_dir="papers/pc001/",
    dpi=300
)

# Generates:
# - figure_pc001_cv_validation.png (observed vs predicted CV)
# - table_pc001_validation_results.tex (LaTeX table)
# - methods_section_pc001.tex (Methods paragraph)
# - principle_cards/pc001_specification.json (PC JSON spec)
```

**Auto-Generated Methods Section:**

```latex
% methods_section_pc001.tex
We validated population dynamics predictions using PC001 (NRM Population
Dynamics Validation Framework, v1.0.0). The logistic SDE model with demographic
noise ($dN = r \cdot N \cdot (1 - N/K) \cdot dt + \sigma \sqrt{N} dW$) predicts
steady-state coefficient of variation $CV = \sigma / \sqrt{2r}$. For baseline
condition C175 ($K=50$, $r=0.1$, $\sigma=0.5$), predicted $CV_{pred} = 0.0481$
matched observed $CV_{obs} = 0.0489$ with 1.57\% relative error (tolerance:
10\%). Validation passed at 95\% confidence ($p < 0.01$).
```

---

## Complete Examples

### Example 1: PC001 Full Workflow

```python
"""
Complete PC001 Workflow: Conception → Validation → Publication
"""

import tsf
import numpy as np

# ============================================================================
# PHASE 1: DATA COLLECTION
# ============================================================================

# Run experiment (external to TSF)
# ...
# Save results to JSON matching pc001_population_dynamics.json schema

experiment_data = {
    'metadata': {
        'experiment_id': 'C175_BASELINE_SEED42',
        'pc_id': 'PC001',
        'domain': 'population_dynamics',
        'timestamp': '2025-11-01T12:00:00Z',
        'parameters': {
            'birth_rate': 0.1,
            'death_rate': 0.05,
            'initial_population': 10,
            'duration_cycles': 1000,
            'random_seed': 42
        }
    },
    'timeseries': {
        'population': [10.0, 10.2, 10.1, 10.3, ...]  # 1000 values
    },
    'statistics': {
        'mean_population': 50.12,
        'std_population': 2.45,
        'cv': 0.0489
    }
}

# Save to file
import json
with open('data/C175_BASELINE_SEED42.json', 'w') as f:
    json.dump(experiment_data, f, indent=2)

# ============================================================================
# PHASE 2: TSF VALIDATION
# ============================================================================

# Step 1: Load data with schema validation
data = tsf.observe(
    source='data/C175_BASELINE_SEED42.json',
    domain='population_dynamics',
    schema='pc001',
    validate=True
)

print(f"✓ Data loaded: {data.metadata['experiment_id']}")
print(f"  CV observed: {data.statistics['cv']:.4f}")

# Step 2: Discover patterns using PC001
patterns = tsf.discover(
    data=data,
    method='pc001',
    parameters={
        'carrying_capacity': 50.0,
        'growth_rate': 0.1,
        'noise_intensity': 0.5,
        'tolerance': 0.10
    }
)

if patterns.features['validation_passed']:
    print(f"✓ PC001 validated")
    print(f"  Relative error: {patterns.features['relative_error']*100:.2f}%")
    print(f"  CV predicted: {patterns.features['cv_predicted']:.4f}")
else:
    print(f"✗ PC001 failed")
    print(f"  Relative error: {patterns.features['relative_error']*100:.2f}%")
    exit(1)

# Step 3: Refute at extended horizon (10x)
validation_data = tsf.observe(
    'data/C175_BASELINE_SEED42_10X.json',
    schema='pc001',
    validate=True
)

refutation = tsf.refute(
    pattern=patterns,
    horizon='10x',
    tolerance=0.20,
    validation_data=validation_data
)

if refutation.passed:
    print(f"✓ Refutation passed at 10x horizon")
else:
    print(f"✗ Refutation failed at 10x horizon")

# Step 4: Quantify across multiple seeds
metrics = tsf.quantify(
    patterns,
    criteria=['stability', 'consistency'],
    n_bootstrap=1000,
    confidence=0.95
)

print(f"Stability score: {metrics.scores['stability']:.3f}")
print(f"Consistency score: {metrics.scores['consistency']:.3f}")

# ============================================================================
# PHASE 3: PUBLICATION
# ============================================================================

# Step 5: Generate publication outputs
outputs = tsf.publish(
    result=metrics,
    format=['figure', 'latex_table', 'methods_section', 'principle_card'],
    output_dir='papers/pc001_validation/',
    dpi=300,
    style='publication'
)

print("\nGenerated outputs:")
for category in ['figures', 'tables', 'text', 'specs']:
    files = getattr(outputs, category, [])
    for f in files:
        print(f"  - {f}")

# Step 6: Verify TEG updated
teg = tsf.TEG.load()
assert teg.has_node('PC001')
assert teg.get_status('PC001') == 'validated'

print("\n✓ PC001 fully validated and published")
```

### Example 2: PC002 Compositional Workflow

```python
"""
Complete PC002 Workflow: Compositional Validation with PC001 Dependency
"""

import tsf

# ============================================================================
# PHASE 1: VALIDATE PC001 (Dependency)
# ============================================================================

baseline_data = tsf.observe(
    'data/C175_BASELINE.json',
    schema='pc001',
    validate=True
)

baseline_pattern = tsf.discover(
    data=baseline_data,
    method='pc001',
    parameters={'tolerance': 0.10}
)

assert baseline_pattern.features['validation_passed'], \
    "PC001 must validate before PC002"

print(f"✓ PC001 (dependency) validated")

# ============================================================================
# PHASE 2: VALIDATE PC002
# ============================================================================

# Load comparative data (transcendental vs PRNG)
comparative_data = tsf.observe(
    'data/PC002_TRANS_VS_PRNG_N50.json',
    schema='pc002',
    validate=True
)

# Discover PC002 patterns
pc002_patterns = tsf.discover(
    data=comparative_data,
    method='pc002',
    parameters={
        'baseline': baseline_pattern,  # PC001 dependency
        'significance_level': 0.05
    }
)

gates_passing = pc002_patterns.features['gates_passing']
print(f"PC002: {gates_passing}/4 gates passing")

if gates_passing == 4:
    print("✓ PC002 validated (all gates passed)")
else:
    print(f"⚠ PC002 partial validation ({gates_passing}/4 gates)")

# ============================================================================
# PHASE 3: QUANTIFY AND PUBLISH
# ============================================================================

metrics = tsf.quantify(
    pc002_patterns,
    criteria=['robustness', 'significance', 'effect_size']
)

outputs = tsf.publish(
    result=metrics,
    format='all',
    output_dir='papers/pc002_validation/',
    dpi=300
)

# ============================================================================
# PHASE 4: TEG VERIFICATION
# ============================================================================

teg = tsf.TEG.load()

# Verify dependency structure
assert 'PC001' in teg.get_dependencies('PC002')
assert 'PC002' in teg.get_dependents('PC001')

# Verify validation order
order = teg.get_validation_order(['PC002'])
assert order == ['PC001', 'PC002']

print("\n✓ PC002 validated with correct dependencies")
```

---

## Best Practices

### 1. Schema-First Design

**DO:** Design JSON schema before implementing PC
```python
# Step 1: Create schema
# Step 2: Generate sample data matching schema
# Step 3: Implement PC validate() using schema structure
# Step 4: Write tests using schema-validated data
```

**DON'T:** Implement PC first, then retrofit schema
```python
# ✗ Anti-pattern: PC assumes data structure that schema doesn't guarantee
```

### 2. Validation Criteria Hierarchy

**Tier 1 (Foundational):** PC self-test passes
```python
result = pc.validate(synthetic_data, tolerance)
assert result.passes
```

**Tier 2 (Extended Horizon):** Refutation at 10x
```python
refutation = tsf.refute(pattern, horizon='10x', tolerance=2*base_tolerance)
assert refutation.passed
```

**Tier 3 (Robustness):** Quantification across conditions
```python
metrics = tsf.quantify(patterns, criteria=['stability', 'robustness'])
assert all(score > 0.90 for score in metrics.scores.values())
```

### 3. Dependency Management

**Explicit Dependencies in Metadata:**
```python
super().__init__(
    pc_id="PC002",
    dependencies=["PC001"],  # Explicit
    enables=["PC005", "PC006"]
)
```

**Runtime Enforcement:**
```python
def validate(self, data, tolerance):
    # Check PC001 validated
    if 'baseline' not in data or data['baseline'].metadata.status != 'validated':
        raise DependencyError("PC002 requires validated PC001 instance")

    # Proceed with validation
    ...
```

**TEG Automatic Ordering:**
```python
# TEG ensures PC001 validates before PC002
order = teg.get_validation_order(['PC002'])  # ['PC001', 'PC002']
```

### 4. Error Handling

**Schema Validation Errors:**
```python
try:
    data = tsf.observe('data.json', schema='pc001', validate=True)
except tsf.SchemaValidationError as e:
    print(f"Schema validation failed: {e.missing_fields}")
    print(f"Expected schema: {e.schema_url}")
    # Fix data file and retry
```

**PC Validation Failures:**
```python
patterns = tsf.discover(data, method='pc001', parameters={...})

if not patterns.features['validation_passed']:
    print(f"PC validation failed:")
    print(f"  Error: {patterns.features['relative_error']*100:.2f}%")
    print(f"  Tolerance: {patterns.features['tolerance']*100:.2f}%")
    # Analyze failure mode
```

**Dependency Failures:**
```python
try:
    patterns = tsf.discover(data, method='pc002', parameters={...})
except tsf.DependencyError as e:
    print(f"Dependency validation failed: {e.required_pc}")
    # Validate dependencies first
```

### 5. Reproducibility

**Always Include:**
- Timestamp (ISO 8601)
- Random seed (if stochastic)
- TSF version
- PC version
- Schema version
- Parameter values
- SHA-256 hash of data

**Example Provenance:**
```python
{
    'timestamp': '2025-11-01T12:00:00Z',
    'tsf_version': '1.0.0',
    'pc_version': '1.0.0',
    'schema_version': '1.0.0',
    'random_seed': 42,
    'parameters': {...},
    'data_hash': 'abc123def456...'
}
```

---

## Troubleshooting

### Issue 1: Schema Validation Fails

**Symptom:**
```python
tsf.SchemaValidationError: Missing required field 'statistics.cv'
```

**Diagnosis:**
```python
# Check data structure
import json
with open('data.json') as f:
    data = json.load(f)

print(data.keys())  # ['metadata', 'timeseries']  ← Missing 'statistics'
```

**Solution:**
```python
# Add missing field
data['statistics'] = {
    'mean_population': np.mean(data['timeseries']['population']),
    'std_population': np.std(data['timeseries']['population']),
    'cv': np.std(data['timeseries']['population']) / np.mean(data['timeseries']['population'])
}

# Save corrected data
with open('data.json', 'w') as f:
    json.dump(data, f)
```

### Issue 2: PC Validation Fails

**Symptom:**
```python
patterns.features['validation_passed'] == False
patterns.features['relative_error'] == 0.15  # > 0.10 tolerance
```

**Diagnosis:**
```python
# Check parameter values
print(f"CV observed: {patterns.features['cv_observed']}")
print(f"CV predicted: {patterns.features['cv_predicted']}")
print(f"Parameters: K={K}, r={r}, sigma={sigma}")

# Verify prediction formula
cv_manual = sigma / np.sqrt(2 * r)
print(f"Manual CV prediction: {cv_manual}")
```

**Solution:**
```python
# Option 1: Adjust parameters (if misspecified)
patterns = tsf.discover(
    data,
    method='pc001',
    parameters={
        'carrying_capacity': 50.0,  # ← Verify this matches experiment
        'growth_rate': 0.1,
        'noise_intensity': 0.5,
        'tolerance': 0.10
    }
)

# Option 2: Relax tolerance (if noise is inherent)
patterns = tsf.discover(
    data,
    method='pc001',
    parameters={..., 'tolerance': 0.20}  # ← 20% tolerance
)

# Option 3: Investigate data quality
# - Check for outliers in timeseries
# - Verify statistics match timeseries
# - Ensure experiment reached steady state
```

### Issue 3: Dependency Not Found

**Symptom:**
```python
tsf.DependencyError: PC002 requires PC001, but PC001 not validated
```

**Diagnosis:**
```python
teg = tsf.TEG.load()
print(teg.get_status('PC001'))  # 'draft' ← Not validated
```

**Solution:**
```python
# Validate PC001 first
baseline_data = tsf.observe('data/C175_BASELINE.json', schema='pc001')
baseline_pattern = tsf.discover(data=baseline_data, method='pc001', parameters={...})

assert baseline_pattern.features['validation_passed'], "PC001 must pass before PC002"

# Now validate PC002
comparative_data = tsf.observe('data/PC002_COMPARATIVE.json', schema='pc002')
pc002_patterns = tsf.discover(
    data=comparative_data,
    method='pc002',
    parameters={'baseline': baseline_pattern}  # ← Pass validated PC001
)
```

### Issue 4: TEG Not Updating

**Symptom:**
```python
# PC001 validated successfully
patterns.features['validation_passed'] == True

# But TEG still shows 'draft'
teg.get_status('PC001')  # 'draft' ← Should be 'validated'
```

**Diagnosis:**
```python
# Check if TEG auto-update is enabled
import tsf
print(tsf.config.get('teg_auto_update'))  # False ← Disabled
```

**Solution:**
```python
# Option 1: Enable auto-update
tsf.config.set('teg_auto_update', True)

# Option 2: Manually update TEG
teg = tsf.TEG.load()
teg.update_status('PC001', 'validated')
teg.save()

# Option 3: Use tsf.publish() which always updates TEG
outputs = tsf.publish(patterns, format='principle_card')
# publish() updates TEG automatically
```

---

## References

### Key Documents

- **TSF Core API Specification:** `/Volumes/dual/DUALITY-ZERO-V2/docs/v6/TSF_CORE_API_SPECIFICATION.md`
- **Data Archiving Protocol (Schemas):** `/Volumes/dual/DUALITY-ZERO-V2/code/tsf/schemas/README.md`
- **Principle Cards README:** `principle_cards/README.md`
- **PC001 Specification:** `code/tsf/pc001_nrm_population_dynamics.py`
- **PC002 Specification:** `code/tsf/pc002_transcendental_substrate.py`

### External Resources

- **JSON Schema Documentation:** https://json-schema.org/understanding-json-schema/
- **TSF GitHub Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
- **NRM Framework Paper:** (In preparation)

---

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Author:** Claude Sonnet 4.5 (DUALITY-ZERO-V2)
**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**Phase:** 2 (Temporal Structure Framework)
**Gate:** 2.3 (PC Formalization)
**Status:** COMPLETE (integration guide formalized, Cycle 882)

---

**Quote:**
> *"Data schemas validate structure. Principle Cards validate science. TSF orchestrates both into publishable knowledge."*

— PC Integration Philosophy

**END PC INTEGRATION GUIDE**
