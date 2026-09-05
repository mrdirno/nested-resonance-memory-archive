# Historical numerical ports

Author: Aldrin Payopay · GPL-3.0-only

These modules preserve earlier NumPy ports of the chamber equations. They are research tools, and their numerical settings are independent of the current browser page. For example, `particle_port.py` retains its original 1/30 s step while HALO uses 1/20 s; reading a newer source page does not make the equations or timesteps identical.

`particle_port.py` reads only the 2,500-digit decimal tables for π, e, √2 and φ from the tracked [canonical HALO page](../../../HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html). The path resolves relative to the module, not the shell's working directory. It no longer requires an untracked adjacent HTML copy. Imports fail explicitly if a table is missing or has the wrong length.

To reproduce a historical digit source, set `HALO_PORT_HTML` to its actual path before importing the module. The `HTML`, `src` and `DEC` module attributes remain available. An override changes the digit tables only; it does not load shaders or synchronize the equations.

```sh
python3 experiments/halo/ports/particle_port.py
# Optional historical source, from any working directory:
HALO_PORT_HTML=/path/to/preserved/chamber.html python3 /path/to/repository/experiments/halo/ports/particle_port.py
```

The direct invocation runs the existing mathematical sanity checks (digit conversion, spherical Bessel functions, Legendre terms and finite-difference gradients). It does not execute a particle campaign or validate agreement with the GPU. Record source hashes, port settings and a matched experiment before using a port result as evidence about the current page.
