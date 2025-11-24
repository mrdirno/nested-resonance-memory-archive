import sys
import time
import numpy as np
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from experiments.cycle394_rf_levitation import RFLevitationController

class SpectralAccumulator:
    def __init__(self, sim_mode=False, resolution=50):
        print("[INIT] Initializing Spectral Accumulator...")
        self.controller = RFLevitationController(sim_mode=sim_mode)
        
        # Grid Configuration
        self.resolution = resolution
        self.grid_shape = (resolution, resolution, resolution)
        self.density_grid = np.zeros(self.grid_shape, dtype=np.int32)
        
        # Bounds (Reuse Safety Limits from Controller)
        self.min_bound = self.controller.SAFE_MIN
        self.max_bound = self.controller.SAFE_MAX
        
    def pos_to_index(self, pos):
        """Converts physical position (mm) to grid index."""
        # Normalize to 0-1
        norm = (pos - self.min_bound) / (self.max_bound - self.min_bound)
        # Scale to resolution
        idx = (norm * (self.resolution - 1)).astype(int)
        # Clamp
        return np.clip(idx, 0, self.resolution - 1)

    def run(self, frames=1000):
        print(f"[START] Accumulating {frames} spectral frames...")
        
        # Start Controller Hardware (SDR/Serial)
        # We manually manage the SDR reading loop here instead of calling controller.run()
        # because we need to intercept the position data.
        
        # Enable Traps (Optional, but good for visual feedback if rig is on)
        self.controller.serial.send_command("ENABLE")
        self.controller.serial.send_command("HOME")
        time.sleep(1)
        
        try:
            for i in range(frames):
                # 1. Read SDR
                samples = self.controller.sdr.read_samples(1024)
                
                # 2. Map to Position
                raw_target = self.controller.map_spectrum_to_pos(samples)
                
                # 3. Smooth & Clamp (Reuse controller logic)
                self.controller.current_pos = self.controller.current_pos * (1 - self.controller.alpha) + raw_target * self.controller.alpha
                clamped_pos = np.clip(self.controller.current_pos, self.controller.SAFE_MIN, self.controller.SAFE_MAX)
                
                # 4. Accumulate
                idx = self.pos_to_index(clamped_pos)
                self.density_grid[idx[0], idx[1], idx[2]] += 1
                
                # 5. Act (Visual Feedback)
                cmd = f"MOVE {clamped_pos[0]:.2f} {clamped_pos[1]:.2f} {clamped_pos[2]:.2f}"
                self.controller.serial.send_command(cmd)
                
                # Log
                if i % 10 == 0:
                    sys.stdout.write(f"\r[ACCUMULATING] Frame {i}/{frames} | Pos: {clamped_pos.round(1)}")
                    sys.stdout.flush()
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted.")
        except Exception as e:
            print(f"\n[ERROR] Accumulation failed: {e}")
        finally:
            print("\n[DONE] Accumulation complete.")
            self.controller.serial.send_command("DISABLE")
            self.controller.serial.close()
            self.controller.sdr.close()
            
        self.save_results()

    def save_results(self):
        print("[SAVE] Saving density map...")
        np.save("rf_density_map.npy", self.density_grid)
        
        print("[PLOT] Generating visualization...")
        self.plot_density()

    def plot_density(self):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Get coordinates of non-zero voxels
        x, y, z = np.where(self.density_grid > 0)
        counts = self.density_grid[x, y, z]
        
        if len(x) == 0:
            print("[WARN] No data accumulated to plot.")
            return

        # Plot
        # Normalize size for better visualization
        sizes = counts / np.max(counts) * 50
        
        img = ax.scatter(x, y, z, c=counts, cmap='viridis', marker='s', s=sizes, alpha=0.6)
        
        ax.set_xlabel('X (Spectral Centroid)')
        ax.set_ylabel('Y (Peak Freq)')
        ax.set_zlabel('Z (RSSI)')
        ax.set_title('RF Spectral Density Map (The Invisible Shape)')
        
        plt.colorbar(img, label='Accumulated Density')
        plt.savefig('rf_density_plot.png')
        print("[PLOT] Saved to rf_density_plot.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action="store_true", help="Run in simulation mode")
    parser.add_argument("--frames", type=int, default=1000, help="Number of frames to accumulate")
    args = parser.parse_args()
    
    accumulator = SpectralAccumulator(sim_mode=args.sim)
    accumulator.run(frames=args.frames)
