import serial
import subprocess
import sys

def check_serial():
    try:
        print("[SERIAL] Connecting to /dev/ttyACM0...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        print("[SERIAL] Success. Sending ping...")
        ser.write(b'\n')
        resp = ser.read(100)
        print(f"[SERIAL] Response: {resp}")
        ser.close()
        return True
    except Exception as e:
        print(f"[SERIAL] FAILED: {e}")
        return False

def check_jtag():
    print("[JTAG] Checking jtagconfig...")
    try:
        res = subprocess.run(['/home/helios/intelFPGA_24_1/quartus/bin/jtagconfig'], capture_output=True, text=True, timeout=5)
        print(f"[JTAG] Output:\n{res.stdout}")
        if "DE-SoC" in res.stdout:
            return True
        return False
    except Exception as e:
        print(f"[JTAG] FAILED: {e}")
        return False

if __name__ == "__main__":
    s = check_serial()
    j = check_jtag()
    if s and j:
        print("HARDWARE READY")
        sys.exit(0)
    else:
        print("HARDWARE FAILURE")
        sys.exit(1)
