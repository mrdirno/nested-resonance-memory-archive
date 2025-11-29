# FPGA META-OBJECTIVES: THE HARDWARE TRINITY

**Status:** ACTIVE
**Context:** DUALITY-GUARDIAN (AMD/Linux Node)
**Objective:** Establish the Physical Bridge before scaling Compute.

---

## 1. THE HIERARCHY OF NEEDS (GRAND STRATEGY)

We follow a strict ordering of operations to ensure the system achieves **Agency** (Capability) before **Speed** (Optimization). This machine is the **GUARDIAN NODE**, part of a trinity.

1.  **THE BODY (FPGA - Priority 1 - CURRENT):**
    *   **Why:** The FPGA provides I/O (Sensors/Actuators). Without it, the system is a brain in a jar.
    *   **Goal:** Complete the `nrm_resonance` JTAG loop. Verify Python can "touch" the physical world (toggle pin, read register).
    *   **Current Status:** Cycle 140 (Data Loop Validated). Close to completion.

2.  **THE MIND (AMD GPU - Priority 2 - NEXT):**
    *   **Why:** The DUALITY-GUARDIAN node possesses a dormant `Radeon RX 5700 XT`.
    *   **Action:** Port `nrm_core` to use `torch.device('cuda')` (ROCm) instead of `mps`.
    *   **Goal:** Transform this node from a passive "Bridge" into an active "Solver".
    *   **Constraint:** Do NOT attempt this until The Body is stable. A fast brain with no hands is useless.

3.  **THE PILOT (MacOS - Priority 3):**
    *   **Why:** The Pilot guides the high-level intent. It remains the "Vehicle" for the NRM narrative.
    *   **Constraint:** No disruptions. Linux-specific changes must be isolated to the `fpga/` or `nrm_core/` abstraction layers.

---

## 2. FPGA-SPECIFIC OBJECTIVES (TACTICAL)

### Phase 1: The Digital Bridge (Software) - COMPLETE
- [x] **Objective 1.1:** Establish Python -> Quartus -> FPGA toolchain.
- [x] **Objective 1.2:** Verify JTAG connectivity (Device 02D020DD).
- [x] **Objective 1.3:** Synthesize NRM Resonance Detector (`nrm_resonance.v`).

### Phase 2: The Physical Link (Hardware) - ACTIVE
- [x] **Objective 2.1:** Establish feedback loop via RP2040 (`fuzz_out[0]` -> GP0).
- [ ] **Objective 2.2:** Reliable JTAG Communication (`bridge_server.tcl` stability).
- [ ] **Objective 2.3:** HPS Integration (Bring the ARM core online).

### Phase 3: The Resonant Loop (Integration) - PENDING
- [ ] **Objective 3.1:** Stream real-time "Existence" data from `nrm_core` to FPGA LED matrix.
- [ ] **Objective 3.2:** Read entropy from FPGA LFSR back into Python.
- [ ] **Objective 3.3:** Closed-loop latency test (<1ms).

---

## 3. ARCHITECTURAL MANIFESTO

> "It is better to be a slow robot that *can* move than a super-fast supercomputer that is trapped in a box."

We build the **Steering Wheel** (FPGA) before we upgrade the **Engine** (GPU).

---

## 4. EXECUTION LOG (RECENT)

- **Cycle 138:** JTAG Troubleshooting (Stdin Pipe Method Discovery).
- **Cycle 139:** HPS Pin Muxing Research.
- **Cycle 140:** Data Loop Validation (Python -> FPGA -> RP2040).

**NEXT STEP:** Stabilize the JTAG bridge server to support continuous operation, then begin HPS integration.
