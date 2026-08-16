/**
 * Invariant sweep for EVICTION — throwing ONE source out of the pool.
 *
 * Run: node tests/unit/evict.invariants.mjs
 *
 * It transpiles the REAL `src/lib/evict.ts` (esbuild, types stripped), so the
 * plan measured here is the plan the click handler performs.
 *
 * THE WISH THIS EXISTS FOR (collage well, improve, about_tool=upload):
 *   *"when full mode is active if I click a box or segment there should be
 *   ability to remove that from the group of images displayed or videos."*
 *
 * WHY A SWEEP AND NOT A COUPLE OF EXAMPLES. The plan drives `URL.revokeObjectURL`
 * and a `setImages` filter — a wrong id is somebody's photograph gone, and a
 * revoked url cannot be un-revoked. The failure mode that matters is not "it
 * crashed" but "it removed one more thing than it was asked to", and that shape
 * is invisible to a happy-path test with three assets in it.
 *
 * I1  THE TARGET ALWAYS LEAVES. If the plan is non-empty, the thing pointed at
 *     is in it. Anything else is a control that does not do its job.
 * I2  NO DUPLICATES, and every id returned is really in the pool.
 * I3  NO COLLATERAL. An asset leaves only if it IS the target or shares the
 *     target's non-empty clipId. This is the one that protects the other 200
 *     photographs.
 * I4  NO HALF-REMOVED VIDEO. Every asset sharing that clipId leaves together —
 *     otherwise the next roll puts the clip you just deleted back on screen at a
 *     different second (`fill.assignSources`: a video is ONE source however many
 *     frames came out of it).
 * I5  CLIPS ARE A SUBSET. `clipIds` never names a clip that is not live, and
 *     never names a clip other than the target's.
 * I6  AN UNKNOWN TARGET IS AN EMPTY PLAN, not a throw and not a purge. The cell
 *     under a stale `shuffledIndices` entry is a real input during a re-layout.
 * I7  IDEMPOTENT. Apply the plan, ask again for the same target: nothing left to
 *     do. A second tap on a dying fragment cannot take a second asset with it.
 * I8  count === imageIds.length, always — the number in the notice IS the number
 *     of tiles that left.
 * I9  TOTAL. Missing fields, null entries, duplicate ids, a `null` pool: a canvas
 *     click handler is the last place allowed to take the app down.
 * I10 AN ORPHANED POSTER STILL EVICTS. `removeClip` cuts the live binding and
 *     leaves the stills; those frames still carry the id, and they must still be
 *     removable — with nothing to revoke.
 * I11 AN EMPTY `clipId` IS ABSENT, NOT A GROUP. Grouping on a falsy key would
 *     make every plain photograph a frame of one enormous shared video, and one
 *     tap would delete the pool. This is the sweep's most important assertion.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

const load = async (rel, tag) => {
  const out = join(mkdtempSync(join(tmpdir(), `${tag}-`)), `${tag}.mjs`);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: out,
    bundle: true,
    format: 'esm',
    platform: 'neutral',
    target: 'es2020',
    logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const E = await load('src/lib/evict.ts', 'evict');

let checks = 0;
const ok = (cond, msg) => { checks++; assert.ok(cond, msg); };

const mulberry = (seed) => () => {
  seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

/**
 * A pool shaped like a real one: some plain photographs, some clips that
 * contributed one poster (the default intake) and some that contributed
 * several (the opt-in frame sheet), plus the awkward cases — a clip whose live
 * binding was already cut, and assets carrying an EMPTY clipId.
 */
const makePool = (rnd) => {
  const images = [];
  const clips = [];
  let n = 0;
  const photos = Math.floor(rnd() * 8);
  for (let i = 0; i < photos; i++) {
    images.push({ id: `a${n++}`, originalName: `photo_${i}.jpg` });
  }
  // DECISION 2's trap, planted on purpose in a third of the pools.
  if (rnd() < 0.34) {
    const blanks = 1 + Math.floor(rnd() * 3);
    for (let i = 0; i < blanks; i++) images.push({ id: `a${n++}`, clipId: '', originalName: `blank_${i}.jpg` });
  }
  const clipCount = Math.floor(rnd() * 4);
  for (let c = 0; c < clipCount; c++) {
    const id = `clip-${c}`;
    const live = rnd() < 0.75;              // the rest are orphaned posters (I10)
    if (live) clips.push({ id });
    const frames = 1 + Math.floor(rnd() * 4);
    for (let f = 0; f < frames; f++) {
      images.push({ id: `a${n++}`, clipId: id, sourceName: `clip_${c}.mov`, sourceTime: f });
    }
  }
  // Shuffle so grouping can never be an artefact of adjacency.
  for (let i = images.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [images[i], images[j]] = [images[j], images[i]];
  }
  return { images, clips };
};

let pools = 0;
let targets = 0;
let clipEvictions = 0;
let orphanEvictions = 0;
let blankGroups = 0;

for (let seed = 1; seed <= 400; seed++) {
  const rnd = mulberry(seed * 104729);
  const { images, clips } = makePool(rnd);
  pools++;

  for (const target of images) {
    targets++;
    const plan = E.planEviction(images, clips, target.id);

    // I1
    ok(plan.imageIds.includes(target.id), `the target must leave (seed ${seed}, ${target.id})`);
    // I8
    ok(plan.count === plan.imageIds.length, 'count is the number of tiles leaving');
    // I2
    ok(new Set(plan.imageIds).size === plan.imageIds.length, 'no id twice');
    for (const id of plan.imageIds) ok(images.some((a) => a.id === id), `${id} is really in the pool`);

    const key = typeof target.clipId === 'string' && target.clipId.length > 0 ? target.clipId : '';

    // I3 + I4 — the membership test, both directions.
    for (const a of images) {
      const shares = key !== '' && a.clipId === key;
      const should = a.id === target.id || shares;
      ok(plan.imageIds.includes(a.id) === should,
        `collateral: ${a.id} (clip ${a.clipId ?? '-'}) vs target ${target.id} (clip ${key || '-'})`);
    }

    // I11 — an empty clipId groups nothing. A blank-clipId asset removes ONLY
    // itself even when three others also carry ''.
    if (target.clipId === '') {
      blankGroups++;
      ok(plan.count === 1, `an empty clipId is not a group (took ${plan.count})`);
      ok(plan.isClip === false, 'an empty clipId is not a clip');
    }

    // I5
    if (key === '') ok(plan.clipIds.length === 0, 'a photograph frees no clip');
    else {
      ok(plan.clipIds.every((id) => id === key), 'only the target clip');
      ok(plan.clipIds.every((id) => clips.some((c) => c.id === id)), 'never a clip that is not live');
      if (clips.some((c) => c.id === key)) { ok(plan.clipIds.length === 1, 'the live clip is freed'); clipEvictions++; }
      else { ok(plan.clipIds.length === 0, 'an orphaned poster frees nothing'); orphanEvictions++; }
      // I10 — orphan or not, the poster leaves.
      ok(plan.count >= 1, 'an orphaned poster is still evictable');
    }

    // I7 — apply and re-ask.
    const after = images.filter((a) => !plan.imageIds.includes(a.id));
    const afterClips = clips.filter((c) => !plan.clipIds.includes(c.id));
    const again = E.planEviction(after, afterClips, target.id);
    ok(again.count === 0 && again.imageIds.length === 0 && again.clipIds.length === 0,
      'a second tap on a gone fragment does nothing');

    // The notice never lies about the count.
    const said = E.describeEviction(plan);
    ok(said.length > 0, 'a removal always says something');
    if (plan.isClip && plan.count > 1) ok(said.includes(String(plan.count)), 'a multi-frame removal says how many');
  }

  // I6 — an id that is not in this pool.
  for (const bogus of ['nope', '', 'a999999', 'clip-0']) {
    const plan = E.planEviction(images, clips, bogus);
    if (!images.some((a) => a.id === bogus)) {
      ok(plan.count === 0 && plan.imageIds.length === 0 && plan.clipIds.length === 0,
        `an unknown target "${bogus}" is an empty plan, never a purge`);
      ok(E.describeEviction(plan) === '', 'and it says nothing');
    }
  }
}
ok(pools === 400, 'swept 400 pools');
ok(clipEvictions > 0 && orphanEvictions > 0, 'both the live-clip and orphaned-poster paths were exercised');
ok(blankGroups > 0, 'the empty-clipId trap was actually planted');

// ---------------------------------------------------------------------------
// I9 — total, against inputs no pool should ever hold.
// ---------------------------------------------------------------------------
const NASTY_POOLS = [
  [],
  [null, undefined],
  [{ id: 'x' }, { id: 'x' }],                                  // the same id twice
  [{ id: 'x', clipId: 'c' }, { id: 'x', clipId: 'c' }],        // and inside a clip
  [{ id: 'a', clipId: undefined }, { id: 'b', clipId: null }],
  [{ id: 'a', clipId: 0 }, { id: 'b', clipId: false }],
  [{ id: 'a', clipId: 'c' }],
  [{ }, { id: '' }],
];
for (const pool of NASTY_POOLS) {
  for (const clips of [[], [{ id: 'c' }], [null], undefined, null]) {
    for (const t of ['x', 'a', 'b', '', null, undefined, 'c']) {
      const plan = E.planEviction(pool, clips, t);
      ok(Array.isArray(plan.imageIds) && Array.isArray(plan.clipIds), 'always a plan');
      ok(plan.count === plan.imageIds.length, 'count agrees even here');
      ok(new Set(plan.imageIds).size === plan.imageIds.length, 'still no id twice');
      ok(typeof plan.label === 'string', 'the label is always a string');
    }
  }
}
// A null pool is a crash waiting in a click handler.
for (const bad of [null, undefined]) {
  const plan = E.planEviction(bad, [], 'a');
  ok(plan.count === 0, 'a missing pool is an empty plan');
}
// The two ids in one pool that share a NAME are still two different sources.
const sameName = [{ id: 'a', originalName: 'IMG_1.jpg' }, { id: 'b', originalName: 'IMG_1.jpg' }];
const byName = E.planEviction(sameName, [], 'a');
ok(byName.count === 1 && byName.imageIds[0] === 'a', 'identity is the id, never the filename');

// Naming: a clip is named by its FILE, a photograph by its own name, and a pool
// that recorded neither still produces a sentence rather than "Removed ."
ok(E.describeEviction(E.planEviction([{ id: 'a', clipId: 'c', sourceName: 'beach.mov' }], [{ id: 'c' }], 'a'))
  === 'Removed beach.mov.', 'a clip is named by its file');
ok(E.describeEviction(E.planEviction([{ id: 'a', originalName: 'dog.jpg' }], [], 'a'))
  === 'Removed dog.jpg.', 'a photograph is named by its file');
ok(E.describeEviction(E.planEviction([{ id: 'a' }], [], 'a'))
  === 'Removed that picture.', 'an unnamed asset still gets a sentence');
ok(E.describeEviction(E.planEviction(
  [{ id: 'a', clipId: 'c' }, { id: 'b', clipId: 'c' }, { id: 'd', clipId: 'c' }], [{ id: 'c' }], 'a'))
  === 'Removed that clip — 3 frames.', 'an unnamed clip says how many frames went');

console.log(`evict invariants: ${checks} assertions over ${pools} pools and ${targets} targets — all green`);
