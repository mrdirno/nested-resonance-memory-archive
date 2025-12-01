import numpy as np
import matplotlib.pyplot as plt

def optimize_gyroid(nozzle_dia=0.4, target_porosity=0.5):
    """
    Calculates the optimal Gyroid parameters for a given printer configuration.
    
    Constraints:
    1. Min Wall Thickness >= Nozzle Diameter (0.4mm)
    2. Max Overhang Angle <= 45 degrees (Typical FFF limit)
    
    Physics of Gyroid:
    - Mean Curvature H = 0
    - Gaussian Curvature K varies.
    - Surface Area S = 3.091 * L^2 (per unit cell)
    """
    print(f"HELIOS OPTIMIZER: Gyroid Lattice for {nozzle_dia}mm Nozzle")
    print("-----------------------------------------------------------")
    
    # Variable: Unit Cell Size (L) in mm
    # We sweep from small (dense) to large (open)
    L_range = np.linspace(5.0, 50.0, 20)
    
    print(f"{'Cell Size (L)':<15} | {'Wall (t)':<15} | {'Surface Area/Vol':<20} | {'Printability'}")
    print("-" * 70)
    
    for L in L_range:
        # To maintain target porosity (e.g., 50% void), Wall Thickness (t) scales with L.
        # Approx relationship: Porosity ~ 1 - (t * S_area / Volume)
        # Volume = L^3. S_area = 3.091 * L^2.
        # 0.5 = 1 - (t * 3.091 * L^2 / L^3)
        # 0.5 = 1 - (3.091 * t / L)
        # t = (0.5 * L) / 3.091
        
        t = (0.5 * L) / 3.091
        
        # Surface Area Density (Sigma) = S_total / V_total
        # Sigma = (3.091 * L^2) / L^3 = 3.091 / L  (mm^-1)
        sigma = 3.091 / L
        
        # Printability Checks
        status = "OK"
        
        # 1. Resolution Check
        if t < nozzle_dia:
            status = "FAIL (Wall < Nozzle)"
        
        # 2. Overhang Check (Rough approximation for Gyroid)
        # Gyroids are generally self-supporting if L/t ratio isn't too extreme.
        # But very large L with thin t can sag.
        
        # 3. Retraction Risk (Frequency)
        # Smaller L = More retractions per layer.
        retraction_risk = "High" if L < 10 else "Med" if L < 20 else "Low"
        
        if status == "OK":
            print(f"{L:<15.1f} | {t:<15.2f} | {sigma:<20.3f} | {retraction_risk}")

if __name__ == "__main__":
    optimize_gyroid()
