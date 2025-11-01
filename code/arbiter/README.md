<!--
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
-->

# ARBITER: Artifact-Based Reproducibility and Integrity Testing

**Version:** 1.0.0
**Gate:** Phase 1 Gate 1.3 (ARBITER CI Integration)
**Status:** ✅ VALIDATED

---

## Overview

ARBITER ensures experimental determinism through cryptographic hash validation of research artifacts. By computing and validating SHA-256 hashes of output files, ARBITER guarantees that experiments produce identical results across runs, platforms, and time.

**Core Principle:** If the same experimental code with the same random seed produces different output hashes, either:
1. The experiment is non-deterministic (BUG - must fix)
2. The code was modified (INTENDED - update manifest)
3. The environment changed (REGRESSION - investigate)

ARBITER makes non-determinism immediately visible in CI, enforcing the highest reproducibility standards.

---

## Why ARBITER?

### Problem: Hidden Non-Determinism

Research code often has subtle sources of non-determinism:
- Uncontrolled randomness (missing seeds)
- Floating-point precision issues
- Platform-dependent behavior
- Time-based logic
- Concurrency bugs

These bugs may go unnoticed for months, invalidating results.

### Solution: Hash-Based Validation

ARBITER detects any output change, no matter how small:
- **Deterministic code:** Hash matches → validation passes
- **Non-deterministic code:** Hash differs → validation fails → investigate immediately

This provides a **reality check** on experimental reproducibility claims.

---

## Key Features

1. **Cryptographic Hashing:** SHA-256 ensures collision-resistant validation
2. **Manifest-Based:** Reference hashes stored in version control
3. **CI Integration:** Automated validation on every commit
4. **Detailed Reports:** Shows exactly which artifacts changed and how
5. **Update Workflow:** Easy process to update hashes when code intentionally changes

---

## Installation

ARBITER is a standalone Python script with no external dependencies beyond Python 3.9+ standard library.

```bash
# No installation required - use directly
python code/arbiter/arbiter.py --help
```

---

## Usage

### Create New Manifest

Generate hash manifest for artifacts matching glob patterns:

```bash
python code/arbiter/arbiter.py create \
  --patterns "code/regime/*.py" "code/regime/*.json" \
  --description "Gate 1.2: Regime Detection Library artifacts"
```

**Output:** `code/arbiter/arbiter_manifest.json`

### Validate Against Manifest

Check if current artifacts match reference hashes:

```bash
python code/arbiter/arbiter.py validate
```

**Exit codes:**
- `0`: All hashes match (validation passed)
- `1`: Hash mismatch or missing file (validation failed)

**Example output:**
```
================================================================================
ARBITER VALIDATION
================================================================================

Manifest: code/arbiter/arbiter_manifest.json
Description: Gate 1.2: Regime Detection Library artifacts (Cycle 815)
Created: 2025-10-31T23:19:14.162691
Artifacts: 5

✓ [1/5] code/regime/cross_validation_test.py
✓ [2/5] code/regime/debug_classification.py
✓ [3/5] code/regime/regime_detector.py
✓ [4/5] code/regime/validation_dataset.json
✓ [5/5] code/regime/validation_dataset_builder.py

================================================================================
VALIDATION SUMMARY
================================================================================

Total artifacts: 5
Errors: 0
Warnings: 0

✓ VALIDATION PASSED

================================================================================
```

### Update Manifest

Update manifest with new/changed artifacts (after intentional code changes):

```bash
python code/arbiter/arbiter.py update \
  --patterns "code/regime/*.py" "code/regime/*.json"
```

**Dry run** (show changes without saving):
```bash
python code/arbiter/arbiter.py update \
  --patterns "code/regime/*.py" \
  --dry-run
```

---

## Manifest Format

**File:** `code/arbiter/arbiter_manifest.json`

```json
{
  "version": "1.0.0",
  "created": "2025-10-31T23:19:14.162691",
  "description": "Gate 1.2: Regime Detection Library artifacts (Cycle 815)",
  "artifacts": [
    {
      "path": "code/regime/regime_detector.py",
      "sha256": "a1b2c3d4e5f6...",
      "size_bytes": 15234,
      "modified": "2025-10-31T22:45:12.345678"
    },
    ...
  ]
}
```

**Fields:**
- `version`: ARBITER version
- `created`: Manifest creation timestamp (ISO 8601)
- `description`: Human-readable purpose
- `artifacts`: List of hashed files
  - `path`: Relative path from repository root
  - `sha256`: SHA-256 hash (64 hex characters)
  - `size_bytes`: File size in bytes
  - `modified`: Last modification timestamp (ISO 8601)

---

## CI Integration

ARBITER runs automatically in GitHub Actions on every commit.

**Workflow:** `.github/workflows/ci.yml`

```yaml
arbiter:
  name: ARBITER Hash Validation
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python 3.9
      uses: actions/setup-python@v5
      with:
        python-version: '3.9'
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run ARBITER validation
      run: |
        python code/arbiter/arbiter.py validate --strict

    - name: Print ARBITER summary
      run: |
        echo "✓ ARBITER hash validation passed"
        echo "✓ Experimental artifacts verified deterministic"
        echo "✓ Phase 1 Gate 1.3 validation complete"
```

**Behavior:**
- ✅ **Validation passes:** CI continues, merge allowed
- ❌ **Validation fails:** CI fails, merge blocked until:
  1. Fix non-determinism bug, OR
  2. Update manifest (if change was intentional)

---

## Workflow: Updating Code

When you modify code that changes output artifacts:

1. **Make changes:**
   ```bash
   # Edit code
   vim code/regime/regime_detector.py

   # Test changes
   python code/regime/cross_validation_test.py
   ```

2. **Update manifest:**
   ```bash
   # Preview changes
   python code/arbiter/arbiter.py update \
     --patterns "code/regime/*.py" "code/regime/*.json" \
     --dry-run

   # Apply changes
   python code/arbiter/arbiter.py update \
     --patterns "code/regime/*.py" "code/regime/*.json"
   ```

3. **Commit both code and manifest:**
   ```bash
   git add code/regime/ code/arbiter/arbiter_manifest.json
   git commit -m "Update regime detector thresholds

   - Refined BISTABILITY mean_population constraint
   - Updated ARBITER manifest with new hashes

   Author: Aldrin Payopay <aldrin.gdf@gmail.com>"
   ```

4. **Push and verify CI:**
   ```bash
   git push origin main
   # Check GitHub Actions - ARBITER should pass
   ```

---

## What ARBITER Validates

**Current artifacts (Cycle 815):**
- `code/regime/regime_detector.py` - Regime classification engine
- `code/regime/validation_dataset_builder.py` - Ground-truth dataset builder
- `code/regime/validation_dataset.json` - 8 labeled samples
- `code/regime/cross_validation_test.py` - LOOCV testing framework
- `code/regime/debug_classification.py` - Debug analysis tool

**Future expansion:**
Add patterns to manifest as more artifacts are created:
```bash
python code/arbiter/arbiter.py update \
  --patterns \
    "code/regime/*.py" \
    "code/regime/*.json" \
    "data/results/C*.json" \
    "data/figures/regime_detection/*.png"
```

---

## Troubleshooting

### Hash Mismatch Detected

**Symptom:** ARBITER validation fails with hash mismatch

**Diagnosis:**
1. **Intentional change?** → Update manifest (see workflow above)
2. **Unintentional change?** → Investigate:
   ```bash
   # Re-run validation to see details
   python code/arbiter/arbiter.py validate

   # Check what changed
   git diff code/regime/

   # Revert if accidental
   git checkout code/regime/file_that_changed.py
   ```

### File Not Found

**Symptom:** ARBITER validation fails with "FILE NOT FOUND"

**Cause:** Artifact was deleted or moved

**Solution:**
```bash
# If intentional deletion:
python code/arbiter/arbiter.py update \
  --patterns "code/regime/*.py" "code/regime/*.json"

# If accidental deletion:
git checkout code/regime/missing_file.py
```

### Size Warning

**Symptom:** File size changed but hash matches (rare)

**Explanation:** File modification timestamp or metadata changed, but content is identical (hash matches). Usually benign.

---

## Design Principles

### 1. Cryptographic Strength

SHA-256 provides:
- **Collision resistance:** Probability of accidental collision is negligible (~2^-256)
- **Avalanche effect:** Single bit change → completely different hash
- **Standardized:** NIST FIPS 180-4 approved algorithm

### 2. Deterministic Ordering

Artifacts sorted alphabetically for consistent manifest structure, enabling clean diffs.

### 3. Human-Readable Metadata

Timestamps and file sizes aid debugging without obscuring core validation logic.

### 4. Fail-Fast Philosophy

Any hash mismatch fails validation immediately - no tolerance for "close enough."

### 5. Version Control Integration

Manifest committed with code - hash changes are visible in git diff.

---

## Comparison to Alternatives

| Approach | Pros | Cons |
|----------|------|------|
| **Manual Testing** | Simple | Error-prone, not scalable |
| **Unit Tests** | Catches logic bugs | Doesn't validate outputs |
| **Golden Files** | Validates outputs | Brittle to formatting changes |
| **ARBITER** | Cryptographic validation, CI-integrated | Requires manifest updates |

ARBITER complements unit tests by validating end-to-end determinism.

---

## Phase 1 Gate 1.3 Validation

**Target:** Hash-based reproducibility validation in CI pipeline

**Implementation:**
- ✅ ARBITER engine (`arbiter.py`, 421 lines)
- ✅ Initial manifest (5 artifacts from Gate 1.2)
- ✅ CI integration (GitHub Actions job)
- ✅ Documentation (this README)

**Status:** ✅ GATE 1.3 COMPLETE

**Validation:**
```bash
# Test ARBITER locally
python code/arbiter/arbiter.py validate

# Verify CI integration
git push origin main
# Check GitHub Actions → "ARBITER Hash Validation" job should pass
```

---

## Future Enhancements

### Planned Features

1. **Selective Validation:**
   ```bash
   arbiter.py validate --pattern "code/regime/*.py"
   ```

2. **Diff Reporting:**
   ```bash
   arbiter.py diff --old manifest_v1.json --new manifest_v2.json
   ```

3. **Multi-Manifest Support:**
   ```bash
   arbiter.py validate --manifest experiments/C256_manifest.json
   ```

4. **Performance Optimization:**
   - Parallel hash computation for large artifact sets
   - Incremental validation (skip unchanged files)

5. **Artifact Provenance:**
   - Track which code version produced each artifact
   - Link artifacts to experiments via metadata

---

## References

### Cryptography

- **NIST FIPS 180-4:** SHA-256 specification
- **RFC 6234:** SHA-256 implementation guidance

### Reproducibility

- **Stodden et al. (2016):** "Enhancing reproducibility for computational methods"
- **Claerbout & Karrenbach (1992):** "Electronic documents give reproducible research a new meaning"

### Related Tools

- **DVC (Data Version Control):** ML artifact versioning
- **git-lfs:** Large file storage with hashing
- **checksums:** Traditional MD5/SHA1 validation

**ARBITER Advantage:** Purpose-built for experimental determinism validation in scientific research.

---

## License

GPL-3.0

---

## Author

**Aldrin Payopay**
- Email: aldrin.gdf@gmail.com
- Repository: https://github.com/mrdirno/nested-resonance-memory-archive

---

## Citation

```bibtex
@software{arbiter2025,
  author = {Payopay, Aldrin},
  title = {ARBITER: Artifact-Based Reproducibility and Integrity Testing for Experimental Research},
  year = {2025},
  url = {https://github.com/mrdirno/nested-resonance-memory-archive},
  version = {1.0.0},
  license = {GPL-3.0}
}
```

---

**Version:** 1.0.0
**Date:** 2025-10-31 (Cycle 816)
**Gate:** Phase 1 Gate 1.3
**Status:** ✅ VALIDATED
