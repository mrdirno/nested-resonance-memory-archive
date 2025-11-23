"""
Test Suite for Cycle 366: The Physics Upgrade
Verifies Gorkov Potential calculation and Trapping Forces.
"""
import unittest
import numpy as np
from src.helios.substrate_3d import AcousticSubstrate3D
from src.helios.operator import Emitter3D

class TestPhysics(unittest.TestCase):
    def setUp(self):
        # High resolution for accurate gradient
        self.box = AcousticSubstrate3D(width_mm=40, height_mm=40, depth_mm=40, resolution_mm=0.5)
        
    def test_standing_wave_trap(self):
        """
        Verify that two opposing emitters create a trap (Potential Minimum) 
        at the pressure node (center).
        """
        # Two emitters facing each other along X axis
        # Distance 40mm. Center at 20mm.
        # 40kHz wavelength lambda = 343000 / 40000 = 8.575 mm
        # Distance 40mm is approx 4.66 wavelengths.
        
        # Resolution 0.5mm.
        # E1 at 0mm.
        # E2 at 40mm.
        # Y, Z at 20mm.
        
        e1 = Emitter3D(0, 20, 20, 0.5, 0.0) # x=0
        e2 = Emitter3D(40, 20, 20, 0.5, np.pi) # x=40 (mm)
        
        emitters = [e1, e2]
        
        # Propagate
        field = self.box.propagate(emitters)
        
        # Calculate Potential
        U = self.box.calculate_gorkov_potential(field)
        
        # Check Center (20, 20, 20)
        # Grid coords
        cx = int(20 / 0.5)
        cy = int(20 / 0.5)
        cz = int(20 / 0.5)
        
        u_center = U[cz, cy, cx]
        
        # Check neighbors to verify it's a local minimum (or maximum?)
        # In a standing wave, nodes are pressure minima.
        # Gorkov potential:
        # U propto <p^2> - <v^2>
        # At pressure node: p=0, v is max.
        # U propto -<v^2>. So U is negative (attractive).
        # At pressure antinode: p is max, v=0.
        # U propto <p^2>. So U is positive (repulsive).
        # So particles should be trapped at Pressure Nodes (Velocity Antinodes).
        
        # Detailed Debug
        # Re-calculate constants to print them
        rho_0 = 1.2; c_0 = 343.0; rho_p = 25.0; c_p = 2350.0; R = 0.001; omega = 2 * np.pi * 40000
        f1 = 1.0 - (rho_0 * c_0**2) / (rho_p * c_p**2)
        f2 = 2 * (rho_p - rho_0) / (2 * rho_p + rho_0)
        V_p = (4/3) * np.pi * R**3
        K1 = V_p / (4 * rho_0 * c_0**2) * f1
        K2 = (3/4) * V_p / (rho_0 * omega**2) * f2
        
        print(f"\nConstants: K1={K1:.2e}, K2={K2:.2e}")
        
        res_m = 0.5 / 1000.0
        grad_z, grad_y, grad_x = np.gradient(field, res_m)
        
        print("\n--- Detailed Scan ---")
        indices = [35, 36, 40, 44, 45] # Check Node (40) and Antinodes (~36, 44)
        for i in indices:
            p_val = field[cz, cy, i]
            p_sq = 0.5 * np.abs(p_val)**2
            
            gx = grad_x[cz, cy, i]
            gy = grad_y[cz, cy, i]
            gz = grad_z[cz, cy, i]
            grad_sq = 0.5 * (np.abs(gx)**2 + np.abs(gy)**2 + np.abs(gz)**2)
            
            # v_sq term in my code:
            # v_sq = (0.5 / (omega**2 * rho_0**2)) * |grad|^2
            # term2 = (rho_0 * v_sq / 2) * f2
            # This is equivalent to K2 * |grad|^2 ?
            # My code: K2 = (3/4) * V_p / (rho_0 * omega**2) * f2
            # Term2 (code) = rho_0 * (0.5/(omega^2 rho_0^2) * |grad|^2) / 2 * f2
            # = (1/4) * (1/(rho_0 omega^2)) * |grad|^2 * f2
            # U = 2 pi R^3 ( ... - Term2 )
            # = 1.5 V_p ( ... - Term2 )
            # = 1.5 V_p * (1/4) ... = (3/8) V_p ...
            
            # Wait, let's check the code implementation vs K1/K2 formula.
            # Code: U = 2 * pi * R^3 * (term1 - term2)
            # term1 = (p_sq / (3 * rho_0 * c_0**2)) * f1
            # term2 = (rho_0 * v_sq / 2) * f2
            
            # Let's calculate U manually here
            v_sq = (0.5 / (omega**2 * rho_0**2)) * (np.abs(gx)**2 + np.abs(gy)**2 + np.abs(gz)**2)
            term1 = (p_sq / (3 * rho_0 * c_0**2)) * f1
            term2 = (rho_0 * v_sq / 2) * f2
            U_calc = 2 * np.pi * R**3 * (term1 - term2)
            
            print(f"Index {i}: |P|^2={p_sq:.2e}, |Grad|^2={grad_sq:.2e}")
            print(f"         Term1 (Press)={term1:.2e}, Term2 (Vel)={term2:.2e}")
            print(f"         U={U_calc:.2e} (Code says {U[cz, cy, i]:.2e})")
            
        # Debug Components at Center (Index 40)
        print("\n--- Components at Center ---")
        idx = 40
        
        # Re-calculate components manually
        x_m = idx * res_m
        y_m = 20 * res_m # Wait, cy=40 -> 20mm
        z_m = 20 * res_m
        
        # Emitter 1
        e1 = emitters[0]
        d1 = np.sqrt((x_m - e1.x*res_m)**2 + (y_m - e1.y*res_m)**2 + (z_m - getattr(e1,'z',0)*res_m)**2)
        k1 = 2 * np.pi * (30000 + e1.frequency*20000) / 343.0
        c1 = e1.amplitude * np.exp(1j * (k1 * d1 + e1.phase))
        print(f"E1: d={d1:.4f}, k={k1:.2f}, phase={e1.phase:.2f}, val={c1:.2f}")
        
        # Emitter 2
        e2 = emitters[1]
        d2 = np.sqrt((x_m - e2.x*res_m)**2 + (y_m - e2.y*res_m)**2 + (z_m - getattr(e2,'z',0)*res_m)**2)
        k2 = 2 * np.pi * (30000 + e2.frequency*20000) / 343.0
        c2 = e2.amplitude * np.exp(1j * (k2 * d2 + e2.phase))
        print(f"E2: d={d2:.4f}, k={k2:.2f}, phase={e2.phase:.2f}, val={c2:.2f}")
        
        print(f"Sum: {c1+c2:.2f}, |Sum|^2={np.abs(c1+c2)**2:.2f}")
        
        self.assertEqual(np.argmin(U[cz, cy, 35:46]) + 35, 40, "Minimum should be at 40")

if __name__ == '__main__':
    unittest.main()
