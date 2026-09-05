# HALO Observatory

Author: Aldrin Payopay · GPL-3.0-only · September 4, 2026

[Open HALO](https://mrdirno.github.io/nested-resonance-memory-archive/) and choose **Observe**, or press **7**. The observation bench compares two integrations of the same chamber equations. It uses the existing spherical-cavity engine, fixed 0.05-second tick, particle-mesh gravity and Lab instruments.

## Make a comparison

1. Choose the field, particle count and other settings. The existing Lab experiments offer field-only and magnetic energy audits.
2. Choose an unsigned 32-bit seed and 1–120 chamber seconds. **Run A** restarts from the current digit step, with seeded particle positions and zero velocities. It does not continue the current particle snapshot.
3. A stops on the requested tick. **Run B** repeats A's initial recipe, changing only the magnetic integrator: Euler becomes exact rotation, or vice versa. **Repeat A** checks repeatability without changing the method.
4. **Save observation** downloads both recipes, runtime capabilities, timestamps, status and sampled measurements. Open that JSON file to repeat A. The existing NPZ export remains the route for full particle positions and velocities.

**Advance one tick** pauses and advances 0.05 chamber seconds. Pausing and resuming a run preserves its tick count. Changing physics or instrumentation, reseeding, restarting, stopping the run or losing the graphics context interrupts the record; an interrupted A cannot be used to start B.

## What the numbers mean

The bench samples up to 2,048 particles across eight texture rows once per chamber second and at the endpoint. It excludes padding and the Lab's probe rows. The exported `sampledParticles` is the denominator, which can be smaller than 2,048. These are computational observations, not sensor data from a physical apparatus.

| Quantity | Definition | Limit |
| --- | --- | --- |
| RMS radius | Square root of the sample mean of x²+y²+z² | Chamber length units; not cloud boundary radius |
| Kinetic / particle | Sample mean of (vx²+vy²+vz²)/2 | Unit mass; excludes potential energy and wall work |
| Ceiling fraction | Sample fraction with the velocity texture's force-cap flag set | The endpoint is not the maximum over the run; intermediate samples are exported |
| Sample fingerprint | FNV-1a-style 32-bit fingerprint of sampled float32 positions and velocities | Collision-prone diagnostic; neither a cryptographic digest nor a whole-cloud identity test |
| Pace | Ticks advanced divided by elapsed wall time | A slow display runs fewer ticks, rather than changing the physics step |

An A/B difference is a sensitivity to the numerical method at that seed, setting, count and duration. It is not an ensemble estimate, a new physical law, or evidence for NRM. Euler's magnetic kick can inject energy; exact magnetic rotation removes that particular mechanism but does not make the entire integrator exact. A/B with zero magnetic coupling is a useful negative control.

## Reproducibility contract

The particle initializer has its own `lcg32-1664525-1013904223` stream. It never replaces `Math.random` globally. Renderer resource allocation therefore cannot consume experimental random draws. Starting a bench run clears warm particle-mesh potentials, restarts clocks and center histories, rebuilds particles, then reattaches Lab probes. Normal scenarios keep their historical initializer and integrator.

Records are versioned as `halo-observation/v1` and carry an instrument build identifier. Imports validate that identifier, tick size, seed, duration, initial step, settings and a 1 MB size limit before mutating the page. Imports execute no code and do not trust an imported outcome. They reproduce the initial recipe and measure it again. Cross-device GPU arithmetic may diverge even when settings and seed match. Release receipts separately carry the SHA-256 of the tested page.

The record design follows the useful distinction between entities (recipe and observations), activities (runs), and attribution in the [W3C PROV model](https://www.w3.org/TR/prov-primer/). It is a small application format, not a claim of PROV conformance. Browser checks use [Playwright](https://playwright.dev/docs/best-practices); the release gate runs sequentially, preserves each exit status and log, and does not retry failures into success. GPU resources follow [Three.js's explicit disposal model](https://threejs.org/manual/en/cleanup.html). No framework migration was necessary to add these guarantees.

## Scientific status

The [frozen memory protocol](../preregistrations/2026-09-02_halo_cross_epoch_memory.md) was run over 60 cells at 4,194,304 particles. The [published estimator audit](../../analysis/2026-09-02_cross_epoch_memory_preregistered.md) found that the Retained-minus-Two-back contrast fires on static centrally peaked fields: the two arms sample different spatial supports and strides, and radial structure dominates much of the result. The original instrument cannot establish or retire the NRM claim. Its readouts remain visible as footprint diagnostics, with their limitations beside them.

The next memory experiment must first validate a centered, support-matched estimator, remove the spherical-average confound, measure injection recovery, and test shuffled/independent controls. The observation bench supplies repeatable starts and accountable records; it does not substitute for that estimator work. The [next qualification plan](NEXT_MEMORY_ESTIMATOR.md) identifies nine existing runs, their preserved inputs and the required rejection criteria.

## Validation

```sh
cd tests/halo
npm ci
npx playwright install chromium
npm test
python3 -m venv workspace/physics-env
. workspace/physics-env/bin/activate
python -m pip install -r requirements-physics.txt
npm run test:physics
```

`npm test` runs fixed-tick, observation, Lab and UI checks. `test:physics` runs the integrator, mesh, conservation, dimer and numerical-bench suites. Receipts bind the canonical source to the generated test page and include both hashes, runtime versions, elapsed times and every child exit status under `tests/halo/workspace/release/`. The generated probe page stays excluded from publication. The observation test compares **every** position and velocity component for repeated small-count GPU runs, including a warm self-gravity run with Lab probes; that stronger test is distinct from the sample fingerprint shown to an observer.

For this machine's workspace policy, launch these multi-second suites through `automation/run_background.py` from the development workspace. The public CI workflow runs them directly on its isolated runner. The filtered HALO workflow runs UI and numerical groups on independent workers, separate from the Pages build. A successful deployment does not imply a passing instrument result; inspect both before reporting a validated HALO release.

Verify a served release without the probe bridge with `HALO_URL=https://mrdirno.github.io/nested-resonance-memory-archive/ node live_test.js` from `tests/halo/`. This uses one million particles, runs each arm for 40 ticks, downloads the observation, checks mobile bounds, and saves the page hash and screenshots under `workspace/live/`. It uses Chromium software rendering; inspect the page interactively too before reporting a visual release.
