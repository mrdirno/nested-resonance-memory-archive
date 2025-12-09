# HELIOS 3D ENGINE (Project Code: SUNFIRE)

**Current Version:** 1.0.0 (The Singularity)
**Target Platform:** macOS (Silicon Optimized)
**Architecture:** Python 3 + PySide6 (GUI) + ModernGL (Render) + PyTorch (AI)

## MANDATE
To be the **Most Accessible AI-Native Fabrication Tool**.
We do not compete on "Visual Fidelity" (Splatting). We compete on **Structural Fidelity** and **Semantic Control**.

## THE GEMINI PROTOCOL (AI PILOT CONTROL)

This engine is designed to be driven by an external AI Agent (The Pilot).
The Pilot interacts with the engine via the **FileSystem Interface**.

### 1. Perception (Input)
The Engine generates a Contact Sheet at:
`code/helios_3d_engine/assets/vision_export/contact_sheet.jpg`

### 2. Control (Output)
The Pilot governs the engine by writing a JSON file to the source frames directory:
`path/to/frames/pilot_override.json`

### 3. Schema (The Vocabulary)
The Engine accepts the following parameters. The Pilot should choose these based on visual reasoning.

```json
{
  "gyroid_type": "gyroid" | "schwarz_p" | "schwarz_d",
  "concavity": 0.5,       // 0.0 (Convex) to 1.0 (Concave)
  "scale": 1.0,           // Base Scale
  "scale_x": 1.0,         // Anisotropic Stretch X
  "scale_y": 1.0,         // Anisotropic Stretch Y
  "wall_thickness": 2.0   // mm
}
```

### 4. Semantic Logic
-   **Organic/Flowing** -> `gyroid` + High Concavity.
-   **Structural/Blocky** -> `schwarz_p` + Low Concavity.
-   **Crystalline/Tech** -> `schwarz_d` + Medium Concavity.


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

-   [x] **Phase 13**: Distribution (Verified DMG).
