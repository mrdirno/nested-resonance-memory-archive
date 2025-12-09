# HELIOS 3D ENGINE (Project Code: SUNFIRE)

**Current Version:** 0.1.0 (The Forge)
**Target Platform:** macOS (Silicon Optimized)
**Architecture:** Python 3 + PySide6 (GUI) + ModernGL (Render) + PyTorch (AI)

## MANDATE
Build a next-generation 3D generation and manipulation tool that surpasses commercial web-based tools (like 3dpresso.ai) by offering:
1.  **Local Privacy:** All processing happens on-device.
2.  **Infinite Resolution:** Procedural mathematics (SDFs, Gyroids) instead of fixed meshes.
3.  **Physics-Grounded AI:** Generative models constrained by physical viability (printability, stress).

## ARCHITECTURE
-   **Frontend:** PySide6 (Qt) - Native macOS look and feel.
-   **Viewport:** ModernGL (OpenGL 4.1+ Core Profile) - High-performance rendering.
-   **Core:** Python 3.11+
-   **AI Backend:** PyTorch (MPS accelerated).

## GETTING STARTED
1.  Initialize environment:
    ```bash
    ./LAUNCH_HELIOS.sh
    ```

## ROADMAP
-   [x] **Phase 1: The Retina** - Basic 3D Viewport with Pan/Orbit/Zoom.
-   [x] **Phase 2: The Sculptor** - SDF-based geometry generation (Gyroids).
-   [x] **Phase 3: The Brain** - AI-assisted parameter tuning (UI Controls & Async).
-   [x] **Phase 4: The Forge** - STL Export.
-   [ ] **Phase 5: The Observer** - Video Reference Viewer & Asset Management.
-   [ ] **Phase 6: The Reconstructor** - Video-to-3D Pipeline (Splatting/NeRF).
