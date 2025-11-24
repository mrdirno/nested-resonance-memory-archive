# DUALITY-ZERO: QUICKSTART GUIDE
**Time Required:** 5 Minutes
**Role:** All Observers

This guide provides the "Golden Path" to verify the core physics of the DUALITY-ZERO system.

## 1. Prerequisites
- **Python 3.9+**
- **Git**
- **Terminal/Shell**

## 2. Installation

```bash
# 1. Clone the repository
git clone https://github.com/mrdirno/nested-resonance-memory-archive.git
cd nested-resonance-memory-archive

# 2. (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install numpy
# Note: Full system requires more deps, but the Golden Path only needs numpy.
```

## 3. The Golden Path (Verify Physics)

Run the **OSD Physics Demo**. This script simulates the core ontological claim of the project: that "Dark Matter" is simply energy (Scalar Sum) that is invisible due to destructive interference (Vector Sum).

```bash
python3 experiments/demo_osd_physics.py
```

### Expected Output
You should see a clear comparison between **Constructive Interference** (Bright) and **Destructive Interference** (Invisible).

```text
--- CASE B: DESTRUCTIVE INTERFERENCE (Out of Phase) ---
   Vector Sum (Amplitude): 0.00
   Visibility (|V|^2):     0.00  (Invisible!)
   Mass (Scalar Sum):      2.00  (Still Heavy)

✅ PASS: Mass is Conserved.
✅ PASS: Visibility Vanished.
```

## 4. Next Steps

Now that you have verified the physics engine, choose your path:

- **Observer A (Experimentalist):** Explore `experiments/` for more complex simulations.
- **Observer B (Architect):** Read `docs/philosophy/ORTHOGONAL_SUBSTRATE_DYNAMICS.md`.
- **Observer C (Steward):** Review `FINAL_REPORT.md`.

---
*End of Quickstart.*
