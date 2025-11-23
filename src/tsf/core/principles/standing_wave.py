"""
Standing Wave Expanding Universe (Reconstructed)
Salvaged from legacy test patterns.
"""

import numpy as np
from dataclasses import dataclass
from scipy.integrate import odeint, quad
from scipy.optimize import brentq
import warnings

@dataclass
class CosmologicalParameters:
    H0: float = 67.4
    Omega_m: float = 0.315
    Omega_Lambda: float = 0.685
    Omega_r: float = 9.24e-5
    Omega_k: float = 0.0
    c: float = 299792.458  # km/s

    def __post_init__(self):
        total = self.Omega_m + self.Omega_Lambda + self.Omega_r + self.Omega_k
        if abs(total - 1.0) > 0.01:
            warnings.warn(f"Omega total {total} != 1.0")

@dataclass
class WaveEvolutionResult:
    success: bool
    time_array: np.ndarray
    redshift_array: np.ndarray
    scale_factor_array: np.ndarray
    wave_amplitude: np.ndarray
    wave_velocity: np.ndarray
    physical_wavelength_mpc: np.ndarray
    physical_frequency_hz: np.ndarray
    energy_density: np.ndarray
    comoving_wavelength_mpc: float
    initial_frequency_hz: float
    final_amplitude_ratio: float
    horizon_crossing_redshift: float = None

class StandingWaveExpandingUniverse:
    def __init__(self, cosmo_params: CosmologicalParameters = None):
        self.cosmo = cosmo_params if cosmo_params else CosmologicalParameters()
        self.c_light_kmps = self.cosmo.c
        self.c_light_mps = self.c_light_kmps * 1000.0
        
        # H0 in SI (1/s)
        # 1 Mpc = 3.086e22 m
        self.MPC_IN_M = 3.086e22
        self.KM_M_CONV = 1000.0
        self.H0_SI = self.cosmo.H0 * self.KM_M_CONV / self.MPC_IN_M
        self.t_hubble = 1.0 / self.H0_SI if self.H0_SI > 0 else 0

        self.z_recombination = 1090.0
        self.z_reionization = 6.0
        self.cs_early_kmps = self.c_light_kmps / np.sqrt(3.0)

    def scale_factor(self, z: float) -> float:
        if z == -1: return float('inf')
        return 1.0 / (1.0 + z)

    def hubble_parameter(self, z: float) -> float:
        """Returns H(z) in km/s/Mpc"""
        zp1 = 1.0 + z
        E_sq = (self.cosmo.Omega_r * zp1**4 + 
                self.cosmo.Omega_m * zp1**3 + 
                self.cosmo.Omega_k * zp1**2 + 
                self.cosmo.Omega_Lambda)
        return self.cosmo.H0 * np.sqrt(E_sq)

    def cosmic_time_from_redshift(self, z: float) -> float:
        """Returns cosmic time in seconds."""
        # Integral dt = da / (a * H) = -dz / ((1+z) * H(z))
        def integrand(z_prime):
            H = self.hubble_parameter(z_prime) * self.KM_M_CONV / self.MPC_IN_M # to SI
            return 1.0 / ((1.0 + z_prime) * H)
        
        # Integrate from z to infinity (t=0 at z=inf)
        # Practical infinity = 1e5
        t_sec, _ = quad(integrand, z, 1e5)
        return t_sec

    def conformal_time(self, z: float) -> float:
        """Returns conformal time in Mpc (distance light could travel)."""
        # eta = Integral c/H(z) dz
        def integrand(z_prime):
            return self.c_light_kmps / self.hubble_parameter(z_prime)
        
        eta_mpc, _ = quad(integrand, 0, z) # From 0 to z (lookback distance)
        return eta_mpc

    def sound_speed(self, z: float) -> float:
        """Returns sound speed in km/s."""
        if z > self.z_recombination:
            return self.cs_early_kmps
        elif z <= self.z_reionization:
            return 10.0 # Placeholder for ionized IGM
        else:
            return 0.1 # Placeholder for neutral IGM

    def horizon_crossing_redshift(self, lambda_comoving_mpc: float) -> float:
        """Find z where lambda_phys = Hubble radius (c/H)."""
        # lambda_phys = a * lambda_comoving
        # Hubble radius = c / H(z)
        # Solve: scale_factor(z) * lambda_comoving_mpc - c_light_kmps / hubble_parameter(z) = 0
        
        def func(z):
            if z < -0.99: return -1e9
            H = self.hubble_parameter(z)
            if H == 0: return 1e9
            return self.scale_factor(z) * lambda_comoving_mpc - self.c_light_kmps / H

        try:
            z_cross = brentq(func, 0, 1e5)
            return z_cross
        except:
            return None

    def wave_equation_expanding_universe(self, t, y, k_comoving_SI, freq_comoving_hz):
        """
        d^2psi/dt^2 + 2H dpsi/dt + (c_s^2 k_phys^2) psi = 0
        y = [psi, psi_dot]
        """
        psi, psi_dot = y
        
        # Need z from t. This is expensive to invert integral.
        # Approximation: Matter dominated t = 2/3H0 * a^3/2
        # a = (3/2 H0 t)^(2/3)
        # z = 1/a - 1
        # Better: use a lookup or pass z if possible. 
        # For ODE solver, we only have t.
        
        # Simple inversion for matter domination (valid for most of history)
        # t * H0 ~ 2/3 * a^1.5
        # a ~ (1.5 * H0 * t)^(2/3)
        if t <= 0: t = 1e-10
        a_approx = (1.5 * self.H0_SI * t)**(2.0/3.0)
        z_approx = 1.0/a_approx - 1.0
        if z_approx < 0: z_approx = 0
        
        H_SI = self.hubble_parameter(z_approx) * self.KM_M_CONV / self.MPC_IN_M
        cs_kmps = self.sound_speed(z_approx)
        cs_SI = cs_kmps * 1000.0
        
        k_phys_SI = k_comoving_SI / a_approx
        
        # Term: (cs * k_phys)^2
        # Also need to handle intrinsic frequency if any? 
        # The wave equation usually is just k term. If driven, that's different.
        # Assuming free standing wave.
        
        omega_sq = (cs_SI * k_phys_SI)**2
        
        dpsi_dt = psi_dot
        dpsi_dot_dt = -2.0 * H_SI * psi_dot - omega_sq * psi
        
        return [dpsi_dt, dpsi_dot_dt]

    def evolve_standing_wave(self, initial_physical_frequency_hz, comoving_wavelength_mpc, 
                             z_initial, z_final, initial_amplitude=1.0, initial_amplitude_derivative=0.0, 
                             n_points=1000):
        
        t_start = self.cosmic_time_from_redshift(z_initial)
        t_end = self.cosmic_time_from_redshift(z_final)
        t_eval = np.linspace(t_start, t_end, n_points)
        
        k_comoving_SI = (2 * np.pi) / (comoving_wavelength_mpc * self.MPC_IN_M)
        
        y0 = [initial_amplitude, initial_amplitude_derivative]
        
        try:
            sol = odeint(self.wave_equation_expanding_universe, y0, t_eval, args=(k_comoving_SI, initial_physical_frequency_hz))
            
            # Reconstruct auxiliary arrays
            z_eval = []
            a_eval = []
            for t in t_eval:
                # Invert t to z (approx)
                a_approx = (1.5 * self.H0_SI * t)**(2.0/3.0)
                z_approx = 1.0/a_approx - 1.0
                if z_approx < 0: z_approx = 0
                z_eval.append(z_approx)
                a_eval.append(a_approx)
            
            z_eval = np.array(z_eval)
            a_eval = np.array(a_eval)
            
            return WaveEvolutionResult(
                success=True,
                time_array=t_eval,
                redshift_array=z_eval,
                scale_factor_array=a_eval,
                wave_amplitude=sol[:, 0],
                wave_velocity=sol[:, 1],
                physical_wavelength_mpc=comoving_wavelength_mpc * a_eval,
                physical_frequency_hz=initial_physical_frequency_hz / a_eval, # Approx redshift
                energy_density=sol[:, 0]**2, # Proportional
                comoving_wavelength_mpc=comoving_wavelength_mpc,
                initial_frequency_hz=initial_physical_frequency_hz,
                final_amplitude_ratio=abs(sol[-1, 0]/initial_amplitude) if initial_amplitude != 0 else 0
            )
            
        except Exception as e:
            print(f"Evolution failed: {e}")
            return WaveEvolutionResult(False, [], [], [], [], [], [], [], [], 0, 0, 0)

