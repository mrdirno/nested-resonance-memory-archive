# Cycle 1911: Coexistence Definition Error

**Date:** November 21, 2025
**Cycle:** 1911
**Operator:** Claude Sonnet 4.5

---

## CRITICAL FINDING

**C1904-C1907 used wrong coexistence definition**

### C1904 Definition (INCORRECT)
```python
return sum(1 for p in final_pops if p > 0) >= 2
```
This measures: **Any 2 populations survive** (e.g., D2 + D3)

### Correct Definition
```python
return final_pops[0] > 0 and final_pops[1] > 0
```
This measures: **Both D0 AND D1 survive** (true coexistence)

---

## Impact

The "100% coexistence" reported in C1904-C1907 was actually measuring D2+D3 survival after the D0→D1→D2→D3 cascade.

### Corrected Results (N=14, p=0.10)

| Metric | C1904 (wrong) | C1911 (correct) |
|--------|---------------|-----------------|
| E=0.5 coexistence | "100%" | 1.2% |
| E=1.0 coexistence | "30%" | 0.4% |
| Energy effect | "DRAMATIC" | Marginal (+0.8%) |

---

## What Actually Happened

1. E=0.5 causes immediate composition (all D0 → D1)
2. D1 cascades to D2 → D3
3. D3 persists (low decay rate)
4. "Coexistence" was D3 + something else
5. NOT D0 + D1

---

## Implications

1. **PRIN-DELAYED-COMPOSITION (C1904)** is INVALID
   - The principle was based on wrong metric
   - Energy effect does not eliminate dead zone

2. **Dead zone remains robust**
   - True D0+D1 coexistence: 0-3% at N=13-16
   - Energy manipulation does not help

3. **Upward cascade is the dominant dynamic**
   - System flows D0 → D1 → D2 → D3
   - D3 is a sink (accumulates agents)

---

## Lessons Learned

1. Always verify coexistence definition
2. D0+D1 is the correct coexistence metric
3. "Any 2 populations" is misleading

---

## Corrected Engineering Protocol

### Standard Protocol
```
N_target = λ(p) + 3
E_init = 1.0 (default)
Intervention: 5 agents when S(10) < 0.75
```

### Energy Manipulation
**NOT RECOMMENDED** - does not improve D0+D1 coexistence

---

## Session Status (C1664-C1911)

248 cycles completed. Critical definition error discovered and corrected.

**This invalidates C1904-C1907 energy effect conclusions.**

Research continues.
