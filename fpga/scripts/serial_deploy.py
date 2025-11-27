import serial
import time
import base64
import os
import sys

# Config
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATES = [115200, 57600, 38400, 9600]
BINARY_PATH = 'fpga/de10-nano/hps_sw/hello_world'
CHUNK_SIZE = 64
TIMEOUT = 2

def debug_print(msg):
    sys.stderr.write(f"[DEBUG] {msg}\n")
    sys.stderr.flush()

def read_buffer(ser):
    if ser.in_waiting > 0:
        try:
            data = ser.read(ser.in_waiting)
            text = data.decode('utf-8', errors='ignore')
            return text
        except Exception:
            return ""
    return ""

def check_baud(baud):
    debug_print(f"Testing baud rate: {baud}")
    try:
        ser = serial.Serial(SERIAL_PORT, baud, timeout=1)
        # Flush junk
        ser.read_all()
        
        # Send wakeups
        ser.write(b'\n\n')
        time.sleep(0.5)
        
        resp = read_buffer(ser)
        if len(resp) > 0:
            debug_print(f"Activity detected at {baud}!")
            return ser
            
        # Try echo
        ser.write(b"echo PING\n")
        time.sleep(0.5)
        resp = read_buffer(ser)
        if "PING" in resp:
            debug_print(f"Echo confirmed at {baud}!")
            return ser
            
        ser.close()
    except Exception as e:
        debug_print(f"Error at {baud}: {e}")
    return None

def main():
    if not os.path.exists(BINARY_PATH):
        print(f"Error: Binary not found at {BINARY_PATH}")
        return

    active_ser = None
    for baud in BAUD_RATES:
        active_ser = check_baud(baud)
        if active_ser:
            break
    
    if not active_ser:
        debug_print("CRITICAL: No baud rate successful. Target dead/hung.")
        return

    # Use the active connection
    ser = active_ser
    debug_print(f"Proceeding with {ser.baudrate}...")

    # Transfer Logic (Simplified from previous)
    debug_print("Starting transfer...")
    with open(BINARY_PATH, 'rb') as f:
        binary_data = f.read()
    b64_data = base64.b64encode(binary_data).decode('utf-8')

    ser.write(b"cat > hello_world.b64\n")
    time.sleep(0.5)
    
    for i in range(0, len(b64_data), CHUNK_SIZE):
        chunk = b64_data[i:i+CHUNK_SIZE]
        ser.write(chunk.encode())
        time.sleep(0.02)
    
    time.sleep(1)
    ser.write(b'\x04') # EOF
    time.sleep(1)
    
    ser.write(b"base64 -d hello_world.b64 > hello_world\n")
    time.sleep(0.5)
    ser.write(b"chmod +x hello_world\n")
    time.sleep(0.5)
    ser.write(b"./hello_world &\n")
    
    debug_print("Monitoring output (5s)...")
    start = time.time()
    while time.time() - start < 5:
        output = read_buffer(ser)
        if output:
            sys.stdout.write(output)
            sys.stdout.flush()
        time.sleep(0.1)

    ser.close()

if __name__ == "__main__":
    main()