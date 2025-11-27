import serial
import time
import sys

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATES = [115200, 57600, 38400, 9600]

def main():
    print(f"🚀 Starting Serial Baud Rate Sweep on {SERIAL_PORT}...")
    
    for baud in BAUD_RATES:
        print(f"\n📡 Testing Baud Rate: {baud}")
        try:
            ser = serial.Serial(SERIAL_PORT, baud, timeout=2)
            ser.write(b"\n") # Wake up
            time.sleep(0.5)
            
            # Read whatever is there
            if ser.in_waiting:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                print(f"   ✅ DATA RECEIVED: {data.strip()}")
                if "login" in data or "#" in data or "$" in data:
                    print(f"   🎉 SUCCESS! Active console found at {baud}")
                    ser.close()
                    return
            else:
                print("   ❌ No response.")
            
            ser.close()
            
        except Exception as e:
            print(f"   ⚠️ Error: {e}")

    print("\n🏁 Sweep complete. No active console detected.")

if __name__ == "__main__":
    main()
