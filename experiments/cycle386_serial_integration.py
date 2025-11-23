import time
import math
import sys
import glob

# Try to import serial, but don't crash if missing (though we installed it)
try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    print("WARNING: pyserial not found. Physical Serial will be unavailable.")

class VirtualSerial:
    """
    Simulates a serial connection to the Acoustic Controller.
    Used as fallback if physical hardware is unavailable.
    """
    def __init__(self, port="VIRTUAL", baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.is_open = True
        print(f"[VirtualSerial] Connected to {port} @ {baudrate}")

    def write(self, data):
        """
        Simulates sending data. Prints to stdout.
        """
        if not self.is_open:
            raise RuntimeError("Port is closed")
        
        # Decode bytes to string for display
        try:
            msg = data.decode('utf-8').strip()
            print(f"[VirtualSerial] TX -> {msg}")
        except:
            print(f"[VirtualSerial] TX -> {data}")
        return len(data)

    def readline(self):
        """
        Simulates receiving a response.
        """
        if not self.is_open:
            raise RuntimeError("Port is closed")
        # Simulate generic "OK" response
        return b"OK\n"

    def close(self):
        self.is_open = False
        print("[VirtualSerial] Connection Closed")

class PhysicalSerial:
    """
    Wraps the actual serial connection.
    """
    def __init__(self, port, baudrate=115200, timeout=1):
        if not HAS_SERIAL:
            raise ImportError("pyserial not installed")
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2) # Wait for Arduino reset
        print(f"[PhysicalSerial] Connected to {port} @ {baudrate}")

    def write(self, data):
        return self.ser.write(data)

    def readline(self):
        return self.ser.readline()

    def close(self):
        self.ser.close()
        print("[PhysicalSerial] Connection Closed")

def find_serial_port():
    """
    Attempts to find a valid serial port.
    """
    if sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*')
    elif sys.platform.startswith('linux'):
        ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
    else:
        ports = []
    
    if ports:
        return ports[0]
    return None

def get_serial():
    """
    Factory to get the best available serial interface.
    """
    port = find_serial_port()
    
    if port and HAS_SERIAL:
        try:
            print(f"Attempting to connect to Physical Serial at {port}...")
            return PhysicalSerial(port)
        except Exception as e:
            print(f"Physical Serial failed: {e}")
            print("Falling back to Virtual Serial...")
            return VirtualSerial()
    else:
        print("No physical serial port found (or pyserial missing).")
        print("Falling back to Virtual Serial...")
        return VirtualSerial()

def run_experiment():
    print("Cycle 386: Physical Serial Integration")
    print("======================================")
    
    ser = get_serial()
    
    try:
        # 1. Homing Sequence
        print("\n--- Homing Sequence ---")
        commands = [
            "HOME",
            "ENABLE",
            "SET_POWER 50"
        ]
        for cmd in commands:
            ser.write(f"{cmd}\n".encode('utf-8'))
            time.sleep(0.1)
            
        # 2. Circle Trajectory
        print("\n--- Circle Trajectory ---")
        center_x, center_y, z = 50, 50, 50
        radius = 20
        for i in range(10):
            angle = i * (2 * math.pi / 10)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            cmd = f"MOVE {x:.2f} {y:.2f} {z:.2f}"
            ser.write(f"{cmd}\n".encode('utf-8'))
            time.sleep(0.1)
            
        print("\n--- Shutdown ---")
        ser.write(b"DISABLE\n")
        
    except Exception as e:
        print(f"Error during transmission: {e}")
    finally:
        ser.close()
        print("SUCCESS: Serial pipeline verified.")

if __name__ == "__main__":
    run_experiment()
