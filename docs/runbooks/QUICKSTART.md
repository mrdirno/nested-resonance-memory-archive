# DUALITY-ZERO: Quickstart

Author: Aldrin Payopay · Updated 2026-09-04 · GPL-3.0-only

This guide runs one scale-selection algorithm and writes a figure. The signal, cost model and declining energy budget are prescribed by the script. It is a computational demonstration, not a measurement of human cognition or biological metabolism.

## 1. Prerequisites

Python 3.9 or later, Git and a terminal. For a browser instrument requiring no installation, open [HALO](https://mrdirno.github.io/nested-resonance-memory-archive/) and its [Observatory guide](../halo/OBSERVATORY.md).

## 2. Installation

```sh
git clone https://github.com/mrdirno/nested-resonance-memory-archive.git
cd nested-resonance-memory-archive
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python3 -m pip install numpy matplotlib
```

These are the two packages required by this demo. The historical repository contains projects with different dependencies; installing every requirement is unnecessary for this example.

## 3. Run the demonstration

```sh
python3 experiments/cycle2568_starving_philosopher.py
```

The script prints its parameters and a historical verdict, then writes `data/figures/cycle2568_starving_philosopher.png`. Inspect the selected averaging scale, prediction error and energy schedule together. The model makes computational cost inversely proportional to scale and changes the budget on a fixed schedule; those assumptions influence what it selects.

The console's phrase `HYPOTHESIS VALIDATED` is the script's own model-specific decision rule. It does not establish that a person voluntarily chooses ignorance or validate a universal law. The [source](../../experiments/cycle2568_starving_philosopher.py) defines the criterion and parameters.

Use `--out` to keep generated figures in your development workspace:

```sh
python3 experiments/cycle2568_starving_philosopher.py --out /your/development-workspace/scale-selection.png
```

Replace the output path with your actual workspace location. On the project's dual-drive setup, active development belongs under `/Volumes/dual/DUALITY-ZERO-V2/`.

## 4. Choose a next step

- **Experimentalist:** Read the [HALO memory protocol](../preregistrations/2026-09-02_halo_cross_epoch_memory.md) and [estimator audit](../../analysis/2026-09-02_cross_epoch_memory_preregistered.md).
- **Architect:** Explore the [BCP allocator and its tests](../../bcp_lib/README.md).
- **Steward:** Use the [archive lifecycle map](../archive/README.md) to distinguish active tools from historical snapshots.

The older [interference demonstration](../legacy/QUICKSTART_OSD_DEMO.md) is retained as historical source.
