import serial
import time
import subprocess
import sys
import os

# Configuration
RP2040_PORT = '/dev/ttyACM0'
RP2040_BAUD = 115200
SYSTEM_CONSOLE_BIN = '/home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console'
TEMP_TCL = 'fpga/host_tools/temp_fuzz_cmd.tcl'

def log(msg):
    try:
        print(msg, flush=True)
        with open("fpga/host_tools/batch_log.txt", "a") as f:
            f.write(msg + "\n")
    except:
        pass

def create_tcl_script(val_hex):
    """Creates a standalone Tcl script to write a single value to the master."""
    script = f"""
set retry 0
set master_path ""
while {{$retry < 5}} {{
    set masters [get_service_paths master]
    if {{[llength $masters] > 0}} {{
        set master_path [lindex $masters 0]
        break
    }}
    after 1000
    incr retry
}}

if {{$master_path eq ""}} {{
    puts "ERROR: No JTAG Master found"
    exit 1
}}

if {{ [catch {{ open_service master $master_path
    master_write_32 $master_path 0x0000 {val_hex}
    close_service master $master_path
    puts "SUCCESS_WRITE {val_hex}" }} err] }} {{
    puts "ERROR: $err"
    exit 1
}}
"""
    with open(TEMP_TCL, 'w') as f:
        f.write(script)

def run_jtag_command(val):
    """Generates Tcl and runs system-console."""
    create_tcl_script(hex(val))
    try:
        # Run system-console in batch mode.
        result = subprocess.run(
            [SYSTEM_CONSOLE_BIN, '--cli', f'--script={TEMP_TCL}'],
            capture_output=True,
            text=True,
            timeout=30 
        )
        if "SUCCESS_WRITE" in result.stdout:
            return True
        else:
            log(f"JTAG Error: {result.stdout} {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log("JTAG Timeout")
        return False

def main():
    # Clear log
    with open("fpga/host_tools/batch_log.txt", "w") as f:
        f.write("--- STARTING BATCH FUZZER V6 ---\n")

    log("--- FPGA-RP2040 Pin Fuzzer (Batch Mode - V6) ---")
    
    # 1. Open Serial Connection
    try:
        # Added write_timeout and flow control settings
        ser = serial.Serial(RP2040_PORT, RP2040_BAUD, timeout=0.1, write_timeout=1, rtscts=False, dsrdtr=False)
        log(f"Connected to {RP2040_PORT}")
    except Exception as e:
        log(f"Serial Error: {e}")
        return

    # 2. Arm the RP2040
    log("Arming RP2040 (V6)...")
    try:
        ser.write(b'\n')
        time.sleep(0.5)
        if ser.in_waiting:
            resp = ser.read(ser.in_waiting).decode(errors='replace').strip()
            log(f"RP2040 Response: {resp}")
        else:
            log("No immediate response. Continuing.")
    except Exception as e:
        log(f"Arming Error: {e}")

    # 3. Iterate Pins
    for i in range(8):
        val = (1 << i)
        log(f"\n[Testing Pin {i}] Writing 0x{val:X}...")
        
        # A. Set Pin High
        if not run_jtag_command(val):
            log("  -> JTAG Write Failed. Skipping.")
            continue
        
        # B. Monitor for reaction
        start_wait = time.time()
        reacted = False
        while time.time() - start_wait < 2.0:
            try:
                if ser.in_waiting:
                    line = ser.readline().decode(errors='replace').strip()
                    log(f"  RP2040: {line}")
                    if "DONE" in line or "COMPUTATION" in line or "TRIGGER" in line:
                        log(f"\n****** FOUND IT! PIN {i} IS THE TRIGGER! ******")
                        reacted = True
                        break
                time.sleep(0.1)
            except Exception as e:
                log(f"Read Error: {e}")
        
        # C. Reset Pin Low (Important!)
        log("  Resetting...")
        run_jtag_command(0)
        
        if reacted:
            break

    ser.close()
    log("\n--- Scan Complete ---")

if __name__ == "__main__":
    main()