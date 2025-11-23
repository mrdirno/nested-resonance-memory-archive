import threading
import time
import sys
import json
import termios
import tty
from experiments.cycle391_physical_levitation import PhysicalLevitationController

class TuningDashboard:
    def __init__(self):
        self.controller = PhysicalLevitationController()
        self.running = True
        
    def get_key(self):
        """Reads a single keypress from stdin."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def save_config(self):
        config = {
            "kp": self.controller.pid.kp,
            "ki": self.controller.pid.ki,
            "kd": self.controller.pid.kd
        }
        with open("pid_config.json", "w") as f:
            json.dump(config, f, indent=4)
        print("\n[DASHBOARD] Config saved to pid_config.json")

    def run(self):
        print("="*60)
        print("DUALITY-ZERO: PID TUNING DASHBOARD")
        print("="*60)
        print("Controls:")
        print("  p/P : Increase/Decrease Kp")
        print("  i/I : Increase/Decrease Ki")
        print("  d/D : Increase/Decrease Kd")
        print("  s   : Save Config")
        print("  q   : Quit")
        print("="*60)
        
        # Start Controller in a separate thread
        controller_thread = threading.Thread(target=self.controller.run)
        controller_thread.daemon = True
        controller_thread.start()
        
        try:
            while self.running and self.controller.is_running:
                # Display current gains
                sys.stdout.write(f"\rPID: Kp={self.controller.pid.kp:.3f} | Ki={self.controller.pid.ki:.3f} | Kd={self.controller.pid.kd:.3f} > ")
                sys.stdout.flush()
                
                key = self.get_key()
                
                if key == 'q':
                    self.running = False
                    self.controller.is_running = False
                    break
                elif key == 's':
                    self.save_config()
                elif key == 'p':
                    self.controller.pid.kp += 0.01
                elif key == 'P':
                    self.controller.pid.kp -= 0.01
                elif key == 'i':
                    self.controller.pid.ki += 0.001
                elif key == 'I':
                    self.controller.pid.ki -= 0.001
                elif key == 'd':
                    self.controller.pid.kd += 0.01
                elif key == 'D':
                    self.controller.pid.kd -= 0.01
                    
                # Clamp values to be non-negative
                self.controller.pid.kp = max(0.0, self.controller.pid.kp)
                self.controller.pid.ki = max(0.0, self.controller.pid.ki)
                self.controller.pid.kd = max(0.0, self.controller.pid.kd)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.controller.is_running = False
            controller_thread.join(timeout=1)
            print("\n[DASHBOARD] Exiting.")

if __name__ == "__main__":
    dashboard = TuningDashboard()
    dashboard.run()
