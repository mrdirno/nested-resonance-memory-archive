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

- Field: `Ψ(r) = cos(m·k·x + φₘ)·cos(n·k·y + φₙ)·cos(p·k·z + φₚ)`, with
  `k = π/L` — the separable standing-wave form whose integer mode numbers
  `(m, n, p)` also label particle-in-a-box eigenstates and 3-D Chladni
  nodal patterns.
- Two field forms:
  - **Chladni nodes** (default): the three cyclic permutations of
    `(m, n, p)` are degenerate eigenmodes (equal energy `m²+n²+p²`), so
    their superposition `S = ψ(m,n,p) − ψ(p,m,n) + ψ(n,p,m)` is itself an
    exact eigenmode. Dynamics descend `∇S²`, driving particles onto the
    curved 2-D surface `S = 0` — the three-dimensional analogue of sand
    collecting on the nodal lines of a vibrating plate, i.e. structure
    drawn by the *absence* of field (total destructive interference).
  - **Potential wells**: `a = −A·∇Ψ` on the single product mode, so
    particles collect at field minima.
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
