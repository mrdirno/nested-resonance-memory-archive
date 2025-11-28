import serial
import time

print("Opening...")
try:
    s = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    print("Opened.")
    s.write(b'\n')
    print("Wrote.")
    time.sleep(1)
    print("Reading...")
    print(s.read_all())
    print("Done.")
    s.close()
except Exception as e:
    print(f"Error: {e}")

