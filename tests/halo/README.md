# Headless tests for the Resonance Chamber (HELIOS-V501, code name HALO)

These tests drive the page in a headless browser and check the physics tick, the
instruments in the Lab panel, and the whole user interface. They were written for
software rendering (SwiftShader), so they run the same on a laptop and in CI.

## Run

```bash
cd tests/halo
npm init -y >/dev/null && npm i playwright@1
python3 make_test_page.py      # builds rc-test.html from ../../HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html
node tick_test.js              # fixed tick, interpolation, Boris toggle, float deposit — 13 checks, ~10 s
node lab_test.js               # the instruments in three regimes — 23 checks, ~2 min
node smoke.js                  # the whole interface, including the CSV exports — 95 checks, ~4 min
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
