<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# HELIOS BRIDGE
### Nested Resonance Memory Archive

The **HELIOS BRIDGE** is a high-fidelity visualization interface for the DUALITY-ZERO project. It renders the "Nested Resonance Memory" (NRM) system, visualizing the interaction of 1,000,000 particles driven by transcendental number sequences (φ, e, π) and prime harmonics.

## 🎛 User Manual

### Global Controls
The main dashboard provides high-level control over the simulation physics and rendering engine.

| Control | Description |
| :--- | :--- |
| **Phase Duration (Speed)** | Controls the simulation time step. `FAST` (16ms) is real-time. `SLOW` (3s) allows detailed observation of particle flow. |
| **Existence Threshold** | Controls the "Exposure" or brightness accumulation. Higher values create a "Void" effect; lower values reveal faint trails. |
| **Particle Density** | Adjusts the number of active particles (10k - 1M). Higher density requires a powerful GPU. |
| **Visual Quality** | Super-sampling factor. `1.0x` is native. `2.0x` provides ultra-sharp rendering but halves FPS. |
| **Field Amplitude** | Global force multiplier. Controls how strongly the particles react to the potential field. |

### Research Labs
The **Labs** panel offers granular control over specific force fields.

- **Crystallographic Symmetry:** Enforces geometric order (3-Fold, 6-Fold, Hexagonal Lattice).
- **Pythagorean Harmonics:** Applies musical ratios and spiral dynamics (Comma Spiral, Perfect Fifths).
- **Topological Forms:** Shapes the field into complex manifolds (Trefoil Knot, Toroidal Attractor).

> **Note:** These effects can be mixed. Dragging a slider > 0% activates that force.

### Reset Controls
- **Green Reset (Rotate):** **Reset Particles**. Re-initializes particle positions to the starting grid without changing settings. Use this if the simulation becomes too chaotic or "explodes".
- **Red Reset (Rotate):** **Reset Defaults**. Resets all sliders in the current panel to their default values.

---

## 👨‍💻 Developer Guide

### Adding New Presets
Presets allow users to instantly load a specific configuration of sliders and settings. They are defined in `components/UIComponents.tsx`.

#### Step 1: Locate the Dropdown
Open `HELIOS-BRIDGE/components/UIComponents.tsx` and search for `Quick Load Presets`. You will find a `<select>` element.

#### Step 2: Add an Option
Add a new `<option>` tag inside the `<select>`:
```tsx
<option value="my_new_preset">My New Preset Name</option>
```

#### Step 3: Define the Logic
In the `onChange` handler of the `<select>`, add an `else if` block for your new value:

```tsx
} else if (e.target.value === 'my_new_preset') {
  setConfig(c => ({
    ...c,
    // Global Settings (Optional)
    speed: 5,              // 5 = 200ms (1000/200)
    exposure: 1.5,
    particleCount: 500000,
    
    // Lab Extensions
    extensions: {
      crystal: { threeFold: 0.5, sixFold: 0, lattice: 0 },   // 0.0 - 1.0
      harmonic: { commaSpiral: 0, perfectFifths: 0.8, equalTemp: 0 },
      topology: { trefoil: 0, torus: 0, hopf: 0 }
    }
  }));
}
```

### Tuning Physics
The physics engine is located in `components/ParticleSystem.tsx`.
- **Force Calculations:** Forces are calculated in the main loop.
- **Optimization:** Force coefficients (`getStrength`) are pre-calculated outside the loop for performance.
- **Infinity Tail:** Effects use an exponential curve (`val^4 * 20`) to allow fine control at low values and massive power at 100%.

## 🚀 Run Locally

1. **Install dependencies:**
   ```bash
   npm install
   ```
2. **Run the app:**
   ```bash
   npm run dev
   ```
3. **Build for production:**
   ```bash
   npm run build
   ```
