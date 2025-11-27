# DE10-Nano Workspace

## Hardware Specs
- **Device**: Cyclone V SE 5CSEBA6U23I7
- **HPS**: Dual-core ARM Cortex-A9
- **Memory**: 1GB DDR3 (HPS), 64MB SDRAM (FPGA)
- **Interfaces**: HDMI, Gigabit Ethernet, USB OTG, UART, GPIO (Arduino header)

## Project Structure
- `projects/` - Individual FPGA projects (Quartus)
- `hps_sw/` - Software for the ARM processor (C/C++/Python)
- `common/` - Shared IP and libraries

## Toolchain
- **Quartus Prime Lite 24.1**: `/home/helios/intelFPGA_24_1/quartus/bin`
- **JTAG**: Verified (`jtagconfig`)
- **UART**: `/dev/ttyUSB0`

## Current Objectives
1. Validate compilation flow (Golden Top compilation).
2. Establish HPS-FPGA Bridge communication.
3. Port Physics Simulation to HPS (using NEON/Hardware acceleration).
