# Cycle 397: Web Visualization (OBJ Viewer)

## Goal
Create a lightweight, browser-based visualization for the "Invisible Sculpture" (RF Density Mesh) generated in Cycle 396. This allows the "Invisible Shape" to be viewed and shared easily.

## User Review Required
> [!NOTE]
> **External Dependencies:** The viewer uses Three.js via `unpkg.com` CDN. Internet access is required to load the libraries.

## Proposed Changes

### Experiments
#### [NEW] [cycle397_web_viewer.html](file:///Volumes/dual/DUALITY-ZERO-V2/experiments/cycle397_web_viewer.html)
- **Purpose:** Standalone 3D Viewer.
- **Tech Stack:** HTML5, JavaScript, Three.js.
- **Features:**
    - Load `rf_sculpture.obj`.
    - Orbit Controls (Rotate/Zoom).
    - Auto-rotation.
    - Wireframe/Solid toggle (optional).

## Verification Plan

### Automated Tests
- **Static Analysis:** Check if file exists.
- **Browser Test:** (Manual) Open the HTML file in a browser.

### Manual Verification
- **Visual Inspection:**
    1. Open `experiments/cycle397_web_viewer.html` in Chrome/Safari.
    2. Verify the mesh loads and is visible.
    3. Verify rotation works.
