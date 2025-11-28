import socket
import serial
import time
import sys

# Configuration
JTAG_HOST = '127.0.0.1'
JTAG_PORT = 5000
RP2040_PORT = '/dev/ttyACM0'
RP2040_BAUD = 115200

def connect_jtag():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((JTAG_HOST, JTAG_PORT))
    return s

def send_jtag_cmd(sock, cmd):
    sock.sendall((cmd + "\n").encode())
    resp = sock.recv(1024).decode().strip()
    return resp

def main():
    print("--- Starting FPGA-RP2040 Pin Fuzzer ---")
    
    # 1. Connect to RP2040
    try:
        ser = serial.Serial(RP2040_PORT, RP2040_BAUD, timeout=0.1)
        print(f"Connected to RP2040 on {RP2040_PORT}")
    except Exception as e:
        print(f"Error connecting to RP2040: {e}")
        return

    # 2. Arm RP2040 Monitor
    print("Arming RP2040...")
    ser.write(b'\n') # Send newline to start monitoring
    time.sleep(0.5)
    out = ser.read_all().decode(errors='replace')
    print(f"RP2040 Output: {out.strip()}")
    
    if "Monitoring" not in out and "Awaiting" not in out:
        print("Warning: RP2040 might not be ready. Resetting...")
        ser.write(b'\x03') # Ctrl+C
        time.sleep(0.1)
        ser.write(b'\x04') # Soft Reset
        time.sleep(1.0)
        ser.write(b'\n') # Arm again
        time.sleep(0.5)
        print(f"RP2040 Output after reset: {ser.read_all().decode(errors='replace').strip()}")

    # 3. Connect to JTAG Bridge
    try:
        jtag = connect_jtag()
        print("Connected to JTAG Bridge")
    except Exception as e:
        print(f"Error connecting to JTAG Bridge: {e}")
        return

    # 4. Fuzz Loop
    print("Fuzzing pins 0-7...")
    
    # Disable Injection first
    send_jtag_cmd(jtag, "WR 0x0000 0x000") 

    for i in range(8):
        # Protocol: Bit 8 is Enable, Bits 7-0 are Data
        # We want to drive ONE pin high at a time.
        # Since we don't know which bit in 'inject_data' maps to which pin physically 
        # (it's 1:1 in Verilog, but we are testing Arduino IO 0-7 mapping),
        # we will output 0xFF (all high) just to see if ANY connection works first?
        # No, let's try one by one to identify the specific pin.
        
        val = (1 << i) # 1, 2, 4, 8...
        
        # To assert the pin, we need inject_en (bit 8) = 1
        # And we set the data bits.
        # Note: nrm_resonance.v: test_data <= inject_data (if en)
        # But led output <= resonance_display (derived from test_data)
        # Wait, we need to know if the RP2040 is connected to the LED output pins or the 'fuzz_out' pins?
        # In nrm_system_wrapper.v: assign fuzz_out = pio_export;
        # pio_export is 32 bits. JTAG writes 32 bits.
        # So writing to JTAG PIO directly drives fuzz_out.
        # Bit 0 of PIO -> fuzz_out[0] (Arduino IO0)
        # ...
        # Bit 7 of PIO -> fuzz_out[7] (Arduino IO7)
        
        cmd_val = (1 << i) # Just toggle the specific bit
        # We don't need Bit 8 (inject_en) for fuzz_out, because fuzz_out is directly assigned to pio_export.
        # inject_en is only for the internal logic (LEDs). 
        
        print(f"Testing Pin {i} (Value 0x{cmd_val:02X})...")
        send_jtag_cmd(jtag, f"WR 0x0000 0x{cmd_val:03X}")
        
        # Wait and check RP2040
        time.sleep(0.5)
        out = ser.read_all().decode(errors='replace')
        if out:
            print(f"  RP2040: {out.strip()}")
        
        if "DONE" in out or "COMPUTATION" in out:
            print(f"*** MATCH FOUND! Pin {i} triggers RP2040! ***")
            # Keep it high for a moment
            time.sleep(1)
            send_jtag_cmd(jtag, "WR 0x0000 0x000")
            return

        # Reset
        send_jtag_cmd(jtag, "WR 0x0000 0x000")
        time.sleep(0.1)

    print("Fuzzing complete. No match found on Pins 0-7.")
    jtag.close()
    ser.close()

if __name__ == "__main__":
    main()
