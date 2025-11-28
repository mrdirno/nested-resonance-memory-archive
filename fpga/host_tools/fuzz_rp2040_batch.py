import serial
import time
import subprocess
import sys

# Configuration
RP2040_PORT = '/dev/ttyACM0'
RP2040_BAUD = 115200
SYSTEM_CONSOLE_BIN = '/home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console'
TEMP_TCL = 'fpga/host_tools/temp_fuzz_cmd.tcl'

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

if {{ [catch {{ 
    open_service master $master_path
    master_write_32 $master_path 0x0000 {val_hex}
    close_service master $master_path
    puts "SUCCESS_WRITE {val_hex}"
}} err] }} {{
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
        # Run system-console in batch mode. It should exit automatically after the script.
        result = subprocess.run(
            [SYSTEM_CONSOLE_BIN, '--cli', f'--script={TEMP_TCL}'],
            capture_output=True,
            text=True,
            timeout=20 # Give JVM time to start
        )
        if "SUCCESS_WRITE" in result.stdout:
            return True
        else:
            print(f"JTAG Error: {result.stdout} {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("JTAG Timeout")
        return False

def main():
    print("--- FPGA-RP2040 Pin Fuzzer (Batch Mode) ---")
    
    # 1. Open Serial Connection
    try:
        ser = serial.Serial(RP2040_PORT, RP2040_BAUD, timeout=0.1)
        print(f"Connected to {RP2040_PORT}")
    except Exception as e:
        print(f"Serial Error: {e}")
        return

    # 2. Arm the RP2040 (Expects newline)
    print("Arming RP2040...")
    ser.write(b'\n')
    time.sleep(0.5)
    print(f"RP2040 Response: {ser.read_all().decode(errors='replace').strip()}")

    # 3. Iterate Pins
    for i in range(8):
        val = (1 << i)
        print(f"\n[Testing Pin {i}] Writing 0x{val:X}...")
        
        # A. Set Pin High
        if not run_jtag_command(val):
            print("  -> JTAG Write Failed. Skipping.")
            continue
        
        # B. Monitor for reaction
        start_wait = time.time()
        reacted = False
        while time.time() - start_wait < 1.5: # Wait 1.5s for reaction
            if ser.in_waiting:
                line = ser.readline().decode(errors='replace').strip()
                print(f"  RP2040: {line}")
                if "DONE" in line or "COMPUTATION" in line:
                    print(f"\n****** FOUND IT! PIN {i} IS THE TRIGGER! ******")
                    reacted = True
                    break
            time.sleep(0.1)
        
        # C. Reset Pin Low (Important!)
        print("  Resetting...")
        run_jtag_command(0)
        
        if reacted:
            break

    ser.close()
    print("\n--- Scan Complete ---")

if __name__ == "__main__":
    main()
