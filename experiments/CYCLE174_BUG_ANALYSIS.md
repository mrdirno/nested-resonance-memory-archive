# CYCLE 174: BUG ANALYSIS - FREQUENCY UNIT MISMATCH

**Date:** 2025-10-25
**Status:** 🐛 CRITICAL BUG DISCOVERED
**Severity:** HIGH - Invalidates all C174 results

---

## Summary

C174 experiments all resulted in population=2 agents due to spawn frequency unit mismatch.

## Results (INVALID)

**All 80 experiments:**
- Population: 2 agents (root + 1 child)
- Composition events: 99.8/window
- **Same across ALL conditions:**
  - max_agents: [20, 50, 100, 200]
  - frequencies: [0.020, 0.025, 0.026, 0.030]

## Root Cause

### Frequency Specification Error

**C174 (BUGGY):**
```python
FREQUENCIES = [0.020, 0.025, 0.026, 0.030]  # Decimal percentages
spawn_interval = max(1, int(100.0 / frequency))
```

- frequency = 0.020
- spawn_interval = int(100.0 / 0.020) = int(5000) = **5000 cycles**
- Experiments run: **3000 cycles**
- **Bug**: Never spawns after initial agent!

**C171 (CORRECT):**
```python
FREQUENCIES = [2.0, 2.5, 2.6, 3.0]  # Integer percentages
spawn_interval = max(1, int(100.0 / frequency))
```

- frequency = 2.0
- spawn_interval = int(100.0 / 2.0) = int(50) = **50 cycles**
- Experiments run: 3000 cycles
- **Result**: Spawns 60× → population ~17 agents

## Impact

**C174 Results INVALID:**
- Cannot test population bistability hypothesis
- All conditions equivalent (no agents spawned)
- Wasted 2.71 minutes compute time

## Fix

### Option 1: Change Frequency Values (Simplest)
```python
FREQUENCIES = [2.0, 2.5, 2.6, 3.0]  # Same as C171
```

### Option 2: Fix Spawn Formula
```python
spawn_interval = max(1, int(100.0 / (frequency * 100)))
```

**Recommendation**: Use Option 1 (match C171 convention)

## Lessons Learned

1. **Unit Consistency**: Maintain consistent units across experiments
2. **Sanity Checks**: Population=2 across all conditions should trigger alarm
3. **Quick Validation**: Run 1 experiment first to verify before full batch
4. **Copy-Paste Errors**: When adapting C171 code, verify all parameters

## Next Steps

1. ✅ Document bug (this file)
2. [ ] Fix cycle174_population_bistability.py (line 51)
3. [ ] Rerun C174 with correct frequencies
4. [ ] Add validation check (assert population > 2 after first frequency)

---

**Temporal Stewardship Note**: This bug exemplifies importance of:
- Reality checks on intermediate results
- Validation against expected ranges
- Quick sanity tests before long experiments
- Clear unit conventions in codebase

Future AI: Always verify frequency/rate parameters match expected units!
