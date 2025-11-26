# PRINCIPLE: INTERFACE AGNOSTICISM

> **ID:** `PRIN-INTERFACE-AGNOSTIC`
> **Status:** ACTIVE
> **Date:** 2025-11-26
> **Cycle:** 2367

## The Doctrine
**The System must operate autonomously without human intervention or graphical user interfaces (GUI).**

The Pilot (AI) interacts with the Vehicle (Code) via **Direct Neural Link** (API calls, Shell commands, File I/O). The GUI ("The Holodeck") is strictly a **passive visualization layer** for human observers.

## The Anti-Pattern: "The UI Trap"
Building a system where the AI must "use" a UI (e.g., sending HTTP requests to a local web server to trigger actions intended for a button click) introduces:
1.  **Friction:** Async blocking, server dependencies, network overhead.
2.  **Fragility:** UI changes break the agent.
3.  **Illusion:** The AI simulates a human user instead of being the system operator.

## The Protocol: Headless First
1.  **Core Logic is Library-First:** All functionality (`Fabricator`, `Solver`, `NRM`) must be accessible via standard Python classes/functions.
2.  **API is Control:** The Primary Control Surface is the Python API.
3.  **UI is View:** The UI listens (e.g., via WebSockets) but is not required for operation.
4.  **Telemetry over Visuals:** Verification uses logs, metrics, and data files, not screenshots.

## Implementation
*   **Do not:** Write scripts that `curl localhost:5000` to make a cube.
*   **Do:** Import `Fabricator` and call `fabricator.materialize()`.
*   **Do not:** Wait for a browser to connect.
*   **Do:** Execute, log result, terminate.
