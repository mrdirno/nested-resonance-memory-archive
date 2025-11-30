# Creative Fabrication Experiments

This directory stores the outputs of creative "data physicalization" experiments.

## Principle Card Tokens
We generate physical tokens where the surface topography is determined by the validation statistics of the Principle Card.

### PC001 Token
*   **Source:** `principle_cards/pc001_specification.json`
*   **Algorithm:** `fabrication/generators/pc_token_gen.py`
*   **Logic:**
    *   **Base:** 20mm Cylinder.
    *   **Surface:** Radial wave pattern.
    *   **Amplitude:** Controlled by `std_population` (Volatility).
    *   **Offset:** Controlled by `mean_population`.
*   **Result:** `fabrication/output/pc001_token.stl`

### Helios Resonance Sample (The Invisible Made Visible)
*   **Concept:** A physicalization of the "Orthogonal Sum Dynamics" (OSD) field. It represents the standing-wave interference patterns used by Helios to trap matter.
*   **Algorithm:** `fabrication/generators/helios_field_gen.py`
*   **Geometry:** A voxelized Gyroid Isosurface.
    *   **Equation:** `sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = 0`
    *   This structure is naturally self-supporting (printable without internal infill) and represents a "Zero-Sum" energy state where constructive and destructive interference balance out.
*   **Result:** `fabrication/output/helios_resonance_sample_01.stl`

## Usage
To generate a new token:
```bash
python3 fabrication/generators/pc_token_gen.py <path_to_pc.json> <output.stl>
```
