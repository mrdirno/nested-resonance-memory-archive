# HELIOS-BRIDGE ARCHIVE — 500 visual studies

Author: Aldrin Payopay · GPL-3.0-only

[Open the gallery](index.html) or [enter HALO Observatory](HELIOS-V501-halo-resonance-chamber.html). The 500 generated studies are a preserved creative collection; HALO V501 is the active instrument, with its own equations, controls and [browser tests](../tests/halo/README.md). Scientific-sounding field names in the older studies are visual labels and do not certify physical fidelity.

## Nested Resonance Memory Archive × Persona500 LLC

500 self-contained particle visualization variations, each a unique combination of chromatic palette, mathematical sequences, force field physics, particle behavior, and UI theme.

### Architecture

The pages have no build step. They load Three.js and fonts from external CDNs, so they are not an offline bundle. Browser and GPU compatibility varies; this pass does not claim fresh runtime verification of all 500 studies.

### Variation Space

| Axis | Count | What It Controls |
|------|-------|-----------------|
| **Color Palettes** | 50 | Primary, secondary, accent colors, background, glass panel tint |
| **Mathematical Sequences** | 10 | Transcendental number digit streams driving the potential field (Pi/E/Phi, Sqrt series, Primes, Fibonacci, Catalan, Euler-Mascheroni, Ln series, Apery/Plastic/Omega, Champernowne, Feigenbaum) |
| **Force Fields** | 10 | The `getPotential()` GLSL function — determines particle motion patterns (Interference, Gravitational, Vortex, Crystalline, Wave, Magnetic, Fluid, Quantum, Fractal, Toroidal) |
| **Particle Behaviors** | 10 | Lifecycle (decay rate, respawn pattern, damping, force scale, particle size) |
| **UI Themes** | 10 | Font families, border radius, panel width, visual style |

**Total unique combinations:** 50 × 10 × 10 × 10 × 10 = 500,000 possible. This archive contains 500 curated selections.

### Force Field Types

| Field | Modes | Physics |
|-------|-------|---------|
| **Interference** | Interference · Lattice · Chaos | Cosine product standing waves |
| **Gravitational** | Gravity Well · Orbital · Tidal | Inverse-square radial fields |
| **Vortex** | Spiral · Cyclone · Maelstrom | Angular momentum + cylindrical symmetry |
| **Crystalline** | FCC · BCC · Diamond | Periodic lattice potentials |
| **Wave** | Plane Wave · Circular · Spherical | Propagating wave equations |
| **Magnetic** | Dipole · Quadrupole · Flux Tube | Multipole magnetic field approximations |
| **Fluid** | Laminar · Turbulent · Convection | Navier-Stokes-inspired flow fields |
| **Quantum** | S-Orbital · P-Orbital · D-Orbital | Hydrogen-like orbital probability densities |
| **Fractal** | IFS · Strange · Animated | Iterated function system attractors |
| **Toroidal** | Torus · Helical · Knot | Toroidal coordinate potential fields |

### Controls (Every Variation)

- **Particle Density**: Low (260k) / High (1M) / Ultra (4M)
- **Entropy (Curl Noise)**: Turbulence injection strength
- **Metabolism Rate**: Particle lifecycle speed
- **Orthogonal Stagger**: Sequence offset between XYZ axes
- **Archive Flux**: Speed of traversal through digit sequences
- **Mode Buttons**: Three physics modes per force field type
- **Touch**: 1-finger orbit, 2-finger pan + pinch zoom, double-tap reset

### Generation and preservation

[`generate_500_variations.mjs`](../generate_500_variations.mjs) is the programmatic source of the variation collection. It writes HTML into this directory; rerunning it can replace hand-edited archive pages and the gallery. Preserve this snapshot and review generated differences before publication. The dimensions of the variation space describe configuration possibilities, not experimental coverage.

### File Naming Convention

```
HELIOS-V{NNN}-{palette}-{forcefield}.html
```

Example: `HELIOS-V042-obsidian-interference.html`

### Quick Start

Open `index.html` for the full gallery with all 500 variations, or open any individual HTML file directly.

### Beyond the 500 — V501 · HALO Observatory

[HALO](HELIOS-V501-halo-resonance-chamber.html) uses a fixed 0.05-second tick, spherical-cavity modes, particle-mesh gravity and Lab instruments. **Observe** starts seeded A/B experiments that change only the magnetic integrator, with exact tick stops and replayable JSON records. The [observation contract](../docs/halo/OBSERVATORY.md) explains sampling, GPU precision and interpretation limits.

The existing Retained/Two-back readouts have a spatial-support confound. They remain footprint diagnostics, not a validated memory test; the [60-run estimator audit](../analysis/2026-09-02_cross_epoch_memory_preregistered.md) records why. No NRM result follows from a visually persistent shape.

HALO is the [site front page](https://mrdirno.github.io/nested-resonance-memory-archive/). The [classic Bridge](https://mrdirno.github.io/nested-resonance-memory-archive/archive/classic/) retains its own address and receives compatibility and dependency fixes. Historical ring records remain inside the HALO source.
