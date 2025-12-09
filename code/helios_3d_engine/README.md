# HELIOS 3D ENGINE (Project Code: SUNFIRE)

**Current Version:** 1.0.5 (The Open Door)
**Target Platform:** macOS (Silicon Optimized)
**Architecture:** Python 3 + PySide6 (GUI) + ModernGL (Render) + PyTorch (AI)

## MANDATE
To be the **Most Accessible AI-Native Fabrication Tool**.
We do not compete on "Visual Fidelity" (Splatting). We compete on **Structural Fidelity** and **Semantic Control**.

## THE GEMINI PROTOCOL (TWIN ENGINE ARCHITECTURE)

This engine is designed to be driven by a dual-layer AI system:
1.  **The Pilot (Strategy):** High-level directive and aesthetic intent.
2.  **The Co-Pilot (Tactics):** A local Gemini Agent instance that executes the loop.

### 1. Perception (Input)
The Engine generates a Contact Sheet at:
`code/helios_3d_engine/assets/vision_export/contact_sheet.jpg`

### 2. The Loop (Handshake)
-   **Helios:** Saves image -> Enters "Waiting" state.
-   **Co-Pilot (Local Gemini):** Monitors folder -> Reads image -> Reasons -> Writes JSON.
-   **Helios:** Detects JSON -> Updates Geometry.

### 3. Control (Output)
The Co-Pilot controls the engine by writing:
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

*Example:* See `assets/examples/mondrian_jellyfish_override.json` for a "Mondrian Jellyfish" configuration.

### 4. Semantic Logic
-   **Organic/Flowing** -> `gyroid` + High Concavity.
-   **Structural/Blocky** -> `schwarz_p` + Low Concavity.
-   **Crystalline/Tech** -> `schwarz_d` + Medium Concavity.

## KEY FEATURES
1.  **Local Privacy:** All processing happens on-device. No cloud subscriptions.
2.  **Fabrication First:** Output is guaranteed watertight and 3D printable (Voxel/SDF math).
3.  **Fabrication Bridge (Voxel Slicer):** Realtime cross-section analysis to verify printability (islands/overhangs) before export.
4.  **Semantic Reasoning (Smart Scan):**
    -   **The Local Eye:** Uses macOS Native Vision Framework to classify objects *offline*.
    -   **Auto-Tuning:** Detects "Organic" vs "Structural" forms and adjusts Gyroid params automatically.
5.  **Pilot Override:** 
    - For advanced users, place a `pilot_override.json` in the frames directory.
    - The engine will strictly adhere to these parameters, bypassing AI inference.
    - Example JSON: `{"concavity": 0.8, "gyroid_type": "schwarz_d"}`
6.  **Generative Infusion:** Automatically fills objects with mathematical lattices (Gyroids) for strength and aesthetics.
7.  **Natural Language Interface:** Chat with the engine to control parameters (Verified Integration).
8.  **Multi-Modal Bridge:** Experimental support for Audio/Thermal inputs (Verified Integration).
9.  **Isomorphic Transfer:** Apply NRM principles to new domains (Trade, Medical, Law) (In Progress).
10. **Helios Web:** Run the engine in the browser via WebAssembly (In Progress).
11. **Helios Mobile:** Native app for iPad Pro with Apple Pencil support (In Progress).
12. **Helios VR/AR:** Spatial Computing interface for Apple Vision Pro (In Progress).
13. **Helios Agent:** Autonomous research and design iteration (In Progress).

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

-   [x] **Phase 14**: Fabrication Bridge (Voxel Slicer).

-   [x] **Phase 15**: Natural Language Interface (Verified Integration).

-   [x] **Phase 16**: Multi-Modal Bridge (Audio/Thermal).

-   [ ] **Phase 17**: Isomorphic Transfer (New Domains).

-   [ ] **Phase 18**: Helios Web (WASM / WebGPU).

-   [ ] **Phase 19**: Helios Mobile (iOS/iPadOS).

-   [ ] **Phase 20**: Helios VR/AR (Vision Pro).

-   [ ] **Phase 21**: Helios Agent (Autonomous Research).
