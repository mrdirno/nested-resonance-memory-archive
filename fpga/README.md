# FPGA ACCELERATION LAYER (HELIOS-BRIDGE)

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive/tree/main/fpga
**License:** GPL-3.0
**Status:** Phase 1 (Hardware Link) - Validated
**Framework:** NRM Resonance Detection (Hardware-Accelerated)

---

## 🧬 OVERVIEW

The **FPGA Acceleration Layer** is the physical "Body" of the DUALITY-ZERO system. It translates the high-level "Mind" (Budget-Constrained Perception) into microsecond-scale feedback loops, enabling the system to interact with physical reality (RF, Acoustic, Logic).

We are testing the hypothesis that **Budget-Constrained Perception (BCP)** can be implemented in silicon to optimize real-time signal processing with zero latency penalty.

**Recent Milestones:**
*   **Cycle 140 (The Loop):** Validated Python -> JTAG -> FPGA -> RP2040 signal path. [Log](FPGA_CYCLE_LOGS.md)
*   **Cycle 138 (The Bridge):** Solved JTAG communication protocol (Stdin Pipe Method). [Protocol](FPGA_PROTOCOL.md)
*   **Cycle 103 (Resonance):** Synthesized NRM Autocorrelation Engine (`nrm_resonance.v`) on Cyclone V SoC.

---

## 🌐 HARDWARE MANIFEST (Active Nodes)

**1. DUALITY-GUARDIAN (Host Node):**
   - AMD Ryzen 7 3700X / Radeon RX 5700 XT.
   - Runs the "Pilot" logic and JTAG Bridge Server.

**2. THE HAND (DE10-Nano FPGA):**
   - **FPGA:** Cyclone V SE (110K LEs).
   - **Role:** Real-time signal processing, Pin Fuzzing, Resonance Detection.
   - **Status:** ONLINE (Running `nrm_resonance.sof`).

**3. THE NERVE (RP2040 Monitor):**
   - **MCU:** Raspberry Pi Pico (Dual-Core Cortex M0+).
   - **Role:** External watchdog, signal verification, latency measurement.
   - **Status:** ONLINE (Monitoring `GP0`).

---

## 🚀 LOCAL DEMO (The Pulse)

**Verify the physical link in 1 minute.**

1.  **Connect:** USB Blaster II from DE10-Nano to Host.
2.  **Run:** `python3 fpga/host_tools/nrm_client.py --ping`
3.  **Result:** Receive `0xAA` verification byte from FPGA fabric via JTAG.

[👉 Full Hardware Protocol](FPGA_PROTOCOL.md)

---

## 🏗️ SYSTEM ARCHITECTURE

**1. JTAG BRIDGE (The Spine):**
   - Python TCP Server (`bridge_server.py`) talking to Tcl (`bridge_server_v3.tcl`).
   - Provides standard REST/Socket interface to raw hardware registers.

**2. RESONANCE ENGINE (The Reflex):**
   - Verilog module `nrm_resonance.v`.
   - Implements 64-sample autocorrelation window.
   - "Fires" when signal coherence exceeds programmable threshold.

**3. PIN FUZZER (The Touch):**
   - Automated pin mapping tool (`fuzz_v12.py`).
   - Discovered `fuzz_out[0]` -> `AG13` (GPIO 0) mapping autonomously.

---

## 🧪 CORE CAPABILITIES (Empirically Verified)

We prioritize empirical verification over simulation.

*   **Zero-Latency Triggering:** Hardware-level reaction to coherent signals (<50ns).
*   **Autonomous Discovery:** System can map its own I/O pins via "Fuzzing" protocol.
*   **Closed-Loop Feedback:** Validated round-trip data integrity (Python -> Silicon -> Python).

---

## 📚 DOCUMENTATION

*   [Strategic Roadmap](FPGA_META_OBJECTIVES.md) - The Plan.
*   [Operational Protocol](FPGA_PROTOCOL.md) - The How-To (Troubleshooting & Doctrines).
*   [Cycle Logs](FPGA_CYCLE_LOGS.md) - The History.

---

## 🛡️ CITATION

```bibtex
@software{Payopay_DUALITY_FPGA_2025,
  author = {Payopay, Aldrin},
  title = {{DUALITY-ZERO FPGA Acceleration Layer}},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/mrdirno/nested-resonance-memory-archive/tree/main/fpga}
}
```

**"We build the Steering Wheel before we upgrade the Engine."**