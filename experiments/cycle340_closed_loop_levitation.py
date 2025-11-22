"""
CYCLE 340: Closed-Loop Levitation (Active Damping)
Objective: Demonstrate that Active Feedback (Electronic Damping) stabilizes a particle 
faster than passive physics alone.
"""
import numpy as np
import json
import os
import sys
import time

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate_3d import AcousticSubstrate3D

class Particle:
    def __init__(self, x, y, z, mass=1.0):
        self.pos = np.array([x, y, z], dtype=float)
        self.vel = np.array([0.0, 0.0, 0.0], dtype=float)
        self.mass = mass
        
    def update(self, force, dt):
        acc = force / self.mass
        self.vel += acc * dt
        self.pos += self.vel * dt
        # Damping (Air Resistance)
        self.vel *= 0.99

class PhysicsEngine:
    def __init__(self, substrate):
        self.substrate = substrate
        
    def get_force(self, particle_pos, trap_pos):
        """
        Calculates the restoring force of the trap.
        Approximation: The trap acts like a spring (Hooke's Law) near the center.
        F = -k * (x - x_trap)
        
        In reality, it's the gradient of the Gorkov potential, but for small 
        displacements, a spring model is a valid approximation for control theory.
        """
        k_spring = 10.0 # Stiffness of the acoustic trap
        displacement = particle_pos - trap_pos
        force = -k_spring * displacement
        return force

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = np.array([0.0, 0.0, 0.0])
        self.prev_error = np.array([0.0, 0.0, 0.0])
        
    def update(self, target_pos, current_pos, dt):
        error = target_pos - current_pos
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        return output

def run_simulation(mode="PASSIVE"):
    print(f"\nRunning Simulation: {mode}")
    
    # 1. Setup
    center = np.array([25.0, 25.0, 25.0])
    particle = Particle(25.0, 25.0, 25.0, mass=0.1)
    physics = PhysicsEngine(None) # Substrate not needed for spring approx
    
    # PID for Active Damping
    # We want to move the TRAP to oppose velocity.
    # If particle moves RIGHT, move trap RIGHT to reduce restoring force (reduce acceleration).
    # Wait, that reduces stiffness.
    # Active Damping: F_damping = -c * v.
    # We want the trap to exert a force that opposes velocity.
    # F_trap = -k * (x_p - x_t).
    # We want F_trap to have a component -c * v.
    # -k * (x_p - x_t) = -k*x_p + k*x_t.
    # We want k*x_t ~ -c * v  =>  x_t ~ -(c/k) * v.
    # So we shift the trap in the OPPOSITE direction of velocity?
    # No, if particle moves RIGHT (v > 0), we want force LEFT (F < 0).
    # Spring force is already LEFT (-k*x).
    # To increase damping, we want MORE force LEFT.
    # So we move trap LEFT (x_t < 0).
    # So x_t should be proportional to -v.
    
    # Let's use a simple Derivative term on the position error for the "Trap Position".
    # Target is Center.
    # Active Control: Trap Position = Center - Kd * Velocity
    
    kd = 0.5 if mode == "ACTIVE" else 0.0
    
    # 2. Initial Kick
    particle.vel = np.array([5.0, 0.0, 0.0]) # Kick in X
    
    dt = 0.01
    steps = 1000
    history = []
    
    settled = False
    settling_time = None
    
    for i in range(steps):
        t = i * dt
        
        # Control Law
        # Trap follows the "Anti-Velocity" to absorb energy
        trap_pos = center - (kd * particle.vel)
        
        # Physics
        force = physics.get_force(particle.pos, trap_pos)
        particle.update(force, dt)
        
        dist = np.linalg.norm(particle.pos - center)
        history.append({"t": t, "dist": dist, "x": particle.pos[0]})
        
        # Check Settling (within 0.1mm)
        if not settled and dist < 0.1 and np.linalg.norm(particle.vel) < 0.1:
            settled = True
            settling_time = t
            
    return history, settling_time

def main():
    print("CYCLE 340: CLOSED-LOOP LEVITATION")
    print("=================================")
    
    # Run Passive
    hist_passive, time_passive = run_simulation("PASSIVE")
    print(f"Passive Settling Time: {time_passive} s")
    
    # Run Active
    hist_active, time_active = run_simulation("ACTIVE")
    print(f"Active Settling Time: {time_active} s")
    
    # Compare
    if time_active and time_passive:
        improvement = time_passive / time_active
        print(f"\nSpeedup: {improvement:.2f}x")
        
        if improvement > 1.5:
            print(">> SUCCESS: Active Damping is significantly faster.")
        else:
            print(">> FAILURE: No significant improvement.")
    else:
        print(">> WARNING: Simulation did not settle in time.")

    # Save Results
    results = {
        "passive": {"time": time_passive, "history": hist_passive},
        "active": {"time": time_active, "history": hist_active}
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c340_closed_loop.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
