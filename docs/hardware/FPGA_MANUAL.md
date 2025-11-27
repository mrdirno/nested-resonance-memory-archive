# HELIOS FPGA Accelerator Manual

**Version:** 1.0 (Gate 14.3)
**Date:** 2025-11-27
**Target:** Xilinx Zynq-7000 (PYNQ-Z2) / Generic FPGA

---

## 1. Overview

The HELIOS FPGA Accelerator offloads the Gorkov Potential calculation from the Host CPU to a dedicated hardware pipeline. This enables real-time acoustic field synthesis for dense volumetric traps (64+ emitters) with update rates > 1kHz.

### Architecture

```mermaid
graph TD
    Host[Host CPU (Python)] -->|AXI4-Lite| Wrapper[AXI Wrapper]
    Wrapper -->|Control/Data| PhaseMem[Phase Memory (BRAM)]
    Wrapper -->|Start| Core[Physics Core]
    PhaseMem -->|Flat Phases| Core
    Core -->|Potential (32-bit)| Wrapper
    Wrapper -->|Result| Host
```

### Components
1.  **AXI Wrapper (`gorkov_axi_wrapper.v`):** Handles the AXI4-Lite protocol, memory mapping, and control signals (Start, Reset).
2.  **Phase Memory (`gorkov_accelerator.v`):** A 64x16-bit register file/BRAM that stores the phase delay for each emitter.
3.  **Physics Core (`gorkov_potential.v`):** The compute engine. Calculates $\sum \sin(\phi + kr)$ using a pre-computed LUT.
4.  **Sine LUT (`sine_lut.mem`):** 1024-entry lookup table for high-speed sine/cosine generation.

---

## 2. Register Map

**Base Address:** 0x43C00000 (Default for PYNQ Overlays)
**Address Width:** 6 bits

| Offset | Name | R/W | Description |
| :--- | :--- | :--- | :--- |
| `0x00` | `CTRL` | R/W | Control Register. Bit 0: Start, Bit 1: Reset, Bit 2: IRQ Enable. |
| `0x04` | `STATUS` | R | Status Register. Bit 0: Reserved, Bit 1: Busy, Bit 2: Done, Bit 3: Error. |
| `0x08` | `EMITTER_CNT` | R/W | Number of active emitters (Default: 64). |
| `0x0C` | `VOXEL_CNT` | R/W | Number of voxels to compute (Default: 1 - Point Mode). |
| `0x10` | `PHASE_L` | W | Phase Data (16-bit). Write triggers update to address in `PHASE_H`. |
| `0x14` | `PHASE_H` | R/W | Phase Index (0-63). Set this before writing `PHASE_L`. |
| `0x18` | `VOXEL_L` | R/W | Target X (16-bit signed) \| Target Y (16-bit signed). |
| `0x1C` | `VOXEL_H` | R/W | Target Z (16-bit signed). |
| `0x20` | `RESULT_L` | R | Computed Potential (Lower 32 bits). |
| `0x24` | `RESULT_H` | R | Reserved (Upper 32 bits for 64-bit results). |

---

## 3. Build Process

### Prerequisites
*   Xilinx Vivado (2020.2 or later recommended).
*   Linux Build Agent or Windows Workstation.

### Steps
1.  **Clone Repository:**
    ```bash
    git clone https://github.com/your-repo/DUALITY-ZERO-V2.git
    cd DUALITY-ZERO-V2
    ```

2.  **Run Synthesis Script:**
    ```bash
    cd FPGA/bitstreams
    vivado -mode batch -source synth.tcl
    ```

3.  **Output:**
    *   Bitstream location: `FPGA/bitstreams/build/helios_accelerator.runs/impl_1/gorkov_accelerator.bit` (after implementation).
    *   *Note:* The current `synth.tcl` only runs synthesis. For full bitstream, extend the script to run `launch_runs impl_1 -to_step write_bitstream`.

---

## 4. Driver Usage

The Python driver (`src/fpga/driver.py`) provides a high-level API for the accelerator. It supports a **Simulation Mode** for development without hardware.

### Example

```python
from src.fpga.driver import GorkovAccelerator

# Initialize (Simulation Mode defaults to True if hardware not found)
accel = GorkovAccelerator(simulation_mode=True)

# 1. Load Phases
# Phases must be 0-1023 (10-bit mapped to 0-2pi)
phases = [0] * 64
accel.load_phases(phases)

# 2. Set Target
# Coordinates in mm (Fixed Point 16-bit)
accel.set_target(x=0, y=0, z=50)

# 3. Execute
accel.run()

# 4. Read Result
potential = accel.read_result()
print(f"Calculated Potential: {potential}")
```

### Hardware Integration (PYNQ)
To use with real hardware, update `src/fpga/driver.py` to use `pynq.Overlay`:

```python
from pynq import Overlay
from pynq import MMIO

class GorkovAcceleratorHardware(GorkovAccelerator):
    def __init__(self, bitstream="helios.bit"):
        self.overlay = Overlay(bitstream)
        self.mmio = self.overlay.gorkov_accelerator.mmio
        # Override methods to use self.mmio.write / read
```

---

## 5. Troubleshooting

*   **Zero Potential Result:** Check if `sine_lut.mem` is loaded correctly in simulation. Ensure phases are not cancelling out perfectly (unlikely for random/zero phases).
*   **Synthesis Failed:** Check `FPGA/constraints/helios.xdc` for conflicting pin assignments.
*   **Driver Error:** Ensure the Python environment has access to `src/fpga` in `PYTHONPATH`.

---
**End of Manual**
