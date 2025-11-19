# S3: Visualization Utilities

## Location

`../visualization_utils.py`

## BistabilityVisualizer Class

Complete publication-grade visualization system for bistable dynamics.

### Features:
- 300 DPI output (journal quality)
- Consistent styling across all figures
- Proper axis labels and legends
- Color-blind friendly palettes

### Methods:

#### 1. `plot_bifurcation_diagram(frequencies, basin_a_percentages, critical_freq)`
Generates bifurcation diagram showing Basin A percentage vs frequency.

**Output**: Figure 1 from manuscript

#### 2. `plot_linear_regression(thresholds, critical_frequencies, slope, intercept, r_squared)`
Plots linear regression from C170 multi-threshold validation.

**Output**: Figure 2 from manuscript (R² = 0.9954)

#### 3. `plot_phase_diagram(frequency_range, threshold_range, slope, intercept)`
Creates 2D phase diagram showing dead zone vs. resonance zone.

**Output**: Figure 3 from manuscript

#### 4. `plot_composition_rate_validation(frequencies, avg_composition_events)`
Validates that composition events ≈ spawn frequency.

**Output**: Figure 4 from manuscript

### Usage Example:

```python
from pathlib import Path
from visualization_utils import BistabilityVisualizer

# Initialize
viz = BistabilityVisualizer(output_dir=Path('visualizations'))

# Generate figure
viz.plot_bifurcation_diagram(
    frequencies=[2.0, 2.1, ..., 3.0],
    basin_a_percentages=[0, 0, ..., 100],
    critical_freq=2.55
)
```

### Generated Figures

All figures saved to `../visualizations/`:
- `bifurcation_diagram.png` (Figure 1)
- `linear_regression.png` (Figure 2)
- `phase_diagram.png` (Figure 3)
- `composition_rate_validation.png` (Figure 4)

## Running

```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
python visualization_utils.py  # Generates all 4 figures
```

## Dependencies

- `matplotlib>=3.7.0`
- `numpy>=1.24.0`
- `scipy>=1.10.0` (for interpolation)

## See Also

- **S4_RESEARCH_SUMMARY.md** - Context for each figure
- **Manuscript Figure Captions** - Detailed descriptions
