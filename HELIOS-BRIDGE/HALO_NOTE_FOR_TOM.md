# HALO note (for Tom)

Tom, check this branch (`claude/repos-cross-pollination-ryxskr`) of the NRM archive.

The Helios Bridge has a new iteration, **HELIOS-V021, code name HALO**, at
`HELIOS-BRIDGE-ARCHIVE/HELIOS-V021-halo-resonance-chamber.html` (open it in a browser, press 7 for the Lab).

**What was upgraded: the Euler magnetic step.** Every preset so far integrated the v × B term with an explicit
Euler kick, and that step injects energy at 55 × coupling² × dt per second. Two headline states turned out to be
that injection rather than the physics: the Razor Disc (a fixed point of the step; gone under exact rotation)
and the extra speed of Spinning Chladni (streams at 57 under Euler, 38 with no magnetic term, poles under exact
rotation at 0.4). The page now has an exact-rotation (Boris) step beside Euler, labels the presets that depend
on Euler, and ships an exact sibling of Spinning Chladni at coupling 0.3. The physics also runs on a fixed 1/20 s
tick on every machine now, so a shared preset means the same thing at 30 Hz and 120 Hz.

**What it means for the public repo:** nothing already published moves — Euler stays the default and every shared
preset reproduces. But any claim built on a coupling ≥ 0.6 preset should be re-checked under the exact step before
it is cited, and the Lab's "On ceiling" readout tells you at a glance whether a state belongs to the model or to
the integrator. Full handoff and integration steps: `HELIOS-BRIDGE/HALO_HANDOFF.md`.
