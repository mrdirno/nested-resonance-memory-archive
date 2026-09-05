#!/usr/bin/env python3
"""Build rc-test.html, the headless test copy of the Resonance Chamber (HELIOS-V501).

Source: ../../HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html
Output: rc-test.html beside this script. It is a TEST BUILD ONLY and is
git-ignored: never publish it.

Test-only edits, never shipped:
  1. the CDN three.js tag -> the vendored local copy three.min.js
  2. a probe bridge on window.__probe just before the IIFE closes, so a
     headless driver can set state, read the GPU position texture back, call the
     Lab's own density readback and correlation, and report GL capabilities
  3. a window.__forceDt hook so a test can pin the wall-clock step
  4. a window.__tickBudget hook so a test can raise the per-frame tick budget
  5. a window.__simStop hook so a test can halt on an exact tick boundary
"""
import re
import hashlib
import pathlib
import subprocess
import sys

d = pathlib.Path(__file__).parent
REL = 'HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html'

# --from-git <rev> builds the test page from a COMMITTED revision instead of the
# working tree. An experiment whose test build came from an uncommitted tree is not
# reproducible by anyone else, and it can silently inherit another lane's in-progress
# edits -- which is how a stray <script> tag once made every run of the pre-registered
# memory grid log a console error and fail its own validity gate.
rev = None
if '--from-git' in sys.argv:
    rev = sys.argv[sys.argv.index('--from-git') + 1]
if rev:
    src = subprocess.run(['git', '-C', str(d.parent.parent), 'show', f'{rev}:{REL}'],
                         capture_output=True, text=True, check=True).stdout
    print(f'source: {REL} at {rev}')
else:
    src = (d.parent.parent / REL).read_text()
    print(f'source: {REL} in the working tree')

out, n = re.subn(r'<script src="https://cdnjs[^"]*three[^"]*"[^>]*></script>',
                 '<script src="three.min.js"></script>', src)
assert n == 1, f'three.js tag swap matched {n} times'

# 3. a wall-clock override so a headless driver can play a 60 Hz or a 3 Hz
#    machine and check the fixed physics tick (test copy only)
out, n = re.subn(r"const dtWall = Math\.min\(\(now - lastTime\) / 1000, 0\.5\);",
                 "const dtWall = window.__forceDt || Math.min((now - lastTime) / 1000, 0.5);", out)
assert n == 1, f'dtWall hook matched {n} times'

# 4. a per-frame physics-tick budget override so a headless driver can advance
#    simulated time faster than wall clock. The tick is FIXED (TICK = 1/20 s) and
#    simTick() takes no wall-clock argument, so raising the budget changes only how
#    many ticks are issued per rendered frame, never what a tick does. Identity
#    against the shipped budget is asserted by memory_budget_identity.js.
out, n = re.subn(r"const budget = dtWall < 0\.07 \? 2 : 1;",
                 "const budget = window.__tickBudget || (dtWall < 0.07 ? 2 : 1);", out)
assert n == 1, f'tick budget hook matched {n} times'

# 5. a simulated-time stop, checked BETWEEN ticks, so a driver can halt a run on
#    an exact tick boundary rather than an unpredictable frame boundary. simTime
#    is exactly (number of ticks) x TICK, so this makes tick counts reproducible.
out, n = re.subn(r"while \(tickAccum >= TICK && ticks < budget && playing\) \{ simTick\(\); tickAccum -= TICK; ticks\+\+; \}",
                 "while (tickAccum >= TICK && ticks < budget && playing && "
                 "!(window.__simStop && simTime >= window.__simStop - 1e-9)) "
                 "{ simTick(); tickAccum -= TICK; ticks++; }", out)
assert n == 1, f'simStop hook matched {n} times'

PROBE = """
/* ---- test-only probe bridge (rc-test.html only; never shipped) ---- */
window.__probe = {
  SESSION: SESSION, benchObserve: benchObserve, benchParseRecord: benchParseRecord, benchRecord: benchRecord, benchStart: benchStart, sanitizeState: sanitizeState, DEFAULTS: DEFAULTS, deepPatch: deepPatch, applyPreset: applyPreset,
  renderer: renderer, reseed: reseed,
  get state() { return state; },
  get step() { return step; },
  get simTime() { return simTime; },
  get texSize() { return texSize; },
  get posA() { return posA; },
  get velA() { return velA; },
  get pmPot() { return pmPotA; },
  PM: { N: PM_N, TX: PM_TX, TY: PM_TY, HALF: EXTENT * 1.02 },
  lab: lab, applyScenario: applyScenario, TICK: TICK,
  effectiveSubsteps: typeof effectiveSubsteps === 'function' ? effectiveSubsteps : null,
  autoSubsteps: typeof autoSubsteps === 'function' ? autoSubsteps : null,
  labReadDensity: labReadDensity, labCorr: labCorr, PM_N: PM_N,
  get epochN() { return epochN; },
  caps: function () {
    const g = renderer.getContext();
    const d = g.getExtension('WEBGL_debug_renderer_info');
    return { renderer: d ? g.getParameter(d.UNMASKED_RENDERER_WEBGL) : 'unknown',
             float_blend: !!g.getExtension('EXT_float_blend'),
             color_buffer_float: !!g.getExtension('EXT_color_buffer_float'),
             pmWanted: pmType() === THREE.FloatType ? 'float' : 'half',
             pmDensType: !pmDens ? 'unallocated' : (pmDens.texture.type === THREE.FloatType ? 'float' : 'half'),
             posType: !posA ? 'unallocated' : (posA.texture.type === THREE.FloatType ? 'float' : 'half') };
  },
  pointsMat: pointsMat, velMat: velMat,
  get tickAccum() { return tickAccum; },
  get lerpOK() { return lerpOK; },
  get posPrev() { return posPrev; },
  get posB() { return posB; },
  get pmDens() { return pmDens; },
  get pmPotB() { return pmPotB; },
  pmSolve: pmSolve, pmDeposit: pmDeposit, simTick: simTick, syncPm: syncPm,
  readTarget: readTarget, writeRow: writeRow,
  get dimer() { return DIMER; }, dimerTick: dimerTick, dimerEig: dimerEig, dimerParams: dimerParams,
  dimerDensityShare: dimerDensityShare, dimerDraw: dimerDraw, labReadDensity: labReadDensity,
  get modeB() { return modeB; }, radialProfile: radialProfile, schmidt: schmidt, RAD_N: RAD_N,
  get cons() { return lab.cons; },
  get consRT() { return consRT; },
  get velB() { return velB; },
  consSample: labConsSample, consReduce: labConsReduce, consReset: labConsReset, consCopyUniforms: consCopyUniforms,
  consLedgerLive: labConsLedgerLive, fieldAmp: fieldAmp, simStep: simStep, labConsPredict: labConsPredict,
  PM_HALF_JS: PM_HALF_JS, SG_GAIN: SG_GAIN, EXTENT: EXTENT,
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

# 4. site-root scripts cannot resolve under file:// (the wishing well's feedback.js is served
#    from the site root); the test build drops them so console-error checks stay strict.
out, n_site = re.subn(r'<script src="/nested-resonance-memory-archive/[^"]*"></script>\n?', '', out)
print('site-root scripts dropped from the test build:', n_site)
out = '<!-- halo-test-source-sha256: ' + hashlib.sha256(src.encode()).hexdigest() + ' -->\n' + out
(d / 'rc-test.html').write_text(out)
print('rc-test.html regenerated:', len(out), 'bytes')
