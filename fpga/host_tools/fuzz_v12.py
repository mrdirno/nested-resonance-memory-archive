#!/usr/bin/env python3
"""
FPGA-RP2040 Pin Fuzzer V12
Now that we know:
- RP2040 monitors GP0 for FPGA DONE signal
- It needs a "START" command first via serial
- Then it watches GP0 (with pull-down) for HIGH
"""

import serial
import time
import subprocess

# Configuration
RP2040_PORT = '/dev/ttyACM0'
RP2040_BAUD = 115200
SYSTEM_CONSOLE = '/home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console'
LOG_FILE = '/media/helios/DUALITY-GUARDIAN/DUALITY-ZERO-V2/fpga/host_tools/fuzz_v12_log.txt'

def log(msg):
    print(msg, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

def jtag_write(val):
    """Write value to FPGA PIO via JTAG."""
    val_hex = hex(val)
    cmd = f'set m [lindex [get_service_paths master] 0]; open_service master $m; master_write_32 $m 0x0 {val_hex}; close_service master $m; puts "W_OK"'
    try:
        result = subprocess.run(
            [SYSTEM_CONSOLE, '--cli'],
            input=cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        return "W_OK" in result.stdout
    except:
        return False

def main():
    with open(LOG_FILE, "w") as f:
        f.write(f"=== Pin Fuzzer V12 (Protocol-Aware) ===\n")
        f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    log("=== Pin Fuzzer V12 ===")
    log("RP2040 waits for serial START, then monitors GP0")
    log("")

    # Open serial
    try:
        ser = serial.Serial(RP2040_PORT, RP2040_BAUD, timeout=1)
        log("Serial: Connected")
    except Exception as e:
        log(f"Serial Error: {e}")
        return

    # Soft reboot to get clean state
    log("\n--- Resetting RP2040 ---")
    ser.write(b'\x03')  # Ctrl+C
    time.sleep(0.3)
    ser.write(b'\x04')  # Ctrl+D (soft reboot)
    time.sleep(1)

    # Read boot messages
    if ser.in_waiting:
        boot = ser.read(ser.in_waiting).decode(errors='replace')
        for line in boot.split('\n'):
            if line.strip():
                log(f"  {line.strip()}")

    # Ensure JTAG reset
    log("\n--- Testing JTAG ---")
    if not jtag_write(0):
        log("JTAG FAILED")
        ser.close()
        return
    log("JTAG: OK")

    # Now scan pins by:
    # 1. Send START to RP2040
    # 2. Set pin HIGH
    # 3. Check for FPGA_COMPUTATION_DONE

    log("\n--- Pin Scan (Protocol-Aware) ---")
    found = None

    for pin in range(8):  # Only 8 pins connected
        val = 1 << pin
        log(f"Pin {pin}: 0x{val:02X}")

        # Send START to arm the RP2040
        ser.write(b'START\n')
        time.sleep(0.3)

        # Read any response (e.g., "STATUS: START received. Monitoring...")
        if ser.in_waiting:
            resp = ser.read(ser.in_waiting).decode(errors='replace')
            for line in resp.strip().split('\n'):
                if line.strip():
                    log(f"  RP2040: {line.strip()}")

        # Write the pin value
        if not jtag_write(val):
            log("  Write failed")
            continue

        # Wait for response
        start = time.time()
        while time.time() - start < 2.0:
            if ser.in_waiting:
                line = ser.readline().decode(errors='replace').strip()
                if line:
                    log(f"  RP2040: {line}")
                    if "COMPUTATION_DONE" in line or "DONE" in line.upper():
                        log(f"\n*** PIN {pin} IS THE TRIGGER (GP0 on RP2040)! ***\n")
                        found = pin
                        break
            time.sleep(0.03)

        # Reset
        jtag_write(0)

        if found is not None:
            break

        # Wait a bit before next iteration (RP2040 will timeout after 15s)
        time.sleep(0.5)

    ser.close()

    log("\n--- Result ---")
    if found is not None:
        log(f"SUCCESS! fuzz_out[{found}] connects to RP2040 GP0")
        log(f"This is Arduino header pin AG13/AF13/etc (see QSF)")
    else:
        log("No trigger found.")
        log("RP2040 GP0 may not be wired to any of fuzz_out[0:7]")

    log("\n=== Done ===")

if __name__ == "__main__":
    main()
