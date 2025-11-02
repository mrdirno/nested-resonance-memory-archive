# TSF Data Archiving Protocol - JSON Schemas

**Part of Phase 2, Gate 2.2 (Data Archiving Protocol)**

This directory contains JSON Schema specifications for data formats used in the Temporal Structure Framework (TSF).

## Available Schemas

### 1. `generic_observational_data.json`
**Purpose:** Baseline schema for all observational data

**Use when:** Creating custom data formats not covered by specific schemas

**Required fields:**
- `metadata.experiment_id` - Unique identifier
- `timeseries` - At least one numeric array
- `statistics` - At least one summary statistic

**Example usage:**
```python
import tsf

data = tsf.observe(
    source="my_experiment.json",
    domain="custom_domain",
    schema="generic",
    validate=True  # Validates against generic schema
)
```

### 2. `pc001_population_dynamics.json`
**Purpose:** Data format for PC001 (NRM Population Dynamics Validation Framework)

**Use when:** Validating population dynamics experiments with PC001

**Required fields:**
- `metadata.experiment_id`, `metadata.pc_id`
- `timeseries.population`
- `statistics.mean_population`, `statistics.std_population`, `statistics.cv`

**Validation gates supported:**
- Gate 1.1: CV prediction (requires `validation.cv_predicted`)
- Gate 1.2: Regime detection (requires `validation.regime`)
- Gate 1.3: Hash validation (requires `metadata.artifact_hash`)
- Gate 1.4: Overhead authentication (requires `validation.overhead_observed`, `validation.overhead_predicted`)

**Example usage:**
```python
import tsf

# Load data
data = tsf.observe(
    source="c175_baseline.json",
    domain="population_dynamics",
    schema="pc001",
    validate=True  # Validates against PC001 schema
)

# Validate using PC001
pattern = tsf.discover(
    data=data,
    method="pc001",
    parameters={"tolerance": 0.10}
)

print(f"Validation: {'PASS' if pattern.features['validation_passed'] else 'FAIL'}")
```

### 3. `pc002_comparative_results.json`
**Purpose:** Comparative experiment data for PC002 (Transcendental Substrate Hypothesis)

**Use when:** Comparing transcendental (π,e,φ) vs PRNG substrates

**Required fields:**
- `metadata.experiment_id`, `metadata.pc_id`
- `transcendental_results.pattern_lifetime`, `transcendental_results.memory_retention`, etc.
- `prng_results.pattern_lifetime`, `prng_results.memory_retention`, etc.

**Validation gates supported:**
- Gate 2.1: Transcendental vs PRNG comparison
- Gate 2.2: Pattern persistence metrics
- Gate 2.3: Memory retention analysis
- Gate 2.4: Emergence quality assessment

**Example usage:**
```python
import tsf

# Load comparative data
data = tsf.observe(
    source="transcendental_vs_prng.json",
    domain="nested_resonance_memory",
    schema="pc002",
    validate=True
)

# Validate using PC002
pattern = tsf.discover(
    data=data,
    method="pc002",
    parameters={}
)

print(f"Gates passing: {pattern.features['gates_passing']}/4")
```

## Schema Validation

TSF automatically validates data against schemas when `validate=True` is passed to `observe()`:

```python
# Automatic validation
data = tsf.observe(source="data.json", domain="...", schema="pc001", validate=True)
```

If validation fails, a `SchemaValidationError` is raised with details about what's missing or incorrect.

## Creating Custom Schemas

To create a custom schema:

1. **Start with generic schema** - Copy `generic_observational_data.json` as a template

2. **Define required fields** - Add domain-specific requirements:
```json
{
  "required": ["metadata", "timeseries", "statistics"],
  "properties": {
    "metadata": {
      "required": ["experiment_id", "custom_field"],
      ...
    }
  }
}
```

3. **Add validation rules** - Specify constraints:
```json
{
  "properties": {
    "statistics": {
      "properties": {
        "metric": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        }
      }
    }
  }
}
```

4. **Register schema** - Add to TSF schema registry (future implementation)

## Schema Format

All schemas follow [JSON Schema Draft 07](https://json-schema.org/draft-07/schema).

### Key elements:
- **`$schema`**: JSON Schema version
- **`$id`**: Unique schema identifier (URL)
- **`title`**: Human-readable schema name
- **`description`**: Schema purpose and usage
- **`type`**: Root type (always "object" for TSF)
- **`required`**: Required top-level properties
- **`properties`**: Field definitions with types and constraints
- **`examples`**: Sample valid data

### Validation tools:
- **Python:** `jsonschema` library
- **Online:** https://www.jsonschemavalidator.net/
- **CLI:** `ajv` (Node.js package)

## Data Archiving Protocol

### File naming convention:
```
{experiment_id}_{schema}_{optional_suffix}.json
```

Examples:
- `C175_BASELINE_pc001.json`
- `TRANS_VS_PRNG_pc002.json`
- `CUSTOM_EXP_generic.json`

### Storage locations:
**Development workspace:**
```
/Volumes/dual/DUALITY-ZERO-V2/experiments/results/
```

**Git repository:**
```
/Users/.../nested-resonance-memory-archive/data/results/
```

### Archiving checklist:
- ☐ Data follows schema (validate with `jsonschema`)
- ☐ Experiment ID is unique
- ☐ Timestamp is ISO 8601 format
- ☐ All required fields present
- ☐ Statistics match timeseries (TSF verifies automatically)
- ☐ File committed to git repository
- ☐ Provenance documented (parameters, random seeds, etc.)

## Integration with TSF Workflow

```python
# Complete workflow with schema validation
import tsf

# 1. observe() - Load data with schema validation
data = tsf.observe("experiment.json", "population_dynamics", "pc001", validate=True)

# 2. discover() - Find patterns (uses PC if schema is PC-specific)
pattern = tsf.discover(data, method="pc001", parameters={"tolerance": 0.10})

# 3. refute() - Test at extended horizons
refutation = tsf.refute(pattern, "10x", 0.20, validation_data=val_data)

# 4. quantify() - Measure pattern strength
metrics = tsf.quantify(pattern, val_data, criteria=["stability"])

# 5. publish() - Create validated Principle Card
pc_path = tsf.publish(pattern, metrics, refutation, "PC003", "Title", "Author")
```

## Versioning

**Current version:** 1.0.0 (Gate 2.2, Cycle 882)

**Schema stability:**
- **Breaking changes:** Increment major version (1.x.x → 2.0.0)
- **New optional fields:** Increment minor version (1.0.x → 1.1.0)
- **Documentation fixes:** Increment patch version (1.0.0 → 1.0.1)

**Backward compatibility:**
- Schemas are immutable once published
- New versions created for incompatible changes
- Old versions remain supported

## References

- **TSF Core API Specification:** `/Volumes/dual/DUALITY-ZERO-V2/docs/v6/TSF_CORE_API_SPECIFICATION.md`
- **PC001 Implementation:** `code/tsf/pc001_nrm_population_dynamics.py`
- **PC002 Implementation:** `code/tsf/pc002_transcendental_substrate.py`
- **JSON Schema Docs:** https://json-schema.org/understanding-json-schema/

---

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Author:** Claude Sonnet 4.5 (DUALITY-ZERO-V2)
**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**Phase:** 2 (Temporal Structure Framework)
**Gate:** 2.2 (Data Archiving Protocol)
**Status:** COMPLETE (schemas formalized, Cycle 882)
