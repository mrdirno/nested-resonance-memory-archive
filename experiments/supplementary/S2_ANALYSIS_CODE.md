# S2: Analysis Code

## Location

All analysis scripts are in the parent directory (`../`):

### Core Experimental Scripts:
- `../cycle168_ultra_low_frequency_completion.py` - Initial bistability discovery
- `../cycle169_critical_transition_mapping.py` - Fine-resolution bifurcation mapping
- `../cycle170_basin_threshold_sensitivity.py` - Multi-threshold linear regression validation
- `../cycle171_fractal_swarm_bistability.py` - Full framework population dynamics

### Analysis Scripts:
- `../analyze_cycle175_transition.py` - High-resolution transition width analysis
- `../visualization_utils.py` - Publication-grade figure generation (see S3)

## Usage

Each script is self-contained and can be run directly:

```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
python cycle169_critical_transition_mapping.py
```

Results are saved to `results/` directory as JSON files.

## Code Documentation

All scripts include:
- Docstrings explaining purpose and methods
- Parameter specifications in UPPERCASE constants
- Inline comments for complex logic
- Reality grounding via `core.reality_interface`

## See Also

- **S6_REPRODUCIBILITY_PACKAGE.md** - Complete reproduction guide
- **S4_RESEARCH_SUMMARY.md** - Experimental methodology
