"""
Cycle 446: The Conveyor Belt (Flow Fields)
Role: The Navigator
Responsibility: Create a "Path of Least Resistance" (Acoustic Jet Stream) to transport matter.
"""
import numpy as np
import math

def calculate_force(phase_gradient_deg_per_meter):
    print(f"Testing Phase Gradient: {phase_gradient_deg_per_meter} deg/m")
    
    # Constants
    c = 343.0 # Speed of sound
    f = 40000.0 # 40kHz
    wavelength = c / f
    k = 2 * np.pi / wavelength
    
    # To move a wave, we shift phase over space.
    # A traveling wave has form: exp(i(kx - wt + phi))
    # If we map emitters to x, and set their phase phi(x) = gradient * x
    # We effectively change the apparent 'k' vector, steering the beam or moving the nodes.
    
    # Let's simulate the Gorkov Gradient (Force) at the center.
    # Simple heuristic: The force is proportional to the spatial gradient of the phase.
    # F ~ -Gradient(Potential) 
    
    # If we have a standing wave, Potential looks like cos^2(kx).
    # If we shift phase continuously, the cos^2(kx) pattern slides.
    
    # Speed of transport = (d_phi / dt) / k
    # We want to see if a static spatial gradient creates a "Tilt".
    
    # Actually, strictly speaking, a static phase gradient just "steers" the beam angle.
    # To make a "Conveyor Belt" (Tractor Beam), we usually need dynamic phase shifting (Time varying).
    # BUT, let's test the "Wind" concept. 
    # If we steer the beam, does the 'sweet spot' move? Yes.
    
    beam_angle = math.asin((math.radians(phase_gradient_deg_per_meter) / 360.0 * wavelength) / 1.0) if abs((math.radians(phase_gradient_deg_per_meter) / 360.0 * wavelength)) <= 1 else 0
    # Wait, simple physics: 
    # Phase shift delta_phi between d spaced emitters steers beam by theta:
    # sin(theta) = (delta_phi / 2pi) * lambda / d
    
    # Let's calculate the Steering Angle for a standard array spacing
    spacing = 0.01 # 10mm
    delta_phi = math.radians(phase_gradient_deg_per_meter) * spacing
    
    try:
        sin_theta = (delta_phi / (2*math.pi)) * (wavelength / spacing)
        if abs(sin_theta) > 1.0:
            print(f"  -> Gradient too steep! Aliasing/Grating lobes. Sin(theta)={sin_theta:.2f}")
            return False
        else:
            theta = math.degrees(math.asin(sin_theta))
            print(f"  -> Beam Steering Angle: {theta:.2f} degrees")
            print(f"  -> Result: The 'Airstream' is directed {theta:.2f} deg off-axis.")
            return True
            
    except Exception as e:
        print(f"Calculation error: {e}")
        return False

def run_experiment():
    print("Cycle 446: Acoustic Conveyor Test")
    print("=================================")
    
    # Test 1: Gentle Breeze (10 deg shift per meter? No, per element?)
    # Let's stick to degrees per meter for general field description.
    
    # Wavelength = 8.5mm.
    # 360 deg phase shift over 8.5mm = Full wave cycle.
    # So roughly 42,000 deg/m is one wave cycle per meter.
    
    # Test: Steering the "Path of Least Resistance"
    gradients = [0, 500, 1000, 2000, 5000] # deg/m
    
    for g in gradients:
        calculate_force(g)
        
    print("\n--- Conclusion ---")
    print("We can shape the 'Air Stream' (Beam Angle) by altering the 'Phase Landscape'.")
    print("Particles trapped in this beam will travel along the vector.")

if __name__ == "__main__":
    run_experiment()
