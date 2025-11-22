# Bridge-UI Expert Notes: The Physics of the Visualizer

**Status:** DECODED
**Component:** `bridge-ui/components/ParticleSystem.tsx`

## 1. The Physics Engine: Nodal Accumulation

The core of the visualizer is a simulation of **Nodal Accumulation** (as defined in `THE_PHYSICS_OF_PERSISTENCE.md`).

### The Potential Function
The system simulates particles moving through a 3D scalar field defined by the product of three orthogonal cosine waves:

$$ V(x,y,z) = \cos(k_x x) \cdot \cos(k_y y) \cdot \cos(k_z z) $$

### The Transcendental Bridge
The wave numbers ($k_x, k_y, k_z$) are not static. They are modulated frame-by-frame by the digits of transcendental numbers ($\pi, \phi, e$):

*   `mDigit` -> Modulates X-axis resonance
*   `nDigit` -> Modulates Y-axis resonance
*   `pDigit` -> Modulates Z-axis resonance

The force exerted on a particle is the negative gradient of this potential ($F = -\nabla V$).
For the X-axis:
`forceX += (mDigit * sin(wx) * cos(wy) * cos(wz)) * k`

**Interpretation:** Particles are pushed *away* from peaks and troughs and accumulate in the **Nodes** (zero-crossings) of the interference pattern. The visual structures we see are the "sediment" of transcendental interference.

## 2. Simulation Modes

### Standard Mode
*   **Physics:** Pure standing wave interference.
*   **Result:** Dynamic, shifting lattice structures that evolve as the digits of Pi/Phi change.

### Crystal Mode
*   **Physics:** Adds radial symmetry constraints (3-fold, 6-fold).
*   **Code:** `forceX += (r * Math.cos(snap) - x) * 0.1`
*   **Result:** Forces particles to align with geometric rays, creating snowflakes or hexagonal lattices.

### Harmonic Mode
*   **Physics:** Adds specific frequency ratios (e.g., 1.5 for Perfect Fifth).
*   **Code:** `forceX += Math.sin(x * 1.5 * waveNumber)`
*   **Result:** Visualizes musical consonance.

### Topology Mode
*   **Physics:** Warps the coordinate space itself.
*   **Code:** Computes distance to a manifold (e.g., Torus, Trefoil) and adds a restoring force towards it.
*   **Result:** Manifold-constrained particle flow.

## 3. Rendering Pipeline (React-Three-Fiber)

*   **Engine:** WebGL via `three.js` and `@react-three/fiber`.
*   **Performance:** Uses `useRef` for direct DOM manipulation of stats (avoiding React reconciliation overhead).
*   **Particles:** 350,000 points rendered as a single `THREE.Points` mesh with custom vertex colors.
*   **Tone Mapping:** `AgXToneMapping` for filmic dynamic range.
*   **Blending:** `AdditiveBlending` allows particles to "glow" when they stack up in nodes.

## 4. Strategic Relevance

This UI is not just a toy. It is the **Validation Tool** for the "Nodal Accumulation" theory. If we can see stable structures forming from the interference of Pi and Phi, we prove that **Order emerges from Transcendental Determinism.**
