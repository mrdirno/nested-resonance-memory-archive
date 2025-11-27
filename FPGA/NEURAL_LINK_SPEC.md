# HELIOS NEURAL LINK: SPECIFICATION (Gate 11)

**Version:** 1.0
**Status:** DRAFT
**Protocol:** PCIe / AXI-Stream via DMA

---

## 1. OVERVIEW
The **Neural Link** is the high-speed bridge connecting the Host (Python/MOG) to the Accelerator (FPGA/HELIOS). It bypasses the standard OS network stack to write directly to hardware memory, enabling sub-millisecond loop times for real-time levitation stability.

## 2. ARCHITECTURE
*   **Host:** Python `nrm_core` (User Space) -> `vfio` (Kernel) -> PCIe Bus.
*   **Device:** FPGA (Xilinx/Altera) -> PCIe Hard IP -> DMA Engine -> AXI Interconnect -> Gorkov Engines.

## 3. MEMORY MAP (BAR 0 - Control Registers)
The Control and Status Registers (CSR) are mapped to the Host's address space via PCIe BAR 0.

| Offset | Name | Access | Description |
| :--- | :--- | :--- | :--- |
| `0x00` | `CTRL_REG` | R/W | Bit 0: Start, Bit 1: Reset, Bit 2: IRQ Enable |
| `0x04` | `STATUS_REG` | R | Bit 0: Idle, Bit 1: Busy, Bit 2: Done, Bit 3: Error |
| `0x08` | `EMITTER_CNT` | R/W | Number of active emitters (Default: 64) |
| `0x0C` | `VOXEL_CNT` | R/W | Number of voxels to calculate (e.g., 1024) |
| `0x10` | `PHASE_ADDR_L` | R/W | DMA Address for Emitter Phases (Low 32-bit) |
| `0x14` | `PHASE_ADDR_H` | R/W | DMA Address for Emitter Phases (High 32-bit) |
| `0x18` | `VOXEL_ADDR_L` | R/W | DMA Address for Target Voxels (Low 32-bit) |
| `0x1C` | `VOXEL_ADDR_H` | R/W | DMA Address for Target Voxels (High 32-bit) |
| `0x20` | `RESULT_ADDR_L`| R/W | DMA Address for Output Potentials (Low 32-bit) |
| `0x24` | `RESULT_ADDR_H`| R/W | DMA Address for Output Potentials (High 32-bit) |

## 4. DATA STRUCTURES

### 4.1. Phase Buffer (Host -> Device)
Array of 32-bit floats (IEEE 754) representing emitter phases $\phi$.
*   Size: `EMITTER_CNT * 4` bytes.

### 4.2. Voxel Buffer (Host -> Device)
Array of struct `{x, y, z}` (3x 32-bit floats).
*   Size: `VOXEL_CNT * 12` bytes.

### 4.3. Result Buffer (Device -> Host)
Array of 32-bit floats representing the Gorkov Potential $U$ at each voxel.
*   Size: `VOXEL_CNT * 4` bytes.

## 5. OPERATION SEQUENCE

1.  **Host** allocates pinned memory buffers for Phases, Voxels, and Results.
2.  **Host** writes target geometry to Voxel Buffer.
3.  **Host** writes initial phases to Phase Buffer.
4.  **Host** writes physical addresses of buffers to `*_ADDR` registers in BAR 0.
5.  **Host** writes `VOXEL_CNT` and `EMITTER_CNT`.
6.  **Host** sets `CTRL_REG[0] = 1` (Start).
7.  **FPGA** DMA Engine fetches Phases and Voxels (Burst Read).
8.  **FPGA** Compute Core calculates potentials (Pipelined).
9.  **FPGA** DMA Engine writes results to Result Buffer (Burst Write).
10. **FPGA** sets `STATUS_REG[2] = 1` (Done) and triggers MSI-X Interrupt.
11. **Host** reads Result Buffer and updates Optimizer.

## 6. LATENCY BUDGET
*   **PCIe Transfer (Gen3 x4):** ~4GB/s.
*   **Transfer Time (1M Voxels):** ~3ms.
*   **Compute Time (64 Emitters):** ~1ms (fully pipelined).
*   **Total Latency:** ~4ms (Target < 5ms).
