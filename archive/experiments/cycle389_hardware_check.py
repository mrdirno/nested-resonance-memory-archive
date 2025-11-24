import sys
import torch
import cv2
import serial.tools.list_ports
from experiments.cycle385_physical_camera import get_camera, PhysicalCamera
from experiments.cycle386_serial_integration import get_serial, PhysicalSerial

class SystemHealthCheck:
    def __init__(self):
        self.report = {}

    def check_compute(self):
        print("[CHECK] Compute Subsystem...")
        if torch.cuda.is_available():
            self.report['Compute'] = f"PASS (CUDA: {torch.cuda.get_device_name(0)})"
        elif torch.backends.mps.is_available():
            self.report['Compute'] = "PASS (MPS / Apple Silicon)"
        else:
            self.report['Compute'] = "WARN (CPU Only)"
        print(f"  -> {self.report['Compute']}")

    def check_camera(self):
        print("[CHECK] Vision Subsystem (The Eye)...")
        cam = get_camera()
        if isinstance(cam, PhysicalCamera):
            ret, frame = cam.read()
            if ret:
                self.report['Camera'] = "PASS (Physical Camera Connected)"
            else:
                self.report['Camera'] = "FAIL (Physical Camera Connected but No Frame)"
        else:
            self.report['Camera'] = "WARN (Virtual Camera - Simulation Mode)"
        
        cam.release()
        print(f"  -> {self.report['Camera']}")

    def check_serial(self):
        print("[CHECK] Actuation Subsystem (The Hand)...")
        ser = get_serial()
        if isinstance(ser, PhysicalSerial):
            self.report['Serial'] = f"PASS (Connected to {ser.ser.port})"
        else:
            self.report['Serial'] = "WARN (Virtual Serial - Simulation Mode)"
        
        ser.close()
        print(f"  -> {self.report['Serial']}")

    def run(self):
        print("="*60)
        print("DUALITY-ZERO: SYSTEM HEALTH CHECK")
        print("="*60)
        
        self.check_compute()
        self.check_camera()
        self.check_serial()
        
        print("-" * 60)
        print("SUMMARY:")
        all_pass = True
        for subsystem, status in self.report.items():
            print(f"{subsystem:<10}: {status}")
            if "FAIL" in status:
                all_pass = False
        
        print("-" * 60)
        if all_pass:
            print("SYSTEM STATUS: GREEN (Ready for Operation)")
        else:
            print("SYSTEM STATUS: RED (Fix Failures)")
        print("="*60)

if __name__ == "__main__":
    check = SystemHealthCheck()
    check.run()
