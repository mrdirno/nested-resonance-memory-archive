# DUALITY-ZERO Testing Infrastructure

Comprehensive test suite for reality-grounded Nested Resonance Memory framework implementation.

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>

**License:** GPL-3.0

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

## Test Categories

### 1. Reality Grounding Tests (`reality_grounding/`)

**Purpose:** Verify all modules maintain reality anchoring per Zero Tolerance Policy.

**Requirements:**
- NO external API calls (OpenAI, Anthropic, etc.)
- ALL operations use actual system state (psutil, SQLite, file I/O)
- NO mocks or simulations without reality validation
- Measurable, verifiable outcomes only

**Tests:**
- `test_fractal_reality_grounding.py` - Fractal agent reality anchoring
- `test_memory_reality_grounding.py` - Memory module reality compliance

**Expected:**
- All agents created with real system metrics
- Energy derived from actual CPU/memory availability
- Phase transformations via TranscendentalBridge
- Database persistence operational
- No external API calls detected

---

### 2. Integration Tests (`integration/`)

**Purpose:** Verify component interactions and system-level behavior.

**Tests:**
- `test_nrmv2_integration.py` - NRMv2 framework integration
- `test_autonomous_infrastructure.py` - Autonomous operation validation
- `test_agent_cap_effect.py` - Agent capacity limits
- `test_agent_cap_effect_v2.py` - Agent capacity validation v2
- `test_db_fix.py` - Database integrity checks

**Expected:**
- Components interact correctly
- System maintains coherence under load
- Database operations transactional
- Resource limits respected

---

### 3. Unit Tests (`unit/`)

**Purpose:** Verify individual module functionality in isolation.

**Tests:** (To be populated)

**Expected:**
- Module functions correctly in isolation
- Edge cases handled
- Error handling robust

---

## Running Tests

### Run All Tests
```bash
python3 tests/run_tests.py
```

### Run Specific Category
```bash
# Reality grounding only
python3 tests/reality_grounding/test_fractal_reality_grounding.py

# Integration only
python3 tests/integration/test_nrmv2_integration.py
```

### Expected Output
```
================================================================================
DUALITY-ZERO TEST SUITE
================================================================================

REALITY GROUNDING TESTS
--------------------------------------------------------------------------------
  Running test_fractal_reality_grounding.py... ✅ PASS
  Running test_memory_reality_grounding.py... ✅ PASS

INTEGRATION TESTS
--------------------------------------------------------------------------------
  Running test_nrmv2_integration.py... ✅ PASS
  Running test_autonomous_infrastructure.py... ✅ PASS
  Running test_agent_cap_effect.py... ✅ PASS
  Running test_agent_cap_effect_v2.py... ✅ PASS
  Running test_db_fix.py... ✅ PASS

UNIT TESTS
--------------------------------------------------------------------------------
  No tests found in unit/

================================================================================
TEST SUMMARY
================================================================================
Reality Grounding: 2/2 passed
Integration:       5/5 passed
Unit:              0/0 passed
Total:             7/7 passed

✅ ALL TESTS PASSED
================================================================================
```

---

## Test Development Guidelines

### 1. Reality Anchoring Required
All tests MUST verify reality grounding:
```python
# ✅ GOOD: Reality-anchored test
from core.reality_interface import RealityInterface

def test_agent_creation():
    reality = RealityInterface()
    metrics = reality.get_system_metrics()  # Real psutil metrics
    agent = FractalAgent(initial_reality=metrics)
    assert agent.energy > 0  # Derived from real metrics
    assert agent.phase_state is not None  # Real phase transformation
```

```python
# ❌ BAD: Mock-based test (FORBIDDEN)
from unittest.mock import Mock

def test_agent_creation():
    mock_reality = Mock()  # VIOLATION: No mocks in production tests
    mock_reality.get_system_metrics.return_value = {...}  # VIOLATION: Fabricated data
    agent = FractalAgent(initial_reality=mock_reality)
```

### 2. Test Structure
```python
#!/usr/bin/env python3
"""
Test Description: What this test verifies

Reality Compliance:
- Actual psutil metrics
- Real SQLite operations
- File I/O verification

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))

# Test implementation
def test_functionality():
    # 1. Initialize with reality
    # 2. Perform operations
    # 3. Verify outcomes
    # 4. Validate reality compliance
    pass

if __name__ == '__main__':
    test_functionality()
```

### 3. Timeout Policy
- Each test file: **5 minute maximum**
- If test exceeds timeout → FAIL (indicates blocking operation or infinite loop)

### 4. Output Requirements
- Print clear success/failure indicators
- Show reality compliance verification
- Provide diagnostic info on failure

---

## Continuous Integration

### Pre-Commit Hook (Recommended)
```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 tests/run_tests.py
if [ $? -ne 0 ]; then
    echo "Tests failed - commit blocked"
    exit 1
fi
```

### CI/CD Pipeline (GitHub Actions)
```yaml
name: Reality-Grounded Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python3 tests/run_tests.py
```

---

## Test Coverage Goals

### Current Status (2025-10-29)
- Reality Grounding: **2 tests** (fractal, memory)
- Integration: **5 tests** (nrmv2, infrastructure, agent caps, db)
- Unit: **0 tests** (to be developed)
- **Total: 7 tests**

### Target Coverage
- Reality Grounding: **10+ tests** (all modules)
- Integration: **20+ tests** (all component interactions)
- Unit: **50+ tests** (core functionality)
- **Target: 80+ tests** by end of Phase 2

---

## Known Issues

### Import Path Dependencies
Tests assume they're run from repository root with proper sys.path setup. If imports fail:
```bash
# Ensure code/ modules are importable
export PYTHONPATH=/path/to/nested-resonance-memory-archive/code:$PYTHONPATH
python3 tests/run_tests.py
```

### Database Persistence
Some tests create database files in current directory. Clean up may be required:
```bash
rm -f *.db bridge.db fractal.db duality_v2.db
```

---

## Adding New Tests

1. **Create test file** in appropriate category directory
2. **Implement test** following reality grounding guidelines
3. **Run locally** to verify it passes
4. **Update this README** if adding new test category
5. **Commit with descriptive message** explaining what's tested

---

## Performance Benchmarks

**Test Suite Runtime (as of 2025-10-29):**
- Reality Grounding: ~10 seconds
- Integration: ~30 seconds
- Unit: N/A (no tests yet)
- **Total: ~40 seconds**

**Target:** Keep full suite under 2 minutes for developer productivity.

---

**Last Updated:** 2025-10-29 (Cycle 564)

**Test Infrastructure Status:** ✅ Operational (7/7 tests passing)
