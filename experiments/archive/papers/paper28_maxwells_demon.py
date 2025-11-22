import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class MaxwellsDemonSwarm:
    def __init__(self, n_agents=500, width=100, height=50):
        self.n = n_agents
        self.width = width
        self.height = height
        
        # Initialize Agents
        self.pos = np.random.rand(self.n, 2) * [width, height]
        # Maxwell-Boltzmann distribution for velocities
        self.vel = np.random.normal(0, 1.0, (self.n, 2))
        
        # Wall location (x-coordinate)
        self.wall_x = width / 2.0
        self.gate_y_min = height / 2.0 - 5.0
        self.gate_y_max = height / 2.0 + 5.0
        
        # Demon Parameters
        # Threshold speed to be considered "Hot"
        self.v_threshold = 1.0 
        
        # Metrics
        self.temp_left_history = []
        self.temp_right_history = []

    def step(self, dt=0.1):
        # 1. Move
        next_pos = self.pos + self.vel * dt
        
        # 2. Wall Interaction (The Demon)
        # Check for crossing the wall
        # Left to Right crossing
        crossing_lr = (self.pos[:, 0] < self.wall_x) & (next_pos[:, 0] >= self.wall_x)
        # Right to Left crossing
        crossing_rl = (self.pos[:, 0] > self.wall_x) & (next_pos[:, 0] <= self.wall_x)
        
        # Check if crossing is within gate Y-range (Physical Gate)
        # Actually, let's assume the Demon controls the WHOLE wall for simplicity, 
        # or just a small gate. Let's do a small gate to be realistic.
        in_gate_y = (self.pos[:, 1] > self.gate_y_min) & (self.pos[:, 1] < self.gate_y_max)
        
        # Demon Logic:
        # If crossing L->R: Allow if Speed > Threshold (Hot)
        # If crossing R->L: Allow if Speed < Threshold (Cold)
        
        speeds = np.linalg.norm(self.vel, axis=1)
        
        # Indices of agents attempting to cross
        idx_lr = np.where(crossing_lr)[0]
        idx_rl = np.where(crossing_rl)[0]
        
        for i in idx_lr:
            # Check if allowed
            # Condition: Must be in gate AND (Hot OR Demon allows it)
            # Let's say Demon opens gate for Hot particles anywhere on the wall? 
            # No, usually it's a specific door.
            # Let's assume the wall is solid except the gate.
            
            if in_gate_y[i]:
                # At the gate. Demon decides.
                if speeds[i] > self.v_threshold:
                    # HOT. Let it pass to Right.
                    pass 
                else:
                    # COLD. Block it. (Reflect)
                    self.vel[i, 0] *= -1
                    next_pos[i, 0] = self.wall_x - (next_pos[i, 0] - self.wall_x) # Bounce back
            else:
                # Hit the solid wall. Reflect.
                self.vel[i, 0] *= -1
                next_pos[i, 0] = self.wall_x - (next_pos[i, 0] - self.wall_x)

        for i in idx_rl:
            if in_gate_y[i]:
                # At the gate. Demon decides.
                if speeds[i] < self.v_threshold:
                    # COLD. Let it pass to Left.
                    pass
                else:
                    # HOT. Block it. (Reflect)
                    self.vel[i, 0] *= -1
                    next_pos[i, 0] = self.wall_x + (self.wall_x - next_pos[i, 0])
            else:
                # Hit solid wall
                self.vel[i, 0] *= -1
                next_pos[i, 0] = self.wall_x + (self.wall_x - next_pos[i, 0])
                
        # 3. Boundary Conditions (Box)
        # Reflect off outer walls
        # X-walls
        mask_x_low = next_pos[:, 0] < 0
        mask_x_high = next_pos[:, 0] > self.width
        self.vel[mask_x_low | mask_x_high, 0] *= -1
        next_pos[mask_x_low, 0] *= -1
        next_pos[mask_x_high, 0] = 2*self.width - next_pos[mask_x_high, 0]
        
        # Y-walls
        mask_y_low = next_pos[:, 1] < 0
        mask_y_high = next_pos[:, 1] > self.height
        self.vel[mask_y_low | mask_y_high, 1] *= -1
        next_pos[mask_y_low, 1] *= -1
        next_pos[mask_y_high, 1] = 2*self.height - next_pos[mask_y_high, 1]
        
        self.pos = next_pos
        
    def measure_temperature(self):
        # T ~ Average Kinetic Energy (v^2)
        left_mask = self.pos[:, 0] < self.wall_x
        right_mask = self.pos[:, 0] >= self.wall_x
        
        if np.sum(left_mask) > 0:
            temp_left = np.mean(np.sum(self.vel[left_mask]**2, axis=1))
        else:
            temp_left = 0
            
        if np.sum(right_mask) > 0:
            temp_right = np.mean(np.sum(self.vel[right_mask]**2, axis=1))
        else:
            temp_right = 0
            
        return temp_left, temp_right

def run_maxwells_demon_experiment():
    print("\n--- PAPER 28: THE THERMODYNAMIC COMPUTER (MAXWELL'S DEMON) ---")
    
    swarm = MaxwellsDemonSwarm(n_agents=1000)
    
    print("Running Simulation...")
    for t in range(2000):
        swarm.step(dt=0.1)
        tl, tr = swarm.measure_temperature()
        swarm.temp_left_history.append(tl)
        swarm.temp_right_history.append(tr)
        
        if t % 200 == 0:
            print(f"Step {t}: T_Left={tl:.4f}, T_Right={tr:.4f}, Diff={tr-tl:.4f}")
            
    # Final Analysis
    tl_final = np.mean(swarm.temp_left_history[-100:])
    tr_final = np.mean(swarm.temp_right_history[-100:])
    
    print(f"\nFinal T_Left: {tl_final:.4f}")
    print(f"Final T_Right: {tr_final:.4f}")
    print(f"Temperature Gradient: {tr_final - tl_final:.4f}")
    
    # Criteria
    # Significant positive gradient (Right > Left)
    if (tr_final - tl_final) > 0.5:
        print("SUCCESS: Maxwell's Demon Verified.")
        print("Information (Sorting) was converted into a Temperature Gradient.")
    else:
        print("FAILURE: No significant gradient formed.")

if __name__ == "__main__":
    run_maxwells_demon_experiment()
