# Headless tests for the Resonance Chamber (HELIOS-V501, code name HALO)

These tests drive the page in a headless browser and check the physics tick, the
instruments in the Lab panel, and the whole user interface. They were written for
software rendering (SwiftShader), so they run the same on a laptop and in CI.

## Run

The observation bench and replay contract are documented in [HALO Observatory](../../docs/halo/OBSERVATORY.md). `observation_test.js` tests actual GPU state equality, paired integrators, a zero-coupling negative control, recipe downloads/imports, invalid inputs, interruptions, mobile layout and keyboard/reduced-motion behavior. Release receipts preserve canonical source and generated-page SHA-256, their binding and child exit statuses in the ignored `workspace/release/` directory. The package and lockfile are tracked so CI installs the same browser driver.

```bash
cd tests/halo
npm ci
npx playwright install chromium
npm test                    # release gate: tick, observation, Lab, smoke
python3 -m venv workspace/physics-env
. workspace/physics-env/bin/activate
python -m pip install -r requirements-physics.txt
npm run test:physics        # integrator, mesh, conservation, dimer, numerical bench
python3 make_test_page.py      # builds rc-test.html from ../../HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html
node tick_test.js              # fixed tick, interpolation, Boris toggle, float deposit — 13 checks, ~10 s
node lab_test.js               # the instruments in three regimes — 23 checks, ~2 min
node integ_test.js             # substeps Auto and the phase-space volume meter against Liouville — ~2 min
node dimer_test.js             # the mode dimer: off path, eigenvalues, the loop around the exceptional point, the matter follows — ~3 min (RC_BASE=<probe build without this change> adds the OFF-equivalence check)
node smoke.js                  # the whole interface, including the CSV exports — 95 checks, ~4 min
node bench_test.js             # two clumps in orbit against the numpy twin, Save NPZ (loaded with numpy), the periodic-box growth rates — ~3 min
node mesh_test.js              # self-gravity mesh: Exact solver and cloud-in-cell against a JS reference — 36 checks, ~6 min (RC_BASE=<probe build of the page before this change> adds the two byte-equivalence checks)
node conserve_test.js          # the energy and angular-momentum instruments: the field energy against the
                               # force by finite differences, the three audits, the damping and Euler-pump
                               # rates, the GPU sums against a CPU sum, and (with HALO_BASE_PAGE=<probe
                               # build of the page before this change>, default ../../_base/tests/halo/rc-test.html)
                               # a seeded 100-tick byte comparison proving the instruments change nothing
                               # while they are off — ~3 min
```

Playwright uses its own downloaded Chromium. To use another build, set
`PW_CHROMIUM_PATH=/path/to/chromium`.

`rc-test.html` is a test build: it swaps the three.js CDN tag for the local copy
(`three.min.js`, MIT) and adds a probe bridge on `window.__probe`. It is
git-ignored and must never be published.

The other scripts (`boris*_test.js`, `selfgrav_test.js`, `spin_support.js`,
`gainloss_test.js`, `poisson_check.js`, `half_probe.js`, `ext_probe.js`,
`cam_check.js`, `lab_shot.js`) are the single-question probes that produced the
numbers in the page's rings; each writes its result as JSON or prints it.
