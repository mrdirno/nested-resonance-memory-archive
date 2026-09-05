# Archive lifecycle map

Author: Aldrin Payopay · Reviewed September 5, 2026 · GPL-3.0-only

Start with [HALO](../../HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html), the [current research program](../../META_OBJECTIVES.md), or the [BCP library](../../bcp_lib/README.md). This archive preserves science, mathematics, engineering, creative tools and historical explorations with different levels of evidence. A directory's presence does not make it a supported product or validate its claims.

[The machine-readable registry](components.json) records lifecycle, entry points, evidence and a next action for each reviewed component. Its labels are stewardship decisions. The audit checks paths and the publication boundary; it does not run the projects or certify their science.

| Lane | Current entry | Boundary |
| --- | --- | --- |
| Particle research | HALO, `tests/halo`, `experiments/halo` | Active instrument; registered memory results need a valid estimator before a claim is accepted or rejected. |
| Practical and creative tools | Field Toolkits, Commons, Collage Studio | Active browser surfaces with deployment gates. |
| Reusable software | Root `bcp_lib` | Maintained attention allocator; release still requires tests, measured coverage and the release doctrine. |
| Research source | `nrm_core`, `src`, experiments, papers | Experimental. Prefer a specific script, protocol and receipt to a broad capability claim. |
| Historical source | The 500 visual studies, `archive`, `backup`, `backups`, `code/legacy`, `helios_one`, legacy workflows | Archived in place. Preserve source and citations; do not treat old directives as the current program. |
| Dormant prototypes | Desktop Helios, native bridge, `svd_app` | No fresh production verification. Revive with a scoped environment and acceptance test before promotion. |

The `helios_one` tree last changed in commit `7cca6cdc` (2025-11-30), and `code/legacy` in `d0fad0b9` (2025-12-08). Those commits, copied module layout and existing legacy location support retaining them as historical snapshots. `svd_app` last changed in `0ebd7f53` (2025-12-08); age alone does not prove it is unusable, so it remains a dormant prototype. No source tree was deleted or moved to assign these labels.

Run the read-only audit with Python 3.10 or later:

```sh
python3 tools/archive/audit.py --check
python3 tools/archive/audit.py --output /path/to/development-workspace/archive-inventory.json
python3 -m unittest discover -s tests/archive -v
python3 automation/scripts/cleanup_repo.py --root .
```

The inventory measures the Git index, excludes untracked work and includes the source commit and path digest. Per-component counts may overlap when a focused component sits inside a broader research tree; the total classified count is deduplicated. Unclassified files remain visible as a count and in the top-level distribution. The audit refuses missing registry entry points, unsafe paths and tracked fabrication/manufacturing artifacts. The `.stp` suffix is ambiguous: only actual Quartus SignalTap session XML inside `fpga/` is accepted; STEP geometry remains excluded. It does not inspect secrets or establish execution health. CI uploads a fresh inventory rather than committing a perpetually stale file count.

Cleanup previews are read-only. After reviewing file contents, callers and running processes, apply named candidates with `--apply --only filename`. The tool skips collisions, rejects symlinks and never deletes a source without first creating its archive link. See the [maintenance protocol](../protocols/MAINTENANCE_PROTOCOL.md).

The [provisional research collection](../../archive/provisional/2026-09-04-research-drafts/README.md) preserves eleven former local drafts and result files byte for byte, with explicit validity caveats and no new execution claim.

Before promoting a dormant component, record its purpose, supported platforms, locked dependency environment, runnable entry point, meaningful tests and measured result. Keep negative findings and retractions attached to their original records. New frameworks should answer an experimental need; dependency count is not a quality metric.

The [500 visual studies](../../HELIOS-BRIDGE-ARCHIVE/README.md) remain a browsable creative collection. HALO V501 has its own active entry within that broader historical directory. The conflict-resolution and dated files under `backup` and `backups` are historical copies (last tree change `ac1e7bae`, November 30, 2025), retained in place. No fresh execution or content-validity claim is inferred from these classifications.
