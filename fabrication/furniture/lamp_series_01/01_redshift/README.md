# LAMP SERIES 01: THE REDSHIFT

**Status:** Prototype Generated
**Theme:** "Energy expanding into the void."

## 📦 Parts List (Printed)

1.  **Shade (`redshift_shade.stl`)**
    *   *Description:* Anisotropic Gyroid Frustum.
    *   *Dims:* Base 180mm, Top 60mm, Height 150mm.
    *   *Mount:* 42mm Hole (Top) for E26/E27 socket ring.
    *   *Print Settings:* 0% Infill (Gyroid IS structure), 3 Walls, No Top/Bottom layers (optional, for transparency).

2.  **Shaft (`redshift_shaft.stl`)**
    *   *Description:* Helical wrapper around central core.
    *   *Dims:* Height 200mm, Diameter 30mm (Helix), Core ID 10mm (Rod).
    *   *Print Settings:* 15-20% Infill, 3 Walls.

3.  **Base (`redshift_base.stl`)**
    *   *Description:* Weighted anchor block with wire channel.
    *   *Dims:* 120mm x 120mm x 30mm.
    *   *Features:* 15mm Socket for Shaft, 6mm Wire Channel at bottom.
    *   *Print Settings:* 20-40% Infill (or 0% + Sand fill), 4 Walls.

## 🛠️ Hardware (Amazon)

*   **Threaded Rod:** M10 or 3/8" Lamp Pipe (Length > 380mm).
*   **Nuts/Washers:** M10 or 3/8" (x4).
*   **Socket:** E26/E27 Threaded Socket with Shade Ring.
*   **Cord:** Lamp Cord with Switch.

## 🔧 Assembly

1.  **Base Preparation:**
    *   *Note:* The current `redshift_base.stl` is solid. For stability, print with high infill (40%+) or pause print to add sand.
    *   *Feet:* Stick 4x Rubber feet (min 5mm height) to corners to clear the bottom nut and allow wire exit.
2.  **Base:** Insert threaded rod into Base. Secure with nut/washer from *bottom*.
3.  **Shaft:** Slide Shaft over rod. Sit it in the Base socket.
4.  **Wiring:** Run wire up through the hollow rod.
5.  **Socket:** Screw socket cap onto rod at top of Shaft.
6.  **Shade:** Place Shade onto Socket.
7.  **Secure:** Screw Shade Ring onto Socket from inside the Shade to clamp the Shade's top plate.
8.  **Bulb:** Install LED Bulb (9W Max).

## 📐 Source Code & Updates
*   `redshift_shade_gen.py` (V2: Thick 1-inch walls, Solid Top).
*   `redshift_shaft_gen.py`
*   `redshift_base_gen.py`

**Future Improvements (Protocol Compliance):**
*   [ ] Add dedicated "Ballast Chamber" to base generator.
*   [ ] Add printed "Feet" or recessed nut trap to base generator.
