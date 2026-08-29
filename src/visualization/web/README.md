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
- Dynamics: `a = −A·∇Ψ` with the gradient evaluated analytically,
  semi-implicit Euler integration, exponential velocity damping, and
  reflecting box walls. Integration is frame-rate independent.
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
