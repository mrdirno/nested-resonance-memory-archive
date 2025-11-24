"""
Cycle 413: Environmental Adaptation
Role: The Tracker
Responsibility: Adapt to environmental changes (Target Drift) using visual feedback.
"""
import asyncio
import numpy as np
import time
import sys
import glob
import math
import cv2
import traceback

# --- Reuse Hardware Layer (Dry) ---
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
        ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*') + glob.glob('/dev/ttyACM*')
        if ports:
            try:
                self.serial = serial.Serial(ports[0], 115200, timeout=1)
                time.sleep(2)
                self.serial_connected = True
                print(f"[HARDWARE] Serial connected: {ports[0]}")
                return True
            except: pass
        return False

    def connect_camera(self):
        if self.camera_connected: return True
        try:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.camera_connected = True
                print("[HARDWARE] Camera connected (Index 0)")
                return True
        except: pass
        return False

    def send_command(self, cmd):
        if self.serial_connected:
            try: self.serial.write(f"{cmd}\n".encode('utf-8'))
            except: self.serial_connected = False
        else:
            print(f"[VIRTUAL] TX -> {cmd}")

    def read_camera(self):
        if self.camera_connected:
            return self.camera.read()
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Simulate a moving light source
        t = time.time()
        cx = int(320 + 100 * math.sin(t))
        cy = int(240 + 100 * math.cos(t))
        cv2.circle(img, (cx, cy), 20, (255, 255, 255), -1)
        return True, img

    def close(self):
        if self.serial: self.serial.close()
        if self.camera: self.camera.release()

# --- Adaptive Architect ---

class Architect:
    def __init__(self, hardware):
        self.hardware = hardware
        self.current_pos = {"x": 0, "y": 0, "z": 40}
        self.pid = {"p": 0.1, "i": 0.0, "d": 0.05}
        self.last_error = {"x": 0, "y": 0}
        
    async def track_light(self):
        print("\n=== CYCLE 413: ADAPTIVE TRACKING ONLINE ===")
        print("Objective: Center the Acoustic Trap on the Light Source.")
        
        for i in range(30): # Run for 30 frames
            ret, frame = self.hardware.read_camera()
            if not ret: continue
            
            # 1. Sense (Find Light)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)
            
            # Image Coords: (0,0) top-left. Center is (320, 240)
            target_x, target_y = max_loc
            
            # 2. Map (Calculate Error from Center)
            center_x, center_y = 320, 240
            error_x = (target_x - center_x)
            error_y = (target_y - center_y) # Inverted Y usually? Let's keep simple.
            
            # 3. Plan (PID Control)
            dx = self.pid["p"] * error_x + self.pid["d"] * (error_x - self.last_error["x"])
            dy = self.pid["p"] * error_y + self.pid["d"] * (error_y - self.last_error["y"])
            
            self.last_error = {"x": error_x, "y": error_y}
            
            # Update Acoustic Trap Position (Inverse relationship: Move trap TO the light)
            # Mapping: Image Pixels -> World Millimeters (Scale approx 0.1)
            scale = 0.1
            self.current_pos["x"] += dx * scale
            self.current_pos["y"] -= dy * scale # Flip Y for camera coords
            
            # Clamp
            self.current_pos["x"] = max(-50, min(50, self.current_pos["x"]))
            self.current_pos["y"] = max(-50, min(50, self.current_pos["y"]))
            
            # 4. Act
            cmd = f"MOVE {self.current_pos['x']:.2f} {self.current_pos['y']:.2f} {self.current_pos['z']:.2f}"
            print(f"[FRAME {i}] Light: {max_loc} | Error: ({error_x}, {error_y}) | Action: {cmd}")
            self.hardware.send_command(cmd)
            
            await asyncio.sleep(0.1)

async def main():
    hw = HardwareManager()
    hw.connect_serial()
    hw.connect_camera()
    
    bot = Architect(hw)
    try:
        await bot.track_light()
    finally:
        hw.close()

if __name__ == "__main__":
    asyncio.run(main())
