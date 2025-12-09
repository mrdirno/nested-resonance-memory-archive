# Helios 3D Engine

**Status**: Phase 4.2 (Optimization) Complete
**Goal**: Build a standalone, native macOS 3D generation and manipulation tool that surpasses [3dpresso.ai](https://3dpresso.ai).

## Overview
Helios 3D Engine is a high-performance, native macOS application designed for:
1.  **3D Reconstruction**: Generating high-fidelity 3D models (USDZ) from image sets using Apple's `PhotogrammetrySession`.
2.  **Visualization**: Real-time 3D rendering using `RealityKit` and `RealityView`.
3.  **Mesh Analysis**: Physical property calculation (Vertex Count, Triangle Count, Dimensions).
4.  **Optimization**: Voxel-based remeshing for geometry simplification and watertight mesh generation.

## Architecture
-   **Frontend**: SwiftUI with `HSplitView` layout.
-   **Rendering**: RealityKit (`RealityView`).
-   **Core Logic**: `EngineCore` (Photogrammetry), `MeshAnalyzer` (ModelIO/Metal).
-   **Optimization**: `MDLVoxelArray` for grid-based resampling.

## Features Implemented
-   [x] **Project Structure**: Native Swift Package Manager setup.
-   [x] **Photogrammetry**: Convert image folder -> USDZ asynchronously.
-   [x] **Visualization**: Interactive 3D viewer with auto-scaling and rotation.
-   [x] **Analysis**: Real-time reporting of mesh statistics.
-   [x] **Optimization**: Voxel remeshing tool with adjustable resolution.

## Roadmap
-   [ ] **Phase 5: AI Integration**: Text-to-3D pipeline (CoreML/Python Bridge).
-   [ ] **Phase 6: Advanced Editing**: Texture synthesis, boolean operations, and export formats (OBJ/GLTF).

## Usage
1.  **Generate**: Select an image folder and click "Generate Model".
2.  **Analyze**: View vertex count and dimensions in the sidebar.
3.  **Optimize**: Adjust the "Voxel Resolution" slider and click "Remesh" to simplify the geometry.
