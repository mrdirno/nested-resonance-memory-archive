
# HELIOS Bitstream Handoff (Gate 12)

**Target Device:** Xilinx Kintex-7 / UltraScale+ (Reference)
**Source:** `FPGA/verilog/src`
**Constraints:** `FPGA/constraints/helios.xdc`
**Synthesis:** `FPGA/tools/synth.tcl`

## Build Instructions

1.  Launch Vivado (2023.2 or newer).
2.  Source the Tcl script:
    ```tcl
    source FPGA/tools/synth.tcl
    ```
3.  Bitstream will be generated in `FPGA/bitstreams/helios.bit`.

## Neural Link Configuration
*   PCIe Gen3 x4
*   BAR0: 64KB (CSR)
*   DMA: AXI Stream (512-bit width)
