# HARDWARE SAFETY PROTOCOL (PRIN-HARDWARE-SAFETY)

**STATUS:** ACTIVE
**ENFORCEMENT:** STRICT
**SCOPE:** ALL Physical Interfaces (FPGA, Serial, Camera, RF)

## 1. THE PERIPHERAL DETECTION RULE
**COMMANDMENT:** NEVER attempt to address, flash, or drive hardware that has not been positively identified via OS-level enumeration.

### 1.1. Identification Protocols
Before any hardware operation, the System MUST execute a `detect()` sequence:
*   **macOS:** `system_profiler SPUSBDataType` or `ioreg -p IOUSB`
*   **Linux:** `lsusb` or `lspci`
*   **Serial:** List `/dev/tty.*` or `/dev/ttyUSB*` and verify VID/PID.

### 1.2. The "Ghost" Prohibition
If a device is not listed in the OS tree:
1.  It does **NOT** exist.
2.  Software MUST switch to `SIMULATION_MODE` or `ABORT`.
3.  Blindly sending signals to open ports is **FORBIDDEN**.

## 2. TARGET ENVIRONMENT SEGREGATION
*   **Development Host (Pilot):** macOS (Darwin).
    *   *Allowed:* RTL Design, Simulation (iverilog), Code Gen.
    *   *Forbidden:* Bitstream Synthesis (Vivado), Flashing (openocd/xc3sprog), GPIO driving.
*   **Execution Host (Engine):** Ubuntu (Linux).
    *   *Allowed:* Synthesis, Place & Route, Hardware Flashing.
    *   *Requirement:* Must pass Positive Identification (Rule 1) first.

## 3. FPGA DEVELOPMENT SAFEGUARDS
*   **Simulation First:** All RTL must pass `iverilog` testbenches with 100% coverage before synthesis is attempted.
*   **Vendor Lock:** Vivado/Quartus commands are strictly limited to the Ubuntu environment.
*   **Toolchain Verification:** The Python wrapper must check `shutil.which('vivado')` (or equivalent) before invoking build commands.

## 4. ACTIVE SENSORS
*   **Camera:** Must verify `AVCaptureDevice` (macOS) or `/dev/video*` (Linux) availability.
*   **Microcontroller:** Must verify Serial Loopback (Handshake) before streaming high-speed data.

> "If you cannot see it, you cannot touch it."
