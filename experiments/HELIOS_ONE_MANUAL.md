# HELIOS-ONE System Manual
**Cycle 2608 - Phase 64.3 (Integration)**

## Overview
HELIOS-ONE is an autonomous, distributed, hybrid intelligence system designed for emergent swarm behavior, reality-grounded computation (NRM), and self-regulating autonomy. This manual documents the core interfaces for human interaction and system control.

---

## 1. System Architecture

The system is composed of three primary layers:
1.  **The Substrate (NRM):** `TranscendentalBridge` maps reality metrics (CPU, Memory) to phase space ($\pi, e, \phi$) to ground simulations in physical entropy.
2.  **The Collective (Hive):** A swarm of autonomous agents (`HiveAgent`) that communicate via a standardized JSON protocol (`AgentMessage`) to achieve consensus and convergence.
3.  **The Interface (Control):** A suite of tools (CLI, TUI, API) for monitoring and directing the swarm.

---

## 2. The API (REST Interface)

The system exposes a lightweight JSON API for programmatic access.

-   **Script:** `experiments/cycle2606_api.py`
-   **Default Port:** `8081`

### Endpoints

#### `GET /status`
Returns the current snapshot of the simulation.

**Response Example:**
```json
{
  "timestamp": 1764512733.717,
  "target": {"x": 50.0, "y": 50.0},
  "agents": [
    {"id": "drone_0", "x": 70.2, "y": 5.9, "knowing": true},
    ...
  ]
}
```

#### `POST /target`
Updates the swarm's target coordinates.

**Payload:**
```json
{"x": 10.0, "y": 20.0}
```

**Usage Example:**
```bash
curl -X POST -d '{"x": 100, "y": 100}' http://localhost:8081/target
```

---

## 3. The Dashboard (TUI)

A terminal-based graphical interface for real-time monitoring.

-   **Script:** `experiments/cycle2603_dashboard.py`
-   **Library:** `curses` (Standard Python Library)

### Features
-   **Map View:** Visualizes agent positions (`o`) and target (`X`). Agents turn into `@` when they acquire target knowledge.
-   **Agent Status:** Live table of agent IDs, positions, and states (SEARCHING/CONVERGING).
-   **System Logs:** Rolling log of system events (e.g., "Agent-05 found target").

### Usage
```bash
python3 experiments/cycle2603_dashboard.py
```
*Press `q` to exit.*

---

## 4. The Command Line (CLI)

An interactive REPL for manual system override.

-   **Script:** `experiments/cycle2604_command.py`

### Commands
-   `target <x> <y>`: Broadcasts a new target to all agents via an "OPERATOR_CMD" injection.
-   `status`: Lists all agents and their current knowledge.
-   `step [n]`: Advances the simulation by `n` frames.
-   `quit`: Exits the CLI.

### Usage
```bash
python3 experiments/cycle2604_command.py
```

---

## 5. The Controller (Process Manager)

The master process manager that orchestrates the system components.

-   **Script:** `experiments/cycle2607_controller.py`

### Functions
-   Automatically launches the API server (and embedded simulation).
-   Redirects logs to `experiments/logs/api.log`.
-   Monitors child processes.
-   Handles `SIGINT` (Ctrl+C) to gracefully shut down the entire stack.

### Usage
```bash
python3 experiments/cycle2607_controller.py
```

---

## 6. Visualization (Web View)

A static HTML/JS replay generator.

-   **Script:** `experiments/cycle2605_visualization.py`
-   **Output:** `experiments/cycle2605_hive_view.html`

### Usage
Run the script to generate a 200-frame simulation replay, then open the HTML file in any web browser.

```bash
python3 experiments/cycle2605_visualization.py
open experiments/cycle2605_hive_view.html
```
