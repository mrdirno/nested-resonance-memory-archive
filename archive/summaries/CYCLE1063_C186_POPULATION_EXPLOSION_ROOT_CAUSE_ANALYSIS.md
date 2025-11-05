# CYCLE 1063: C186 POPULATION EXPLOSION - ROOT CAUSE ANALYSIS

**Date:** 2025-11-05
**Session Duration:** ~45 minutes
**Focus:** C186 V1 Simple hung process investigation
**Outcome:** Root cause identified - spawn logic mismatch causing memory exhaustion

---

## EXECUTIVE SUMMARY

**Problem:** C186 V1 Simple process hangs after ~500 cycles with 0% CPU, "RN" state, no output

**Root Cause:** Population explosion due to spawn logic mismatch
- C186 spawns EVERY cycle at F_INTRA rate (2.5% of population size)
- C176/C177 spawn at INTERVALS (every spawn_interval cycles)
- Result: Exponential growth → ~9.7M agents by cycle 500 → ~1.8GB memory allocation → system-level hang

**Status:** Issue diagnosed, fix documented, implementation deferred pending C177 completion

---

## INVESTIGATION TIMELINE

### Phase 1: Initial State Assessment (5 min)
- **Observation:** C186 V1 Simple output log shows only header + "Running seed 42..."
- **Hypothesis:** Buffering issue (flush=True already applied)
- **Action:** Checked process status: PID 63649/65805 both hung with same pattern

### Phase 2: Minimal Test Creation (10 min)
- **Created:** test_c186_minimal.py - Tests individual components
- **Result:** ✅ ALL TESTS PASSED in < 1 second
  - Random initialization: functional
  - Agent/Population creation: functional
  - Spawn logic (1 attempt): functional
  - Migration logic (3 attempts): functional
- **Conclusion:** Core logic has no bugs

### Phase 3: Short-Cycle Full Test (10 min)
- **Created:** test_c186_full_short.py - Full experiment with 100 cycles (vs 3000)
- **Result:** ✅ COMPLETED SUCCESSFULLY in 0.01 seconds
  - Seed 42: 200 → 1,731 agents (8.65× growth)
  - Seed 123: 200 → 1,754 agents (8.77× growth)
- **Conclusion:** Issue is iteration-count / scale related

### Phase 4: Population Explosion Projection (5 min)
**Calculation:**
```
Growth rate: 8.65× per 100 cycles
Projection at 500 cycles: ~9.7 million agents (~1.8 GB memory)
Projection at 1000 cycles: ~471 billion agents (~90 TB memory)
```

**Mechanism:**
1. Initial: 200 agents across 10 populations
2. Each cycle: n_attempts = max(1, int(len(pop.agents) * 0.025))
3. Energy threshold (20) < Initial energy (50), so ALL agents can spawn
4. Child energy = 25 (0.5 * 50), which is ABOVE threshold (20)
5. Children spawn immediately → exponential cascade
6. By cycle 500: Memory allocator blocks → OS puts process in "RN" state → 0% CPU hang

### Phase 5: Comparative Analysis (15 min)
**C176/C177 Spawn Mechanism** (from cycle176_v6_baseline_validation.py:104-125):
```python
# Calculate spawn interval
spawn_interval = max(1, int(100.0 / frequency))

# Run cycles
for cycle_idx in range(cycles):
    should_spawn = (cycle_idx % spawn_interval) == 0  # ← INTERVAL CHECK

    if should_spawn and len(agents) < MAX_AGENTS:
        spawn_count += 1
        parent = agents[np.random.randint(len(agents))]
        child = parent.spawn_child(child_id, energy_fraction=0.3)

        # Only add if spawn succeeded (energy-regulated)
        if child:  # ← NONE CHECK FOR FAILURE
            agents.append(child)
```

**Key Differences:**
1. **Spawn Interval:** C176/C177 spawns every `spawn_interval` cycles, NOT every cycle
2. **Energy Regulation:** `parent.spawn_child()` returns `None` on energy failure
3. **MAX_AGENTS Cap:** 100 agent hard limit
4. **Frequency Interpretation:** C176 frequency = % per 100 cycles, C186 frequency = % per cycle

**C186 Spawn Mechanism** (from c186_v1_hierarchical_spawn_failure_simple.py:142-170):
```python
def _intra_spawning(self):
    for population in self.populations:  # ← EVERY CYCLE
        if len(population.agents) == 0:
            continue

        n_attempts = max(1, int(len(population.agents) * F_INTRA))  # ← 2.5% per cycle

        for _ in range(n_attempts):
            parent = self.random.choice(population.agents)

            if parent.energy >= E_SPAWN_THRESHOLD:  # ← Simple energy check
                parent.energy -= E_SPAWN_COST
                child = Agent(
                    id=self.next_agent_id,
                    population_id=population.id,
                    energy=E_INITIAL * 0.5  # ← 25 energy (ABOVE THRESHOLD 20!)
                )
                population.agents.append(child)  # ← Always appends
```

**Critical Flaw:** Children spawn with energy=25, which exceeds threshold (20), enabling immediate re-spawning

---

## SPAWN LOGIC COMPARISON

| Aspect | C176/C177 (Working) | C186 V1 Simple (Broken) |
|--------|---------------------|-------------------------|
| Spawn Frequency | Every `spawn_interval` cycles | EVERY cycle |
| Interval Calculation | `max(1, int(100.0 / frequency))` | None (always spawn) |
| Energy Check | `parent.spawn_child()` (internal) | `parent.energy >= threshold` |
| Failure Handling | Returns `None`, no append | Always appends if energy sufficient |
| Child Energy | Fraction of parent (0.3) | Fixed: 0.5 * E_INITIAL = 25 |
| Population Cap | MAX_AGENTS = 100 | None (unbounded) |
| Growth Control | Interval + energy + cap | Energy only (insufficient) |

---

## ENERGY DYNAMICS ANALYSIS

**C186 Parameters:**
```python
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
RECHARGE_RATE = 0.5  # per cycle per agent
```

**Critical Issue:** Child energy > spawn threshold
```python
child_energy = E_INITIAL * 0.5  # 25
spawn_threshold = 20.0           # 20
# Result: 25 > 20 → child can spawn immediately!
```

**Growth Cascade:**
1. Parent (E=50) spawns child (E=25), parent now E=40
2. Child (E=25) can spawn next cycle, creates grandchild (E=25)
3. Grandchild (E=25) can spawn next cycle, creates great-grandchild (E=25)
4. **Exponential growth:** Each generation spawns fully-capable offspring

**Energy Recovery Insufficient:**
- Recovery: 0.5/cycle
- Spawn cost: 10
- Time to recover: 20 cycles
- But new high-energy children born every cycle → always fresh spawners available

---

## PROPOSED FIXES

### Fix 1: Implement Spawn Intervals (Recommended)
**Match C176/C177 mechanism:**
```python
# Calculate spawn interval from frequency
spawn_interval = max(1, int(100.0 / F_INTRA_PCT))  # F_INTRA_PCT = 2.5

for cycle in range(CYCLES):
    should_spawn = (cycle % spawn_interval) == 0

    if should_spawn:
        self._intra_spawning()  # Only spawn on interval cycles

    self._inter_migration()
    self._energy_recovery()
```

**Effect:** 2.5% frequency → spawn every 40 cycles (vs every cycle)
**Growth reduction:** ~40× slower spawn rate

### Fix 2: Increase Child Energy Cost
**Prevent immediate re-spawning:**
```python
# Option A: Lower child energy
child_energy = E_SPAWN_THRESHOLD * 0.5  # 10 (below threshold)

# Option B: Increase spawn threshold
E_SPAWN_THRESHOLD = 40.0  # Children with E=25 cannot spawn

# Option C: Implement spawn cooldown
Agent.last_spawn_cycle = cycle_idx
if (cycle_idx - parent.last_spawn_cycle) < SPAWN_COOLDOWN:
    continue  # Skip spawn attempt
```

### Fix 3: Add Population Cap
**Prevent unbounded growth:**
```python
MAX_AGENTS_PER_POP = 100  # Match C176

if len(population.agents) >= MAX_AGENTS_PER_POP:
    continue  # Skip spawning for this population
```

### Fix 4: Implement parent.spawn_child() Method
**Use FractalAgent infrastructure:**
```python
# Replace manual spawn logic with proper FractalAgent.spawn_child()
# This includes built-in energy regulation and failure handling
```

---

## EXPERIMENTAL DESIGN IMPLICATIONS

**Original C186 Hypothesis:**
> f_intra = 2.5% will produce 0% Basin A (complete collapse)
> Confirms α > 1.25 (hierarchical scaling coefficient)

**Actual Behavior:**
- f_intra = 2.5% produces EXPLOSIVE GROWTH (not collapse)
- Memory exhaustion prevents experiment completion
- Hypothesis untestable with current spawn logic

**Corrected Hypothesis** (pending fix validation):
- With spawn intervals: f_intra = 2.5% may produce collapse as predicted
- Without intervals: All frequencies cause explosion
- Energy compartmentalization cannot be tested until spawn intervals implemented

**Impact on C186 V2:**
- Same spawn logic flaw
- f_intra = 5.0% will explode even faster
- Requires same fix before execution

---

## NEXT ACTIONS

### Immediate (Post-C177 Completion):
1. ✅ Document root cause analysis (this file)
2. ⏳ Implement Fix 1 (spawn intervals) in C186 V1 Simple
3. ⏳ Validate fix with short-cycle test (100 cycles)
4. ⏳ Execute full C186 V1 Simple (3000 cycles, 10 seeds)
5. ⏳ Apply same fix to C186 V2 Simple
6. ⏳ Execute C186 V2 Simple
7. ⏳ Run C186 V1/V2 analysis pipeline

### Validation Criteria:
- ✅ Short test completes in < 5 seconds
- ✅ Population remains < 1000 agents at cycle 500
- ✅ Final population shows Basin A/B distribution (not explosion)
- ✅ Memory usage < 100 MB throughout execution

---

## LESSONS LEARNED

1. **Test at Multiple Scales:** Short-cycle tests (100) revealed scale-dependent issues that minimal tests (single operations) missed

2. **Spawn Interval Critical:** Frequency interpretation differs across experiment types
   - C176/C177: % per 100 cycles (spawn interval)
   - C186 original: % per cycle (every cycle)
   - Must match interpretation for valid comparison

3. **Energy Threshold vs Child Energy:** Child energy must be BELOW spawn threshold to prevent cascades
   - Working: child_energy < spawn_threshold
   - Broken: child_energy > spawn_threshold (C186)

4. **Memory Projection Essential:** Calculating growth projections early (Phase 4) confirmed explosion hypothesis before attempting full fix

5. **Comparative Analysis:** Reading working code (C176) revealed proper pattern, avoided re-inventing mechanism

---

## TECHNICAL ARTIFACTS

### Test Files Created:
1. **test_c186_minimal.py** (125 lines)
   - Tests: Random, Agent, Population, Spawn, Migration
   - Result: All passed (< 1 second)

2. **test_c186_full_short.py** (170 lines)
   - Full HierarchicalSystem with 100 cycles
   - Result: Completed successfully, revealed 8.65× growth/100 cycles

### Data Collected:
```
Short Test Results (100 cycles):
  Seed  42: 200 → 1,731 agents (8.65×), 0.01s, Basin A
  Seed 123: 200 → 1,754 agents (8.77×), 0.01s, Basin A

Projected Growth:
  Cycle  100:       1,731 agents (~0.3 MB)
  Cycle  500:   9,713,268 agents (~1.8 GB) ← HANG POINT
  Cycle 1000: 471,737,843,930 agents (~90 TB) ← IMPOSSIBLE
```

---

## SESSION METRICS

- **Investigation Time:** 45 minutes
- **Files Created:** 3 (2 test scripts, 1 summary)
- **Code Lines Written:** 295 lines
- **Root Cause Identified:** ✅ YES
- **Fix Implemented:** ⏳ Documented, pending execution
- **C177 V2 Status:** 71/90 (79%), ~20 minutes to completion

---

## REFERENCES

**Related Files:**
- `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/c186_v1_hierarchical_spawn_failure_simple.py` (362 lines)
- `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/c186_v2_hierarchical_spawn_success_simple.py` (362 lines)
- `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/cycle176_v6_baseline_validation.py` (reference)
- `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/test_c186_minimal.py` (diagnostic)
- `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/test_c186_full_short.py` (diagnostic)

**Prior Session:**
- `CYCLE1060_C186_SIMPLIFIED_BASELINE_AND_ANALYSIS_INFRASTRUCTURE.md` (543 lines)

**Next Session:**
- C186 V1/V2 fix implementation
- C177 V2 analysis execution

---

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude <noreply@anthropic.com>
**License:** GPL-3.0
