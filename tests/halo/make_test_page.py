#!/usr/bin/env python3
"""Build rc-test.html, the headless test copy of the Resonance Chamber (HELIOS-V501).

Source: ../../HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html
Output: rc-test.html beside this script. It is a TEST BUILD ONLY and is
git-ignored: never publish it.

Three test-only edits, never shipped:
  1. the CDN three.js tag -> the vendored local copy three.min.js
  2. a probe bridge on window.__probe just before the IIFE closes, so a
     headless driver can set state and read the GPU position texture back
  3. a window.__forceDt hook so a test can pin the wall-clock step
"""
import re
import pathlib

d = pathlib.Path(__file__).parent
src = (d.parent.parent / 'HELIOS-BRIDGE-ARCHIVE' / 'HELIOS-V501-halo-resonance-chamber.html').read_text()

out, n = re.subn(r'<script src="https://cdnjs[^"]*three[^"]*"[^>]*></script>',
                 '<script src="three.min.js"></script>', src)
assert n == 1, f'three.js tag swap matched {n} times'

# 3. a wall-clock override so a headless driver can play a 60 Hz or a 3 Hz
#    machine and check the fixed physics tick (test copy only)
out, n = re.subn(r"const dtWall = Math\.min\(\(now - lastTime\) / 1000, 0\.5\);",
                 "const dtWall = window.__forceDt || Math.min((now - lastTime) / 1000, 0.5);", out)
assert n == 1, f'dtWall hook matched {n} times'

PROBE = """
/* ---- test-only probe bridge (rc-test.html only; never shipped) ---- */
window.__probe = {
  DEFAULTS: DEFAULTS, deepPatch: deepPatch, applyPreset: applyPreset,
  renderer: renderer, reseed: reseed,
  get state() { return state; },
  get simTime() { return simTime; },
  get texSize() { return texSize; },
  get posA() { return posA; },
  get velA() { return velA; },
  get pmPot() { return pmPotA; },
  PM: { N: PM_N, TX: PM_TX, TY: PM_TY, HALF: EXTENT * 1.02 },
  lab: lab, applyScenario: applyScenario, TICK: TICK,
  pointsMat: pointsMat, velMat: velMat,
  get tickAccum() { return tickAccum; },
  get lerpOK() { return lerpOK; },
  get posPrev() { return posPrev; },
  get posB() { return posB; },
  get pmDens() { return pmDens; },
  look: function (az, el, dist) {
    markCamUser();
    cam.az = az; cam.el = el; cam.dist = dist;
    applyCamera();
  },
};
"""
marker = '\n})();\n</script>'
assert src.count(marker) == 1, 'IIFE close marker not unique'
out = out.replace(marker, PROBE + marker)

(d / 'rc-test.html').write_text(out)
print('rc-test.html regenerated:', len(out), 'bytes')
