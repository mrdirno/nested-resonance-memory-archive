# Ready-to-Execute Edit Commands for cached_metrics Fix

**Purpose:** Instant deployment commands for FractalAgent.evolve() fix post-C256
**Target:** `/Volumes/dual/DUALITY-ZERO-V2/fractal/fractal_agent.py`
**Date:** 2025-10-30
**Cycle:** 638

---

## Edit 1: Update Method Signature

**Target Lines:** 161-175 (signature + docstring)

**Old String:**
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
```

**New String:**
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
```

---

## Edit 2: Add cached_metrics Logic

**Target Lines:** 187-195 (reality sampling section)

**Old String:**
```python
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

**New String:**
```python
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

---

## Edit 3: Update Recursive Call

**Target Lines:** 226-228 (recursive evolution)

**Old String:**
```python
        # Evolve children recursively
        for child in self.children:
            child.evolve(delta_time)
```

**New String:**
```python
        # Evolve children recursively
        # NOTE: Children also receive cached_metrics for consistency
        for child in self.children:
            child.evolve(delta_time, cached_metrics=cached_metrics)
```

---

## Execution Sequence

After C256 completes, execute these Edit tool calls in sequence:

```python
# Edit 1: Method signature + docstring
Edit(
    file_path="/Volumes/dual/DUALITY-ZERO-V2/fractal/fractal_agent.py",
    old_string="""    def evolve(self, delta_time: float) -> None:
        \"\"\"
        Evolve agent state through time.

        Uses transcendental oscillations to drive internal evolution.
        Energy dissipates over time (entropy) but can recharge from reality.

        Framework Enhancement (Cycle 215):
        Added reality-grounded energy recharge to enable sustained population
        dynamics in complete birth-death coupling experiments. Energy flows
        from available system resources (idle CPU/memory) to agents.

        Args:
            delta_time: Time step for evolution
        \"\"\"""",
    new_string="""    def evolve(self, delta_time: float, cached_metrics: Optional[Dict[str, float]] = None) -> None:
        \"\"\"
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
        \"\"\""""
)

# Edit 2: Add cached_metrics logic
Edit(
    file_path="/Volumes/dual/DUALITY-ZERO-V2/fractal/fractal_agent.py",
    old_string="""        # Energy recharge from reality (absorbed from available resources)
        # Agents can slowly recharge by absorbing idle system capacity
        # This enables sustained spawning in birth-death coupled systems
        # V4 Enhancement (Cycle 216): Increased recharge rate 10× (0.001 → 0.01)
        # to enable recovery to spawn threshold (~10 energy) within ~1000 cycles
        # V6 Enhancement (Cycle 243): Add measurement noise for statistical validity
        # Noise represents natural variation in system metric sampling
        if hasattr(self, 'reality') and self.reality is not None:
            current_metrics = self.reality.get_system_metrics()""",
    new_string="""        # Energy recharge from reality (absorbed from available resources)
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
                current_metrics = self.reality.get_system_metrics()"""
)

# Edit 3: Update recursive call
Edit(
    file_path="/Volumes/dual/DUALITY-ZERO-V2/fractal/fractal_agent.py",
    old_string="""        # Evolve children recursively
        for child in self.children:
            child.evolve(delta_time)""",
    new_string="""        # Evolve children recursively
        # NOTE: Children also receive cached_metrics for consistency
        for child in self.children:
            child.evolve(delta_time, cached_metrics=cached_metrics)"""
)
```

---

## Post-Edit Testing

After applying all 3 edits:

```bash
# 1. Run validation tests
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
python test_cached_metrics_fix.py

# 2. If all tests pass, commit fix
cd /Volumes/dual/DUALITY-ZERO-V2
git add fractal/fractal_agent.py
git commit -m "Fix FractalAgent.evolve() cached_metrics parameter support

Add optional cached_metrics parameter to support batched system metric sampling
in optimized experiments. Reduces I/O overhead from 1.08M → 12K psutil calls
(90× reduction).

Changes:
- Add cached_metrics parameter with default None (backward compatible)
- Use cached metrics if provided, fetch fresh otherwise
- Propagate cached_metrics to child agent evolution

Tested:
- Backward compatibility (existing calls work without parameter)
- Cached metrics parameter (optimized calls work with parameter)
- Batched evolution (multiple agents, one metric fetch)
- Recursive propagation (children receive cached metrics)

Resolves TypeError discovered during C256 runtime investigation.

Cycle 638 (2025-10-30)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>"

# 3. Update optimized experiment scripts
# cycle256-260_optimized.py line 191:
# FROM: agent.evolve(delta_time=1.0)
# TO:   agent.evolve(delta_time=1.0, cached_metrics=shared_metrics)
```

---

## Estimated Deployment Time

- Apply 3 edits: ~30 seconds
- Run validation tests: ~10 seconds
- Commit to git: ~5 seconds
- Update 5 optimized scripts: ~2 minutes
- **Total: ~3 minutes**

---

**Status:** READY FOR IMMEDIATE DEPLOYMENT POST-C256
**Created:** Cycle 638 (2025-10-30, 09:55 AM)
**Purpose:** Enable instant bug fix application when C256 completes
