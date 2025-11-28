import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
print(f"Connected to {ser.name}")

# Try to interrupt any running script and get REPL
ser.write(b'\x03') # Ctrl+C
time.sleep(0.5)
ser.write(b'\x03') # Ctrl+C
time.sleep(0.5)

# Read output
out = ser.read_all()
print("Output:", out.decode('utf-8', errors='replace'))

# Try sending help()
ser.write(b'help()\r\n')
time.sleep(0.5)
out = ser.read_all()
print("Help Output:", out.decode('utf-8', errors='replace'))

ser.close()

