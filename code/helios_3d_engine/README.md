# HELIOS 3D ENGINE (Project Code: SUNFIRE)

**Current Version:** 0.3.1 (The Neural Link)
**Target Platform:** macOS (Silicon Optimized)
**Architecture:** Python 3 + PySide6 (GUI) + ModernGL (Render) + PyTorch (AI Sidecar)

## MANDATE
Build a next-generation 3D generation and manipulation tool that surpasses commercial web-based tools (like 3dpresso.ai).
This project follows a **Hybrid Architecture**:
-   **Core Logic:** Python for rapid AI integration and procedural math.
-   **AI Integration:** Native Python bindings for semantic text-to-3D (simulated) and future LLM hooks.
-   **Native Feel:** PySide6 for macOS-compliant UI.

## ARCHITECTURE
-   **Frontend:** PySide6 (Qt)
-   **Viewport:** ModernGL (OpenGL 4.1+ Core Profile)
-   **AI Engine:** PyTorch with MPS (Metal Performance Shaders) acceleration.

## GETTING STARTED
1.  Initialize environment:
    ```bash
    ./LAUNCH_HELIOS.sh
    ```

## ROADMAP
-   [x] **Phase 1: The Retina** - Basic 3D Viewport.
-   [x] **Phase 2: The Sculptor** - SDF-based geometry generation.
-   [x] **Phase 3: The Brain** - UI Controls & Async Processing.
-   [x] **Phase 4: The Forge** - STL Export.
-   [x] **Phase 5: The Architect** - AI Text-to-3D (Semantic Generator).
-   [x] **Phase 6: The Neural Link** - PyTorch/MPS Infrastructure & Device Detection.