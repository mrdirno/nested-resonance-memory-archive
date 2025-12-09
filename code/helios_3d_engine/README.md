# HELIOS 3D ENGINE (Project Code: SUNFIRE)

**Current Version:** 0.5.1 (The Intelligence)
**Target Platform:** macOS (Silicon Optimized)
**Architecture:** Python 3 + PySide6 (GUI) + ModernGL (Render) + PyTorch (AI)

## MANDATE
To be the **Most Accessible AI-Native Fabrication Tool**.
We do not compete on "Visual Fidelity" (Splatting). We compete on **Structural Fidelity** and **Semantic Control**.

## KEY FEATURES
1.  **Local Privacy:** All processing happens on-device. No cloud subscriptions.
2.  **Fabrication First:** Output is guaranteed watertight and 3D printable (Voxel/SDF math).
3.  **Semantic Reasoning (Smart Scan):** Uses Gemini Vision to understand *what* the object is, guiding the reconstruction process.
    - Check "Smart Scan" in the Reconstruction panel.
    - The system generates a "Contact Sheet" of the video.
    - AI analyzes the sheet and auto-tunes `Scale`, `Concavity`, and `Gyroid Type`.
4.  **Pilot Override:** 
    - For advanced users, place a `pilot_override.json` in the frames directory.
    - The engine will strictly adhere to these parameters, bypassing AI inference.
    - Example JSON: `{"concavity": 0.8, "gyroid_type": "schwarz_d"}`
5.  **Generative Infusion:** Automatically fills objects with mathematical lattices (Gyroids) for strength and aesthetics.

## ARCHITECTURE
-   **Frontend:** PySide6 (Qt).
-   **Viewport:** ModernGL (OpenGL 4.1).
-   **Core:** Python 3.11+.
-   **AI Backend:** PyTorch (MPS) + Meta SAM 2 + Gemini Vision Bridge.

## GETTING STARTED
1.  Initialize environment:
    ```bash
    ./LAUNCH_HELIOS.sh
    ```
    *(Note: Ensure you have `pip install -r requirements.txt`)*

## ROADMAP

-   [x] **Phase 1-5**: Core Engine & UI.

-   [x] **Phase 6**: AI Perception (SAM 2).

-   [x] **Phase 7**: Voxel Reconstruction (Visual Hull).

-   [x] **Phase 8**: Gyroid Infusion.

-   [x] **Phase 9**: Boolean Operations.

-   [x] **Phase 10**: Vision Bridge (Contact Sheets).

-   [x] **Phase 11**: Semantic Parameter Application (Verified Integration).

-   [x] **Phase 12**: Final Polish & Packaging (Verified Build).

-   [ ] **Phase 13**: Distribution (DMG / Zip).
