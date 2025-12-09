# Helios 3D Engine

**Status**: Phase 4.1 (Basic Analysis) Complete
**Goal**: Build a standalone, native macOS 3D generation and manipulation tool that surpasses [3dpresso.ai](https://3dpresso.ai).

## Overview
Helios 3D Engine is a high-performance, native macOS application designed for:
1.  **3D Reconstruction**: Generating high-fidelity 3D models (USDZ) from image sets using Apple's `PhotogrammetrySession`.
2.  **Visualization**: Real-time 3D rendering using `RealityKit` and `RealityView`.
3.  **Mesh Analysis**: Physical property calculation (Vertex Count, Triangle Count, Dimensions) using `ModelIO` and `Metal`.

## Architecture
-   **Frontend**: SwiftUI with `HSplitView` layout for a modern macOS experience.
-   **Rendering**: RealityKit (`RealityView`) for interactive 3D visualization.
-   **Core Logic**: Swift for app logic, `EngineCore` for async processing pipeline.
-   **Compute**: Metal-ready infrastructure for advanced geometry processing.

## Features Implemented
-   [x] **Project Structure**: Native Swift Package Manager setup.
-   [x] **Photogrammetry**: Convert image folder -> USDZ asynchronously.
-   [x] **Visualization**: Interactive 3D viewer with auto-scaling and rotation.
-   [x] **Analysis**: Real-time reporting of mesh statistics (Vertices, Triangles, Bounding Box).

## Roadmap
-   [ ] **Phase 4.2: Optimization**: Mesh decimation and simplification tools.
-   [ ] **Phase 5: AI Integration**: Text-to-3D pipeline (CoreML/Python Bridge).
-   [ ] **Phase 6: Advanced Editing**: Texture synthesis and boolean operations.

## Usage
1.  Open the project in Xcode or build via CLI.
2.  Select a folder containing images of an object.
3.  Click "Generate Model".
4.  View the result and analyze statistics in the sidebar.
