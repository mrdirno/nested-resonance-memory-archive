# Web Visualizations

Interactive, browser-based visualizations. Each file is self-contained
(single HTML file, no build step); the only external dependencies are
three.js and fonts, pinned from public CDNs.

## resonance_chamber.html

**Resonance Chamber** — a GPU particle simulation of standing-wave
eigenmodes in a cubic cavity, with mode numbers sequenced by the digits of
mathematical constants (π, e, √2, φ). Open the file directly in any
browser with WebGL support.

### The model

- Field: the exact eigenmodes of a spherical cavity of radius `R`,
  `Ψ = jₗ(zₗₙ·r/R)·Pₗᵐ(cosθ)·cos(mφ − ωt)` — spherical Bessel × associated
  Legendre × azimuthal, with quantum numbers `(n, l, m)` (the same labels
  as electron orbitals and stellar oscillation modes) and mode energy
  `z²ₗₙ`. Radial profiles are computed on the CPU by Miller's stable
  downward recurrence (validated against mpmath: zeros < 4e-15 abs,
  values < 2e-16) and streamed to the GPU as a lookup texture; angular
  parts are evaluated per particle in the shader by Schmidt-normalized
  Legendre recurrences (< 5e-16 rel). Optional azimuthal precession ω
  rotates the mode.
- Two field forms:
  - **Chladni nodes** (default): two degenerate azimuthal orders
    (`m` and `l−m`) of the same `(n, l)` shell are superposed; dynamics
    descend `∇S²`, driving particles onto the curved 2-D nodal surface
    `S = 0` — sand-on-a-plate physics in a volume, structure drawn by the
    *absence* of field (total destructive interference).
  - **Potential wells**: `a = −A·∇Ψ` on the single `(n, l, m)` eigenmode.
- Cosmology layer: a Hubble term (outward acceleration ∝ radius, so
  damping yields `v ≈ H·r`), periodic **epoch zoom-outs** (the frame
  rescales by ½; identical equations each epoch, inherited structure
  persisting as relics across scales), magnetic Lorentz coupling
  (background axial field plus per-center dipoles that flip with the
  pole), and a choice of boundary topology: reflecting wall, or
  **antipodal identification** — leaving through a point of the sphere
  re-enters at its antipode, the construction that makes elliptic space
  finite yet edgeless.
- Reverberation: blast shells echo — in reflect mode from the shell's
  acoustic image source outside the sphere (the image-source method of
  room acoustics), in no-edge mode by refocusing near the antipode of the
  origin, as waves do in closed spaces; two generations at 65% strength.
- Scenarios: five one-click experiment presets (Formation, Chladni study,
  Orbitals, Magnetized, Closed universe) that restart the universe clocks
  deterministically while keeping hardware-facing settings.
- Sonification (opt-in): digit steps play their mode's eigenfrequency and
  detonations land a low thump, via WebAudio behind a user gesture.
- Lineage: centers drift under mutual softened gravity, so hierarchical
  infall and mergers occur. A coalescence crosses over heritable traits
  (swirl handedness, magnetic polarity) digit-deterministically, raises
  the lineage generation, keeps the progenitor core visibly embedded in
  the remnant, and radiates a chirp burst. Each epoch zoom-out, the
  heaviest survivor seeds a mirrored, digit-mutated daughter at its
  antipode (selection + replication + variation); passing blast fronts
  flip an accreting center's swirl and hasten its collapse
  (shock-triggered formation analogue). Merger and generation stats are
  shown in the Overlays panel.
- Collapse centers (feedback cycle, on by default): up to eight softened
  point attractors (Plummer potentials with a tangential inflow term and a
  Gaussian-tapered region of influence) whose spawn positions and masses
  are drawn from the digit stream rather than a random generator. Mass
  sets both strength and lifespan; at end of life the pole flips and a
  traveling spherical blast shell launches, expanding at constant speed
  with amplitude decaying as it spreads. Shells sweep through other
  centers' territory, so standing field, collapses, and traveling waves
  feed back on one another. Growth is modeled by age (not measured
  accretion), and centers are external potentials, not self-gravitating
  masses.
- Dynamics: gradients evaluated analytically, semi-implicit Euler
  integration, exponential velocity damping, and reflecting box walls.
  Integration is frame-rate independent, and digit transitions morph the
  field over the first quarter of each step so pure-eigenmode structure
  has time to form.
- Sequencing: each axis reads successive digits of its assigned constant
  (2,500 decimal digits per constant, verified against mpmath at
  2,620-digit precision). Prime-number strides decorrelate the three
  streams. Consecutive digit states are smoothly blended so the field
  morphs rather than jumps.
- Number bases: expansions in bases 2–16 are recomputed exactly from the
  decimal data with BigInt arithmetic; digit counts are truncated to the
  information actually carried by the source precision, and digits are
  normalized to a common mode range so behavior is comparable across bases.

### Implementation

The physics runs entirely on the GPU: particle positions and velocities
live in ping-pong floating-point textures updated by fragment shader
passes, and the point cloud reads positions directly from those textures
in the vertex shader. This sustains up to 1,000,000 particles at
interactive frame rates. Settings persist in `localStorage`; the page
degrades gracefully (with an explanatory message) when float render
targets are unavailable.

This file supersedes the earlier CPU-based prototype
(`transcendental static` visualization): the rewrite replaced
finite-difference forces with analytic gradients, moved integration off
the main thread onto the GPU, fixed the base-conversion arithmetic, made
the integrator frame-rate independent, and reworked the interface. Note
that √2 and φ are algebraic irrationals, not transcendental numbers; the
interface labels each constant accordingly.
