# META OBJECTIVES: NESTED RESONANCE MEMORY

## Mission

Nested resonance memory, as stated, means the relics of one scale seed the next. This repository exists to test that claim and to say plainly what survives. It now has an instrument for the job: HALO, page V501 in the archive (`HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html`). The page runs its physics on a fixed 1/20 s tick, so a result means the same thing on every machine. Its Lab panel measures the page against its own claims: a memory index with a two-back control beside it, a meter for how fast nearby particles drift apart, a realized spectrum, and a CSV log. On the page's first run the memory index read Retained 0.003 against Two-back 0.098. The control scored higher, so nothing yet shows one epoch seeding the next. The program below is ranked by how much we learn per hour; the reasoning and the numbers behind it are in `HELIOS-BRIDGE/HALO_HANDOFF.md` §7 and §8. Status as of 2026-09-01: nothing below has started. The instrument exists.

## Program, ranked

- [ ] **1. Pre-register the memory test and run it at full particle count.**
  Write the protocol down before running: 4.19 M particles, the Spinning Chladni preset and the default preset, epochs of 10 s, at least 20 epochs, self-gravity {0, 0.15, 0.3, 0.5, 0.8}, gain/loss {0, 0.5}. The Lab's CSV is the record, one JSON per run as `data/results/halo_memory_<preset>_<gravity>.json` (that pattern is exempt from `.gitignore`'s `data/results/*.json`). Pass: Retained − Two-back > 0.10 for three consecutive epochs.
  Status: not started. The instrument exists on the page; the protocol is not yet in the repository.
  Proves the claim wrong: Retained never clears Two-back by more than 0.10 for three epochs running. Then the passive-relic version retires, and the README says only that a self-bound object persists across rescalings.

- [ ] **2. Turn the two choreography theorems and the stability certificate into principle cards.**
  Two failure cards: an axial field cannot confine like charges out of plane; a cyclic time-delay symmetry needs a drive periodic in the delay. One positive card: given a drive, the shooting method returns a periodic matter configuration with a stability certificate (24 multipliers, a million-cycle run). Failure cards already live in `src/tsf/engineering_engine/principle_cards/`.
  Status: not started. The script and its logs are not yet in the repository.
  Proves it wrong: a non-planar orbit under an axial field alone, a stable choreography whose drive is not periodic in the delay, or a multiplier off the unit circle.

- [ ] **3. Audit the archive's magnetic family, V251 to V300, with the numpy port.**
  Those fifty pages carry a magnetic term. If it is an explicit Euler kick, some of their signature states may be integrator states pinned at the force ceiling (the cap the simulation puts on any single force; matter held there is a numerical artefact), like the Razor Disc. Findings go into the archive README as labels, not retractions.
  Status: not started. The port is not yet in the repository.
  Proves the worry wrong: the pages do not use the Euler kick, or their states survive under the exact rotation step.

- [ ] **4. Refresh the front door so every sentence cites a measured number.**
  Keep the Bridge as the visualizer. Put HALO beside it as the laboratory with its three measured numbers (self-gravity threshold: 0.45 holds, 0.6 folds; memory index 0.003 against its two-back control 0.098; disc speed 86 measured, 88 predicted), and cut any sentence the Lab cannot back. One entry in `CYCLE_LOGS.md` per iteration, in the format the log already uses.
  Status: the README has a HALO section (added 2026-09-01: a description and a screenshot, none of the three numbers yet). The stale block in `CLAUDE.md` that the handoff names was replaced the same day.
  Proves it wrong: a sentence on the front page with no measured number behind it.

- [ ] **5. Test the "empty wells" idea where it is cheap.**
  Matter pinned to nodal surfaces is invisible to the field's vector sum but carries mass into the scalar sum. The page has both, so "does nodal matter gravitate the figure?" is a page experiment: the realized spectrum against self-gravity at matched settings, with the ceiling share as the honesty check. Do it after item 1, not before.
  Status: not started.
  Proves the idea wrong: the realized spectrum is the same with and without self-gravity at matched settings. A high ceiling share means the run is integrator-bound and does not count either way.

- [ ] **6. A small library, only if item 1 or 2 lands.**
  A `chamberlab` package (Boris and Euler steps, particle-mesh Poisson, twin-particle Lyapunov, memory index with its nulls, the stability certificate) with more than 90 % test coverage. Publish when ripe; ripe means a positive result to demonstrate on.
  Status: not started, and gated on 1 or 2.
  Proves it premature: no positive result from item 1 or 2.

Not planned, because each is the obvious next move and would teach nothing new: rewriting the Bridge app in HALO's image, adding presets or variations, a paper before a positive result, a WebGPU port, filling cycle logs retroactively.
