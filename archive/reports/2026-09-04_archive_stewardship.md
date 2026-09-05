# Archive stewardship audit — September 4, 2026

Author: Aldrin Payopay · GPL-3.0-only

This review establishes explicit lifecycle boundaries and measures a small set of repository checks. It does not certify all projects as production software or validate the scientific claims in historical records.

## Measured scope

The Git index based on commit `89457225f0064d7932471f10125b5ccc8d701c76`, after removal of eight tracked private-artifact paths, contained **19,265 tracked files**. The thirteen reviewed lifecycle entries covered **18,440 unique files**, leaving **825 unclassified**. Counts exclude untracked work and the new stewardship files before staging. Per-component counts can overlap; the unique coverage count does not.

The path-list SHA-256 was `1d0244c4e130b3332f24a32ec253c78faf9ddba4f465d44b90b4877e0c48d813`. This is an index-path measurement, not a content hash or a clean-checkout claim. Subsequent changes should regenerate the inventory with `python3 tools/archive/audit.py --check --output <development-output-path>`; CI records a fresh artifact for each run.

The publication-boundary check found **zero remaining prohibited tracked artifacts** after the private-preservation/removal step. Earlier Git history is outside this check and was not rewritten. The `.stp` suffix required a real distinction: a Quartus SignalTap XML session is hardware instrumentation, while STEP geometry is a fabrication artifact. The gate accepts only recognized SignalTap session XML under `fpga/`; an adversarial test rejects geometry renamed into that location. The audit does not scan secret values.

## Lifecycle decisions

- `helios_one` is archived in place: it is a copied repository snapshot whose previous change was `7cca6cdc` (2025-11-30). Root `bcp_lib` and `nrm_core` are the current entry points for their respective work.
- `code/legacy` remains archived in place, matching its established location and previous change `d0fad0b9` (2025-12-08).
- Desktop Helios, its native bridge and `svd_app` remain dormant prototypes. No fresh runtime, model availability or platform-support result was inferred from age or filesystem presence.
- The old root `ARCHIVE_MANIFEST.md` is preserved under `archive/manifests/`. Its replacement points to the reviewed lifecycle map and current entry points. Historical source trees and citation paths remain intact.

The [registry](../../docs/archive/components.json) records an evidence path and next action for every reviewed component. Unclassified material is a remaining audit obligation, not an instruction to delete it.

## Verification

**Archive safety:** 11 tests pass using Python 3.13.5. Tests exercise the real filesystem and Git index: untracked-work exclusion, missing entry points, traversal and symlink rejection, SignalTap/STEP discrimination, read-only previews, byte-preserving moves, late destination collisions and explicit filename requirements. The cleanup preview found **zero candidates and changed no files**. `git diff --check` reported no whitespace errors at this review.

**BCP baseline:** All 24 existing tests pass. Package-wide statement coverage is **49.55%**, rounded to 50% in the console summary. `core.py` has 100% statement coverage; `monitor.py` has 32%, and `visualization.py` has 9%. Statement coverage is not a claim that every behavior is tested. [Captured release-gate output](2026-09-04_bcp_release_gate.txt)

The release gate now runs tests across the whole package and requires more than 90% coverage before build/upload. The **initial baseline failed that coverage requirement**. The September 5 measurement below supersedes its test/coverage status; no release was attempted. Build output must also pass `twine check` before upload. These workflow changes have local command evidence; their hosted execution must be read from the subsequent CI run.

Reproduce the measured BCP gate from `bcp_lib/` in an isolated environment with the `dev`, `monitor` and `viz` extras installed:

```sh
python -m pytest tests --cov=bcp --cov-report=term-missing --cov-fail-under=90.01
```

The recorded run used Python 3.13.5, pytest 8.4.1 and pytest-cov 6.1.1. Unrelated pytest plugins were disabled. Source SHA-256:

| Source | SHA-256 |
| --- | --- |
| `bcp_lib/bcp/core.py` | `60ca59f58ca7580448e23c3b1bea9b8aac6c76c9b8ada1ae40376a54761bc322` |
| `bcp_lib/tests/test_core.py` | `a3b4ae6de5233e7bb0cf636b12a1d1cd40f3144628d4bcd16a1a25a5be50f60a` |
| `bcp_lib/pyproject.toml` | `d2426d3b1b4708651057c5ff409cd2038fbf935c9d03f21ac7d3cd879c263317` |

## BCP optional-module hardening — September 5 follow-up

The initial 24-test / 49.55% package baseline above remains the historical measurement. After the focused monitoring and plotting fixes, **55 tests pass in 2.27 seconds**, with **354 of 369 statements covered (95.9349593495935%)**. The existing core algorithm and its 24 tests are unchanged. `monitor.py` now measures 95.00% and `visualization.py` 97.32%; package-wide coverage clears the >90% gate locally. [Exact command, environment, source hashes and pytest output](2026-09-05_bcp_hardening_gate.txt)

The added tests use actual SQLite databases, temporary files, host psutil readings and headless Matplotlib rendering. Four exported PNGs have valid signatures and non-uniform pixel buffers. The tests inspect recorded figure data and geometry: item names align with heatmap rows, image columns are centered on evaluated budgets, and phase regions and stair steps follow configured thresholds even on a three-point grid. Export to a missing directory raises a real filesystem error and releases only the newly created figure. No mocks or fabricated measurements were used. An isolated copy of the initial sources also failed the new timing, row-alignment, phase-shading and failed-export checks before repair.

Monitoring now uses a monotonic deadline and caps its last sleep at the remaining duration. Finite, non-negative budgets and valid schedules are required. Collector errors and non-finite readings are represented by NaN plus an exception-class field, while other collectors continue; exception messages are omitted. System CPU collection measures a real 0.1-second interval. Missing psutil now raises an explicit dependency error instead of returning an invented budget of 0.5. Gains/costs remain caller-chosen weights. An in-flight collector or callback can exceed the requested duration; the monitor does not forcibly cancel it.

Plots reject empty, duplicate or changing item identities and mismatched summary budgets before creating a figure. Heatmap colors retain the same 0/1 scale when every item is ignored. Figure ownership is documented, and failed layout/export releases the new figure. The package README now provides a runnable system-monitor example and describes greedy selection, configured phase labels and synthetic scenario assumptions without a global-optimum or universal-law claim.

This local run used Python 3.13.5, numpy 2.3.5, psutil 7.0.0, Matplotlib 3.10.3 (Agg), pytest 8.4.1 and pytest-cov 6.1.1. Runtime modules also parsed using Python 3.8 grammar; that is syntax evidence, not an execution claim for Python 3.8. Optional-dependency absence branches and every invalid-input case were not exercised. Cross-version hosted CI, comparative performance, scientific validity and release suitability require their own evidence. No package build or upload was performed by this hardening pass.

## Public wording and remaining work

The README and Quickstart now describe model assumptions, keep historical scope counts separate from validation, and link the 60-run HALO memory-estimator finding. Manuscripts are identified as artifacts rather than asserting submission or acceptance. Current browser behavior still needs the separate HALO/browser verification record.

Remaining work includes reviewing the unclassified files, defining a supported root Python API boundary, broader BCP input-domain and performance validation, verifying dormant projects before revival, and checking manuscript publication states against actual records. None of those gaps can be closed by a lifecycle label or a clean Git index.

## Follow-up preservation and port repair

Eleven pre-existing local research files (phase-locking/structural drafts, their superseded report, sensor-filtering script/report and available summary JSON) were preserved under [archive/provisional](../provisional/2026-09-04-research-drafts/README.md). The provenance manifest records original paths, lengths and SHA-256 values. Both workspace copies matched the originals before the former local files were removed. A Git-tracked exact-filename search found no callers; no campaign was run. The wrapper identifies frequency-clipping, edge-count-control and generated-report limitations rather than promoting their historical verdicts.

The tracked `experiments/halo/ports/particle_port.py` previously imported decimal digit tables from an untracked adjacent HTML copy, so a clean checkout could not import it. It now resolves the tracked canonical HALO page relative to the module, with `HALO_PORT_HTML` as an explicit historical override. The parser reads only four 2,500-digit tables; the old port equations and 1/30 s timestep remain independent of current HALO. Imports of `particle_port` and `port2` succeeded from outside the checkout; the existing digit/Bessel/Legendre/finite-difference checks passed, the explicit historical override parsed, and malformed input was rejected. These are import and mathematical sanity checks, not a particle-campaign result.
