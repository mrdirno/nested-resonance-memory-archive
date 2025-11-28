import subprocess
import serial
import time
import sys
import select
import os

RP2040_PORT = '/dev/ttyACM0'
SYSTEM_CONSOLE = '/home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console'
TCL_SCRIPT = 'fpga/host_tools/fuzz_loop.tcl'

def main():
    print("--- Fuzz Monitor ---")
    
    # 1. Open Serial
    try:
        ser = serial.Serial(RP2040_PORT, 115200, timeout=0)
        print(f"Connected to {RP2040_PORT}")
        # Arm
        ser.write(b'\n')
    except Exception as e:
        print(f"Serial Error: {e}")
        return

    # 2. Start System Console
    print("Launching System Console...")
    proc = subprocess.Popen(
        [SYSTEM_CONSOLE, '--cli', f'--script={TCL_SCRIPT}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    # Set non-blocking stdout
    os.set_blocking(proc.stdout.fileno(), False)

    current_pin = None
    running = True
    
    start_time = time.time()

    while running:
        # Timeout check
        if time.time() - start_time > 120:
            print("Timeout!")
            break

        # Check process
        if proc.poll() is not None:
            print("System Console Exited")
            running = False
            # Process remaining output
        
        # Select
        rlist, _, _ = select.select([proc.stdout, ser], [], [], 0.1)
        
        for obj in rlist:
            if obj == proc.stdout:
                data = proc.stdout.read(1024)
                if data:
                    lines = data.decode(errors='replace').split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line: continue
                        print(f"[FPGA] {line}")
                        if "FUZZ_PIN" in line:
                            current_pin = line.split()[-1]
                            print(f">>> Now Testing Pin {current_pin}")
                        if "FUZZ_DONE" in line:
                            print("Fuzzing Done.")
                            running = False
            
            elif obj == ser:
                data = ser.read(1024)
                if data:
                    lines = data.decode(errors='replace').split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line: continue
                        print(f"[RP2040] {line}")
                        if "DONE" in line or "COMPUTATION" in line:
                            print(f"\n!!! MATCH FOUND !!! Pin {current_pin} triggered RP2040!")
                            # We can exit early
                            proc.terminate()
                            return

    proc.terminate()
    ser.close()

if __name__ == "__main__":
    main()
