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
