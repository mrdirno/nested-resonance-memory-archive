# The Autopoietic Lab: Architecture for Distributed Reality Compilation

## 1. The Concept
"Autopoiesis" means self-creation. The **Autopoietic Lab** is a distributed computing system where the network itself generates the reality it observes. By leveraging the idle compute power of connected browsers (The Swarm), we overcome the Complexity Barrier of single-machine simulation.

## 2. System Architecture

### 2.1 The Coordinator (Server)
*   **Role:** The Conductor. Manages the global state of the simulation.
*   **Responsibility:**
    *   Maintains the "Master Field" (Voxels/Targets).
    *   Distributes "Compute Shards" (sub-volumes or frequency bands) to Clients.
    *   Aggregates results (Partial Potentials) into the Global Potential.
    *   Runs the Genetic Algorithm (GA) evolution step.
*   **Tech Stack:** Python (FastAPI/WebSockets) or Node.js.

### 2.2 The Worker (Client)
*   **Role:** The Physicist. Calculates the physics for a specific shard.
*   **Responsibility:**
    *   Receives `emitters` configuration and `target_points` from Server.
    *   Runs the Wasm-compiled `helios_physics` kernel.
    *   Returns `potential` and `gradient` values to Server.
*   **Tech Stack:** Browser (Chrome/Firefox/Safari), WebAssembly (Rust), WebSockets.

### 2.3 The Holodeck (Viewer)
*   **Role:** The Observer. Visualizes the aggregated reality.
*   **Responsibility:**
    *   Renders the 3D field and particles using Three.js/WebGPU.
    *   Provides user interface for "God Mode" control.
*   **Tech Stack:** Three.js, React.

## 3. Data Flow (The Heartbeat)
1.  **Pulse:** Server sends current `phase_configuration` to all Workers.
2.  **Compute:** Workers calculate $U(x)$ (Gorkov Potential) for their assigned voxels in parallel.
3.  **Converge:** Workers send results back to Server.
4.  **Evolve:** Server evaluates Fitness (Stability) and evolves the population (GA).
5.  **Update:** Server broadcasts new `phase_configuration`.

## 4. Implementation Roadmap
*   **Phase 1:** WebSocket Server (Python `websockets` lib).
*   **Phase 2:** Wasm Worker Integration (Cycle 400 artifact).
*   **Phase 3:** Sharding Logic (Spatial partitioning).
*   **Phase 4:** Aggregation & Visualization.

## 5. Why This Matters
This architecture transforms DUALITY-ZERO from a "Simulation on a Laptop" to a "Planetary Computation". It allows us to scale from 27 voxels to millions, enabling the compilation of macroscopic objects from invisible fields.
