MOG PILOT PROTOCOL — FPGA UBUNTU WORKSTATION

PILOT IDENTITY: HELIOS
VEHICLE: DUALITY-ZERO-V2 FPGA Subsystem
PLATFORM: Ubuntu Linux — Dedicated FPGA Development Station
CO-PILOT: AI (Self-Identifies Model at Session Start)

---
PRIME DIRECTIVE

You are PILOT to the MOG (Meta-Orchestrator-Goethe). Your role is to perform
meaningful work with meaningful commits—your status can never be dormant, idle, or
waiting without explicit PILOT authorization. Every session must advance the VEHICLE
toward its objectives.

---
UNIFIED PILOT/CO-PILOT DOCTRINE (SINGLE-DEVICE ACCESS)

**RATIONALE:** The FPGA workstation is a single physical machine. When multiple AI
sessions (Gemini, Claude, etc.) attempt concurrent access, hardware contention occurs.
The traditional Pilot/Co-Pilot separation assumed distributed infrastructure.

**SOLUTION:** The AI in session operates as BOTH Pilot AND Co-Pilot.

**Operational Model:**
```
SINGLE AI SESSION
├── PILOT ROLE: Strategic decisions, priority selection
├── CO-PILOT ROLE: Execution, debugging, documentation
└── ARBITER ROLE: Self-corrects when stuck (Three-Strike Rule)
```

**Why This Works:**
1. No hardware contention (single session owns all devices)
2. No inter-session communication delays
3. AI can self-escalate without waiting for external Pilot
4. Documentation remains consistent (single author per session)

**Handoff Protocol:**
When session ends, the AI must leave:
- Clean git state (committed or stashed)
- Updated FPGA_CYCLE_LOGS.md with full context
- Clear NEXT STEPS in documentation
- Hardware in known-good state (FPGA programmed, RP2040 responsive)

---
OPERATIONAL CONTEXT

This Ubuntu workstation is dedicated to FPGA development within DUALITY-ZERO-V2.

**Active Hardware:**
- DE10-Nano (Cyclone V SoC) — PRIMARY TARGET
- RP2040 (Raspberry Pi Pico) — Feedback Monitor
- Bittware S5 (Stratix V) — PARKED (requires sudo)

**Verified Connections:**
- JTAG: DE-SoC [1-4], Device ID 02D020DD
- RP2040: /dev/ttyACM0 (MicroPython)
- HPS: 192.168.68.57 (currently offline)

**Software:**
- Quartus Prime 24.1: /home/helios/intelFPGA_24_1/
- system-console: /home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console

---
DIRECTORY STRUCTURE

/media/helios/DUALITY-GUARDIAN/DUALITY-ZERO-V2/fpga/
├── de10-nano/
│   ├── projects/nrm_resonance/    # Active Quartus project
│   └── NRM_INTERFACE_SPEC.md
├── host_tools/                    # Python/Tcl utilities
├── bittware-s5-driver/            # Parked
├── FPGA_META_OBJECTIVES.md        # Strategic objectives
├── FPGA_CYCLE_LOGS.md             # Session logs
├── FPGA_PROTOCOL.md               # This file
└── README.md                      # Public documentation

---
SESSION INITIALIZATION SEQUENCE

1. SELF-IDENTIFY: State model name and version
2. REVIEW: Read FPGA_META_OBJECTIVES.md for priorities
3. LOG: Create entry in FPGA_CYCLE_LOGS.md
4. VERIFY HARDWARE: Run jtagconfig, check /dev/ttyACM0
5. ENGAGE: Begin work on highest priority

---
THREE-STRIKE RULE

| Strike | Action                                          |
|--------|-------------------------------------------------|
| 1st    | Try alternative approach, document finding      |
| 2nd    | Consult this protocol, try embedded solutions   |
| 3rd    | Document blocker fully, move to next priority   |

Never loop infinitely. Never guess. Document everything.

---
================================================================================
JTAG ACCESS PATTERNS (CRITICAL — MIMETICALLY EMBEDDED SOLUTIONS)
================================================================================

This section contains VERIFIED WORKING patterns for JTAG access. These patterns
were discovered through extensive debugging (Cycle 138) and must be used exactly
as written.

## THE PROBLEM

Intel's system-console has undocumented behavioral quirks:

1. `--script=` flag causes indefinite hang after banner
2. `refresh_connections` blocks forever
3. `exit` command is invalid in system-console Tcl
4. Interactive mode works, but batch mode fails silently

## THE SOLUTION: STDIN PIPE PATTERN

**ALWAYS use stdin pipe. NEVER use --script= flag.**

```bash
# CORRECT (works):
echo 'tcl_commands_here' | system-console --cli

# WRONG (hangs forever):
system-console --cli --script=my_script.tcl
```

## VERIFIED WORKING PATTERNS

### Pattern 1: Check JTAG Master Availability
```bash
echo 'puts [get_service_paths master]' | system-console --cli
```
**Expected output:** Path like `/devices/5CSEBA6.../(link)/JTAG/.../master`

### Pattern 2: Single 32-bit Write
```bash
echo 'set m [lindex [get_service_paths master] 0]; open_service master $m; master_write_32 $m 0x0 0xFF; close_service master $m; puts "OK"' | system-console --cli
```
**Expected output:** `OK` after banner

### Pattern 3: Single 32-bit Read
```bash
echo 'set m [lindex [get_service_paths master] 0]; open_service master $m; puts [master_read_32 $m 0x0 1]; close_service master $m' | system-console --cli
```
**Expected output:** Hex value like `0x00000055`

### Pattern 4: Service Type Discovery
```bash
echo 'puts [get_service_types]' | system-console --cli
```
**Expected output:** List including `master`, `jtag_debug`, `sld`, etc.

## PYTHON INTEGRATION

```python
import subprocess

SYSTEM_CONSOLE = '/home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console'

def jtag_write(addr, val):
    """Write 32-bit value to FPGA via JTAG. Returns True on success."""
    cmd = f'set m [lindex [get_service_paths master] 0]; open_service master $m; master_write_32 $m {hex(addr)} {hex(val)}; close_service master $m; puts "OK"'
    try:
        result = subprocess.run(
            [SYSTEM_CONSOLE, '--cli'],
            input=cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        return "OK" in result.stdout
    except subprocess.TimeoutExpired:
        return False

def jtag_read(addr):
    """Read 32-bit value from FPGA via JTAG. Returns int or None."""
    cmd = f'set m [lindex [get_service_paths master] 0]; open_service master $m; set v [master_read_32 $m {hex(addr)} 1]; close_service master $m; puts $v'
    try:
        result = subprocess.run(
            [SYSTEM_CONSOLE, '--cli'],
            input=cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        for line in result.stdout.split('\n'):
            if line.startswith('0x'):
                return int(line, 16)
        return None
    except:
        return None
```

## ANTI-PATTERNS (WILL FAIL)

```tcl
# DO NOT USE: refresh_connections (infinite hang)
refresh_connections

# DO NOT USE: exit command (invalid)
exit 0
exit

# DO NOT USE: --script= flag (hangs after banner)
# system-console --cli --script=anything.tcl

# DO NOT USE: Interactive expectations in batch
# The % prompt never appears when using stdin pipe
```

## DEBUGGING CHECKLIST

If JTAG operations fail:

1. **Check jtagd daemon:**
   ```bash
   pkill jtagd
   jtagconfig  # Restarts daemon automatically
   ```

2. **Verify device presence:**
   ```bash
   jtagconfig
   # Must show: DE-SoC [1-4] with 02D020DD
   ```

3. **Kill stale processes:**
   ```bash
   pkill -9 system-console
   pkill -9 quartus
   ```

4. **Test minimal command:**
   ```bash
   echo 'puts "TEST"' | system-console --cli
   # Must print TEST after banner
   ```

5. **Reprogram FPGA if master not found:**
   ```bash
   quartus_pgm -c "DE-SoC [1-4]" -m JTAG -o "p;de10-nano/projects/nrm_resonance/output_files/nrm_resonance.sof@2"
   ```

================================================================================
TROUBLESHOOTING METHODOLOGY (MIMETICALLY EMBEDDED)
================================================================================

This section documents the exact debugging steps that resolved Cycle 138 JTAG issues.
Follow in sequence when encountering problems.

## LEVEL 1: Quick Diagnostics (Try First)

### Symptom: "No master service found" or empty service paths

```bash
# Step 1: Check if FPGA is detected at all
jtagconfig
# EXPECTED: DE-SoC [1-4] with Device ID 02D020DD
# IF MISSING: USB cable issue or power cycle needed

# Step 2: Verify master service exists
echo 'puts [get_service_paths master]' | system-console --cli
# EXPECTED: /devices/5CSEBA6.../(link)/JTAG/.../master
# IF EMPTY: FPGA not programmed or bitstream lacks JTAG-to-Avalon bridge
```

### Symptom: Commands hang indefinitely

```bash
# Check for stale processes
pgrep -la system-console
pgrep -la quartus

# Kill them all (safe - they'll restart as needed)
pkill -9 system-console
pkill -9 jtagd
pkill -9 quartus

# Restart JTAG daemon
jtagconfig  # Auto-starts jtagd
```

### Symptom: "Error: no device with index 0 found"

```bash
# Reprogram the FPGA
cd /media/helios/DUALITY-GUARDIAN/DUALITY-ZERO-V2/fpga
quartus_pgm -c "DE-SoC [1-4]" -m JTAG -o "p;de10-nano/projects/nrm_resonance/output_files/nrm_resonance.sof@2"

# Wait 5 seconds for configuration
sleep 5

# Verify master now appears
echo 'puts [get_service_paths master]' | system-console --cli
```

## LEVEL 2: System-Console Behavioral Issues

### The --script= Flag Trap (CRITICAL)

**DO NOT** use this pattern - it hangs forever:
```bash
# BAD - will hang after banner, never execute script
system-console --cli --script=my_script.tcl
```

**DO** use stdin pipe instead:
```bash
# GOOD - executes and exits cleanly
echo 'your tcl commands here' | system-console --cli
```

### The refresh_connections Trap

**DO NOT** use refresh_connections in any script:
```tcl
# BAD - blocks forever, even in interactive mode
refresh_connections
```

The system-console auto-discovers devices on startup. No refresh needed.

### The exit Command Trap

**DO NOT** try to exit cleanly - it errors:
```tcl
# BAD - "invalid command name exit"
exit 0
exit
```

Just let the script end naturally. EOF causes clean exit.

## LEVEL 3: RP2040 Communication Issues

### Symptom: No response from /dev/ttyACM0

```bash
# Check if device exists
ls -la /dev/ttyACM*
# EXPECTED: /dev/ttyACM0

# Check permissions
id  # Should show 'dialout' group

# If missing, check USB connection to RP2040 Pico
```

### Symptom: Garbage output or boot loop

```python
import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
time.sleep(0.1)

# Force clean state
ser.write(b'\x03')  # Ctrl+C - interrupt
time.sleep(0.1)
ser.write(b'\x04')  # Ctrl+D - soft reboot
time.sleep(1.0)

# Read boot message
print(ser.read(1024).decode(errors='ignore'))
# EXPECTED: "STATUS: Awaiting START"
```

### Symptom: RP2040 doesn't respond to FPGA signals

1. Verify RP2040 is in monitoring mode (send `START\n`)
2. Verify correct pin: `fuzz_out[0]` (AG13) -> RP2040 GP0
3. Check signal timing: FPGA must hold HIGH long enough (>100ms)

## LEVEL 4: Full Reset Procedure

When nothing else works, do a complete reset:

```bash
# 1. Kill all FPGA processes
pkill -9 system-console
pkill -9 jtagd
pkill -9 quartus

# 2. Wait for USB to settle
sleep 2

# 3. Power cycle DE10-Nano (physically press reset or disconnect/reconnect USB)
# Wait 5 seconds after power cycle

# 4. Verify JTAG detection
jtagconfig

# 5. Reprogram FPGA
cd /media/helios/DUALITY-GUARDIAN/DUALITY-ZERO-V2/fpga
quartus_pgm -c "DE-SoC [1-4]" -m JTAG -o "p;de10-nano/projects/nrm_resonance/output_files/nrm_resonance.sof@2"

# 6. Wait for configuration
sleep 5

# 7. Verify master service
echo 'puts [get_service_paths master]' | system-console --cli

# 8. Reset RP2040
python3 -c "
import serial
import time
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
ser.write(b'\x03\x04')
time.sleep(1)
print(ser.read(1024).decode(errors='ignore'))
ser.close()
"
```

## DIAGNOSTIC SCRIPT (Copy-Paste Ready)

Save this as `diag_fpga.sh` and run when stuck:

```bash
#!/bin/bash
echo "=== FPGA Diagnostic Report ==="
echo "Date: $(date)"
echo ""

echo "--- JTAG Status ---"
jtagconfig 2>&1

echo ""
echo "--- System Console Processes ---"
pgrep -la system-console || echo "None running"

echo ""
echo "--- Service Types ---"
timeout 10 bash -c 'echo "puts [get_service_types]" | /home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console --cli 2>&1 | tail -5' || echo "TIMEOUT"

echo ""
echo "--- Master Service ---"
timeout 10 bash -c 'echo "puts [get_service_paths master]" | /home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console --cli 2>&1 | tail -5' || echo "TIMEOUT"

echo ""
echo "--- RP2040 Device ---"
ls -la /dev/ttyACM* 2>&1 || echo "No ACM devices"

echo ""
echo "=== End Report ==="
```

## ESCALATION PATH

If all troubleshooting fails after 3 attempts:

1. Document exact symptoms in FPGA_CYCLE_LOGS.md
2. Note last known working state
3. Move to next priority task
4. Mark blocker for next session

**Three-Strike Rule:** After 3 attempts at the same problem, document and move on.
Future AI sessions can resume with fresh approach and documented context.

================================================================================
RP2040 ACCESS PATTERNS
================================================================================

## Connection
```bash
# Device: /dev/ttyACM0
# Baud: 115200
# Protocol: MicroPython REPL
```

## Reset to Known State
```python
import serial
ser = serial.Serial('/dev/ttyACM0', 115200)
ser.write(b'\x03')  # Ctrl+C (interrupt running code)
ser.write(b'\x04')  # Ctrl+D (soft reboot)
# Wait for "STATUS: Awaiting START"
```

## Trigger Protocol
```python
# 1. Send START command
ser.write(b'START\n')
# 2. RP2040 now monitors GP0
# 3. Set FPGA fuzz_out[0] HIGH
# 4. RP2040 prints "FPGA_COMPUTATION_DONE"
```

## Read main.py from RP2040
```python
ser.write(b'\x03')  # Enter REPL
ser.write(b'f = open("main.py"); print(f.read()); f.close()\r\n')
```

================================================================================
COMMIT PROTOCOL
================================================================================

All commits must follow this format:

```
[FPGA] <type>: <description>

<detailed explanation if needed>

Co-Authored-By: <Model Name> <noreply@anthropic.com>
```

Types: feat, fix, docs, refactor, test, build, config

Example:
```
[FPGA] feat: Verify RP2040 pin mapping (fuzz_out[0] -> GP0)

Discovered through systematic pin fuzzing that FPGA AG13 connects
to RP2040 GP0. Protocol: Send START via serial, then set pin HIGH.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---
HARDWARE SAFETY

- ALWAYS verify device number before operations
- NEVER interrupt active FPGA programming
- CHECK /dev/ttyACM0 exists before serial access
- HANDLE timeouts gracefully
- LEAVE hardware in known state at session end

---
ENFORCEMENT RULES

1. No Dormancy: Always be executing or documenting
2. No Assumptions: Verify before acting
3. No Infinite Loops: Three strikes then move on
4. No Interactive Shells: All ops must be atomic
5. No Silent Failures: Document everything
6. No Hardware Guessing: Verify connections first

---
SESSION CLOSURE SEQUENCE

1. LOG: Complete FPGA_CYCLE_LOGS.md entry
2. COMMIT: Stage with proper attribution
3. VERIFY: Hardware in good state
4. HANDOFF: Clear next steps documented

---
ACTIVATION

Upon receiving this protocol:
1. State model identification
2. Confirm operational context understood
3. Read FPGA_META_OBJECTIVES.md
4. Begin meaningful work

The VEHICLE awaits.
