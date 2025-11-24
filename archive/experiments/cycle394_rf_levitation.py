import sys
import time
import numpy as np
import argparse
from experiments.cycle386_serial_integration import get_serial
from experiments.cycle391_physical_levitation import PhysicalLevitationController

# Try to import rtlsdr, else use mock
try:
    from rtlsdr import RtlSdr
    HAS_SDR = True
except ImportError:
    HAS_SDR = False
    print("[WARN] pyrtlsdr not installed. Will use VirtualSDR if not in sim mode.")

class VirtualSDR:
    def __init__(self):
        print("[SDR] Initializing Virtual SDR...")
        self.sample_rate = 2.048e6
        self.center_freq = 100e6
        self.gain = 'auto'
    
    def read_samples(self, count):
        # Generate synthetic RF data (white noise + random carrier)
        noise = (np.random.randn(count) + 1j*np.random.randn(count)) * 0.1
        
        # Inject a random "signal" that drifts
        t = time.time()
        freq_offset = 200e3 * np.sin(t) # Oscillating signal
        phase = 2 * np.pi * freq_offset * np.arange(count) / self.sample_rate
        signal = 0.5 * np.exp(1j * phase)
        
        return noise + signal

    def close(self):
        print("[SDR] Closed.")

class RFLevitationController:
    def __init__(self, sim_mode=False):
        print("[INIT] Initializing RF Levitation Controller...")
        
        # 1. Initialize Hardware (Serial only, we don't need Camera for this open-loop mode)
        # We reuse get_serial from C386 which handles the mock/real logic
        self.serial = get_serial()
        
        # 2. Initialize SDR
        if sim_mode or not HAS_SDR:
            self.sdr = VirtualSDR()
        else:
            try:
                self.sdr = RtlSdr()
                self.sdr.sample_rate = 2.048e6
                self.sdr.center_freq = 100e6 # FM Band
                self.sdr.freq_correction = 60
                self.sdr.gain = 'auto'
                print(f"[SDR] Connected: {self.sdr.get_sdr_device_name()}")
            except Exception as e:
                print(f"[ERROR] Failed to connect to SDR: {e}. Falling back to Virtual.")
                self.sdr = VirtualSDR()

        # 3. State
        self.is_running = False
        self.current_pos = np.array([50.0, 50.0, 20.0])
        self.target_pos = np.array([50.0, 50.0, 20.0])
        
        # Smoothing (Low Pass Filter)
        self.alpha = 0.1 # Smoothing factor (0.0 - 1.0)
        
        # Safety Limits (Clamp)
        self.SAFE_MIN = np.array([30.0, 30.0, 10.0])
        self.SAFE_MAX = np.array([70.0, 70.0, 40.0])

    def map_spectrum_to_pos(self, samples):
        """
        Maps RF spectrum to X, Y, Z coordinates.
        X: Spectral Centroid (Frequency Balance)
        Y: Peak Frequency Location
        Z: RSSI (Total Power)
        """
        # Compute FFT
        fft_vals = np.fft.fft(samples)
        fft_mag = np.abs(fft_vals)
        fft_shift = np.fft.fftshift(fft_mag) # Center DC
        
        # 1. Z-Axis: RSSI (Total Energy)
        rssi = np.mean(fft_mag)
        # Map RSSI (approx 0.1 to 2.0) to Z (10 to 40)
        z_norm = np.clip((rssi - 0.1) / 1.0, 0, 1)
        z = self.SAFE_MIN[2] + z_norm * (self.SAFE_MAX[2] - self.SAFE_MIN[2])
        
        # 2. X-Axis: Spectral Centroid
        # We use the magnitude distribution as weights
        freqs = np.linspace(-1, 1, len(fft_shift))
        centroid = np.sum(freqs * fft_shift) / (np.sum(fft_shift) + 1e-6)
        # Map Centroid (-0.5 to 0.5) to X (30 to 70)
        x_norm = np.clip((centroid + 0.5), 0, 1)
        x = self.SAFE_MIN[0] + x_norm * (self.SAFE_MAX[0] - self.SAFE_MIN[0])
        
        # 3. Y-Axis: Peak Frequency
        peak_idx = np.argmax(fft_shift)
        peak_freq = freqs[peak_idx]
        # Map Peak (-1 to 1) to Y (30 to 70)
        y_norm = np.clip((peak_freq + 1) / 2, 0, 1)
        y = self.SAFE_MIN[1] + y_norm * (self.SAFE_MAX[1] - self.SAFE_MIN[1])
        
        return np.array([x, y, z])

    def run(self):
        print("[START] Starting RF Levitation Loop...")
        self.is_running = True
        
        # Enable Traps
        self.serial.send_command("ENABLE")
        self.serial.send_command("HOME")
        time.sleep(1)
        
        try:
            while self.is_running:
                # 1. READ SDR
                samples = self.sdr.read_samples(1024)
                
                # 2. MAP TO POSITION
                raw_target = self.map_spectrum_to_pos(samples)
                
                # 3. SMOOTHING (Low Pass)
                self.current_pos = self.current_pos * (1 - self.alpha) + raw_target * self.alpha
                
                # 4. CLAMP (Safety)
                clamped_pos = np.clip(self.current_pos, self.SAFE_MIN, self.SAFE_MAX)
                
                # 5. ACT
                cmd = f"MOVE {clamped_pos[0]:.2f} {clamped_pos[1]:.2f} {clamped_pos[2]:.2f}"
                self.serial.send_command(cmd)
                
                # Log
                sys.stdout.write(f"\r[RF] Tgt: {raw_target.round(1)} -> Act: {clamped_pos.round(1)} | Cmd: {cmd}")
                sys.stdout.flush()
                
                time.sleep(0.05) # ~20Hz
                
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted by user.")
        except Exception as e:
            print(f"\n[ERROR] Loop failed: {e}")
        finally:
            print("\n[SHUTDOWN] Disabling Traps.")
            self.serial.send_command("DISABLE")
            self.serial.close()
            self.sdr.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action="store_true", help="Run in simulation mode (Virtual SDR)")
    args = parser.parse_args()
    
    controller = RFLevitationController(sim_mode=args.sim)
    controller.run()
