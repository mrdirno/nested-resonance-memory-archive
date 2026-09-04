/* Load the page's two logic <script> blocks into a bare V8 context, so the
   composer can be run and measured without a browser. The third block needs a
   DOM and is deliberately not evaluated.

   Author: Aldrin Payopay */

import { readFileSync } from 'node:fs';
import vm from 'node:vm';

export function loadKernel (file) {
  const html = readFileSync(file, 'utf8');
  const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  if (blocks.length < 2) throw new Error('expected at least two <script> blocks, found ' + blocks.length);
  const sandbox = {
    console, Math, Date, JSON, Object, Array, String, Number, Boolean, Error, RegExp,
    Float32Array, Float64Array, Uint8Array, Int8Array, Int16Array, Uint16Array, Int32Array,
    isNaN, isFinite, parseInt, parseFloat, Symbol, Map, Set, Promise,
  };
  sandbox.globalThis = sandbox; sandbox.window = sandbox; sandbox.self = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(blocks[0], sandbox, { filename: 'improvisator-kernel.js' });
  vm.runInContext(blocks[1], sandbox, { filename: 'improvisator-soul.js' });
  if (!sandbox.IMPROV) throw new Error('the kernel did not export IMPROV');
  return sandbox.IMPROV;
}

/* One performance: N bars of a preset from a seed. */
export function run (K, { seed, preset, bars, settings }) {
  const s = Object.assign({}, K.PRESETS[preset || 'reference'], settings || {});
  const c = new K.Composer(seed, s);
  const out = [];
  for (let i = 0; i < bars; i++) out.push(c.nextBar());
  return { bars: out, composer: c, settings: s };
}

/* A bar reduced to the numbers that decide whether two renderings are the same
   performance. Rounded to the microsecond so float noise is not a difference. */
export function fingerprintBar (b) {
  const r = x => Math.round(x * 1e6) / 1e6;
  return [
    b.chord.name, b.tonic, b.mode, r(b.bpm), r(b.lengthBeats), b.meter,
    b.events.map(e => [e.role, e.pitch, r(e.beat), r(e.duration), r(e.velocity),
                       r(e.micro || 0), e.articulation || '', e.hand || ''].join(':')).join(','),
    b.pedal ? [b.pedal.id, r(b.pedal.depth), b.pedal.lift ? 1 : 0, b.pedal.hardClear ? 1 : 0,
               r(b.pedal.liftLead), r(b.pedal.repedalDelay), r(b.pedal.dampTau),
               b.pedal.flutterAt == null ? '-' : r(b.pedal.flutterAt),
               b.pedal.endLiftAt == null ? '-' : r(b.pedal.endLiftAt)].join(':') : '-',
  ].join('|');
}
export const fingerprint = bars => bars.map(fingerprintBar).join('\n');

/* A note a semitone above a chord tone is a minor ninth against it, which is
   the one interval a pianist will not voice — except the b9 and #9 over the
   root of a dominant, where it is the whole point. */
export function tensionOK (pcs, x, dominantRoot) {
  const xp = ((x % 12) + 12) % 12;
  for (const t0 of pcs) {
    const t = ((t0 % 12) + 12) % 12;
    if (((xp - t) % 12 + 12) % 12 === 1) {
      if (dominantRoot !== null && t === dominantRoot &&
          (xp === (t + 1) % 12 || xp === (t + 3) % 12)) continue;
      return false;
    }
  }
  return true;
}
export const isDominantName = n => /(^|[^a-z])(7|9|11|13)\b/.test(n) && !/maj|m7|m9|m11|m13|ø|dim|°/.test(n);
