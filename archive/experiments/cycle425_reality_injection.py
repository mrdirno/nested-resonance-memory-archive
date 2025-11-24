"""
Cycle 425: The Final Integration (Reality Injection)
Role: The Architect (Physical Embodiment)
Responsibility: Connect the Perpetual Engine to Physical Interfaces.
"""
import asyncio
import json
import random
import numpy as np
import time
import copy
import sys
import glob
import math
import cmath
import sqlite3
import cv2

# --- Hardware Interfaces (Cycle 385/386 Integration) ---

# Try to import serial
try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    print("WARNING: pyserial not found. Physical Serial will be unavailable.")

class VirtualSerial:
    def __init__(self, port="VIRTUAL", baudrate=115200, timeout=1):
        self.port = port
        self.is_open = True
        print(f"[VirtualSerial] Connected to {port} @ {baudrate}")

    def send_command(self, cmd):
        if not self.is_open: return
        print(f"[VirtualSerial] TX -> {cmd}")

    def close(self):
        self.is_open = False

class PhysicalSerial:
    def __init__(self, port, baudrate=115200, timeout=1):
        if not HAS_SERIAL: raise ImportError("pyserial not installed")
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2) 
        print(f"[PhysicalSerial] Connected to {port} @ {baudrate}")

    def send_command(self, cmd):
        self.ser.write(f"{cmd}\n".encode('utf-8'))

    def close(self):
        self.ser.close()

def get_serial():
    if sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*')
    elif sys.platform.startswith('linux'):
        ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
    else:
        ports = []
    
    if ports and HAS_SERIAL:
        try:
            return PhysicalSerial(ports[0])
        except Exception as e:
            print(f"Physical Serial failed: {e}. Falling back.")
    return VirtualSerial()

class VirtualCamera:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.frame_count = 0
        print("[VirtualCamera] Initialized")

    def read(self):
        self.frame_count += 1
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Draw "levitating particle"
        cx = int(self.width/2 + 50 * np.cos(self.frame_count * 0.1))
        cy = int(self.height/2 + 50 * np.sin(self.frame_count * 0.1))
        cv2.circle(img, (cx, cy), 10, (255, 255, 255), -1)
        return True, img

    def release(self):
        pass

class PhysicalCamera:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened(): raise RuntimeError("Camera failed")
        print(f"[PhysicalCamera] Initialized (Index {index})")

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()

def get_camera():
    try:
        return PhysicalCamera(0)
    except Exception as e:
        print(f"Physical Camera failed: {e}. Falling back.")
    return VirtualCamera()

# --- Architect Components (Cycle 423) ---

class KnowledgeGraph:
    def __init__(self, db_path="reality_injection.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reality_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_num INTEGER,
                    event_type TEXT,
                    data TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def log(self, cycle, event, data):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO reality_log (cycle_num, event_type, data) VALUES (?, ?, ?)",
                         (cycle, event, json.dumps(data)))

class DreamEngine:
    def __init__(self):
        self.amplitude_scale = 6.4 

    async def hallucinate(self, shape):
        # Simplified hallucination: Just returns a fitness based on "complexity"
        mode = shape['params']['mode']
        if mode == "random": return 2.5
        if mode == "golden_spiral": return 8.0
        return 5.0

class GenerativeDesigner:
    def generate_batch(self):
        batch = []
        modes = ["random", "spherical_shell", "axis_aligned", "golden_spiral"]
        for _ in range(5):
            mode = random.choice(modes)
            x = random.uniform(-20, 20)
            y = random.uniform(-20, 20)
            z = random.uniform(20, 60)
            batch.append({"type": "point", "params": {"mode": mode}, "target": {"x": x, "y": y, "z": z}})
        return batch

class Architect:
    def __init__(self):
        self.memory = KnowledgeGraph()
        self.dreamer = DreamEngine()
        self.designer = GenerativeDesigner()
        
        # Hardware Injection
        self.hands = get_serial()
        self.eyes = get_camera()
        
    async def run_cycle(self, cycle_num):
        print(f"\n=== Cycle {cycle_num} ===")
        
        # 1. Design
        batch = self.designer.generate_batch()
        target = batch[0] # Simple selection
        print(f"[ARCHITECT] Selected Target: {target['params']['mode']} at {target['target']}")
        
        # 2. Act (Injection)
        cmd = f"MOVE {target['target']['x']:.2f} {target['target']['y']:.2f} {target['target']['z']:.2f}"
        print(f"[HANDS] Executing: {cmd}")
        self.hands.send_command(cmd)
        self.memory.log(cycle_num, "ACTION", {"cmd": cmd})
        
        # 3. Wait for Physics
        await asyncio.sleep(0.5)
        
        # 4. Observe (Reality Check)
        ret, frame = self.eyes.read()
        if ret:
            # Simple metric: Brightest pixel intensity
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)
            print(f"[EYES] Max Brightness: {max_val} at {max_loc}")
            self.memory.log(cycle_num, "OBSERVATION", {"max_brightness": max_val})
        else:
            print("[EYES] Failed to capture.")
            
        # 5. Close Loop
        print("[ARCHITECT] Cycle Complete.")

async def main():
    bot = Architect()
    
    # Homing
    bot.hands.send_command("HOME")
    await asyncio.sleep(1)
    
    for i in range(1, 6):
        await bot.run_cycle(i)
        
    bot.hands.close()
    bot.eyes.release()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass