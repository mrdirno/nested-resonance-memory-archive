import serial
import time
import subprocess
import os
import sys

# Configuration
RP2040_PORT = '/dev/ttyACM0'
RP2040_BAUD = 115200
SYSTEM_CONSOLE_BIN = '/home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console'
TEMP_TCL = 'fpga/host_tools/temp_fuzz.tcl'

def generate_tcl(val):
    # Protocol: Bit 8 = Enable, Bits 0-7 = Data
    # But for Fuzzing, we drive pio_export directly.
    # So val 1 = Pin 0 High.
    
    # Note: We use 'master_write_32'
    tcl_content = f"""
set retry_count 0
while {{$retry_count < 3}} {{
    set master_paths [get_service_paths master]
    if {{[llength $master_paths] > 0}} {{
        break
    }}
    after 1000
    incr retry_count
}}

if {{[llength $master_paths] == 0}} {{
    puts "ERROR: No JTAG Master"
    return
}}

set master_path [lindex $master_paths 0]
open_service master $master_path
master_write_32 $master_path 0x0000 {val}
close_service master $master_path
puts "DONE_WRITE"
"""
    with open(TEMP_TCL, 'w') as f:
        f.write(tcl_content)

def run_system_console():
    cmd = [SYSTEM_CONSOLE_BIN, '--cli', f'--script={TEMP_TCL}']
    try:
        print("DEBUG: Launching System Console...")
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        stdout = result.stdout.decode(errors='replace')
        stderr = result.stderr.decode(errors='replace')
        print("DEBUG: System Console Return Code:", result.returncode)
        
        if "DONE_WRITE" in stdout:
            return True
        else:
            print(f"Tcl Error: {stdout} {stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("System Console Timed Out")
        return False

def log(msg):
    with open("fpga/host_tools/fuzz_debug_v2.log", "a") as f:
        f.write(msg + "\n")
    print(msg, flush=True)

def main():
    log("--- Batch Fuzzer V2.1 ---")
    
    try:
        # 1. Connect to RP2040
        try:
            ser = serial.Serial(RP2040_PORT, RP2040_BAUD, timeout=0.5) # 500ms timeout for reads
            log(f"Connected V2 to {RP2040_PORT}")
        except Exception as e:
            log(f"Error opening serial: {e}")
            return

        # 2. Arm RP2040
        log("DEBUG: Arming...")
        ser.write(b'\n')
        time.sleep(1)
        log("DEBUG: Reading initial...")
        initial = ser.read_all()
        print(f"DEBUG: Initial raw: {initial}", flush=True)
        print(f"Initial RP2040: {initial.decode(errors='replace').strip()}", flush=True)

        # 3. Fuzz Loop
        for i in range(8):
            pin_val = (1 << i)
            print(f"\n>>> Testing Pin {i} (Write 0x{pin_val:X})...")
            
            # A. Set Pin High
            generate_tcl(pin_val)
            if not run_system_console():
                print("Failed to set pin high. Retrying...")
                run_system_console()
            
            # B. Monitor
            start_time = time.time()
            found = False
            while time.time() - start_time < 2.0:
                line = ser.readline().decode(errors='replace').strip()
                if line:
                    print(f"RP2040: {line}")
                    if "DONE" in line or "COMPUTATION" in line:
                        print(f"\n!!! MATCH FOUND ON PIN {i} !!!")
                        found = True
                        break
            
            # C. Reset Pin (Low)
            generate_tcl(0)
            run_system_console()
            
            if found:
                break

        print("\n--- Fuzzing Complete ---")
        ser.close()
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
