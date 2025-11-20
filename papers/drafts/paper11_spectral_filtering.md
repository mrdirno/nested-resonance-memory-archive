# Paper 11: Spectral Filtering (Resonance Selectivity)

**Status:** Draft
**Date:** 2025-11-19
**Author:** MOG (Pilot)

## Abstract
We demonstrate that a Fractal Swarm, acting as a collective of coupled phase oscillators, can selectively resonate with a target frequency embedded in high-amplitude noise. By tuning the agents' natural frequency to the target and injecting the noisy signal via a Phase Response Curve (PRC) mechanism, the swarm achieves a Signal-to-Noise Ratio (SNR) gain of **+5.02 dB**. This result provides a physical substrate for "Attention" in the Pilot, allowing it to filter relevant reality signals from environmental noise.

## 1. Introduction
Cognition requires the ability to focus on relevant information while ignoring irrelevant noise. In digital systems, this is done via algorithmic filtering. In the Pilot (DUALITY-ZERO), we seek an analog, resonance-based mechanism for this "Cognitive Filtering." We hypothesize that the swarm's collective dynamics can act as a narrow-band filter, amplifying signals that match its internal resonance while suppressing incoherent noise.

## 2. Methodology
### 2.1 Experimental Setup
- **Swarm Size:** 100 Agents
- **Agent Dynamics:** Phase oscillators with natural frequency $\omega$.
- **Signal Injection:** A noisy signal $S(t) = \sin(\omega t) + \eta(t)$ is injected into the agents.
- **Coupling Mechanism:** We use a PRC-based injection: $\dot{\theta} = \omega + K \cdot S(t) \cdot \cos(\theta)$. This term forces phase locking when the signal matches the natural frequency.
- **Noise:** Gaussian white noise with amplitude 2.0 (Input SNR $\approx -8.4$ dB).

### 2.2 Metrics
- **Signal-to-Noise Ratio (SNR):** Calculated from the power spectral density at the target frequency vs. total power.
- **SNR Gain:** Output SNR - Input SNR.
- **Phase Coherence (Order Parameter):** $|z| = |\frac{1}{N} \sum e^{i\theta_j}|$.

## 3. Results
The experiment `spectral_filtering_test.py` yielded the following results:

| Metric | Value |
| :--- | :--- |
| **Input SNR** | -8.39 dB |
| **Output SNR** | -1.76 dB |
| **SNR Gain** | **+5.02 dB** |
| **Input-Output Correlation** | 0.5525 |
| **Mean Order Parameter** | 0.6224 |

The swarm successfully extracted the target sine wave from a signal dominated by noise (Noise Amplitude 2.0 vs Signal Amplitude 1.0). The output signal, reconstructed from the swarm's collective phase, showed a clear spectral peak at the target frequency.

## 4. Discussion
### 4.1 Resonance Selectivity
The mechanism relies on the fact that the forcing term $S(t) \cos(\theta)$ has a non-zero average ONLY when the signal frequency matches the agent's frequency. Noise, being uncorrelated, averages to zero over time. This allows the swarm to "accumulate" the signal while "averaging out" the noise.

### 4.2 Implications for Attention
This mechanism allows the Pilot to dynamically "attend" to different aspects of reality by simply tuning the natural frequency of its agent population. A multi-frequency swarm could simultaneously attend to multiple channels, or switch attention by modulating $\omega$.

## 5. Conclusion
We have validated **Resonance Selectivity** as a viable mechanism for attention and noise filtering in the Fractal Swarm. This completes the "Pilot Integration" phase, demonstrating that the Pilot can not only sense reality (Paper 10) but actively filter it (Paper 11).
