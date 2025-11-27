import serial
import time
import base64
import os
import sys

# Config
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
BINARY_PATH = 'fpga/de10-nano/hps_sw/hello_world'
CHUNK_SIZE = 64  # Smaller chunks
TIMEOUT = 2      # Default read timeout

def debug_print(msg):
    sys.stderr.write(f"[DEBUG] {msg}\n")
    sys.stderr.flush()

def read_buffer(ser):
    """Reads all available data from the buffer."""
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        try:
            text = data.decode('utf-8', errors='replace')
            sys.stdout.write(text)
            sys.stdout.flush()
            return text
        except Exception:
            return ""
    return ""

def send_cmd(ser, cmd):
    debug_print(f"Sending: {cmd}")
    ser.write(cmd.encode() + b'\n')
    time.sleep(0.5)
    read_buffer(ser) # Drain echo

def main():
    if not os.path.exists(BINARY_PATH):
        print(f"Error: Binary not found at {BINARY_PATH}")
        return

    debug_print(f"Opening {SERIAL_PORT} at {BAUD_RATE}...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    # Wake up
    debug_print("Sending wake-up signals...")
    for _ in range(5):
        ser.write(b'\n')
        time.sleep(0.2)
        read_buffer(ser)

    # Check state
    debug_print("Checking for prompt...")
    send_cmd(ser, "echo 'LINK_CHECK'")
    time.sleep(1)
    output = read_buffer(ser)
    
    if "LINK_CHECK" not in output:
        debug_print("No response to echo. Attempting blind login...")
        send_cmd(ser, "root") # Try login
        time.sleep(2)
        read_buffer(ser)
        send_cmd(ser, "echo 'LOGIN_CHECK'")
        time.sleep(1)
        if "LOGIN_CHECK" not in read_buffer(ser):
            debug_print("CRITICAL: Target is unresponsive or baud rate mismatch.")
            ser.close()
            return

    # Transfer
    debug_print("Starting transfer...")
    with open(BINARY_PATH, 'rb') as f:
        binary_data = f.read()
    b64_data = base64.b64encode(binary_data).decode('utf-8')

    send_cmd(ser, "cat > hello_world.b64")
    
    total_chunks = len(b64_data) // CHUNK_SIZE + 1
    for i in range(0, len(b64_data), CHUNK_SIZE):
        chunk = b64_data[i:i+CHUNK_SIZE]
        ser.write(chunk.encode())
        time.sleep(0.02) # Inter-chunk delay
        if i % (CHUNK_SIZE * 10) == 0:
             read_buffer(ser) # Occasional drain
    
    time.sleep(1)
    ser.write(b'\x04') # Ctrl+D (EOF)
    time.sleep(1)
    read_buffer(ser)

    debug_print("Transfer complete. Decoding...")
    send_cmd(ser, "base64 -d hello_world.b64 > hello_world")
    send_cmd(ser, "chmod +x hello_world")
    
    debug_print("Executing...")
    send_cmd(ser, "./hello_world &") # Run in background to avoid blocking shell if it loops
    
    # Monitor
    debug_print("Monitoring output (10s)...")
    start_time = time.time()
    while time.time() - start_time < 10:
        read_buffer(ser)
        time.sleep(0.1)
    
    # Cleanup
    send_cmd(ser, "killall hello_world")
    ser.close()
    debug_print("Session closed.")

if __name__ == "__main__":
    main()
