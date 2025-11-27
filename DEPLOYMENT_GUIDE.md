# DUALITY-ZERO Deployment Guide (Phase 46)

This guide covers the installation, configuration, and operation of the DUALITY-ZERO Reality Compiler.

---

## 1. System Requirements

*   **OS:** macOS (Apple Silicon recommended) or Linux (Ubuntu 22.04+).
*   **Python:** 3.9+.
*   **Hardware (Optional):**
    *   RTL-SDR (V3 or similar) for RF Grounding.
    *   Webcam (1080p+) for Optical Grounding.
    *   Serial Emitter Array (Arduino/Teensy) for Fabrication.

---

## 2. Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/mrdirno/nested-resonance-memory-archive.git
    cd nested-resonance-memory-archive
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: For hardware support, ensure `librtlsdr` and `OpenCV` system dependencies are met.*

---

## 3. The Pulse Monitor (Control Surface)

The primary interface for DUALITY-ZERO is the **Pulse Monitor**. It handles AI orchestration and task execution.

### Interactive Mode
Launch the Meta-Pilot (AI Chat) session:
```bash
python3 automation/pulse_monitor/pulse_monitor.py --ai auto
```

### Headless Fabrication Mode
Execute a materialization task directly (no UI):
```bash
python3 automation/pulse_monitor/pulse_monitor.py --materialize data/triangle.obj --duration 10
```

---

## 4. Headless Operation (Gate 6/7/8)

The system is designed to run without a GUI ("Headless First").

### CLI Commands
You can interact with the Helios engine directly:

*   **Status Check:**
    ```bash
    python3 src/helios/cli.py status
    ```

*   **Materialize Object:**
    ```bash
    python3 src/helios/cli.py materialize --input data/triangle.obj --duration 5
    ```

### Closed-Loop Control (Gate 8)
To run the autonomous Sense-Think-Act loop (Camera + Fabricator):

```bash
python3 src/helios/control.py
```
*This will connect to the first available camera and the virtual fabricator by default.*

---

## 5. The Holodeck (Legacy UI)

The web interface is optional and serves as a passive visualization layer.

1.  **Start Server:**
    ```bash
    python3 src/helios/api/server.py
    ```
2.  **View:** Open `http://localhost:5001`

---

## 6. Hardware Setup

### Optical Grounding (Camera)
*   Plug in USB Webcam.
*   The system auto-detects device `0`.
*   To test: `python3 src/helios/camera.py`

### Physical Bridge (Serial)
*   Connect Microcontroller via USB.
*   Update `port` in your scripts or pass `--port /dev/ttyUSB0` to the CLI.
*   Protocol: `0xAA 0xBB [CMD] [LEN] [PAYLOAD] [CS]`.

### RF Grounding (SDR)
*   Plug in RTL-SDR.
*   The system auto-detects and tunes to 100MHz.
*   Fallback: Virtual SDR (Noise Generator).