# DUALITY-ZERO: FPGA Workspace

This directory contains the Hardware Acceleration artifacts for the HELIOS core.

## Structure
*   `verilog/src/`: RTL Source Code (SystemVerilog/Verilog).
*   `verilog/tb/`: Testbenches.
*   `constraints/`: Physical constraints (XDC) for target boards.
*   `tools/`: Tcl scripts for synthesis and implementation.
*   `bitstreams/`: Output artifacts (ignored by git).

## Neural Link
The interface between Host (Python) and Device (FPGA) is defined in [NEURAL_LINK_SPEC.md](NEURAL_LINK_SPEC.md).

## Simulation
To run the behavioral simulation using `iverilog`:
```bash
iverilog -o gorkov_sim verilog/src/gorkov_potential.v verilog/tb/tb_gorkov_potential.v
vvp gorkov_sim
```

## Synthesis
To build the bitstream using Vivado (requires Xilinx tools):
```bash
vivado -mode batch -source tools/synth_helios.tcl
```