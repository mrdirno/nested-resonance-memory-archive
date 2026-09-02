# QUICKSTART (older version): the OSD Physics Demo

This section used to be the "Golden Path" in [docs/runbooks/QUICKSTART.md](../runbooks/QUICKSTART.md).
The quickstart now runs the Starving Philosopher experiment instead. The text below is kept as it was.
The demo still runs and needs only numpy:

```bash
python3 -m pip install numpy
```

## The Golden Path (Verify Physics)

Run the **OSD Physics Demo**. This script simulates the core ontological claim of the project: that "Dark Matter" is simply energy (Scalar Sum) that is invisible due to destructive interference (Vector Sum).

```bash
python3 archive/experiments/demo_osd_physics.py
```

### Expected Output
You should see a clear comparison between **Constructive Interference** (Bright) and **Destructive Interference** (Invisible).

```text
--- CASE B: DESTRUCTIVE INTERFERENCE (Out of Phase) ---
   Vector Sum (Amplitude): 0.00
   Visibility (|V|^2):     0.00  (Invisible!)
   Mass (Scalar Sum):      2.00  (Still Heavy)

✅ PASS: Mass is Conserved (Energy Input is constant).
✅ PASS: Visibility Vanished in Case B.
```
