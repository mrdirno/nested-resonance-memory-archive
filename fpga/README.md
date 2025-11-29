# FPGA Acceleration Layer: NRM Hardware Interface

**Parent Project:** [DUALITY-ZERO](https://github.com/mrdirno/nested-resonance-memory-archive)
**License:** GPL-3.0
**Status:** Phase 1 Complete - Hardware Link Verified
**Platform:** DE10-Nano (Intel Cyclone V SoC)

---

## Overview

The FPGA Acceleration Layer provides hardware-accelerated pattern detection for the Nested Resonance Memory (NRM) framework. This subsystem implements real-time autocorrelation and resonance detection in programmable logic, enabling microsecond-scale feedback loops that would be impossible in software alone.

**Current Capability:** JTAG-controlled NRM resonance detector with RP2040 feedback verification.

---

## Quick Start

### Prerequisites
- Intel Quartus Prime 24.1 (Lite Edition)
- DE10-Nano Development Board
- USB Blaster II (JTAG)
- Python 3.10+

### Program the FPGA
```bash
# From the fpga/ directory
quartus_pgm -c "DE-SoC" -m JTAG -o "p;de10-nano/projects/nrm_resonance/output_files/nrm_resonance.sof@2"
```

### Verify Hardware Link
```bash
# Check JTAG connection
jtagconfig
# Expected: DE-SoC [1-4] with device 02D020DD

# Test JTAG write (requires system-console)
echo 'set m [lindex [get_service_paths master] 0]; open_service master $m; master_write_32 $m 0x0 0x55; puts "OK"' | \
  system-console --cli
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOST (Ubuntu)                            │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │ NRM Core    │───▶│ JTAG Bridge  │───▶│ system-console    │  │
│  │ (Python)    │    │ (TCP:5000)   │    │ (Quartus)         │  │
│  └─────────────┘    └──────────────┘    └─────────┬─────────┘  │
└───────────────────────────────────────────────────┼─────────────┘
                                                    │ USB/JTAG
┌───────────────────────────────────────────────────┼─────────────┐
│                     DE10-Nano                     │             │
│  ┌────────────────────────────────────────────────▼──────────┐  │
│  │                    FPGA Fabric (Cyclone V)                │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌──────────────┐   │  │
│  │  │ JTAG-Avalon │───▶│ PIO (32b)   │───▶│ nrm_resonance│   │  │
│  │  │ Master      │    │ fuzz_out    │    │ detector     │   │  │
│  │  └─────────────┘    └──────┬──────┘    └──────────────┘   │  │
│  └────────────────────────────┼──────────────────────────────┘  │
│                               │ GPIO (AG13)                     │
│  ┌────────────────────────────▼──────────────────────────────┐  │
│  │                    RP2040 (Pico)                          │  │
│  │  GP0 ◀── Trigger Input                                    │  │
│  │  USB ──▶ Serial Feedback to Host                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Hardware Mapping (Verified)

| Signal | FPGA Pin | Connected To | Status |
|--------|----------|--------------|--------|
| `fuzz_out[0]` | AG13 | RP2040 GP0 | **VERIFIED** |
| `fuzz_out[1]` | AF13 | Arduino Header | Available |
| `fuzz_out[2]` | AG10 | Arduino Header | Available |
| `fuzz_out[3]` | AG9 | Arduino Header | Available |
| `fuzz_out[4]` | U14 | Arduino Header | Available |
| `fuzz_out[5]` | U13 | Arduino Header | Available |
| `fuzz_out[6]` | AG8 | Arduino Header | Available |
| `fuzz_out[7]` | AH8 | Arduino Header | Available |
| `led[7:0]` | Various | Onboard LEDs | Resonance Display |

---

## Core Modules

### 1. NRM Resonance Detector (`nrm_resonance.v`)
64-sample autocorrelation engine detecting periodic patterns in input streams.

**Features:**
- Configurable detection threshold
- 8-bit LED bar graph output
- JTAG-injectable test patterns
- Internal LFSR for self-test

**Location:** `de10-nano/projects/nrm_resonance/nrm_resonance.v`

### 2. JTAG-Avalon Bridge (`jtag_system`)
Platform Designer (Qsys) system providing host access to FPGA registers.

**Capabilities:**
- 32-bit read/write to PIO
- No HPS dependency (pure JTAG path)
- TCP bridge available via `bridge_server_v3.tcl`

**Location:** `de10-nano/projects/nrm_resonance/jtag_system/`

### 3. RP2040 Monitor (`main.py`)
MicroPython firmware for external computation verification.

**Protocol:**
1. Host sends `START\n` via serial
2. RP2040 monitors GP0 for rising edge
3. On trigger: Reports `FPGA_COMPUTATION_DONE`

**Location:** RP2040 internal flash (read via REPL)

---

## Host Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `bridge_server_v3.tcl` | TCP-to-JTAG proxy (port 5000) | `system-console --cli --script=bridge_server_v3.tcl` |
| `fuzz_v12.py` | Pin discovery with RP2040 protocol | `python3 fuzz_v12.py` |
| `fuzz_final.py` | Generic 32-pin scanner | `python3 fuzz_final.py` |

**Location:** `host_tools/`

---

## Project Structure

```
fpga/
├── de10-nano/
│   ├── projects/
│   │   └── nrm_resonance/          # Main Quartus project
│   │       ├── nrm_resonance.v     # Resonance detector
│   │       ├── nrm_system_wrapper.v# Top-level wrapper
│   │       ├── jtag_system/        # Qsys IP
│   │       └── output_files/       # Compiled bitstreams
│   └── NRM_INTERFACE_SPEC.md       # Protocol specification
├── host_tools/                     # Python/Tcl utilities
├── FPGA_META_OBJECTIVES.md         # Strategic planning
├── FPGA_CYCLE_LOGS.md              # Development history
├── FPGA_PROTOCOL.md                # Operational procedures
└── README.md                       # This file
```

---

## Development Status

### Completed
- [x] DE10-Nano JTAG connectivity
- [x] NRM resonance detector synthesis
- [x] JTAG-Avalon bridge integration
- [x] RP2040 pin mapping (`fuzz_out[0]` -> GP0)
- [x] End-to-end signal verification

### In Progress
- [ ] HPS bridge integration (requires GHRD pin assignments)
- [ ] Bidirectional NRM data streaming
- [ ] Real-time pattern injection from host

### Planned
- [ ] Multi-channel resonance detection
- [ ] Hardware timestamp capture
- [ ] DMA-based bulk transfer

---

## Troubleshooting

### JTAG Not Detected
```bash
# Restart JTAG daemon
pkill jtagd
jtagconfig  # Should auto-restart daemon
```

### system-console Script Hangs
Known issue: `--script=` flag causes indefinite hang after banner.

**Workaround:** Use stdin pipe instead:
```bash
echo 'puts [get_service_paths master]' | system-console --cli
```

### RP2040 Not Responding
Reset to known state:
```python
import serial
ser = serial.Serial('/dev/ttyACM0', 115200)
ser.write(b'\x03')  # Ctrl+C (interrupt)
ser.write(b'\x04')  # Ctrl+D (soft reboot)
```

---

## References

- [DE10-Nano User Manual](https://www.terasic.com.tw/cgi-bin/page/archive.pl?Language=English&No=1046)
- [Intel Quartus Prime Documentation](https://www.intel.com/content/www/us/en/docs/programmable/quartus-prime-standard/)
- [NRM Interface Specification](de10-nano/NRM_INTERFACE_SPEC.md)
- [FPGA Protocol Guide](FPGA_PROTOCOL.md)

---

## Citation

```bibtex
@software{Payopay_DUALITY_FPGA_2025,
  author = {Payopay, Aldrin},
  title = {{DUALITY-ZERO FPGA Acceleration Layer}},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/mrdirno/nested-resonance-memory-archive/tree/main/fpga}
}
```

---

**"Hardware provides the substrate. Software provides the logic. Resonance provides the signal."**
