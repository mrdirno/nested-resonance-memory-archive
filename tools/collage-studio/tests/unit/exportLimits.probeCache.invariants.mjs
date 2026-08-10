/**
 * INVARIANT SWEEP for the GPU-class probe cache in src/lib/exportLimits.ts.
 *
 *   node tests/unit/exportLimits.probeCache.invariants.mjs
 *
 * Transpiles and imports the REAL module. No re-implementation: a sweep against
 * a copy grades the copy.
 *
 * WHAT WENT WRONG. `gpuMaxTextureSize()` wrote the result of
 * `getContext('webgl')` straight into a module cache and returned it forever
 * after. That call fails TRANSIENTLY for reasons that say nothing about the
 * device — Chromium evicts the oldest WebGL context past its per-page cap, a
 * GPU-process crash blanks every one of them until it restarts, and
 * `createSurface` itself can fail under allocation pressure. A blip therefore
 * became this realm's permanent verdict.
 *
 * AND THE VERDICT WAS NOT EVEN CONFINED TO THE PAGE. `probeBudgetAreaPx` only
 * consults the GPU on the branch where `navigator.deviceMemory` is absent —
 * Safari, iOS and Firefox, the engines with the tightest real ceilings and the
 * most aggressive context eviction. A cached 0 falls through every rung to
 * SAFE_FLOOR_AREA*4 = 16.7 MP, against 268 MP for a real 16384 answer: a 16x
 * cut. That number is the search ceiling `probeMaxArea` measures up to, so the
 * measurement it returns is a fact about the guess rather than about the
 * device — and it was then written to sessionStorage as `source: 'probe'`,
 * indistinguishable from a genuine one, where `readCache` accepts it on nothing
 * more than clearing the floor. One blank probe in the moment the export sheet
 * first opened deleted the top of the size ladder for the whole browser
 * session and SURVIVED THE RELOAD that would have cured it.
 *
 * WHY NODE IS THE RIGHT HARNESS FOR THIS ONE. There is no WebGL here and no
 * `document`, so `createSurface` returns null and the probe is blank on every
 * single attempt — the failure mode under test, permanently and for free. What
 * a browser cannot easily give us is exactly what node gives us by default.
 *
 * THE TWO HALVES, AND EACH ALONE IS A DIFFERENT BUG
 *   E1  a blank is RE-PROBED rather than cached — without it, a blip is
 *       permanent and only a reload clears it (and via sessionStorage, not even
 *       that).
 *   E2  a blank SETTLES after a bounded number of tries — without it, a realm
 *       that genuinely has no WebGL pays a context probe every time anyone asks,
 *       forever.
 */
import esbuild from 'esbuild';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

const src = readFileSync(join(root, 'src/lib/exportLimits.ts'), 'utf8');
const { code } = await esbuild.transform(src, { loader: 'ts', format: 'esm' });
const dir = mkdtempSync(join(tmpdir(), 'exportlimits-'));

/**
 * A FRESH MODULE INSTANCE PER SCENARIO. The thing under test is module-level
 * mutable state, so two scenarios sharing one import would grade whichever ran
 * first. ESM caches by URL, so each scenario gets its own file.
 */
let instances = 0;
const freshModule = async () => {
  const p = join(dir, `exportLimits-${instances++}.mjs`);
  writeFileSync(p, code);
  return import(pathToFileURL(p).href);
};

let checks = 0, fails = 0;
const ok = () => { checks++; };
const fail = (m) => { fails++; if (fails <= 40) console.error('  ✗', m); };

const setNavigator = (value) => {
  Object.defineProperty(globalThis, 'navigator', { value, configurable: true, writable: true });
};
const originalNavigator = Object.getOwnPropertyDescriptor(globalThis, 'navigator');
const restoreNavigator = () => {
  if (originalNavigator) Object.defineProperty(globalThis, 'navigator', originalNavigator);
  else delete globalThis.navigator;
};

// =============================================================================
// E1/E2  A BLANK PROBE IS RETRIED, THEN SETTLED — the whole policy, counted.
// =============================================================================
{
  setNavigator({ userAgent: 'node-sweep' }); // no deviceMemory => the GPU branch
  const m = await freshModule();
  const { probeBudgetAreaPx, lastProbeBudgetWasBlind, BLANK_GL_PROBE_RETRIES } = m;

  ok(); if (!Number.isInteger(BLANK_GL_PROBE_RETRIES) || BLANK_GL_PROBE_RETRIES < 1) {
    fail(`E0 BLANK_GL_PROBE_RETRIES is ${BLANK_GL_PROBE_RETRIES}`);
  }

  const blindByCall = [];
  const budgets = [];
  for (let i = 0; i < BLANK_GL_PROBE_RETRIES + 6; i++) {
    budgets.push(probeBudgetAreaPx());
    blindByCall.push(lastProbeBudgetWasBlind());
  }

  // E1 While the class is UNKNOWN the answer is flagged as a guess. That flag
  // is what keeps a measurement taken under it out of sessionStorage.
  for (let i = 0; i < BLANK_GL_PROBE_RETRIES; i++) {
    ok(); if (blindByCall[i] !== true) fail(`E1 call ${i + 1} of ${BLANK_GL_PROBE_RETRIES} was not flagged blind`);
  }
  // E2 ...and it settles. "No WebGL here" becomes a fact about the realm, the
  // probing stops, and caching resumes exactly as it did before.
  for (let i = BLANK_GL_PROBE_RETRIES; i < blindByCall.length; i++) {
    ok(); if (blindByCall[i] !== false) fail(`E2 call ${i + 1} still flagged blind — the settle never happens`);
  }
  // E3 The BUDGET itself never wavers: the retry changes what we believe about
  // the answer, never what we hand to a caller sizing an allocation.
  ok(); if (new Set(budgets).size !== 1) fail(`E3 the budget moved across calls: ${[...new Set(budgets)].join(', ')}`);
  ok(); if (!(budgets[0] > 0)) fail(`E3b budget ${budgets[0]} is not usable`);
  console.log(`  blank realm: flagged blind for ${BLANK_GL_PROBE_RETRIES} call(s), then settled; `
    + `budget steady at ${(budgets[0] / 1e6).toFixed(1)} MP throughout`);
}

// =============================================================================
// E4  A DEVICE THAT ANSWERS IS NEVER BLIND. `deviceMemory` short-circuits the
//     GPU branch entirely, so Chromium must never take the provisional path —
//     if it did, this fix would stop the export ladder caching on the one
//     engine that was never affected.
// =============================================================================
{
  setNavigator({ userAgent: 'node-sweep', deviceMemory: 8 });
  const { probeBudgetAreaPx, lastProbeBudgetWasBlind } = await freshModule();
  for (let i = 0; i < 5; i++) {
    const b = probeBudgetAreaPx();
    ok(); if (lastProbeBudgetWasBlind()) fail('E4 a device reporting deviceMemory was flagged blind');
    ok(); if (!(b > 0)) fail(`E4b budget ${b}`);
  }
  // And it must be a REAL budget, not the blank realm's floor rung — otherwise
  // E4 would pass on a value that had quietly collapsed anyway.
  const withMem = probeBudgetAreaPx();
  setNavigator({ userAgent: 'node-sweep' });
  const { probeBudgetAreaPx: blankBudget } = await freshModule();
  const withoutMem = blankBudget();
  ok(); if (!(withMem > withoutMem)) {
    fail(`E4c deviceMemory bought nothing: ${withMem} vs blank ${withoutMem}`);
  }
  console.log(`  the cut a cached blip caused: ${(withMem / 1e6).toFixed(1)} MP -> `
    + `${(withoutMem / 1e6).toFixed(1)} MP (${(withMem / withoutMem).toFixed(0)}x), `
    + `and it was persisted to sessionStorage as a real measurement`);
}

// =============================================================================
// E5  THE PROVISIONAL MEASUREMENT IS NOT PERSISTED. The flag above only matters
//     because `probeMaxCanvas` acts on it, so drive the real thing: with a
//     sessionStorage that RECORDS WRITES, a probe taken while the class is
//     unknown must leave it untouched, and must not memoise either — the next
//     open has to be free to find the truth.
// =============================================================================
{
  setNavigator({ userAgent: 'node-sweep' });
  const writes = [];
  Object.defineProperty(globalThis, 'sessionStorage', {
    configurable: true, writable: true,
    value: {
      getItem: () => null,
      setItem: (k, v) => writes.push([k, v]),
      removeItem: () => {},
    },
  });

  const { probeMaxCanvas, lastProbeBudgetWasBlind } = await freshModule();
  const first = await probeMaxCanvas();
  ok(); if (!first || !(first.maxAreaPx > 0)) fail(`E5 probeMaxCanvas returned ${JSON.stringify(first)}`);
  // It still ANSWERS — provisional is not "refuse to export".
  ok(); if (!(first.maxDimPx > 0)) fail('E5b provisional run produced no usable dimension');

  if (lastProbeBudgetWasBlind()) {
    ok(); if (writes.length !== 0) fail(`E5c a provisional measurement was persisted: ${JSON.stringify(writes)}`);
    // Not memoised either, or the session is stuck with it regardless of storage.
    const second = await probeMaxCanvas();
    ok(); if (second === first) fail('E5d the provisional result was memoised — the next open cannot re-probe');
  } else {
    // The class settled during the first probe; then caching is CORRECT and the
    // opposite assertion applies. Derived, never assumed, so this stays a
    // grader under either ordering rather than a stale promise.
    ok(); if (writes.length === 0) fail('E5e a settled measurement was NOT persisted');
  }
  console.log(`  probeMaxCanvas under a blank GPU probe: blind=${lastProbeBudgetWasBlind()}, `
    + `sessionStorage writes=${writes.length}`);
  delete globalThis.sessionStorage;
}

restoreNavigator();
console.log(`\nexportLimits.probeCache.invariants: ${checks} checks, ${fails} failure(s)`);
process.exit(fails ? 1 : 0);
