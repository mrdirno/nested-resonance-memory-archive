# HALO experiments — the falsifiers behind the Resonance Chamber's claims

The page `HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html` states
its findings with the numbers that could kill them. This directory holds the
scripts that produced those numbers, so anyone can rerun them.

## ports/ — a NumPy twin of the page's physics

`port2.py` reproduces the page's particle-mesh gravity on the CPU and was
checked cell by cell against the page's own GPU mesh (potential correlation
0.99994, force 0.99995). The `jeans_*.py`, `disc_*.py` and `memory_*.py`
scripts use it to answer one question each:

- `jeans_*.py` — does the self-gravity threshold follow the expansion rate
  (a Jeans criterion) or the swarm's spin? Result: the spin.
- `disc_*.py` — is the Razor Disc physics or the integrator's? Result: the
  integrator's (its speed is 500·√(dt/2γ)); under the exact rotation the
  same settings pile matter at the poles.
- `memory_*.py` — does one epoch imprint the next? Result: a null at low
  self-gravity; where memory rises the two-back control rises with it.

Each script writes its JSON next to itself; the copies that back the page are
in `data/results/halo/`. Requirements: `numpy`; `numba` speeds some of them up.

## jeans_dispersion.py — the growth rates the page's sphere cannot host

`jeans_dispersion.py` runs the page's self-gravity operator (nearest-cell
deposit, 7-point Laplacian, two-point gradient, tick 1/20, SG_GAIN 14,
PM_CELL 0.95625) on a periodic box, where plane waves are eigenmodes, and
measures the growth rate of cold-dust waves m = 1, 2, 4, 8 against two closed
forms for the discrete operator: D = k sin k (sin(k/2)/(k/2)) / (4 sin²(k/2))
for a smooth wave, and D = cos²(k/2) for the per-cell displacement that the
scheme's kicks make, which is the one the dynamics follow. The derivation is
in its docstring; the numbers go to `results/jeans_dispersion.json` (tracked).
`orbit_twin.py` is the numpy twin of the page's "Two clumps in orbit"
experiment: the same start, the same operator, both solvers, the same
readouts. `load_chamber_npz.py` reads a snapshot saved by the page's "Save
NPZ" button, checks it, recomputes the density on the page's grid and reports
the correlation with the exported one.

```bash
python3 jeans_dispersion.py                              # ~30 s, numpy only
python3 orbit_twin.py                                    # ~3 s
python3 load_chamber_npz.py resonance-chamber-snapshot.npz
```

## the memory estimator: qualification, and the pilot that looks for something to measure

`memory_estimator_qualify.py` is the **frozen** scorer for the replacement
cross-epoch memory estimator; it implements
`docs/halo/2026-09-05_memory_estimator_qualification_protocol.md` section by
section and must not be edited. It qualifies an instrument and claims nothing
about memory. Scored on the recorded 60-run grid it returned *insufficient
support*: 0 of 60 runs measurable
([result](../../analysis/2026-09-06_memory_estimator_qualification.md)).

Three small scripts around it run a **measurability pilot** — a search for
settings the frozen estimator can measure at all, before any confirmatory grid
is registered. They add no statistic and change no gate.

- `../../tests/halo/memory_pilot_grid.sh` runs one *arm* (one particle count and
  epoch length) over a set of self-gravity values at three seeds. It passes every
  flag as its own argv word, and then re-reads each finished run's recorded
  `params` and aborts if the seed, particle count, epoch length or epoch count is
  not the one asked for. That gate exists because the runner matches flags by
  prefix: a whole flag string passed through one shell variable arrives as a
  single argument in zsh, only its first flag is read, and every other flag
  silently falls back to its default while the run reports success.
- `memory_pilot_manifest.py` writes the input manifest the frozen scorer checks
  with `--manifest`. It is a self-attestation written between recording and
  scoring, not an independent preservation audit.
- `memory_pilot_report.py` reads the frozen scorer's own result documents and
  prints the measurability diagnostic per run — eligible epochs, per-gate refusal
  counts, the two run-level gates, the seed null values, and the median template
  correlation, participation ratio and block mass. It computes nothing new, so it
  cannot change a verdict.

An arm needs its own output directory: the frozen scorer keys a condition on
(preset, self-gravity, gain/loss) alone, and the run harness leaves epoch length
out of the file name, so two arms sharing a self-gravity value would collide on
the file name and then merge into a group the scorer skips.

```bash
OUT=../../data/results/halo/memory_pilot/<arm> N=4194304 EPOCHLEN=10 EPOCHS=24 \
  PRESET=spinchladni SGS="0.3 0.4 0.5" GLS="0" SEEDS="777 12345 31337" \
  bash ../../tests/halo/memory_pilot_grid.sh
python3 memory_pilot_manifest.py ../../data/results/halo/memory_pilot/<arm> <arm>-manifest.json
python3 memory_estimator_qualify.py --input-dir ../../data/results/halo/memory_pilot/<arm> \
  --manifest <arm>-manifest.json \
  --synthetic-json ../../data/results/halo/memory_estimator_qualification/synthetic.json \
  --output <arm>.json
python3 memory_pilot_report.py <arm>.json
```

## choreography/ — a four-charge choreography with a stability certificate

`choreo4.py` searches for a periodic four-charge orbit in a magnetic field
(Boris step, exact tangent map, Newton shooting, Floquet multipliers, a
million-cycle run). `final_spec.txt` records that no non-planar orbit exists
under the original specification (proved and witnessed); `final_extension.txt`
records the orbit that does exist once an axial spring is added: all 24
Floquet multipliers on the unit circle, drift 7e-5 over a million cycles.

```bash
pip install numpy numba
python3 choreography/choreo4.py --quick --N 128     # ~35 s, every layer except the million-cycle run
python3 choreography/choreo4.py --N 256             # ~95 s, the specification as written
python3 choreography/choreo4.py --N 256 --kz 1.0    # ~95 s, the extension (axial spring)
```
