# Nested Resonance Memory (NRM) — DUALITY-ZERO

**[Open HALO, the Helios Bridge particle laboratory](https://mrdirno.github.io/nested-resonance-memory-archive/)**

[![HALO Observatory with a recorded A/B comparison](archive/reports/assets/2026-09-05_halo_observatory.png)](https://mrdirno.github.io/nested-resonance-memory-archive/)
*Choose Observe for seeded A/B runs, exact tick stops and replayable records. [Release evidence](archive/reports/2026-09-05_halo_observatory.md).*

**Author:** Aldrin Payopay ([@mrdirno](https://github.com/mrdirno)) · Persona500 LLC<br>
**Copyright:** © 2025–2026 Aldrin Payopay · [GPL-3.0-only](LICENSE)<br>
**Repository:** [nested-resonance-memory-archive](https://github.com/mrdirno/nested-resonance-memory-archive)<br>
**Status:** Active browser tools and experimental research archive<br>
**Frameworks:** Nested Resonance Memory hypothesis; Budget-Constrained Perception attention allocator

[Citation metadata](CITATION.cff) · [Citation formats](https://mrdirno.github.io/nested-resonance-memory-archive/citation.html) · [Authorship](ATTRIBUTION.md) · [AI assistance disclosure](ACKNOWLEDGMENTS.md)

---

## 🧬 OVERVIEW

This archive connects particle research, constrained optimization, practical software and creative tools. Its central NRM question is whether patterns retained at one scale influence the next. Each experiment needs its own measurements and controls. A shared mathematical objective does not establish a universal physical or social law.

**Recent findings and engineering work:**

* **A memory test that measures geometry:** The registered grid contains 60 runs at 4,194,304 particles and 24 epochs each. Its Retained − Two-back statistic also fires on static radial profiles and is confounded by sampling geometry. This audit supports neither acceptance nor rejection of the NRM claim. [Protocol](docs/preregistrations/2026-09-02_halo_cross_epoch_memory.md) · [Analysis and controls](analysis/2026-09-02_cross_epoch_memory_preregistered.md)
* **A replacement estimator the recorded grid cannot support:** An estimator that re-centres each snapshot, compares only the region both snapshots cover and removes the spherically symmetric part, with five falsifiers declared in advance, was frozen on 2026-09-05 and scored once on the same 60 runs. It declares 0 of 60 runs measurable: 179 of 1,320 run-epochs (one epoch of one run) pass its eligibility gates, so its result is "insufficient support"; its recovery test could not be evaluated, and its sensitivity is stated on synthetic controls only. The three seeds of a condition are near-copies in 17 of 20 conditions, the shrunken copy of the previous snapshot it compares against covers only 4 to 7 cells in about half of the epochs where the matter has collapsed, and 12 runs are static fields that barely change between epochs. This is a result about the grid, not about NRM; the next grid has to be shown measurable first. [Protocol](docs/halo/2026-09-05_memory_estimator_qualification_protocol.md) · [Result and controls](analysis/2026-09-06_memory_estimator_qualification.md)
* **A reproducible comparison bench:** HALO adds seeded A/B magnetic comparisons, exact stopping ticks and JSON observation recipes. These are tools for testing numerical behavior, with their scope and replay limits stated in the [Observatory guide](docs/halo/OBSERVATORY.md).
* **An archive with explicit lifecycles:** Active tools, experimental work, dormant prototypes and historical snapshots have a [reviewed map](docs/archive/README.md) and [machine-readable registry](docs/archive/components.json). A read-only audit checks entry points and the publication boundary.

---

## 🌐 THE BRIDGE (Live Interface)

**[Enter HALO](https://mrdirno.github.io/nested-resonance-memory-archive/)** · [Source](HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html) · [Browser tests](tests/halo/) · [Observatory guide](docs/halo/OBSERVATORY.md)

HALO advances its numerical model in fixed 1/20 s steps and interpolates the rendered frames. Compare the original Euler magnetic kick with the exact magnetic rotation, inspect force-ceiling occupancy and the realized spectrum, and save an observation recipe. A fixed tick controls simulation time; it does not guarantee that every device processes 20 ticks per wall-clock second or produces bit-identical GPU results.

Press **7** for the Lab and **8** for Tools. The memory indicators retain their historical labels, but their original comparison is confounded; read the [estimator audit](analysis/2026-09-02_cross_epoch_memory_preregistered.md) before interpreting them. Particle count, force caps, browser performance and discretization are experimental conditions, not evidence of physical validation.

The [classic Bridge](https://mrdirno.github.io/nested-resonance-memory-archive/archive/classic/) remains accessible. Field Toolkits, Commons and Collage Studio are reached through Tools. Their [deployment workflow](.github/workflows/deploy_bridge.yml) defines which sources are actually served.

---

## 🚀 LOCAL DEMO (The Proof)

Run a small computational demonstration of scale selection under a specified cost function:

1. Install the demo dependencies: `python3 -m pip install numpy matplotlib` in a virtual environment.
2. From the repository root, run `python3 experiments/cycle2568_starving_philosopher.py`.
3. Inspect the selected averaging scale as the script's prescribed energy budget decreases. The output figure is `data/figures/cycle2568_starving_philosopher.png`; use `--out` to write to your development workspace.

The [script](experiments/cycle2568_starving_philosopher.py) generates a synthetic signal, assigns computational cost inversely to scale and schedules the energy decline. Its output illustrates those assumptions. It does not measure human ignorance, biological metabolism or voluntary behavior. Its historical console verdict should be read within that model.

[Full Quickstart Guide](docs/runbooks/QUICKSTART.md)

---

## 🔭 OBSERVER LANES (Choose Your Path)

* **Experimentalist:** [HALO protocol](docs/preregistrations/2026-09-02_halo_cross_epoch_memory.md) · [Measured analysis](analysis/2026-09-02_cross_epoch_memory_preregistered.md) · [Experiment source](experiments/halo/)
* **Architect:** [Observatory](docs/halo/OBSERVATORY.md) · [BCP library](bcp_lib/README.md) · [NRM research source](nrm_core/)
* **Steward:** [Lifecycle map](docs/archive/README.md) · [Archive navigation](ARCHIVE_MANIFEST.md) · [Maintenance protocol](docs/protocols/MAINTENANCE_PROTOCOL.md)

---

## 🏗️ SYSTEM OVERVIEW

**1. HELIOS BRIDGE — Interface:** HALO renders the numerical chamber and exposes measurements. The [classic React interface](HELIOS-BRIDGE/) is maintained under its archive URL.

**2. RESEARCH ENGINES:** [NRM and Helios Python source](nrm_core/) and [experiment scripts](experiments/) contain several generations of numerical models. Select a specific implementation and test before relying on it; the repository is not a single certified engine.

**3. MEMORY AND PATTERNS:** [Memory implementations](src/memory/) encode pattern storage and evolution. Their presence is separate from experimental evidence for cross-scale memory in HALO.

<p align="center">
  <img src="data/figures/holocron_overview.png" width="45%" alt="Historical research knowledge graph overview"/>
  <img src="data/figures/holocron_zoomed_cropped.png" width="45%" alt="Detail of historical research knowledge graph"/>
</p>
<p align="center"><em>Historical knowledge-graph visualizations. Links in a graph record relationships; they do not validate the linked claims.</em></p>

**4. PRACTICAL AND CREATIVE TOOLS:** [Shared Field Toolkit runtime](shared/) and [Collage Studio](tools/collage-studio/) support browser workflows. Their deployment and interaction checks are scoped to those tools.

**5. HISTORICAL AUTOMATION:** [The Seed](bootstrap_bcp.py), [Guardian](src/core/guardian.py) and [repository-analysis experiment](experiments/cycle3434_repo_analysis.py) preserve earlier automated research approaches. Inspect their assumptions and effects before execution; they do not replace the [current program](META_OBJECTIVES.md).

**6. HARDWARE:** [FPGA work](fpga/) and the [fabrication protocol](docs/protocols/FABRICATION_PROTOCOL.md) connect research to hardware. Proprietary designs are excluded from the public working tree. A physical capability claim requires a hardware-specific measurement.

---

## 🧪 CORE CAPABILITIES (Evidence and Limits)

* **Controlled particle comparisons:** A fixed tick, alternative magnetic integration steps and recorded settings make numerical comparisons inspectable. [HALO source](HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html) · [Tests](tests/halo/)
* **Attention allocation:** BCP scores candidates by gain minus budget-dependent cost, then chooses an attention set subject to its rules. Tests cover its core behavior; the application-domain presets are examples, not independent validation of those domains. [Implementation](bcp_lib/bcp/core.py) · [Tests](bcp_lib/tests/test_core.py)
* **Memory-test falsification:** Static profiles and radialized recorded meshes expose an estimator confound. This is a result about the instrument, not a verdict on NRM. [Audit](analysis/2026-09-02_cross_epoch_memory_preregistered.md) Its replacement, frozen with predeclared falsifiers, finds the recorded grid unmeasurable: 0 of 60 runs, 179 of 1,320 run-epochs eligible. [Qualification](analysis/2026-09-06_memory_estimator_qualification.md)
* **Historical control and cooperation experiments:** Earlier reports include closed-loop damping and threshold-based cooperation models. Their findings are bounded by their original equations and experimental conditions. [Damping script](archive/experiments/cycle340_closed_loop_levitation.py) · [Recorded result](archive/experiments/results/c340_closed_loop.json) · [Cooperation script](archive/experiments/phase24_social_physics/cycle2077_harsh_winter.py)

---

## 📚 LIBRARIES

**[BCP — Budget-Constrained Perception](bcp_lib/README.md):** a discrete attention allocator for resource-constrained decisions. [Source](bcp_lib/) · [Tests](bcp_lib/tests/)

The September 5 hardening pass runs 55 tests against allocation, real system monitoring, SQLite/files and plotted output. Whole-package statement coverage is 95.93%, up from the initial 49.55%. This clears the coverage threshold; a new release still requires the repository's evidence of usefulness and independence. [Audit record](archive/reports/2026-09-04_archive_stewardship.md)

---

## 📚 TUTORIALS & EXAMPLES

* [Scale-selection Quickstart](docs/runbooks/QUICKSTART.md)
* [HALO Observatory](docs/halo/OBSERVATORY.md)
* [Research CLI source](src/helios/cli.py)
* [Historical self-modeling experiment](src/experiments/cycle2282_self_modeling.py)

---

## 🏗️ ARCHITECTURE DOCUMENTATION

* [Substrate abstraction](nrm_core/helios/substrate.py)
* [Orthogonal Sum Dynamics framework](docs/philosophy/ORTHOGONAL_SUM_DYNAMICS.md)
* [Historical unified-field model](docs/THE_UNIFIED_FIELD.md) · [Simulator definition](archive/experiments/phase28_unification/cycle2103_rosetta_stone.py)
* [Memory structures](src/memory/) · [Component lifecycle registry](docs/archive/components.json)

---

## 📊 RESEARCH & PAPERS

These links identify manuscript and historical report artifacts. A filename or old readiness label does not establish peer review, submission or acceptance.

* [The Book of BCP](docs/philosophy/BOOK_OF_BCP.md): conceptual draft containing broad historical claims.
* [Computational Expense as Framework Validation](papers/compiled/paper1/README.md): manuscript package.
* [Energy-Regulated Population Homeostasis](papers/PAPER2_V3_MASTER_MANUSCRIPT.md): manuscript draft.
* [Encoding Discoverable Patterns: Temporal Stewardship](papers/compiled/paper3/PAPER3_MASTER_MANUSCRIPT.md): manuscript draft.
* [Pattern Mining Framework for Temporal Stability](papers/compiled/paper5d/README.md): manuscript package.

The [November 2025 synthesis](archive/reports/FINAL_REPORT_V8_GRAND_UNIFICATION.md) reports 122 domains and 3,438 research cycles. These are historical scope counts, not 122 independent empirical validations or evidence of a grand unified theory. Current claims should cite a protocol, result and appropriate control.

---

## 🛡️ PHILOSOPHY & STEWARDSHIP

[The Manifesto](THE_MANIFESTO.md) · [Vision](docs/VISION.md) · [Post-Coercion Protocol](docs/philosophy/POST_COERCION_PROTOCOL.md) · [Historical Helios Arc](STEWARDSHIP_HELIOS_ARC_ROADMAP.md) · [Naming Convention](docs/philosophy/NAMING_CONVENTION.md)

These texts explain motivations and exploratory frameworks. Their philosophical scope is distinct from the evidence attached to an experiment.

---

## 🛡️ CITATION

```bibtex
@software{Payopay_Duality_Zero_2025,
  author = {Payopay, Aldrin},
  title = {{Duality-Zero: A Reality Compiler Framework}},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  url = {https://github.com/mrdirno/nested-resonance-memory-archive}
}
```

See [CITATION.cff](CITATION.cff) for the maintained citation metadata. AI assistance is disclosed in [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md); authorship rests with Aldrin Payopay.
