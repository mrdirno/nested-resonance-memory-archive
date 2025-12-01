# LAMP SERIES 01: THE EVENT HORIZON
# DESIGN 2/10

**Status:** In Development
**Theme:** "Heavy, cosmic, consuming."

## 📦 Parts List (Printed)

1.  **Shade (`event_horizon_shade.stl`)**
    *   *Description:* Spherical/Dome shade with Schwarz D (Diamond) surface structure.
    *   *Dims:* Diameter 160mm, Height 140mm.
    *   *Mount:* 42mm Hole (Top) for E26/E27 socket ring.
    *   *Print Settings:* 0% Infill, 3 Walls.

2.  **Shaft (`event_horizon_shaft.stl`)**
    *   *Description:* Distorted pillar, gravitational lensing effect (bulging helix).
    *   *Dims:* Height 180mm, Diameter 35mm (Max bulge), Core ID 10mm.
    *   *Print Settings:* 20% Infill.

3.  **Base (`event_horizon_base.stl`)**
    *   *Description:* Accretion disk. Swirling, flattened torus shape.
    *   *Dims:* Diameter 140mm, Height 30mm.
    *   *Features:* 15mm Socket for Shaft, 6mm Wire Channel.
    *   *Print Settings:* High Infill (Ballast recommended).

## 🛠️ Hardware (Standard)

*   Threaded Rod: M10 / 1/8 IP.
*   Socket: E26/E27.
*   Cord: Standard Lamp Cord.

## 🔧 Assembly

Same as Redshift.
1.  Threaded rod into Base.
2.  Shaft over rod.
3.  Socket on top.
4.  Shade clamped by socket ring.

## 📐 Source Code

*   `event_horizon_shade_gen.py`: Schwarz D implementation.
*   `event_horizon_base_gen.py`: Spiral implementation.
*   `event_horizon_shaft_gen.py`: Bulging helix.
