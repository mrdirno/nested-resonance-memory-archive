# Ender 3 (Klipper) - Print Tuning Notes

**Date:** 2025-11-30
**Issue:** Stringing (Thin wisps of plastic between print features)
**Artifact Context:** TPMS Gyroid Lattices (e.g., Artifacts 01, 02, 03)

---

## Diagnosis & Tuning Recommendations for Stringing

Stringing is often caused by plastic oozing from the nozzle during travel moves. Gyroid lattices are particularly susceptible due to the high number of retractions over open space.

### 1. Retraction Distance (Most Common Cause)

*   **Problem:** Insufficient retraction allows molten plastic to ooze. Excessive retraction can lead to clogs.
*   **Current Profile Baseline (Estimated):** 4mm to 5mm (typical for Bowden).
*   **Recommendation (Bowden):**
    *   Start with **5mm**.
    *   Adjust in **1mm** increments (e.g., try 6mm, but rarely exceed 7mm).
*   **Recommendation (Direct Drive):**
    *   Start with **0.8mm**.
    *   Adjust in **0.2mm** increments.

### 2. Retraction Speed

*   **Problem:** If too fast, it can create a vacuum that pulls air/material into the hotend, leading to clogs. If too slow, plastic oozes.
*   **Current Profile Baseline (Estimated):** 60mm/s.
*   **Recommendation:**
    *   **Decrease** retraction speed to **45mm/s - 50mm/s**. For Bowden setups, a slightly slower retraction can sometimes be more effective at relieving pressure without grinding filament.

### 3. Print Temperature

*   **Problem:** Printing too hot makes the plastic more liquid and prone to oozing.
*   **Current Profile Baseline (Estimated):** 200°C - 210°C for Generic PLA.
*   **Recommendation:**
    *   **Decrease** print temperature by **5°C to 10°C**. For PLA, try **195°C to 200°C**. Lower temp increases viscosity, reducing ooze.

### 4. Z-Hop (Avoid for Lattices)

*   **Problem:** Lifting the nozzle during retraction (`Z-Hop`) can increase travel time, giving plastic more time to ooze. It also adds unnecessary vertical movement for complex lattices.
*   **Recommendation:**
    *   Ensure **Z-Hop is OFF** (0.0mm). Only enable if the nozzle is colliding with the print (which Gyroids are prone to, but Z-hop often makes stringing worse).

### 5. Advanced Klipper Tuning (Pressure Advance)

*   **Feature:** Klipper's **Pressure Advance** compensates for pressure lag in the Bowden tube.
*   **Impact:** Significantly reduces stringing at corners and end-of-lines.
*   **Action:** Calibrate Pressure Advance using the standard Klipper square tower test. Typically `0.4 - 0.6` for Bowden Ender 3.

---

**Attribution:**
Research synthesized from community knowledge bases including:
*   **All3DP** (Retraction/Stringing Guides)
*   **Klipper Documentation** (Pressure Advance/Firmware Retraction)
*   **Obico** (Ender 3 Stringing Solutions)
*   **Reddit r/3Dprinting & r/Ender3** (Community consensus on Bowden retraction limits)

**Next Steps for Tuning:**
*   Start with **Retraction Distance** adjustments.
*   If stringing persists, try **Retraction Speed**.
*   Finally, adjust **Temperature**.
*   **Always change one setting at a time** and print a small test to isolate the effect.