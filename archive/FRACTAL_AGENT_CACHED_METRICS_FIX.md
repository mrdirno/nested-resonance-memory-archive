# FractalAgent.evolve() Cached Metrics Parameter Fix

**Date:** 2025-10-30
**Issue:** TypeError when cycle256_h1h4_optimized.py passes `cached_metrics` parameter to FractalAgent.evolve()
**Status:** READY FOR DEPLOYMENT (after C256 completes)

---

## Problem

**Error:**
```
TypeError: FractalAgent.evolve() got an unexpected keyword argument 'cached_metrics'
```

**Root Cause:**
The optimized experiment scripts (cycle256_h1h4_optimized.py, cycle257-260 equivalents) attempt to pass pre-fetched system metrics to `FractalAgent.evolve()` for performance optimization, but the method signature doesn't support this parameter.

**Current Signature:**
```python
def evolve(self, delta_time: float) -> None:
```

**Required Signature:**
```python
def evolve(self, delta_time: float, cached_metrics: Optional[Dict[str, float]] = None) -> None:
```

---

## Solution

### File to Modify

**Path:** `/Volumes/dual/DUALITY-ZERO-V2/fractal/fractal_agent.py`
**Line:** 161 (evolve method definition)

### Code Changes

**BEFORE (Lines 161-195):**
```python
def evolve(self, delta_time: float) -> None:
    """
    Evolve agent state through time.

    Uses transcendental oscillations to drive internal evolution.
    Energy dissipates over time (entropy) but can recharge from reality.

    Framework Enhancement (Cycle 215):
    Added reality-grounded energy recharge to enable sustained population
    dynamics in complete birth-death coupling experiments. Energy flows
    from available system resources (idle CPU/memory) to agents.

    Args:
        delta_time: Time step for evolution
    """
    # Oscillate phase state using transcendental substrate
    frequency = 0.1 * delta_time
    oscillation = self.bridge.generate_oscillation(frequency, duration=1)

    if oscillation:
        # Move to new phase state
        self.phase_state = oscillation[0]

    # Energy dissipation (entropy)
    energy_decay = 0.01 * delta_time  # ~0.0001/cycle

    # Energy recharge from reality (absorbed from available resources)
    # Agents can slowly recharge by absorbing idle system capacity
    # This enables sustained spawning in birth-death coupled systems
    # V4 Enhancement (Cycle 216): Increased recharge rate 10× (0.001 → 0.01)
    # to enable recovery to spawn threshold (~10 energy) within ~1000 cycles
    # V6 Enhancement (Cycle 243): Add measurement noise for statistical validity
    # Noise represents natural variation in system metric sampling
    if hasattr(self, 'reality') and self.reality is not None:
        current_metrics = self.reality.get_system_metrics()
```

**AFTER (with cached_metrics support):**
```python
def evolve(self, delta_time: float, cached_metrics: Optional[Dict[str, float]] = None) -> None:
    """
    Evolve agent state through time.

    Uses transcendental oscillations to drive internal evolution.
    Energy dissipates over time (entropy) but can recharge from reality.

    Framework Enhancement (Cycle 215):
    Added reality-grounded energy recharge to enable sustained population
    dynamics in complete birth-death coupling experiments. Energy flows
    from available system resources (idle CPU/memory) to agents.

    Optimization Enhancement (Cycle 637):
    Added optional cached_metrics parameter to support batched system metric
    sampling for optimized experiments. When provided, uses pre-fetched metrics
    instead of calling get_system_metrics() for each agent, reducing I/O overhead
    from 1.08M psutil calls → 12K calls (90× reduction).

    Args:
        delta_time: Time step for evolution
        cached_metrics: Optional pre-fetched system metrics dict with keys:
                        'cpu_percent', 'memory_percent'. If None, fetches fresh
                        metrics (default behavior for backward compatibility).
    """
    # Oscillate phase state using transcendental substrate
    frequency = 0.1 * delta_time
    oscillation = self.bridge.generate_oscillation(frequency, duration=1)

    if oscillation:
        # Move to new phase state
        self.phase_state = oscillation[0]

    # Energy dissipation (entropy)
    energy_decay = 0.01 * delta_time  # ~0.0001/cycle

    # Energy recharge from reality (absorbed from available resources)
    # Agents can slowly recharge by absorbing idle system capacity
    # This enables sustained spawning in birth-death coupled systems
    # V4 Enhancement (Cycle 216): Increased recharge rate 10× (0.001 → 0.01)
    # to enable recovery to spawn threshold (~10 energy) within ~1000 cycles
    # V6 Enhancement (Cycle 243): Add measurement noise for statistical validity
    # Noise represents natural variation in system metric sampling
    # V7 Optimization (Cycle 637): Support cached_metrics for batched sampling
    if hasattr(self, 'reality') and self.reality is not None:
        # Use cached metrics if provided, otherwise fetch fresh
        if cached_metrics is not None:
            current_metrics = cached_metrics
        else:
            current_metrics = self.reality.get_system_metrics()
```

### Complete Modified Method

**Full replacement for lines 161-229:**
```python
def evolve(self, delta_time: float, cached_metrics: Optional[Dict[str, float]] = None) -> None:
    """
    Evolve agent state through time.

    Uses transcendental oscillations to drive internal evolution.
    Energy dissipates over time (entropy) but can recharge from reality.

    Framework Enhancement (Cycle 215):
    Added reality-grounded energy recharge to enable sustained population
    dynamics in complete birth-death coupling experiments. Energy flows
    from available system resources (idle CPU/memory) to agents.

    Optimization Enhancement (Cycle 637):
    Added optional cached_metrics parameter to support batched system metric
    sampling for optimized experiments. When provided, uses pre-fetched metrics
    instead of calling get_system_metrics() for each agent, reducing I/O overhead
    from 1.08M psutil calls → 12K calls (90× reduction).

    Args:
        delta_time: Time step for evolution
        cached_metrics: Optional pre-fetched system metrics dict with keys:
                        'cpu_percent', 'memory_percent'. If None, fetches fresh
                        metrics (default behavior for backward compatibility).
    """
    # Oscillate phase state using transcendental substrate
    frequency = 0.1 * delta_time
    oscillation = self.bridge.generate_oscillation(frequency, duration=1)

    if oscillation:
        # Move to new phase state
        self.phase_state = oscillation[0]

    # Energy dissipation (entropy)
    energy_decay = 0.01 * delta_time  # ~0.0001/cycle

    # Energy recharge from reality (absorbed from available resources)
    # Agents can slowly recharge by absorbing idle system capacity
    # This enables sustained spawning in birth-death coupled systems
    # V4 Enhancement (Cycle 216): Increased recharge rate 10× (0.001 → 0.01)
    # to enable recovery to spawn threshold (~10 energy) within ~1000 cycles
    # V6 Enhancement (Cycle 243): Add measurement noise for statistical validity
    # Noise represents natural variation in system metric sampling
    # V7 Optimization (Cycle 637): Support cached_metrics for batched sampling
    if hasattr(self, 'reality') and self.reality is not None:
        # Use cached metrics if provided, otherwise fetch fresh
        if cached_metrics is not None:
            current_metrics = cached_metrics
        else:
            current_metrics = self.reality.get_system_metrics()

        # V6: Apply measurement noise if configured (Cycle 243+)
        if hasattr(self, 'measurement_noise_std') and self.measurement_noise_std is not None:
            import numpy as np
            # Add proportional Gaussian noise to reality metrics
            # Noise std = measurement_noise_std × metric_value
            cpu_noise = np.random.normal(0, self.measurement_noise_std * current_metrics['cpu_percent'])
            mem_noise = np.random.normal(0, self.measurement_noise_std * current_metrics['memory_percent'])

            # Apply noise with bounds checking [0, 100]
            cpu_with_noise = max(0.0, min(100.0, current_metrics['cpu_percent'] + cpu_noise))
            mem_with_noise = max(0.0, min(100.0, current_metrics['memory_percent'] + mem_noise))

            available_capacity = (100 - cpu_with_noise) + (100 - mem_with_noise)
        else:
            # No noise: deterministic reality sampling (default behavior)
            available_capacity = (100 - current_metrics['cpu_percent']) + \
                                (100 - current_metrics['memory_percent'])

        energy_recharge = 0.01 * available_capacity * delta_time  # ~1.0/100 cycles
    else:
        # Fallback: minimal recharge if no reality interface
        energy_recharge = 0.01 * delta_time  # ~0.0001/cycle (negligible)

    # Net energy change (recharge dominates decay by ~1000×)
    self.energy = self.energy - energy_decay + energy_recharge

    # Cap energy at 200 (prevents unlimited accumulation)
    self.energy = max(0.0, min(200.0, self.energy))

    # Evolve children recursively
    # NOTE: Children also receive cached_metrics for consistency
    for child in self.children:
        child.evolve(delta_time, cached_metrics=cached_metrics)
```

### Critical Addition: Recursive Calls

**Line 228 BEFORE:**
```python
child.evolve(delta_time)
```

**Line 228 AFTER:**
```python
child.evolve(delta_time, cached_metrics=cached_metrics)
```

**Reason:** Child agents must also use cached metrics for consistency. If parent uses cached metrics from cycle N, children should use same metrics, not fetch fresh ones.

---

## Testing Plan

### Test 1: Backward Compatibility (Unoptimized Scripts)

**Command:**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
python3 << 'EOF'
from fractal.fractal_agent import FractalAgent
from bridge.transcendental_bridge import TranscendentalBridge
from core.reality_interface import RealityInterface

# Test original calling pattern (no cached_metrics)
bridge = TranscendentalBridge()
reality = RealityInterface()
agent = FractalAgent(
    agent_id=0,
    bridge=bridge,
    initial_reality={'cpu': 0.5, 'memory': 0.5},
    reality=reality
)

# Original call (should work without cached_metrics parameter)
agent.evolve(delta_time=1.0)
print("✅ Backward compatibility test passed")
EOF
```

**Expected:** No errors, method executes with fresh metrics.

### Test 2: Optimized Script (Cached Metrics)

**Command:**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
python3 << 'EOF'
from fractal.fractal_agent import FractalAgent
from bridge.transcendental_bridge import TranscendentalBridge
from core.reality_interface import RealityInterface

# Test optimized calling pattern (with cached_metrics)
bridge = TranscendentalBridge()
reality = RealityInterface()
agent = FractalAgent(
    agent_id=0,
    bridge=bridge,
    initial_reality={'cpu': 0.5, 'memory': 0.5},
    reality=reality
)

# Pre-fetch metrics once (optimization)
cached_metrics = reality.get_system_metrics()

# Optimized call (should use cached metrics)
agent.evolve(delta_time=1.0, cached_metrics=cached_metrics)
print("✅ Cached metrics test passed")
EOF
```

**Expected:** No errors, method executes with cached metrics.

### Test 3: Full Optimized Script

**Command:**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
python cycle256_h1h4_optimized.py --test-mode --cycles 100
```

**Expected:** Script runs without TypeError, completes 100-cycle test in ~1-2 minutes.

---

## Deployment Checklist

**After C256 completes:**

- [ ] Apply fix to `/Volumes/dual/DUALITY-ZERO-V2/fractal/fractal_agent.py`
- [ ] Run Test 1 (backward compatibility)
- [ ] Run Test 2 (cached metrics)
- [ ] Run Test 3 (full optimized script, 100 cycles)
- [ ] If all tests pass: Sync to git repository
- [ ] Commit with attribution
- [ ] Update cycle257-260 scripts to use optimized versions
- [ ] Execute C257-C260 batch

**Estimated time:** ~5 minutes (fix + 3 tests)

---

## Impact Assessment

**Before Fix:**
- C256 ran unoptimized version (40× overhead, ~20h runtime)
- C257-C260 scripts would crash with TypeError
- Paper 3 optimization validation impossible

**After Fix:**
- C257-C260 run optimized versions (~13-14h each, 90× psutil reduction)
- Paper 3 Section 3.1 can compare C255 (unoptimized) vs C257-C260 (optimized)
- Runtime estimates accurate for future experiments

**Total Impact:**
- Prevents ~20h × 4 experiments = ~80h of wasted unoptimized runtime
- Enables optimization validation in Paper 3
- Maintains backward compatibility for existing scripts

---

## Notes

**Why Cycle 256 took 17.5-20h:**
The optimized script crashed immediately (TypeError), and the system fell back to running the unoptimized `cycle256_h1h4_mechanism_validation.py` script. This is consistent with C255's 20.1h unoptimized runtime (40× overhead from 1.08M psutil calls).

**Why the fix is simple:**
The optimization logic is already implemented in the experiment scripts - they batch-fetch metrics once per cycle and attempt to pass them to agents. The only missing piece is the `evolve()` method accepting the parameter.

**Backward compatibility:**
Using `cached_metrics: Optional[Dict[str, float]] = None` ensures all existing experiment scripts continue to work without modification. Only optimized scripts (which already attempt to pass the parameter) will benefit.

---

**Document Status:** READY FOR DEPLOYMENT
**Created:** Cycle 637 (2025-10-30, 09:45 AM)
**Purpose:** Prepare bug fix during C256 blocking period for immediate deployment post-completion
**Pattern:** Blocking Periods = Preparatory Work for Next Phase
