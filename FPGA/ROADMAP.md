# Open Source Circuit Designer Roadmap

## Vision
To create a real-time, open-source FPGA development environment integrated into the DUALITY-ZERO system. This bypasses proprietary vendor lock-in (Intel Quartus/Xilinx Vivado) where possible, utilizing open toolchains.

## Target Hardware
- **Terasic DE10-Nano** (Intel Cyclone V SoC)
- **Lattice iCE40** (Alternative for fully open flow)

## Toolchain Strategy (The "Yosys" Route)
1.  **Synthesis:** Yosys (Open Synthesis Suite).
2.  **Place & Route:** nextpnr (Portable P&R).
3.  **Bitstream Generation:** Project Trellis (Lattice) or Mistral (Intel Cyclone V - *Experimental*).
4.  **Simulation:** Verilator (Open source Verilog simulator).

## Integration Plan
1.  **Verilog Compiler Module:** A Python wrapper (`src/fpga/compiler.py`) to invoke Yosys/nextpnr.
2.  **Hot-Reload Bridge:** The `sdr_bridge` logic will be adapted to stream bitstreams to the FPGA via JTAG/USB.
3.  **The "Circuit Fabricator":** Extending the HELIOS Fabricator to "print" logic circuits as well as acoustic fields.

## Directory Structure
- `FPGA/verilog/src`: Source `.v` files.
- `FPGA/verilog/tb`: Testbenches.
- `FPGA/tools`: Dockerfiles or scripts to set up the open toolchain.
