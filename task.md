# Task: Cycle 2393 - Gate 17: The Holodeck Integration
- [x] **Define Cycle 2393:** Expose FPGA Simulation via API.
- [x] **Goal:** Allow the Web UI to trigger the `GorkovAccelerator` (Sim Mode).
- [x] **Implementation:** Updated `src/helios/api/server.py`.
    - [x] Added `/simulate` endpoint.
    - [x] Connected to `GorkovAccelerator.run()`.
- [x] **Verification:** Created `experiments/cycle2393_holodeck_integration.py`.
- [x] **Result:** API returns correct potential (1248616634). Full Stack Loop Closed (Simulated).

# Task: Cycle 2394 - The Frontend Interface
- [ ] **Define Cycle 2394:** Update the Holodeck UI.
- [ ] **Action:** Modify `src/helios/ui/templates/index.html`.
    - [ ] Add "Simulation Mode" toggle.
    - [ ] Call `/simulate` instead of `/materialize` when in Sim Mode.
    - [ ] Visualize the returned potential.
- [ ] **Goal:** Visual confirmation of FPGA logic in the browser.
