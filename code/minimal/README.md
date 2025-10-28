# Minimal NRM Package

This folder now exposes a *reality-grounded* slice of the Nested Resonance
Memory (NRM) stack so experiments can be run without navigating the entire
research codebase.

Key components:

* `MinimalRealityGateway` wraps the production `RealityInterface` and
  persists measurements to a dedicated workspace (configurable for tests).
* `MinimalAgent` converts snapshots to transcendental phase states via the
  real `TranscendentalBridge` and tracks resonance history from actual
  bridge computations.
* `find_resonant_clusters` simply delegates to the bridge for pairwise
  resonance detection so the minimal package shares the same semantics as
  the full framework.
* `MinimalSwarm` orchestrates snapshot capture, agent updates, and cluster
  descriptions with only a few lines of glue code.

## Quickstart

```bash
python -m code.minimal
```

Optional flags include `--workspace` to point the helper at an isolated
output directory, `--agents` to control how many agents are spawned, and
`--cycles` to select the number of update iterations.

Because the implementation depends on the actual NRM infrastructure it is
suitable for both lightweight analysis and validation of the larger stack.
