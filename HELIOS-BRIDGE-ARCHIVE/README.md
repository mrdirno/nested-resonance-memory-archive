# HELIOS-BRIDGE ARCHIVE — 500 Variations

## Nested Resonance Memory Archive × Persona500 LLC

500 self-contained particle visualization variations, each a unique combination of chromatic palette, mathematical sequences, force field physics, particle behavior, and UI theme.

### Architecture

Every HTML file is **fully self-contained** — zero build step, zero dependencies beyond Three.js CDN. Open any file in a browser and it runs.

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

### Generation Pipeline

| Tier | Model | Role | Cost |
|------|-------|------|------|
| **Tier 1** | Programmatic (DeepSeek-equivalent) | Bulk generation of 500 variations | $0.00 |
| **Tier 2** | Sonnet 4.6 | GLSL shader validation, syntax verification | ~$0.02 |
| **Tier 3** | Opus 4.6 | Final UI polish, archive integration, documentation | Session cost |

### File Naming Convention

```
HELIOS-V{NNN}-{palette}-{forcefield}.html
```

Example: `HELIOS-V042-obsidian-interference.html`

### Quick Start

Open `index.html` for the full gallery with all 500 variations, or open any individual HTML file directly.

### Beyond the 500 — V501 · HALO

`HELIOS-V501-halo-resonance-chamber.html` is not a point in the 5-axis variation space above. It is the Resonance
Chamber at Ring 9 (code name HALO): a GPU particle laboratory in a spherical cavity whose eigenmodes are sequenced
by the digits of π, e, √2 and φ, with self-gravity, an expanding background, a magnetic term stepped either as Euler
(how every preset was found) or as the exact Boris rotation, and a Lab (press 7) that measures the chamber against
its own claims — Lyapunov exponent, cross-epoch memory beside its two-back control, realized spectrum, force-ceiling
share. Rings 1–12 are sealed in a comment at the end of the file. Self-contained: three.js from cdnjs, no build.

HALO is now the site's front page: https://mrdirno.github.io/nested-resonance-memory-archive/ opens it. The classic bridge, the
visualizer that came before it, lives at `archive/classic/` on the published site
(https://mrdirno.github.io/nested-resonance-memory-archive/archive/classic/), kept as it ran, at its own address.
