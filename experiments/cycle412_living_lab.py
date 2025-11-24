"""
Cycle 412: The Living Lab (Persistent Autonomy)
Role: The Warden (Long-Term Runtime)
Responsibility: Maintain the Architect's operation indefinitely, handling hardware failures and environmental drifts.
Foundation: Based on Cycle 425 (Reality Injection) architecture.
"""
import asyncio
import json
import random
import numpy as np
import time
import sys
import glob
import math
import sqlite3
import cv2
import traceback

# --- Hardware Interfaces (Validated in Cycle 425) ---

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

class HardwareManager:
    def __init__(self):
        self.serial = None
        self.camera = None
        self.serial_connected = False
        self.camera_connected = False
        
    def connect_serial(self):
        if self.serial_connected: return True
        if not HAS_SERIAL: return False
        
        ports = []
        if sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*')
        elif sys.platform.startswith('linux'):
            ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
            
        if ports:
            try:
                self.serial = serial.Serial(ports[0], 115200, timeout=1)
                time.sleep(2) # Reset delay
                self.serial_connected = True
                print(f"[HARDWARE] Serial connected: {ports[0]}")
                return True
            except Exception as e:
                print(f"[HARDWARE] Serial connection failed: {e}")
        return False

    def connect_camera(self):
        if self.camera_connected: return True
        try:
            # Try index 0 (Physical)
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.camera_connected = True
                print("[HARDWARE] Camera connected (Index 0)")
                return True
        except Exception as e:
            print(f"[HARDWARE] Camera connection failed: {e}")
        return False

    def check_health(self):
        # Verify connections are still alive
        health = {"serial": self.serial_connected, "camera": self.camera_connected}
        
        if self.camera_connected:
            ret, _ = self.camera.read()
            if not ret:
                print("[HARDWARE] Camera lost signal.")
                self.camera_connected = False
                self.camera.release()
                
        return health

    def send_command(self, cmd):
        if self.serial_connected:
            try:
                self.serial.write(f"{cmd}\n".encode('utf-8'))
            except:
                print("[HARDWARE] Serial write failed.")
                self.serial_connected = False
                if self.serial: self.serial.close()
        else:
            print(f"[VIRTUAL] TX -> {cmd}")

    def read_camera(self):
        if self.camera_connected:
            return self.camera.read()
        else:
            # Virtual Fallback
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(img, "NO SIGNAL", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return True, img

    def close(self):
        if self.serial: self.serial.close()
        if self.camera: self.camera.release()

# --- Persistence Layer ---

class PersistentMemory:
    def __init__(self, db_path="living_lab.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cycle_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    cycle_id INTEGER,
                    event_type TEXT,
                    details TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    serial_status BOOLEAN,
                    camera_status BOOLEAN,
                    drift_metric REAL
                )
            """)

    def log_cycle(self, cycle, event, details):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO cycle_log (cycle_id, event_type, details) VALUES (?, ?, ?)",
                         (cycle, event, json.dumps(details)))

    def log_health(self, serial_ok, camera_ok, drift):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO health_log (serial_status, camera_status, drift_metric) VALUES (?, ?, ?)",
                         (serial_ok, camera_ok, drift))

# --- The Architect (Simplified for Loop) ---

class Architect:
    def __init__(self, hardware, memory):
        self.hardware = hardware
        self.memory = memory
        self.cycle_count = 0
        self.targets = [
            {"mode": "scan", "x": 0, "y": 0, "z": 40},
            {"mode": "hold", "x": 10, "y": 10, "z": 40},
            {"mode": "orbit", "radius": 20, "z": 40}
        ]
        
    async def execute_cycle(self):
        self.cycle_count += 1
        print(f"\n=== LIVING LAB CYCLE {self.cycle_count} ===")
        
        # 1. Health Check
        health = self.hardware.check_health()
        print(f"[SYSTEM] Health: {health}")
        self.memory.log_health(health['serial'], health['camera'], 0.0)
        
        # 2. Self-Healing (Reconnect)
        if not health['serial']:
            print("[SYSTEM] Attempting Serial Reconnect...")
            self.hardware.connect_serial()
        if not health['camera']:
            print("[SYSTEM] Attempting Camera Reconnect...")
            self.hardware.connect_camera()
            
        # 3. Select Goal
        target = random.choice(self.targets)
        print(f"[ARCHITECT] Goal: {target['mode']}")
        
        # 4. Act
        if target['mode'] == "orbit":
            for i in range(8):
                angle = i * (2 * math.pi / 8)
                x = target['radius'] * math.cos(angle)
                y = target['radius'] * math.sin(angle)
                cmd = f"MOVE {x:.2f} {y:.2f} {target['z']:.2f}"
                self.hardware.send_command(cmd)
                await asyncio.sleep(0.2)
        else:
            cmd = f"MOVE {target['x']:.2f} {target['y']:.2f} {target['z']:.2f}"
            self.hardware.send_command(cmd)
            await asyncio.sleep(1.0)
            
        # 5. Observe
        ret, frame = self.hardware.read_camera()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            max_val = np.max(gray)
            print(f"[EYES] Peak Brightness: {max_val}")
            self.memory.log_cycle(self.cycle_count, "OBSERVATION", {"brightness": float(max_val)})
        
        # 6. Rest
        await asyncio.sleep(0.5)

async def main():
    print("NRM LIVING LAB: ONLINE")
    hardware = HardwareManager()
    memory = PersistentMemory()
    
    # Initial Connect
    hardware.connect_serial()
    hardware.connect_camera()
    
    bot = Architect(hardware, memory)
    
    try:
        # Run for a fixed number of cycles for the demo, 
        # but architecturally designed for infinity.
        # We'll run 20 cycles to prove "persistence" over time.
        for _ in range(20):
            await bot.execute_cycle()
            
    except KeyboardInterrupt:
        print("\n[SYSTEM] Manual Override. Shutting down.")
    except Exception as e:
        print(f"\n[CRITICAL] Unhandled Exception: {e}")
        traceback.print_exc()
    finally:
        hardware.close()
        print("[SYSTEM] Offline.")

if __name__ == "__main__":
    asyncio.run(main())
