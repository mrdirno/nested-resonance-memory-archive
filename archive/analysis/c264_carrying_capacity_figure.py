#!/usr/bin/env python3
"""
C264 Carrying Capacity Analysis Figure
Visualizes K = beta × E_recharge relationship with R² = 0.94

Author: Aldrin Payopay
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Data from C264 intermediate results (experiment still running)
e_recharge = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
mean_k = [0.0, 0.0, 2.6604, 2.9190, 4.1501, 8.6665]
sem_k = [0.0, 0.0, 0.2629, 0.3382, 0.3990, 0.2553]
extinction = [1.0, 1.0, 0.15, 0.20, 0.15, 0.0]

# Linear fit parameters
beta = 2.09436671065033
intercept = 0.32586188689915163
r_squared = 0.9408373673325369
p_value = 0.0013393636188548123

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Carrying Capacity vs E_recharge
ax1 = axes[0]
ax1.errorbar(e_recharge, mean_k, yerr=sem_k, fmt='o', capsize=5,
             color='#2E86AB', markersize=8, linewidth=2, label='Observed')

# Add regression line
x_fit = np.linspace(0, 4.5, 100)
y_fit = beta * x_fit + intercept
ax1.plot(x_fit, y_fit, '--', color='#E94F37', linewidth=2,
         label=f'K = {beta:.2f}E + {intercept:.2f}')

ax1.set_xlabel('Energy Recharge Rate (E_recharge)', fontsize=12)
ax1.set_ylabel('Carrying Capacity (K)', fontsize=12)
ax1.set_title(f'Linear Carrying Capacity Model\n$R^2$ = {r_squared:.3f}, p = {p_value:.4f}', fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-0.1, 4.5)
ax1.set_ylim(-0.5, 10)

# Plot 2: Extinction Rate vs E_recharge
ax2 = axes[1]
ax2.bar(e_recharge, [e * 100 for e in extinction], width=0.3,
        color=['#E94F37' if e > 0 else '#2E86AB' for e in extinction],
        edgecolor='black', linewidth=0.5)

# Add threshold line
ax2.axvline(x=0.5, color='black', linestyle='--', linewidth=2, alpha=0.7)
ax2.text(0.55, 80, 'Threshold', fontsize=10, rotation=90, va='bottom')

ax2.set_xlabel('Energy Recharge Rate (E_recharge)', fontsize=12)
ax2.set_ylabel('Extinction Rate (%)', fontsize=12)
ax2.set_title('Phase Transition: Extinction Threshold', fontsize=14)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_xlim(-0.2, 4.5)
ax2.set_ylim(0, 110)

plt.tight_layout()

# Save figure
output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/c264_carrying_capacity_analysis.png")
output_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"Figure saved: {output_path}")
print(f"Key findings:")
print(f"  - Linear model: K = {beta:.2f} × E_recharge + {intercept:.2f}")
print(f"  - R² = {r_squared:.3f}")
print(f"  - p-value = {p_value:.4f}")
print(f"  - Extinction threshold: E_recharge < 0.5")
