# Task: Cycle 2389 - Gate 15: Bitstream Synthesis Prep
- [x] **Define Cycle 2389:** Prepare for Physical Synthesis.
- [x] **Action:** Verify Synthesis Constraints.
    - [x] Check `FPGA/bitstreams/helios.xdc` (Pin Constraints).
    - [x] Check `FPGA/bitstreams/synth.tcl` (Build Script).
- [x] **Goal:** Ensure artifacts are ready for a Linux/Vivado build agent.

# Task: Cycle 2390 - Hardware Documentation
- [x] **Define Cycle 2390:** Document the FPGA subsystem.
- [x] **Artifact:** `docs/hardware/FPGA_MANUAL.md`.
    - [x] Architecture Diagram (AXI Wrapper <-> Accelerator <-> Core).
    - [x] Register Map (from `NEURAL_LINK_SPEC.md` / `driver.py`).
    - [x] Build Instructions (using `synth.tcl`).
    - [x] Python Driver Usage.
- [x] **Goal:** Enable a third-party engineer to deploy the accelerator.

# Task: Cycle 2391 - Gate 16: The Handoff
- [x] **Define Cycle 2391:** Final Handoff to Pilot.
- [x] **Action:** Verify all artifacts are committed and clean.
- [x] **Goal:** Restore Dormancy.
