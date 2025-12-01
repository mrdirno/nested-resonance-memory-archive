# Fabrication Report: Helios Anisotropic Prism (Giza Frustum)

**Date:** 2025-12-01
**Artifact:** `helios_giza_frustum_2inch_top.stl`

## 1. Request Analysis
*   **Goal:** Create a Gyroid structure with Giza-pyramid proportions at the base, tapering to a 2-inch (50.8mm) square top.
*   **Constraint:** High resolution for smooth gyroid gradients.

## 2. Artifact Specifications

### High Resolution Version (Recommended for Quality)
*   **Filename:** `helios_giza_frustum_2inch_top.stl`
*   **Resolution:** 200 voxels (approx 0.9mm voxel size)
*   **Triangle Count:** 1,446,928
*   **File Size (Binary):** ~69 MB
*   **Print Time (Est):** 12-18 hours (depending on speed)

### Medium Resolution Version (Recommended for Fast Slicing)
*   **Filename:** `helios_giza_frustum_2inch_top_medium.stl`
*   **Resolution:** 150 voxels (approx 1.2mm voxel size)
*   **Triangle Count:** 816,304
*   **File Size (Binary):** ~39 MB

## 3. Validation
*   **Integrity Check:** Passed (Binary Header, Triangle Count Match, No NaN).
*   **Loading Issues:** The 69MB / 1.4M triangle count is heavy. If slicer lags, use the Medium version.

## 4. Slicing Recommendations
*   **Infill:** 0% (The gyroid IS the infill).
*   **Walls:** 3-4 perimeters.
*   **Top/Bottom Layers:** 0 (Expose the gyroid) OR Standard (Cap it). *Design has a solid rim, so capping works.*
*   **Layer Height:** 0.2mm.

## 5. Generation Command
```bash
python3 fabrication/generators/helios_anisotropic_prism_gen.py \
    fabrication/output/helios_giza_frustum_2inch_top.stl \
    180.0 180.0 0.0 120.0 200 0.01 25.4 0.0 50.8 50.8 0.0 false false
```