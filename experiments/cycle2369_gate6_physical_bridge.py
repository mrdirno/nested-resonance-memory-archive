"""
Gate 6: Physical Bridge Validation
Tests the SerialArray implementation using a loopback interface (socat).
Requires 'socat' to be installed: brew install socat
"""

import os
import sys
import time
import subprocess
import threading
import numpy as np

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.serial_bridge import SerialArray

def start_socat():
    """Starts a virtual serial pair using socat."""
    print("[TEST] Starting socat loopback...")
    # Create two virtual ports: ./ttyV0 and ./ttyV1
    cmd = ["socat", "-d", "-d", "pty,raw,echo=0,link=./ttyV0", "pty,raw,echo=0,link=./ttyV1"]
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    time.sleep(1) # Wait for ports to initialize
    return process

def read_socat_output(process):
    """Debug tool to see what socat is doing"""
    while True:
        if process.poll() is not None:
            break
        line = process.stderr.readline()
        if line:
            pass # print(f"[SOCAT] {line.decode().strip()}")

def run_gate6_test():
    print("="*60)
    print("GATE 6: PHYSICAL BRIDGE VALIDATION (LOOPBACK)")
    print("="*60)
    
    # Check for socat
    try:
        subprocess.run(["which", "socat"], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("❌ 'socat' not found. Please install: brew install socat")
        return False

    socat_proc = start_socat()
    
    # Thread to keep socat pipe clear
    t = threading.Thread(target=read_socat_output, args=(socat_proc,))
    t.daemon = True
    t.start()

    try:
        # Initialize SerialArray on one end
        array = SerialArray(port="./ttyV0", num_emitters=64)
        
        # Connect
        print("[TEST] Connecting to ./ttyV0...")
        if not array.connect():
            print("❌ Connection Failed")
            return False
            
        # Send Data
        print("[TEST] Sending Phase Data...")
        phases = np.linspace(0, 2*np.pi, 64)
        array.set_phases(phases)
        
        # Verify Data (Simulated Hardware on ttyV1)
        print("[TEST] Reading from ./ttyV1 (Simulated Hardware)...")
        with open("./ttyV1", "rb", buffering=0) as f:
            # Protocol: AA BB [CMD] [LEN_L] [LEN_H] [PAYLOAD...] [CS]
            # Payload = 64 bytes
            # Total = 2 + 1 + 2 + 64 + 1 = 70 bytes
            data = f.read(70)
            
            header = data[0:2]
            cmd = data[2]
            length = data[3] + (data[4] << 8)
            payload = data[5:69]
            checksum = data[69]
            
            print(f"[RECV] Header: {header.hex().upper()}")
            print(f"[RECV] Command: {cmd}")
            print(f"[RECV] Length: {length}")
            print(f"[RECV] Payload Checksum: {checksum}")
            
            if header == b'\xaa\xbb' and length == 64:
                print("✅ Packet Structure Valid")
            else:
                print("❌ Packet Structure Invalid")
                return False
                
            # Check content (first byte should be 0, last byte 255)
            if payload[0] == 0 and payload[63] == 255:
                 print("✅ Data Integrity Verified (0..255 ramp)")
            else:
                 print(f"❌ Data Mismatch: {payload[0]}..{payload[63]}")
                 return False

        array.disconnect()
        return True

    finally:
        print("[TEST] Cleaning up socat...")
        socat_proc.terminate()
        socat_proc.wait()
        if os.path.exists("./ttyV0"): os.remove("./ttyV0")
        # ttyV1 is usually cleaned up by socat, but just in case
        if os.path.exists("./ttyV1"): os.remove("./ttyV1")

if __name__ == "__main__":
    success = run_gate6_test()
    sys.exit(0 if success else 1)
