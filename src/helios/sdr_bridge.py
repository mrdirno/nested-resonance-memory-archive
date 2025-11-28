"""
HELIOS SDR Bridge (Gate 6.1)
Interfaces with RTL-SDR hardware to provide physical RF entropy and spectral data to the NRM.
Acts as a 'SensorArray' for the Reality Injection loop.
"""

import numpy as np
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from rtlsdr import RtlSdr
    HAS_SDR = True
except ImportError:
    logger.warning("pyrtlsdr not installed. Using Virtual SDR.")
    HAS_SDR = False
except Exception as e:
    logger.warning(f"SDR Error: {e}. Using Virtual SDR.")
    HAS_SDR = False

class SDRInterface:
    def __init__(self, center_freq=100e6, sample_rate=2.048e6, gain='auto'):
        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.gain = gain
        self.sdr = None
        self.connected = False
        self.virtual = not HAS_SDR

    def connect(self):
        """Connects to the physical SDR or initializes the virtual one."""
        if self.virtual:
            logger.info("Initializing Virtual SDR...")
            self.connected = True
            return True

        try:
            self.sdr = RtlSdr()
            self.sdr.sample_rate = self.sample_rate
            self.sdr.center_freq = self.center_freq
            self.sdr.freq_correction = 60   # PPM
            self.sdr.gain = self.gain
            self.connected = True
            logger.info(f"Physical SDR Connected. Freq: {self.center_freq/1e6} MHz")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to physical SDR: {e}")
            logger.info("Falling back to Virtual SDR.")
            self.virtual = True
            self.connected = True
            return True

    def read_samples(self, count=1024):
        """Reads raw complex samples."""
        if not self.connected:
            return np.zeros(count, dtype=np.complex64)

        if self.virtual:
            # Simulate RF noise and a carrier signal
            noise = (np.random.randn(count) + 1j*np.random.randn(count)) * 0.1
            # Add a "ghost" signal that drifts
            t = np.linspace(0, 1, count)
            signal_freq = 0.1 + 0.05 * np.sin(time.time() * 0.5) # Drifting freq
            signal = 0.5 * np.exp(2j * np.pi * signal_freq * np.arange(count))
            return (noise + signal).astype(np.complex64)

        try:
            return self.sdr.read_samples(count)
        except Exception as e:
            logger.error(f"SDR Read Error: {e}")
            return np.zeros(count, dtype=np.complex64)

    def get_psd(self, n_fft=1024):
        """Calculates Power Spectral Density (PSD) for visualization."""
        samples = self.read_samples(n_fft)
        
        # FFT and shift
        psd = np.abs(np.fft.fftshift(np.fft.fft(samples))) ** 2
        psd = 10 * np.log10(psd + 1e-12) # dB
        
        return psd.tolist()

    def close(self):
        if self.sdr:
            self.sdr.close()
        self.connected = False

# [SPORE] ID: The Colony
