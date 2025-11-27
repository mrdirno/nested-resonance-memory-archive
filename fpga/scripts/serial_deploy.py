import serial
import time
import base64
import os
import sys

# Config
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
BINARY_PATH = 'fpga/de10-nano/hps_sw/hello_world'
CHUNK_SIZE = 128  # Small chunks for reliability

def wait_for(ser, token, timeout=10):
    end_time = time.time() + timeout
    buffer = b""
    while time.time() < end_time:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            buffer += data
            sys.stdout.buffer.write(data) # Echo to stdout for debugging
            sys.stdout.flush()
            if token.encode() in buffer:
                return True
        time.sleep(0.1)
    return False

def send_cmd(ser, cmd):
    ser.write(cmd.encode() + b'\n')
    time.sleep(0.2)

def main():
    if not os.path.exists(BINARY_PATH):
        print(f"Error: Binary not found at {BINARY_PATH}")
        return

    print(f"Opening {SERIAL_PORT}...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    print("Waking up console...")
    ser.write(b'\n\n')
    time.sleep(1)
    
    # Simple logic: Check if we need to login or if we are at prompt
    # Note: This is a basic heuristic.
    if wait_for(ser, "login:", timeout=3):
        print("Login prompt detected. Sending 'root'...")
        send_cmd(ser, "root")
        wait_for(ser, "#", timeout=5)
    else:
        print("No login prompt detected immediately. Checking for shell prompt...")
        send_cmd(ser, "") # Hit enter
        if wait_for(ser, "#", timeout=3):
             print("Shell prompt detected.")
        else:
             print("Warning: Could not confirm shell prompt. Proceeding blindly.")

    # Read binary and encode
    print("Reading and encoding binary...")
    with open(BINARY_PATH, 'rb') as f:
        binary_data = f.read()
    b64_data = base64.b64encode(binary_data).decode('utf-8')

    # Start Transfer
    print("Starting transfer...")
    send_cmd(ser, "cat > hello_world.b64")
    time.sleep(1)

    total_chunks = len(b64_data) // CHUNK_SIZE + 1
    for i in range(0, len(b64_data), CHUNK_SIZE):
        chunk = b64_data[i:i+CHUNK_SIZE]
        ser.write(chunk.encode())
        # Small delay to prevent buffer overrun on target
        time.sleep(0.05) 
        print(f"\rSending chunk {i//CHUNK_SIZE + 1}/{total_chunks}", end="")
    print("\nTransfer complete.")

    # EOF
    time.sleep(1)
    ser.write(b'\x04') # Ctrl+D
    time.sleep(1)
    
    print("Decoding...")
    send_cmd(ser, "base64 -d hello_world.b64 > hello_world")
    wait_for(ser, "#", timeout=5)

    print("Setting permissions...")
    send_cmd(ser, "chmod +x hello_world")
    wait_for(ser, "#", timeout=2)

    print("Executing...")
    send_cmd(ser, "./hello_world")
    
    # Listen for output for a few seconds
    print("Listening for output (5s)...")
    start = time.time()
    while time.time() - start < 5:
        if ser.in_waiting > 0:
            sys.stdout.buffer.write(ser.read(ser.in_waiting))
            sys.stdout.flush()
    
    # Kill the infinite loop process on target (optional cleanup)
    # send_cmd(ser, "\x03") # Ctrl+C
    
    ser.close()
    print("\nSession closed.")

if __name__ == "__main__":
    main()
