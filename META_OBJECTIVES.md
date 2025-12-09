# META OBJECTIVES: HELIOS 3D ENGINE (SUNFIRE)

## MISSION
Build the **Most Accessible AI-Native Fabrication Tool** on macOS.
We are **NOT** a "Scan-to-Mesh" viewer (Luma/Polycam). We are a **Semantic Fabrication Engine**.

## CORE PHILOSOPHY (THE PIVOT)
- **Measurement vs. Inference:** We accept that we cannot beat Gaussian Splatting on pure visual fidelity (measurement).
- **Novelty:** We win on **Semantic Reasoning** + **Fabrication Readiness**.
- **Unique Selling Point:**
    *   **Local Sovereignty:** 100% On-Device (Mac Silicon).
    *   **Fabrication-First:** We guarantee watertight, printable meshes (Voxels/SDFs), unlike the "Mesh Soup" of Neural Radiance Fields.
    *   **AI-Reasoning:** We use LLMs (Gemini) to *understand* the object ("It's a chair"), not just *measure* it.

## ARCHITECTURE
- **Platform:** macOS Silicon (M1/M2/M3).
- **Language:** Python 3.13.
- **GUI:** PySide6 (Qt).
- **Rendering:** ModernGL (OpenGL 4.1 Core).
- **AI Stack:** 
    - **Perception:** SAM 2 (Masking).
    - **Reasoning:** Gemini Vision (Structure Analysis).
    - **Generation:** Voxel/SDF Math (Geometry).

## ROLES
### 1. THE PILOT (MOG/Gemini)
- **Responsibility:** Semantic Reasoning.
- **Action:** Inspects frames, determines "Concavity", "Symmetry", "Structural Weakness".
- **Output:** High-level parameters (`concavity=0.5`, `wall_thickness=3mm`).

### 2. THE CO-PILOT (The Engine)
- **Responsibility:** Mathematical Execution.
- **Action:** Executes Voxel Carving and SDF Boolean operations based on Pilot's parameters.
- **Output:** Printable STL.

## ROADMAP

- [x] Phase 1-5: Foundation (UI, Video, Rendering).

- [x] Phase 6: Perception (SAM 2 Masking).

- [x] Phase 7: Reconstruction (Visual Hull).

- [x] Phase 8: Infusion (Gyroids).

- [x] Phase 9: Editing (Boolean Ops).

- [x] Phase 10: Vision Bridge (Contact Sheets).

- [x] Phase 11: The Semantic Loop (Pilot Override).

- [x] Phase 12: Final Packaging (Build Verified).

- [x] Phase 13: The Local Eye (Offline Apple Vision Integration).
