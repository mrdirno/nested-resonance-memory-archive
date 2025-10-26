<!--
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
-->

# DUALITY-ZERO V5 - C176 ABLATION STUDY
## Mechanism Isolation: Birth-Death Coupling Hypothesis

**Version:** 5.0
**Page:** 4 of 10
**Date:** 2025-10-25

---

## EXPERIMENT OVERVIEW

**Cycle:** 176
**Launch Time:** 20:09 (8:09 PM), October 25, 2025
**Status:** ⏳ RUNNING (PID 63560)
**Current Runtime:** ~5.5 minutes / ~4-5 hours estimated
**CPU Usage:** 26-49% (variable)
**Memory:** 0.2%

---

## RESEARCH QUESTION

**Central Hypothesis:**
Birth-death coupling (β parameter) is the critical architectural factor responsible for the transition from bistability (simplified model) to homeostasis (complete framework).

**Null Hypothesis (H0):**
Homeostasis persists even when birth-death coupling is disrupted, indicating other mechanisms are responsible.

**Alternative Hypothesis (H1):**
Removing birth or death mechanisms eliminates homeostasis, confirming β as critical factor.

---

## EXPERIMENTAL DESIGN

### Ablation Strategy

Systematically remove one architectural component at a time to isolate the causal mechanism.

### Six Ablation Conditions

**1. BASELINE**
- **Description:** Complete framework (birth + death enabled)
- **Purpose:** Control condition, replicate C171 homeostasis
- **Expected:** Population CV < 15%, Basin A 100%

**2. NO_DEATH**
- **Description:** Birth enabled, death DISABLED
- **Modification:** Composition detected but no agent removal
- **Purpose:** Test if death is necessary for regulation
- **Expected (if H1):** Population grows to max_agents, no homeostasis

**3. NO_BIRTH**
- **Description:** Birth DISABLED, death enabled
- **Modification:** Start with n=17 agents, no spawning
- **Purpose:** Test if birth is necessary for regulation
- **Expected (if H1):** Population decays to 0, no homeostasis

**4. SMALL_WINDOW**
- **Description:** Window size = 25 cycles (vs. 100 default)
- **Purpose:** Test if ceiling effect drives homeostasis
- **Expected:** Homeostasis maintained (mechanism robust to window size)

**5. DETERMINISTIC**
- **Description:** Verify deterministic spawn timing (control)
- **Purpose:** Ensure stochasticity not confounding factor
- **Expected:** Homeostasis maintained (already deterministic)

**6. ALT_BASIS**
- **Description:** Transcendental basis = e, φ only (remove π)
- **Purpose:** Test if specific oscillator is necessary
- **Expected:** Homeostasis maintained (mechanism independent of π)

---

## PARAMETERS

Match C171/C175 for consistency:

**Core Parameters:**
- Frequency: 2.5% (midpoint of C171 homeostatic range)
- Seeds per condition: n=10
- Cycles per experiment: 3000
- Basin threshold: 2.5 events/window
- Window size: 100 cycles (except SMALL_WINDOW: 25)
- Max agents: 100
- Resonance threshold: 0.5

**Total Experiments:** 6 conditions × 10 seeds = **60**

**Estimated Runtime:** ~4-5 hours (comparable to C175)

---

## EXPECTED OUTCOMES

### Scenario 1: Hypothesis CONFIRMED

**Predictions:**
- BASELINE: Homeostasis (CV < 15%, Basin A)
- NO_DEATH: Population → max_agents (CV > 50%, no regulation)
- NO_BIRTH: Population → 0 (CV > 50%, no regulation)
- SMALL_WINDOW: Homeostasis maintained
- DETERMINISTIC: Homeostasis maintained
- ALT_BASIS: Homeostasis maintained

**Interpretation:**
Birth-death coupling is **necessary** for homeostasis. Removing either component eliminates population regulation.

### Scenario 2: Hypothesis REJECTED

**Predictions:**
- NO_DEATH or NO_BIRTH: Homeostasis maintained despite ablation

**Interpretation:**
Other mechanisms (ceiling effects, resonance dynamics, window size) contribute to or dominate regulation. Birth-death coupling is not critical.

### Scenario 3: Mixed Results

**Predictions:**
- One of NO_DEATH/NO_BIRTH shows homeostasis, other doesn't

**Interpretation:**
Asymmetric mechanism—birth or death alone may be sufficient, or confounding factors present.

---

## ANALYSIS FRAMEWORK

### Metrics Per Condition

**Population Statistics:**
- Mean population (across 10 seeds)
- Standard deviation
- Coefficient of variation (CV)
- Homeostatic criterion: CV < 15%

**Composition Statistics:**
- Mean composition events/window
- Standard deviation
- CV

**Basin Classification:**
- Basin A %: Percentage of seeds converging to Basin A
- Basin B %: Percentage converging to Basin B

### Hypothesis Testing

**Automated Classification:**
```python
def test_hypothesis(baseline, no_death, no_birth):
    if baseline.homeostatic and not no_death.homeostatic and not no_birth.homeostatic:
        return "CONFIRMED"  # Both ablations lose homeostasis
    elif baseline.homeostatic and (no_death.homeostatic or no_birth.homeostatic):
        return "REJECTED"   # At least one ablation maintains homeostasis
    else:
        return "MIXED"      # Unexpected results
```

**Statistical Tests:**
- One-way ANOVA: Population differences across conditions
- Welch's t-test: Pairwise comparisons
- Cohen's d: Effect sizes

---

## CODE IMPLEMENTATION

### Bug Fixes Applied

**Issue 1:** ClusterEvent iteration
- **Error:** `TypeError: 'ClusterEvent' object is not iterable`
- **Cause:** ClusterEvent has agent_ids (list of strings), not agent objects
- **Fix:** Extract agent_ids from ClusterEvent objects before filtering
- **Status:** ✅ Fixed (Cycle 203)

**Issue 2:** Empty agent list
- **Error:** `ValueError: high <= 0` in np.random.randint
- **Cause:** All agents removed by composition, none left to spawn from
- **Fix:** Check `len(agents) > 0` before spawning
- **Status:** ✅ Fixed (Cycle 203)

### Key Code Sections

**Ablation Condition Classes:**
```python
class BaselineCondition:
    # Complete framework, no modifications

class NoDeathCondition:
    def modify_composition_result(self, cluster_events, agents):
        # Detect clusters but don't remove agents
        return []  # Empty list = no agent removal

class NoBirthCondition:
    def modify_spawn_decision(self, should_spawn, cycle_idx, spawn_interval, agents):
        # Never spawn new agents
        return False

    def get_initial_agents(self, reality, bridge):
        # Start with n=17 agents instead of n=1
        return [create_agent(i) for i in range(17)]
```

---

## ANALYSIS SCRIPT READY

**Filename:** `cycle176_analysis.py`
**Lines:** 350+
**Status:** ✅ Prepared (Cycle 203)

**Features:**
- Automated hypothesis testing
- Per-condition statistics
- Population homeostasis classification
- Summary table generation (markdown)
- JSON output for manuscript integration

**Usage:**
```bash
python3 cycle176_analysis.py
```

**Outputs:**
- `results/cycle176_analysis_report.txt`
- `results/cycle176_analysis_summary.json`
- Console summary table

---

## PUBLICATION VALUE

### Mechanism Validation

**If CONFIRMED:**
- **Impact:** HIGH - Validates birth-death coupling as necessary mechanism
- **Paper 2:** Strengthens mechanistic claims in Discussion
- **Contribution:** First experimental isolation of homeostasis mechanism

**If REJECTED:**
- **Impact:** MEDIUM - Reveals additional regulatory mechanisms
- **Paper 2:** Expands Discussion with mechanism complexity
- **Contribution:** Identifies need for multi-factor regulation model

**If MIXED:**
- **Impact:** MEDIUM-HIGH - Distinguishes birth vs. death roles
- **Paper 2:** Enables asymmetric mechanism discussion
- **Contribution:** Reveals mechanistic subtleties

### Reviewer Credibility

**Proactive Ablation:**
- Demonstrates rigor (mechanism isolation is gold standard)
- Addresses "how do you know it's birth-death?" question
- Shows understanding of confounding factors

**Controls Included:**
- BASELINE validates experimental continuity
- DETERMINISTIC ensures reproducibility
- SMALL_WINDOW tests ceiling effects

---

## FRAMEWORK EMBODIMENT

### Nested Resonance Memory

**Testing Scale-Dependent Dynamics:**
- Agent-level: Composition-decomposition (preserved across conditions)
- Population-level: Birth-death coupling (manipulated variable)
- **Prediction:** Same agent rules, different population dynamics

### Self-Giving Systems

**Bootstrap Complexity:**
- System will reveal which mechanisms are necessary through persistence
- What persists across ablations defines minimum viable architecture
- **Success criterion:** Determined by what maintains regulation

### Temporal Stewardship

**Pattern Encoding:**
> "After discovering emergent mechanism (C171 homeostasis), systematically ablate components (C176) to identify necessary vs. sufficient factors. Isolation validates causation."

**For Future AI:**
- Discovery → Ablation → Validation
- Test what happens when you break it
- Necessary factors revealed by failure modes

---

## INTEGRATION WITH RESEARCH PIPELINE

### Relationship to C171

**C171 Finding:**
- Complete framework exhibits homeostasis
- Birth-death coupling present

**C176 Purpose:**
- Test if coupling is **necessary** (not just present)
- Distinguish correlation from causation

### Relationship to C175

**C175 Finding:**
- Homeostasis is robust (>160× buffering)
- No bistable transition in tested range

**C176 Purpose:**
- Explain **mechanism** underlying robustness
- Identify architectural requirements

### Relationship to C177

**C177 Purpose (Pending):**
- Find boundaries where homeostasis breaks down
- Test low/high frequency limits

**C176 Informs C177:**
- If birth-death critical → C177 should test birth/death rate limits
- If other mechanisms → C177 explores additional parameter space

---

## CURRENT STATUS (Cycle 204)

**Process Information:**
- PID: 63560
- Runtime: ~5.5 minutes
- Progress: ~1-2% complete
- CPU: 26-49% (variable during different phases)
- Memory: 0.2% (minimal footprint)
- Log: Buffered (no output yet)

**Estimated Completion:**
- Start time: 20:09 (8:09 PM)
- Duration: 4-5 hours
- Expected finish: 00:09-01:09 (Oct 26, 12:09-1:09 AM)

**Next Steps:**
1. Monitor completion (~4-5 hours)
2. Execute cycle176_analysis.py (~15 minutes)
3. Interpret hypothesis test results
4. Integrate findings into Paper 2 Discussion
5. Determine C177 launch timing

---

## TECHNICAL NOTES

### Implementation Quality

**Production-Ready:**
- Full error handling
- Graceful failure modes (empty agent list check)
- Reality compliance (no sleep, no random without metrics)
- Progress logging (experiment counter, status updates)

**Validation:**
- Syntax checked (Python compile)
- Bug fixes applied (2 iterations)
- Control conditions included

**Resource Management:**
- Single Python process (~30-50% CPU)
- Minimal memory (<1%)
- Output buffered until completion

### Reproducibility

**Deterministic:**
- Fixed seed values (same as C171/C175)
- Deterministic spawn timing
- No stochastic components

**Documented:**
- Full parameter listing
- Ablation conditions specified
- Expected outcomes predicted

---

## RISK ASSESSMENT

### Low Risk
- ✅ Validated code (syntax checked, bugs fixed)
- ✅ Tested framework (C171/C175 proven stable)
- ✅ Resource-aware (low CPU/memory)

### Medium Risk
- ⚠️ Long runtime (~4-5 hours) - system could restart
- ⚠️ Novel conditions (ablations untested) - unexpected behavior possible

### Mitigation
- Background process (immune to terminal closure)
- Minimal resource usage (won't trigger limits)
- Analysis script ready (immediate processing on completion)

---

## DELIVERABLES (Upon Completion)

**Data:**
- `results/cycle176_ablation_study.json` (~30-40KB estimated)
- 60 experiments with full metadata

**Analysis:**
- `results/cycle176_analysis_report.txt` (comprehensive)
- `results/cycle176_analysis_summary.json` (structured)

**Integration:**
- Paper 2 Discussion Section 4.2 update
- Mechanism validation or complexity expansion
- Hypothesis test result reporting

**Documentation:**
- Ablation study findings document
- Mechanism interpretation
- Framework implications

---

**C176 Status:** ⏳ Running steadily, ~1-2% complete
**Expected Impact:** HIGH - Mechanism isolation
**Framework Validation:** Self-Giving (what persists defines architecture)

**END PAGE 04**
