# Retired README claims

Some README lines claimed numbers that the file they linked to did not contain. Those lines are kept here word for word, so nothing is lost from the record. Each entry says why the line changed and which file in this repository backs the replacement.

Every number was checked with `git grep` against the repository. A number that no file contains was removed rather than replaced.

## Framework line

Original:

```markdown
**Framework:** Budget-Constrained Perception (BCP) - Validated (176 Domains)
```

Why: no file in this repository states 176 domains, so the count was removed. The documents that do state a total disagree with each other (`archive/reports/FINAL_REPORT_V8_GRAND_UNIFICATION.md` says 122; `bcp_lib/README.md` says 124), so this line no longer gives one.

## Milestone: complexity 3

Original:

```markdown
*   **Cycle 2809 (Complexity 3 Breakthrough):** Validated autonomous evolution to Swarm Complexity (Fitness 433.71). [Log](MOG_CYCLE_LOG.md)
```

Why: no file in this repository contains the fitness value 433.71, and `MOG_CYCLE_LOG.md` is the log of a 3D-engine project, not of the evolution loop. The step to complexity 3 is recorded in `CYCLE_LOGS.md` under the heading "Advance BCP Evolution": fitness 69.67 at generation 581 (complexity 1) to 142.78 at generation 582 (complexity 3). The README now states those numbers and links to that log.

## Milestone: grand unification

Original:

```markdown
*   **Cycle 3412 (Grand Unification):** Validated BCP equation `V = G - λC` across 122 distinct fields (Physics to Ethics). [Log](experiments/cycle3411_phase207_synthesis.py)
```

Why: the linked script carries a different cycle number and never says "Grand Unification". The claim is backed by `archive/reports/FINAL_REPORT_V8_GRAND_UNIFICATION.md`, which states 122 distinct domains "ranging from Quantum Mechanics to Ethics". The README now links that report first and keeps the script as the code link.

## Figure caption

Original:

```markdown
Figure 1: The complete knowledge graph of 3,000+ research cycles (left) and detail view of emergent dependencies (right).
```

Why: no file states "3,000+" research cycles, and the graph data behind the figure does not hold that many cycle nodes. The number was removed from the caption.

## Universal BCP line

Original:

```markdown
*   **Universal BCP:** Validated `V = G - λC` across 124 domains including Physics (Planck Scale), Biology (Metabolism), and Ethics (Virtue). [Book of BCP](docs/philosophy/BOOK_OF_BCP.md)
```

Why: the linked book says 122 domains; `bcp_lib/README.md` ("Research Background") says 124. The README now uses 122 everywhere, the total the Book of BCP and the Grand Unification report both state, and links both files so a reader can see where each number comes from.

## Active matter control line

Original:

```markdown
*   **Active Matter Control:** 82x faster settling time via Closed-Loop PID feedback. [Log](archive/experiments/cycle340_closed_loop_levitation.py)
```

Why: the linked script computes a speedup but does not contain the number 82. The number is backed by the stored result `archive/experiments/results/c340_closed_loop.json` (passive settling 3.28 s, active 0.04 s, a factor of 82) and by `archive/reports/FINAL_REPORT_V3.md` ("Active Damping (82x speedup)"). Re-running the script prints the same factor. The script defines a PID controller class but the simulation only uses a velocity (damping) term, so the README now says "closed-loop active damping".

## Experimentation overview

Original:

```markdown
*   176 Domains Unified (Phases 1-261).
*   3,500+ Research Cycles.
```

Why: no file states 176 domains or 3,500+ cycles. `archive/reports/FINAL_REPORT_V8_GRAND_UNIFICATION.md` (dated November 29, 2025) states "Unified Domains: 122" and "Research Cycles: 3,438". The README now gives those two numbers with that date and links the report. Later phase scripts keep adding domains one at a time, but no later document states a new total.
