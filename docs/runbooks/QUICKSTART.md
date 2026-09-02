# DUALITY-ZERO: QUICKSTART GUIDE
**Time Required:** 5 Minutes
**Role:** All Observers

This guide is the "Golden Path": one command that runs a real experiment from this repository and writes a figure.

## 1. Prerequisites
- **Python 3.9+**
- **Git**
- **Terminal/Shell**

## 2. Installation

```bash
# 1. Clone the repository
git clone https://github.com/mrdirno/nested-resonance-memory-archive.git
cd nested-resonance-memory-archive

# 2. Create a virtual environment (optional, but some systems refuse to install packages without one)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install the two packages the demo needs
python3 -m pip install numpy matplotlib
# Note: the full system needs more (see requirements.txt). The Golden Path needs only these two.
```

## 3. The Golden Path (Run the Experiment)

Run **The Starving Philosopher**. Observe an agent voluntarily choosing ignorance to survive scarcity (The Starving Philosopher Effect).

Run this from the repository root (the folder you moved into above):

```bash
python3 experiments/cycle2568_starving_philosopher.py
```

### Expected Output
The script prints its parameters, runs the simulation, and ends with a verdict and the path of the figure it wrote:

```text
✓ HYPOTHESIS VALIDATED:
  Agent voluntarily increased perceptual scale (became 'more ignorant')
  under metabolic pressure to minimize computational potential.

Generating figure...
Figure saved: .../data/figures/cycle2568_starving_philosopher.png
```

The figure lands in `data/figures/cycle2568_starving_philosopher.png` inside the repository. To write it somewhere else, add `--out`:

```bash
python3 experiments/cycle2568_starving_philosopher.py --out my_figure.png
```

## 4. Next Steps

Now that you have run your first experiment, choose your path:

- **Observer A (Experimentalist):** Explore [`experiments/`](../../experiments/) for more simulations.
- **Observer B (Architect):** Read [Orthogonal Sum Dynamics](../philosophy/ORTHOGONAL_SUM_DYNAMICS.md).
- **Observer C (Steward):** Read [The Manifesto](../../THE_MANIFESTO.md).

An older demo of the interference physics (numpy only) was moved to [docs/legacy/QUICKSTART_OSD_DEMO.md](../legacy/QUICKSTART_OSD_DEMO.md). It still runs.

---
*End of Quickstart.*
