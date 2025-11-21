# Cycle 1725: N=40 Failure Analysis

**Date:** November 21, 2025
**Cycle:** 1725
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Investigated why N=40 showed unexpected failures in C1724.

**FINDING: N=40 mostly succeeds (98%), but secondary dead zone at N=42**

---

## Results by Repro

### Repro = 0.05

| N | D1 | Dec | D1D2 | Coex |
|---|---|-----|------|------|
| 35 | 39 | 20 | 4.03 | 100% ✓ |
| 40 | 111 | 90 | 0.77 | 98% ✓ |
| 45 | 54 | 30 | 1.76 | 62% ✗ |

### Repro = 0.10

| N | D1 | Dec | D1D2 | Coex |
|---|---|-----|------|------|
| 35 | 44 | 25 | 2.52 | 100% ✓ |
| 40 | 67 | 45 | 2.89 | 98% ✓ |
| 45 | 111 | 86 | 1.36 | 90% ✓ |

### Repro = 0.15

| N | D1 | Dec | D1D2 | Coex |
|---|---|-----|------|------|
| 35 | 85 | 64 | 1.46 | 100% ✓ |
| 40 | 60 | 37 | 2.22 | **70% ✗** |
| 45 | 65 | 40 | 2.63 | 88% ✗ |

---

## Extended Range (repro=0.10)

| N | Coexist |
|---|---------|
| 35 | 100% ✓ |
| 38 | 100% ✓ |
| 40 | 98% ✓ |
| **42** | **68% ✗** |
| 45 | 90% ✓ |
| 50 | 98% ✓ |

---

## Key Findings

### 1. N=40 Mostly Robust

- 98% at low/standard repro
- Fails only at high repro (70%)

### 2. Secondary Dead Zone at N=42

- Only 68% coexistence
- Isolated failure point

### 3. N=45 Has Mixed Results

- 62% at low repro
- 90% at standard repro
- 88% at high repro

---

## Failure Zone Map (Updated)

| N Range | Status | Notes |
|---------|--------|-------|
| 20-26 | Safe | Some edge cases |
| 27-31 | **Dead Zone 1** | Primary failure |
| 32 | Mixed | Fails at low repro |
| 33-40 | Safe | Generally robust |
| 41-44 | **Dead Zone 2?** | Needs verification |
| 45+ | Mixed | Variable results |

---

## Mechanism Hypothesis

### Dead Zone 1 (N=27-31)

- Too many for offspring-dominated regime
- Too few for population-dominated regime

### Dead Zone 2 (N=42?)

- Possible resonance interference
- Population size creates destructive phase alignment?

---

## Session Status (C1664-C1725)

62 cycles investigating NRM dynamics.

---

## Conclusions

1. **N=40 mostly succeeds (98%)**
2. **Secondary dead zone around N=42**
3. **N=45 has mixed results (62-90%)**
4. **Multiple failure zones in system**
5. **Need to verify N=41-44 regime**

