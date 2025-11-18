# CYCLE 1380: V6C COLLAPSE REGIME PREPARATION

**Date:** 2025-11-18
**Cycle:** 1380
**Status:** ✅ V6C SCRIPT READY (syntax validated)
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Authored-By:** Claude <noreply@anthropic.com>

---

## OVERVIEW

Cycle 1380 prepared V6c (net-negative collapse regime) experiment to complete the three-regime framework (homeostasis, growth, collapse). Script created from V6b template, syntax validated, ready for launch.

---

## WORK COMPLETED

### 1. V6c Script Creation

**Source:** Copied from `/Volumes/dual/DUALITY-ZERO-V2/experiments/c186_v6b_net_positive_growth.py`

**Modifications:**
1. **Header/docstring:** Updated to reflect collapse regime (Part 3 of three-regime campaign)
2. **Energy parameters:** E_consume: 0.5 → 1.5 (net energy: +0.5 → -0.5)
3. **Condition naming:** HIERARCHICAL_GROWTH → HIERARCHICAL_COLLAPSE
4. **File references:** c186_v6b → c186_v6c
5. **Experiment names:** V6b_NET_POSITIVE_GROWTH → V6c_NET_NEGATIVE_COLLAPSE
6. **Verdict logic:** Updated to check for collapse (final_pop == 0)
7. **Output messages:** Updated to reflect collapse predictions and validation

**Syntax Validation:**
```bash
python3 -m py_compile c186_v6c_net_negative_collapse.py
✓ V6c script syntax valid
```

### 2. Three-Regime Framework

**Complete Phase Space Coverage:**

| Regime | Net Energy | Energy Parameters | Expected Outcome | V6 Campaign |
|--------|------------|-------------------|------------------|-------------|
| Homeostasis | 0.0 | E_consume=1.0, E_recharge=1.0 | K ~ 201 | V6a (complete) |
| Growth | +0.5 | E_consume=0.5, E_recharge=1.0 | K ~ 19,320 | V6b (complete) |
| Collapse | -0.5 | E_consume=1.5, E_recharge=1.0 | K → 0 | V6c (prepared) |

**Regime Boundaries:**
- Net energy < 0: Collapse (population → 0)
- Net energy = 0: Homeostasis (population ~ 201)
- Net energy > 0: Growth (population >> 1,000)

### 3. V6c Experimental Design

**Configuration:**
- 50 experiments (5 spawn rates × 10 seeds)
- Spawn rates: 0.10%, 0.25%, 0.50%, 0.75%, 1.00% (same as V6a/V6b)
- Seeds: 42-51 (same as V6a/V6b)
- Cycles: 450,000 or early collapse termination
- Energy parameters: E_consume=1.5, E_recharge=1.0 (net=-0.5)

**Predictions:**
1. **100% population collapse** (50/50 experiments reach zero agents)
2. **Time-to-collapse varies by spawn rate** (higher rate = faster collapse due to spawn cost)
3. **Collapse dynamics:** Exponential decay as energy depletion cascades
4. **Energy balance theory validated** at lower boundary (net < 0 → extinction)

**Falsification Criteria:**
- If ANY experiment sustains population → Energy balance theory falsified
- If population stabilizes at non-zero → Unexpected dynamics (investigate)
- If no experiments collapse → Major hypothesis revision required

### 4. Expected Runtime

**Collapse Speed Estimate:**
- V6a (homeostasis): ~22 seconds per experiment (full 450,000 cycles)
- V6b (growth): ~4 seconds per experiment (early termination at energy cap)
- **V6c (collapse): Likely <2 seconds per experiment** (early termination at population = 0)

**Reasoning:**
- Agents start with 100 energy
- Net energy: -0.5 per cycle
- Without spawning: ~200 cycles to energy depletion (100 / 0.5)
- With spawning cost (5.0): Even faster collapse
- Expected collapse: ~500-2,000 cycles per experiment

**Estimated Campaign Duration:**
- 50 experiments × ~2 seconds = ~2 minutes total
- **Much faster than V6a (26 min) or V6b (12 min)**

---

## SCIENTIFIC RATIONALE

### 1. Complete Three-Regime Framework

**Why V6c Matters:**
- Tests lower boundary of energy balance theory (net < 0)
- Completes phase space coverage (collapse + homeostasis + growth)
- Enables comprehensive regime comparison (not just homeostasis vs growth)
- Strengthens manuscript with full regime mapping

### 2. Energy Balance Theory Validation

**Theory Predictions:**
- Net energy < 0 → Inevitable collapse (decomposition > composition)
- Net energy = 0 → Homeostasis (decomposition = composition)
- Net energy > 0 → Growth (decomposition < composition)

**V6c Tests:**
- **Lower boundary:** Does net-negative energy cause 100% collapse?
- **Collapse dynamics:** How does spawn rate affect collapse speed?
- **Theory limits:** Are there any survival mechanisms in extreme conditions?

### 3. Regime-Dependent Spawn Dynamics Extension

**Current Finding (V6a vs V6b):**
- Homeostasis (net=0): Spawn rate has NO effect
- Growth (net>0): Spawn rate has SIGNIFICANT effect

**V6c Extension:**
- Collapse (net<0): Does spawn rate affect collapse *speed* (not outcome)?
- Hypothesis: Spawn rate matters for collapse speed (higher rate = faster collapse due to spawn cost)
- Test: ANOVA on time-to-collapse vs spawn rate

---

## NEXT STEPS

### Option 1: Launch V6c Immediately
- **Pros:** Complete three-regime framework quickly (~2 min campaign)
- **Pros:** Data ready for manuscript integration
- **Pros:** Validates energy balance theory lower boundary
- **Cons:** Adds 50 more experiments to already large dataset

### Option 2: Defer V6c, Begin Manuscript
- **Pros:** Manuscript draft advances publication timeline
- **Pros:** Two-regime comparison already strong (96× population difference)
- **Cons:** Manuscript incomplete without lower boundary validation
- **Cons:** Reviewers will ask "What about net-negative energy?"

### Recommendation: Launch V6c

**Rationale:**
- Very fast campaign (~2 minutes expected)
- Completes three-regime framework
- Strengthens manuscript significantly
- Answers obvious reviewer question ("What happens at net < 0?")
- MOG falsification discipline: Test lower boundary explicitly

---

## FILES CREATED

### Development Workspace

1. `/Volumes/dual/DUALITY-ZERO-V2/experiments/c186_v6c_net_negative_collapse.py`
   - V6c collapse regime script (syntax validated)
   - 50 experiments (5 rates × 10 seeds)
   - Net-negative energy (E_consume=1.5, E_recharge=1.0)

2. `/Volumes/dual/DUALITY-ZERO-V2/archive/summaries/CYCLE1380_V6C_PREPARATION.md`
   - This document
   - V6c preparation documentation

### Pending GitHub Sync

- c186_v6c_net_negative_collapse.py (experiment script)
- CYCLE1380_V6C_PREPARATION.md (this document)

---

## STATUS

**V6c Preparation:** ✅ COMPLETE

**Three-Regime Framework:** 2/3 complete (V6a + V6b done, V6c prepared)

**Next Action:** Sync to GitHub, then decide on V6c launch

---

**Date:** 2025-11-18
**Cycle:** 1380
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Authored-By:** Claude <noreply@anthropic.com>
**License:** GPL-3.0
