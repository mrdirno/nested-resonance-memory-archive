# HELIOS 3D ENGINE (Project Code: SUNFIRE)

**Current Version:** 0.3.2 (The Reconstructor)
**Target Platform:** macOS (Silicon Optimized)
**Architecture:** Python 3 + PySide6 + Native Swift Bridge + PyTorch

## MANDATE
Build a next-generation 3D generation and manipulation tool that surpasses commercial web-based tools.
**Hybrid Architecture Active:**
-   **Host:** Python/Qt.
-   **Native Bridge:** Swift CLI for `PhotogrammetrySession` (Apple Object Capture).
-   **AI Sidecar:** PyTorch/MPS.

## ARCHITECTURE
-   **Frontend:** PySide6 (Qt)
-   **Reconstruction:** 
    -   *Legacy:* Voxel Carving (Visual Hull).
    -   *Native:* Apple Object Capture (via `HeliosCLI`).
-   **AI Engine:** Custom Semantic Parser & PyTorch hooks.

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
-   [ ] **Phase 8:** The Loader (USDZ Import to ModernGL).
