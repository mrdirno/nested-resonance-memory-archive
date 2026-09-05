# Provisional research drafts recovered from the working tree

Author: Aldrin Payopay · Reviewed 2026-09-04 · GPL-3.0-only

This collection preserves eleven pre-existing local files while removing ambiguity about their status. The original script, analysis, retraction and result bytes are retained under `source/` with mirrored former repository paths. The [provenance manifest](provenance.json) records lengths and SHA-256 values. **The experiments were not executed in this review, and their numerical narratives have not been independently verified here.** They are research leads, not current operating directives or accepted scientific results.

Before relocation, a Git-tracked reference search for all eleven exact filenames found zero callers or links. A process-name check found no running instances of the six scratch Python scripts. Source copies were compared byte for byte before the former untracked paths were removed. The ignored sensor result JSON was also preserved. Common credential patterns were checked across the preserved text, and the sensor JSON keys were inspected recursively; no matches were found. No source was executed by this preservation process.

## Phase locking and structural comparison

[Phase-locking draft](source/analysis/2026-09-02_phase_locking_governs_survival.md) · [Comparison draft](source/analysis/2026-09-02_uncontrolled_comparison_pattern.md) · [Superseded June report](source/analysis/retracted/2026-06-26_transcendental_substrate_experiment_report.SUPERSEDED.md)

The five associated scripts are `h_sweep.py`, `proper_control.py`, `lock_law.py`, `replicate_structural.py` and `degree_control.py` under `source/experiments/`. They identify concrete questions about driving parameters, synchronization and comparison controls. Their fixed seeds and parameter loops provide starting points for reproducibility work, but the preserved drafts do not attach captured stdout or per-run data for all the reported tests.

Validity boundaries requiring review before promotion:

- A finite 42-triple result does not establish an unrestricted necessary-and-sufficient phase-locking law. The draft itself leaves parameter and metabolic-cost sweeps open.
- `proper_control.py` clips individual frequencies into a bounded interval after constructing integer-ratio triples. That can break their commensurability, so the group label requires verification before interpreting the comparison.
- `degree_control.py` matches final edge count, not degree sequence or graph modularity. The claimed explanation should remain bounded to that comparison; the mechanistic account is not directly measured by these scripts.
- The five scripts launch their parameter loops at import and resolve dependencies from the working directory. They are historical experiment scripts, not safe library imports or production test modules.
- The superseded report belongs with its correction lineage. Its original `CONFIRMED` language and the newer drafts' strong claims are preserved as historical text, not endorsed by this wrapper.

A revival should first separate importable model code from execution, define the actual matched variables, write a protocol and capture run-level outputs and uncertainty. Do not run a large campaign merely to reproduce a favorable headline.

## Sensor spoofing and filtering

[Script](source/experiments/test_sensor_spoofing.py) · [Generated analysis](source/analysis/sensor_spoofing_findings.md) · [Available summary JSON](source/data/results/sensor_spoofing_results.json)

The JSON contains parameters, summary statistics, filtering and noise sweeps. Its presence is evidence that a result file was recorded locally, not a fresh validation of its origin or numerical conclusions. The original per-trial records are not part of this collection.

The script hardcodes the report date `2026-06-26`, writes both result and analysis paths on execution, and expands `\alpha` and `\approx` in a normal Python string into control characters. Those reporting defects are retained in the original bytes. Its final claim of a fundamental thermodynamic necessity exceeds the scope of the prescribed numerical budget, noise and filtering model. Model behavior and physical thermodynamic evidence must be distinguished before publication of any efficacy claim.

All six Python files passed a syntax-only AST parse; that check executes no experiment and does not establish runtime correctness. A revival should repair reporting, retain seeds and per-trial outputs, distinguish paired from independent comparisons, and test the chosen filtering mechanism against appropriate controls.

## How to use this collection

Use the [current program](../../../META_OBJECTIVES.md) and [lifecycle map](../../../docs/archive/README.md) to select new work. Paths inside the preserved files reflect their original repository location and may be contextual rather than clickable from this directory. Start a reviewed experiment in the development workspace and retain these originals as provenance. Historical instructions embedded in the drafts do not override the current program.
