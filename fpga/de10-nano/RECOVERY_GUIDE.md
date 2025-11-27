# DE10-Nano Recovery Guide

## Symptom
- **Serial Console Dead:** No response from `/dev/ttyUSB0` (115200 baud).
- **FPGA Alive:** JTAG works, "Breathing LED" runs.
- **Diagnosis:** HPS (ARM Processor) is hung, crashed, or stuck in a boot loop.

## Recovery Steps

### 1. Warm Reset (Button)
- Locate the **HPS_RST** button (KEY0) on the board.
- Press and hold for 1 second.
- **Check:** Watch `screen /dev/ttyUSB0 115200` for boot logs.

### 2. Cold Reset (Power Cycle)
- Unplug the 5V DC barrel jack.
- Wait 10 seconds (let capacitors drain).
- Replug power.
- **Check:** Blue POWER LED should light up. Boot logs should appear on serial.

### 3. SD Card Re-Flash (If Boot Fails)
- If the HPS fails to boot after power cycle (no logs), the SD card image might be corrupted.
- **Action:**
    1. Eject microSD card.
    2. Mount on PC.
    3. Re-flash the `DE10_Nano_LXDE.img` (or equivalent) using `dd` or Etcher.
    4. Verify partition table.

### 4. Factory Default Restore
- If all else fails, ensure the **MSEL** switches (switches on the back) are set to default (Standard Mode):
    - MSEL[4:0] = 01010 (Usually default for SD Boot).

---
**Current Status:** Awaiting Level 2 (Cold Reset).