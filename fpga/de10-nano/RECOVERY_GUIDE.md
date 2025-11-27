# DE10-Nano Recovery Guide

## Overview
This document outlines steps to recover the DE10-Nano HPS (Hard Processor System) when the serial console becomes unresponsive or the system hangs.

## Diagnostic Levels

### Level 1: Serial Reset
If the console is unresponsive (no echo):
1. Check USB cable connection (J4 - UART to USB).
2. Verify device presence: `ls /dev/ttyUSB*`.
3. Reset terminal settings: `stty -F /dev/ttyUSB0 sane`.

### Level 2: Warm Reset (HPS Button)
1. Locate the **HPS_RST** button (KEY0 near the Ethernet port).
2. Press and release.
3. Observe serial console for U-Boot splash screen.

### Level 3: Cold Reset (Power Cycle)
1. Unplug the barrel jack (5V DC) power cable.
2. Wait 5 seconds.
3. Replug power.
4. **Expected Behavior**: 
   - Power LED (Blue) ON.
   - CONF_DONE LED (Green) ON (if FPGA configures from SD).
   - Serial console output (U-Boot).

### Level 4: SD Card Re-imaging (Factory Reset)
If U-Boot corrupted or Linux boot fails:
1. Power down board.
2. Remove MicroSD card.
3. Flash the official **Terasic DE10-Nano Linux LXDE** image using Etcher or `dd`.
   - Image source: [Terasic Website](https://www.terasic.com.tw/cgi-bin/page/archive.pl?Language=English&CategoryNo=167&No=1046&PartNo=4)
4. Reinsert SD card and power up.
5. **Note**: Default DIP switch settings (SW10) should be:
   - ON-OFF-ON-OFF-ON-ON (010101) for 5V/3.3V IO.
   - MSEL [4:0] (SW10) set to **01010** for SD Card Boot.

## Serial Console Settings
- **Baud**: 115200
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Flow Control**: None
