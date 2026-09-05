# HALO Observatory release record — September 5, 2026

Author: Aldrin Payopay · GPL-3.0-only

HALO now has a reproducible observation bench: seeded starts, paired magnetic integrators, exact tick stops, sampled energy/radius/force-ceiling measurements, and downloadable recipes that can be replayed. Its existing spherical-cavity engine and historical presets remain the computational model. [Use the bench](../../docs/halo/OBSERVATORY.md) · [Structured local receipts](2026-09-05_halo_observatory.json)

![HALO observation bench beside the one-million-particle field](assets/2026-09-05_halo_observatory.png)

## Numerical and interaction evidence

Nine sequential browser/numerical suites passed locally: tick, observation, Lab, UI smoke, integrator, mesh, conservation, dimer and numerical bench. The 24 observation checks include full small-count GPU position/velocity equality on replay, zero magnetic coupling as a negative control, warm mesh/probe reset, actual JSON download/import, interruption paths, invalid settings, keyboard input and reduced motion. The numerical bench also loads the real NPZ export in NumPy and compares the orbit and periodic mesh behavior with independent computations.

The full local suites measured source `e0fc351eb46cce21f2d9e4a4a594b23d308b9a522318f9df593fc6ddbfb2d0a5`. A subsequent CSS-only correction makes the sticky Lab heading opaque and keeps the navigation on one row where its 44px targets fit; every inline script remained byte-identical. The first published commit carried source `87bfc66c17cc359d76bd2e40a041032d175e6834b01694aa5564b19bc88c3769`; its 24 observation checks and served-page test passed locally. The hosted gate then exposed a navigation overlap and refused deployment, as recorded below.

The served-page check uses the actual production HTML, without the probe bridge: 1,048,576 particles, seed 12345, two 40-tick runs, matching sampled initial states, finite endpoints, a downloaded record, mobile bounds and zero JavaScript page errors. Chromium software rendering and the in-app browser were both used for visual inspection. The screenshot above is from that local production preview, not a claimed new scientific result.

Optional old-versus-new OFF-equivalence checks had no historical probe build and were skipped; their substantive solver/conservation assertions ran. The observation fingerprint is only a small-sample diagnostic. Device arithmetic can differ. Nothing here is a new full-count memory campaign or evidence that validates NRM.

## Software and archive changes

The classic Bridge now runs TypeScript checking before its Vite build. The touch-control constant, icon prop typing and numeric overlay values were corrected. Compatible dependency updates reduced its npm advisory count from eight to zero at this measurement. Obsolete client-side API-key substitutions were removed after finding no callers. The production build passes, but its roughly 334 kB compressed JavaScript chunk still warrants a measured loading-performance review.

The lifecycle map covers HALO, the classic Bridge, creative/practical tools, BCP, research code, papers, hardware and historical copies. The 500 visual studies are preserved as a creative collection, with clear limits on their physics labels. Provisional drafts retain original bytes and provenance; the dormant SEVEN integration retains its source and patch with the observed anonymous authorization failure documented. Eight prohibited tracked artifact paths were preserved privately and removed from the current index. Earlier Git history was not rewritten.

Archive boundary and cleanup checks pass (11 real-filesystem/Git tests; zero cleanup candidates). Eight existing fractal, memory and reality checks also pass in an isolated copy, with real SQLite and grounded psutil readings; [the receipt](2026-09-05_nrm_core_check.txt) states the limited scope. Workflow validation passes with actionlint 1.7.12 and shellcheck 0.11.0, installed through Homebrew for this review. BCP monitoring/plotting repairs pass 55 tests with 95.93% whole-package coverage; the [stewardship report](2026-09-04_archive_stewardship.md) preserves the initial 49.55% baseline and the new evidence. No package release was attempted.

## Publication status

The [first hosted HALO gate](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33952410864) failed at a real interaction: the bottom navigation covered the Lab switch after scrolling. A new pointer-target regression failed on that source at 1280×800. The repair places desktop panels above the navigation and reserves scrolling space for the header and mobile navigation. All 28 observation checks now pass, including actual clicks at 1280×800, 900×600, 360×844 and 390×844. The served one-million-particle A/B check passed again. The repaired source is `e515335b1d4159b396779a9b3e3bac6132a6b24b2434eb8b20cf4710763724ea`; every inline script is byte-identical to the first commit.

Main pushes now enter the reusable HALO gate through Pages once, removing the duplicate standalone push job. Pull-request and manual checks remain available. The subsequent deployment receipt will identify the published commit, hosted checks and live page inspection. A clean index or source hash alone is not live visual evidence.

## Remaining research and maintenance

A valid memory estimator still needs centered and matched spatial support, radial controls, null checks and measured injection recovery before a new protocol is frozen. Unclassified archive files and unverified dormant projects remain visible obligations in the inventory. Coverage and lifecycle labels do not certify the entire repository or its historical claims.
