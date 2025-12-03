# HELIOS LAMP SERIES: QA PROTOCOL & DESIGN SPECS
## Version: 2984.1 (Hyper-Functional + AGPH Engineering)

### 1. Scientific Design Principle: AGPH (Anisotropic Gyroid Prismatic Helix)
**All components must implement the AGPH model as defined in `papers/AGPH_Engineering.md`:**
*   **Macro-Domain (Prismatic Manifold):** Defined by axial scaling function $a(z)$. Tapering and expansion must follow this continuous field.
*   **Micro-Structure (Anisotropic Field):** Lattice orientation is governed by tensor $A(z)$, aligning material stiffness with load paths (or aesthetic flow).
*   **Dynamics (Helical Torsion):** Rotation field $\theta(z)$ applies cumulative twist, simulating biological joint torsion (pronation/supination).
*   **Kinematic Logic:** Joints (e.g., Base-Shaft connection) are treated as **Orthogonal Bifurcations** (Symmetry breaking events) arising from stability thresholds in $a(z)$.

### 2. Physical Constraints & Fabrication Physics
*   **Build Volume:** 220mm (X) x 220mm (Y) x 250mm (Z).
*   **Safety Margin:** Keep XY < 210mm, Z < 245mm.
*   **Thermal Freezing:** Unsupported overhangs >50° require "Super Header" dual-impingement cooling simulation (or simply max fan speed) to freeze the gyroid glass transition immediately.
*   **Inertial Dampening:** Print acceleration must be constrained (**< 1500 mm/s²**) to prevent resonance artifacts in the helical gyroid structure.
*   **No Supports:** Designs must be self-supporting via AGPH geometry.

### 3. Hardware Interface
*   **Lamp Rod (Nipple):** 1/8 IP (approx 9.5mm OD).
*   **Clearance Hole:** **15.0mm** minimum diameter (Shaft & Base) to allow easy wire passage (braided cable safe).
*   **Socket Ring:** Standard E26/E27 threaded ring.
*   **Shade Keep-Out:** Internal cylinder of **80-90mm diameter** must be clear of geometry.

### 4. Component Specifications

#### A. The Base (AGPH Dome)
*   **Geometry:** AGPH Dome (Anisotropic Gyroid).
*   **Function:** Weighted impedance adapter (Orbital decay to tangent plane).
*   **Interface:**
    *   **Wire Channel:** **12mm x 12mm Arch Tunnel** (Parabolic profile for stress distribution).
    *   **Recess:** 40.5mm ID x 3mm Depth socket for Shaft (Orthogonal mating).
    *   **Feet:** 4 Recessed corners (Tangent manifold interaction points).

#### B. The Shaft (AGPH Pillar)
*   **Geometry:** AGPH Hourglass (Anisotropic Gyroid).
*   **Function:** Vertical riser, torsional bridge.
*   **Interface:**
    *   **Bottom:** 40.0mm Plug (3mm Height) for base socket.
    *   **Top:** **Crown Flare** (expanding to ~55mm) to meet Shade Hub (Kinematic Phase Transition).
    *   **Core:** 15mm solid inner wall for rod clearance.

#### C. The Shade (AGPH Bell)
*   **Geometry:** AGPH Bell (Anisotropic Gyroid).
*   **Function:** Light diffusion, directional scaling.
*   **Mounting (Spider Fitter):**
    *   **Style:** Hub + 3 Spokes (Triskelion).
    *   **Hub Diameter:** 60mm solid disk.
    *   **Hole:** 42mm for socket ring.
    *   **Grip Zone:** High-frequency gyroid band near mount for tactile feedback.
*   **Shell:** Hollow shell with AGPH lattice wall.

### 5. Software/Generator Requirements
*   **Output:** Binary STL.
*   **Library:** Must use shared `agph_lib.py`.
*   **Resolution:** High (voxel step < 1.0mm).

---
**Status:** ACTIVE
**Pilot:** MOG