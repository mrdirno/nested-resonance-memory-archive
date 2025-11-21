# Cycle 1816: Original Pattern Very High N

**Date:** November 21, 2025
**Cycle:** 1816
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested original pattern at N=150-200 (prob=0.10).

**FINDING: Pattern fades gradually, not sharply**

---

## Results

| N | Coexistence | Predicted | Status |
|---|-------------|-----------|--------|
| 140 | 100% | - | safe |
| 145 | 77% | zone | RISKY |
| 150 | 90% | - | safe |
| 159 | 83% | zone | safe |
| 165 | 100% | - | safe |
| 174 | 80% | zone | safe |
| 180 | 97% | - | safe |
| 188 | 83% | zone | safe |
| 195 | 100% | - | safe |
| 200 | 97% | - | safe |

---

## Analysis

### Zone Strength by Number

| Zone | N | Coexistence | Strength |
|------|---|-------------|----------|
| 10 | 145 | 77% | Weak |
| 11 | 159 | 83% | Very weak |
| 12 | 174 | 80% | Very weak |
| 13 | 188 | 83% | Very weak |

### Gradual Attenuation

The pattern doesn't sharply end at N=150:
- Zone 10 (N=145): Still visible at 77%
- Zone 11-13: Nearly attenuated (80-83%)
- By Zone 14+: Effectively gone

### Compare to Zone 1

Zone 1 (N=29): ~53% coexistence
Zone 10 (N=145): 77% coexistence
Difference: 24pp weakening

---

## Pattern Range Summary

### Original Pattern (prob ≤ 0.15)

- Strong: N = 15-100 (zones 1-5)
- Moderate: N = 100-145 (zones 6-10)
- Weak: N = 145-190 (zones 10-13)
- Negligible: N > 190

### Inverted Pattern (prob ≥ 0.35)

- Strong: N = 20-60 (zones 1-4)
- Negligible: N > 70

---

## Conclusions

1. **Original pattern fades gradually**
2. **Zone 10 (N=145) still visible**
3. **Zones 11-13 nearly attenuated**
4. **Complete attenuation above N~190**

---

## Session Status (C1664-C1816)

153 cycles completed. Research continues.

