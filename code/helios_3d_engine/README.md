# HELIOS 3D ENGINE (Project Code: SUNFIRE)

**Current Version:** 0.4.0 (The Architect)
**Target Platform:** macOS (Silicon Optimized)
**Architecture:** Python 3 + PySide6 + Native Swift Bridge + PyTorch

## MANDATE
Build a next-generation 3D generation and manipulation tool that surpasses commercial web-based tools.
**Hybrid Architecture Active:**
-   **Host:** Python/Qt.
-   **Native Bridge:** Swift CLI for `PhotogrammetrySession`.
-   **AI Sidecar:** PyTorch/MPS.
-   **Advanced Editing:** SDF Boolean Operations via Voxel Remeshing.

## ARCHITECTURE
-   **Frontend:** PySide6 (Qt)
-   **Reconstruction:** Native Apple Object Capture & Visual Hull.
-   **Editing:** Mesh-to-SDF conversion and CSG (Constructive Solid Geometry).

## GETTING STARTED
1.  Compile Native Bridge:
    ```bash
    cd ../helios_native_bridge && swift build -c release
    ```
2.  Run Engine:
    ```bash
    python3 main.py
    ```

## ROADMAP
-   [x] **Phase 1-4:** Viewport, SDFs, UI, Export.
-   [x] **Phase 5:** AI Text-to-3D (Semantic).
-   [x] **Phase 6:** Neural Link (MPS Detection).
-   [x] **Phase 7:** The Reconstructor (Native Swift Bridge).
-   [x] **Phase 8:** The Loader (USDZ Import).
-   [x] **Phase 9:** The Architect (SDF Boolean Operations).
-   [ ] **Phase 10:** Deployment (Bundle as .app).