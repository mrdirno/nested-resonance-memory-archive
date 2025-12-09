# META OBJECTIVES: HELIOS 3D ENGINE (SUNFIRE)

## MISSION
Build a **Native macOS Fabrication Engine** that bridges the gap between **AI Perception** (Video Tracking) and **Mathematical Creation** (SDF/Gyroids).

## ARCHITECTURE
- **Platform:** macOS Silicon (M1/M2/M3).
- **Language:** Python 3.13.
- **GUI:** PySide6 (Qt).
- **Rendering:** ModernGL (OpenGL 4.1 Core).
- **AI:** 
    - **Local:** PyTorch (MPS) + Meta SAM 2 (Masking).
    - **Remote/Meta:** Gemini CLI (Vision/Depth Reasoning).
- **Math:** NumPy + Scikit-Image (Marching Cubes).

## ROLES (SEPARATION OF CONCERNS)
### 1. THE PILOT (MOG/Gemini)
- **Responsibility:** Strategy, Architecture, **Active Vision Analysis**.
- **Domain:** `MOG_CYCLE_LOG.md`, `README.md`, `src/ui/`.
- **Action:** Inspects video frames, determines 3D structure, feeds parameters to the Co-Pilot.

### 2. THE CO-PILOT (The Engine)
- **Responsibility:** Heavy Compute, Math, AI Inference, File I/O.
- **Domain:** `src/core/`, `src/render/`, `assets/`.
- **Action:** Executes `segmentation.py` (SAM 2) and `reconstruction.py` (Voxels) based on Pilot's guidance.

## OPERATIONAL PROTOCOLS
1.  **The Hybrid Strategy:**
    *   AI is for **Perception** (Masking).
    *   Math is for **Generation** (Meshing).
    *   **Gemini is the Depth Sensor:** We use LLM Vision to understand shape semantics (e.g., "It's concave") which standard Visual Hull misses.
2.  **The Visual Loop:**
    *   User Clicks -> Mask Appears (Immediate Feedback).
    *   User Reconstructs -> Mesh Appears (Asynchronous).
3.  **Hygiene:**
    *   No legacy artifacts (Swift/Package.swift).
    *   No loose scripts in root.
    *   All heavy assets in `assets/`.

## CURRENT PHASE: PHASE 10 (GEMINI VISION BRIDGE)
**Objective:** Integrate Gemini Vision as the high-level semantic depth sensor.

**Pipeline:**
1.  **Input:** `VideoPlayer` extracts keyframes.
2.  **Bridge:** `VisionBridge` collates frames into a "Contact Sheet".
3.  **Analysis:** User/System prompts Gemini: "Analyze this object's structure."
4.  **Feedback:** Gemini returns parameters (Scale, Taper, Concavity).
5.  **Output:** Helios adjusts the Voxel Reconstruction logic.

## ROADMAP
- [x] Phase 1-5: Foundation, UI, Video, AI.
- [x] Phase 6: Interactive Masking.
- [x] Phase 7: Full 3D Reconstruction.
- [x] Phase 8: Gyroid Infusion.
- [x] Phase 9: Boolean Operations.
- [ ] Phase 10: Gemini Vision Integration.