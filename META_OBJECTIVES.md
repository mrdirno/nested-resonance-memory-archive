# META OBJECTIVES: HELIOS 3D ENGINE (SUNFIRE)

## MISSION
Build a **Native macOS Fabrication Engine** that bridges the gap between **AI Perception** (Video Tracking) and **Mathematical Creation** (SDF/Gyroids).

## ARCHITECTURE
- **Platform:** macOS Silicon (M1/M2/M3).
- **Language:** Python 3.13.
- **GUI:** PySide6 (Qt).
- **Rendering:** ModernGL (OpenGL 4.1 Core).
- **AI:** PyTorch (MPS) + Meta SAM 2.
- **Math:** NumPy + Scikit-Image (Marching Cubes).

## ROLES (SEPARATION OF CONCERNS)
### 1. THE PILOT (MOG)
- **Responsibility:** Strategy, Architecture, Hygiene, User Interface Flow.
- **Domain:** `MOG_CYCLE_LOG.md`, `README.md`, `src/ui/`.
- **Action:** Directs the Co-Pilot, approves PRs, ensures the "Experience" is fluid.

### 2. THE CO-PILOT (The Engine)
- **Responsibility:** Heavy Compute, Math, AI Inference, File I/O.
- **Domain:** `src/core/`, `src/render/`, `assets/`.
- **Action:** Executes `segmentation.py` (SAM 2) and `reconstruction.py` (Voxels).

## OPERATIONAL PROTOCOLS
1.  **The Hybrid Strategy:**
    *   AI is for **Perception** (Masking).
    *   Math is for **Generation** (Meshing).
    *   We do NOT use AI to "guess" geometry (NeRF/Splatting is too heavy/messy). We use Visual Hull to **guarantee** a printable volume.
2.  **The Visual Loop:**
    *   User Clicks -> Mask Appears (Immediate Feedback).
    *   User Reconstructs -> Mesh Appears (Asynchronous).
3.  **Hygiene:**
    *   No legacy artifacts (Swift/Package.swift).
    *   No loose scripts in root.
    *   All heavy assets in `assets/`.

## CURRENT PHASE: PHASE 7 (THE RECONSTRUCTOR)
**Objective:** Connect the 2D Masks (SAM 2) to the 3D Voxel Engine.

**Pipeline:**
1.  **Input:** `VideoPlayer` (User clicks object).
2.  **Process A:** `SegmentationEngine.propagate_all()` -> Tensor(F, H, W).
3.  **Process B:** `VoxelReconstructor.project_and_carve()` -> VoxelGrid(64^3).
4.  **Process C:** `MarchingCubes` -> Mesh(Verts, Faces).
5.  **Output:** `HeliosViewport` (Displays Mesh).

## ROADMAP
- [x] Phase 1-5: Foundation, UI, Video, AI.
- [x] Phase 6: Interactive Masking.
- [ ] Phase 7: Full 3D Reconstruction.
- [ ] Phase 8: Gyroid Infusion (Boolean Intersection).
