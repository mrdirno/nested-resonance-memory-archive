import serial
import time

def read_file(filename):
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    # Enter raw REPL
    ser.write(b'\x01') # Ctrl+A
    time.sleep(0.1)
    
    # Command to print file content
    cmd = f"f = open('{filename}', 'r'); print(f.read()); f.close()"
    ser.write(cmd.encode() + b'\x04') # Ctrl+D to execute
    
    # Read response
    response = b""
    while True:
        chunk = ser.read(1024)
        if not chunk:
            break
        response += chunk
        if b'\x04>' in response: # End of raw REPL output
            break
            
    ser.close()
    
    # Clean up output (remove OK and prompt)
    try:
        content = response.split(b'OK')[1].split(b'\x04')[0].decode('utf-8')
        return content
    except Exception as e:
        return f"Error parsing response: {response}"

print("--- main.py Content ---")
print(read_file('main.py'))
