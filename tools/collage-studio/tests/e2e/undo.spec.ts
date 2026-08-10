/**
 * UNDO, AT THE ARTIFACT — proved on PIXELS.
 *
 * The stack itself is swept against a reference model in
 * tests/unit/compositionHistory.invariants.mjs (569k assertions, 160k random
 * operations). That proves the ARITHMETIC of past/present/future and cannot see
 * a single thing about whether the app is wired to it.
 *
 * SCAR, earned twice in this repo and once more in C87b: "a unit sweep grades
 * arithmetic and cannot see WIRING", and "a test suite inherits its author's
 * hypothesis". The stack could be perfect and undo still not restore the
 * picture — a setter missing from `applyCompositionCode`, the locks not put
 * back, the recipe name left on the old roll, the snapshot taken AFTER the
 * fifteen setState calls instead of before. Reading the controls back would
 * agree with the wiring by construction.
 *
 * So the assertion here is a fingerprint of the CANVAS: undo must put back the
 * same pixels, and redo must put back the pixels it left. Nothing else is
 * evidence.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.undo.config.ts
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.undo.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** A solid-colour PNG built in-process — no fixture files, fully deterministic. */
function makePng(r: number, g: number, b: number, size = 96): Buffer {
  const w = size, h = size;
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0);
    const t = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4); crc.writeUInt32BE(zlib.crc32(Buffer.concat([t, data])) >>> 0, 0);
    return Buffer.concat([len, t, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2; // 8-bit truecolour RGB
  const row = Buffer.alloc(1 + w * 3);
  for (let x = 0; x < w; x++) { row[1 + x * 3] = r; row[1 + x * 3 + 1] = g; row[1 + x * 3 + 2] = b; }
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  const idat = zlib.deflateSync(raw);
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

/** Six distinct, distinctly-coloured sources. Distinct so the DEAL is visible. */
const TILES = [
  [230, 40, 40], [40, 200, 90], [50, 90, 240],
  [240, 200, 40], [200, 60, 220], [30, 220, 220],
].map(([r, g, b], i) => ({
  name: `tile-${i}.png`, mimeType: 'image/png', buffer: makePng(r, g, b),
}));

type Shot = { w: number; h: number; hash: string; sig: string; mean: number; live: boolean };

/**
 * What is actually on the preview — TWO witnesses, because one of them is not
 * always admissible.
 *
 * MEASURED, NOT ASSUMED (this file's first draft got it wrong and the flake
 * looked exactly like a product bug): a composition carrying a MOVE mounts the
 * live Stage canvas instead of the static JPEG, and a drifting canvas renders
 * DIFFERENT PIXELS EVERY FRAME. Sampling it twice 700ms apart with no
 * interaction at all gives two different FNV hashes at identical luma — the
 * precise signature of the failure ("same size, same luma, different hash")
 * that this spec first reported against the app. An exact pixel hash is not a
 * witness for a picture that is supposed to be moving.
 *
 *   `sig` — 256 blocks (16x16 over a 128px downsample), each reduced to its
 *   dominant channel or a luma bucket. Swept before adoption on ten rolls:
 *   ZERO drift blocks across frames INCLUDING on live canvases, and ten
 *   distinct signatures from ten rolls. Stable under the drift, and still able
 *   to fail — a witness that cannot fail is not a witness.
 *
 *   `hash` — the exact FNV-1a, asserted ONLY when both shots came from the
 *   static JPEG, where it is proven stable and is strictly the stronger claim.
 */
async function fingerprint(page: Page): Promise<Shot> {
  return page.evaluate(() => {
    const liveEl = document.querySelector('canvas') as HTMLCanvasElement | null;
    const el = liveEl ?? (document.querySelector('img[src^="blob:"]') as HTMLImageElement | null);
    const blank = { w: 0, h: 0, hash: 'no-preview', sig: '', mean: -1, live: false };
    if (!el) return blank;
    const sw = el instanceof HTMLCanvasElement ? el.width : el.naturalWidth;
    const sh = el instanceof HTMLCanvasElement ? el.height : el.naturalHeight;
    if (!sw || !sh) return { ...blank, hash: 'empty-preview' };
    const S = 128;
    const c = document.createElement('canvas');
    c.width = S; c.height = S;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    if (!ctx) return { ...blank, w: sw, h: sh, hash: 'no-2d' };
    ctx.drawImage(el as CanvasImageSource, 0, 0, S, S);
    const px = ctx.getImageData(0, 0, S, S).data;

    let hash = 0x811c9dc5, sum = 0;
    for (let i = 0; i < px.length; i++) {
      hash ^= px[i];
      hash = Math.imul(hash, 0x01000193) >>> 0;
      if (i % 4 !== 3) sum += px[i];
    }

    const N = 16, B = S / N;
    let sig = '';
    for (let by = 0; by < N; by++) {
      for (let bx = 0; bx < N; bx++) {
        let R = 0, G = 0, Bl = 0, n = 0;
        for (let y = by * B; y < (by + 1) * B; y++) {
          for (let x = bx * B; x < (bx + 1) * B; x++) {
            const i = (y * S + x) * 4;
            R += px[i]; G += px[i + 1]; Bl += px[i + 2]; n++;
          }
        }
        R /= n; G /= n; Bl /= n;
        const mx = Math.max(R, G, Bl), mn = Math.min(R, G, Bl);
        sig += (mx - mn) > 36
          ? (mx === R ? 'R' : mx === G ? 'G' : 'B')
          : '0123'[Math.min(3, Math.floor(((R + G + Bl) / 3) / 64))];
      }
    }
    return {
      w: sw, h: sh, sig, live: !!liveEl,
      hash: hash.toString(16).padStart(8, '0'),
      mean: sum / ((px.length / 4) * 3),
    };
  });
}

/**
 * Is an EXACT pixel hash admissible in this browser?
 *
 * MEASURED PER ENGINE, over 20 readbacks per preview, three compositions each:
 *
 *              still preview      live (drifting) canvas
 *   Chromium   1 distinct hash    1 distinct hash
 *   WebKit     1 distinct hash    6 distinct hashes
 *
 *   …and separately, across two RE-RENDERS of the same composition, WebKit does
 *   not reproduce the JPEG byte-for-byte: identical luma to two decimals,
 *   identical block signature, different FNV hash. That is the red this spec
 *   reported on Mobile Safari and nowhere else — the app was not moving, the
 *   ruler was.
 *
 * So the exact hash is asserted only on the engine where it was proven
 * reproducible ACROSS renders, and `sig` carries the claim everywhere — which
 * is why `sig` was validated for discrimination (ten distinct signatures from
 * ten rolls) before it was adopted. The composition CODE is asserted exactly on
 * every engine, and that is a hard, byte-level witness of every parameter of
 * the picture that no browser is free to perturb.
 */
let exactAdmissible = true;

const same = (a: Shot, b: Shot) =>
  a.w === b.w && a.h === b.h && a.sig === b.sig
  // The exact hash is the stronger claim, so it is asserted wherever it is
  // admissible — neither picture moving, and a browser that reads back honestly.
  && (a.live || b.live || !exactAdmissible || a.hash === b.hash);

const show = (f: Shot) =>
  `${f.w}x${f.h} ${f.live ? 'live' : 'still'} #${f.hash} luma=${f.mean.toFixed(2)} sig=${f.sig.slice(0, 24)}…`;

/**
 * WAIT FOR THE PICTURE TO STOP MOVING, rather than waiting a number.
 *
 * The inherited helper in the sibling specs is `waitForTimeout(1400)`, and 1400
 * is a hope: the layout runs on a 50ms debounce and then asynchronously, and a
 * roll can land a 146-fragment Truchet that is still painting when the clock
 * runs out — on a loaded machine the fingerprint then captures a half-settled
 * picture and the comparison fails for a reason that has nothing to do with
 * undo. That is the intermittent red this file showed before this helper
 * existed.
 *
 * So: sample until two consecutive samples 250ms apart agree on the block
 * signature (which IS stable on a drifting canvas — see `fingerprint`), then
 * return that shot. Converges in ~600ms for an ordinary composition and takes
 * as long as it needs for a heavy one.
 */
async function settled(page: Page, changedFrom?: Shot, timeoutMs = 20_000): Promise<Shot> {
  const started = Date.now();
  await page.waitForTimeout(200);
  let prev = await fingerprint(page);
  let stable = 0;
  while (Date.now() - started < timeoutMs) {
    await page.waitForTimeout(200);
    const next = await fingerprint(page);
    const agrees = !!next.sig && next.sig === prev.sig && next.w === prev.w && next.h === prev.h;
    prev = next;
    // NOT YET MOVED is not the same as SETTLED, and conflating them is how this
    // spec produced its most convincing false red: click undo, sample twice
    // before the repaint lands, get two identical readings OF THE PICTURE BEING
    // REPLACED, and report "undo did not restore" against a shot taken from the
    // composition undo was leaving. It only ever fired on WebKit, where the
    // repaint is slower — i.e. the bug was in the wait, and the engine that
    // exposed it was the phone.
    if (changedFrom && next.sig === changedFrom.sig && next.w === changedFrom.w && next.h === changedFrom.h) {
      stable = 0;
      continue;
    }
    if (agrees && ++stable >= 2) return next;
    if (!agrees) stable = 0;
  }
  return prev;
}


async function boot(page: Page, browserName?: string) {
  exactAdmissible = browserName === 'chromium';
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(TILES);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  const first = await settled(page);
  // Calibrate the ruler before using it: two readbacks of the same untouched
  // preview. Any disagreement is the browser's, not the app's.
  const again = await fingerprint(page);
  // The ruler is checked before it is used, every run: a signature that moves on
  // an untouched preview would make every assertion below meaningless.
  expect(first.sig, 'the block signature is unstable on an untouched preview — the witness is broken')
    .toBe(again.sig);
}

const codeOf = (page: Page) => page.getByTestId('composition-code').innerText();

/** In the dock the pair carries a label; in full bleed it is icon-only. */
const undoBtn = (page: Page, rail = false) => page.getByTestId(rail ? 'undo' : 'undo-dock');
const redoBtn = (page: Page, rail = false) => page.getByTestId(rail ? 'redo' : 'redo-dock');

async function rollDock(page: Page, from?: Shot): Promise<Shot> {
  await page.getByRole('button', { name: /Roll the dice/i }).first().click();
  return settled(page, from);
}

/**
 * Roll until the picture actually MOVES.
 *
 * Not a filter on the state space (see the scar in roll-code.spec.ts — a helper
 * that excludes cases is where a bug hides). It excludes exactly one thing: a
 * roll that landed on the composition already on screen, which would make
 * "undo restored it" unfalsifiable because there is nothing to restore. The
 * composition code is checked too, so a roll that changed a parameter the
 * canvas cannot show still counts as movement.
 */
async function rollToSomethingNew(page: Page, from: Shot): Promise<Shot> {
  for (let i = 0; i < 8; i++) {
    const before = await codeOf(page);
    const shot = await rollDock(page, from);
    if (!same(shot, from) && (await codeOf(page)) !== before) return shot;
  }
  throw new Error('eight rolls in a row produced the same picture — the dice is not rolling');
}

test.describe('undo — the roll you liked, brought back', () => {
  test.setTimeout(240_000);

  test('U1 — undo puts the previous composition back, pixel for pixel; redo goes forward', async ({ page, browserName }) => {
    await boot(page, browserName);
    const shot0 = await settled(page);
    const shotA = await rollToSomethingNew(page, shot0);
    const codeA = await codeOf(page);
    const shotB = await rollToSomethingNew(page, shotA);
    const codeB = await codeOf(page);

    await undoBtn(page).click();
    const back = await settled(page, shotB);
    expect(same(back, shotA), `undo did not restore the picture.\n  want ${show(shotA)}\n  got  ${show(back)}`).toBe(true);
    expect(await codeOf(page), 'undo restored the pixels but not the code').toBe(codeA);

    await redoBtn(page).click();
    const fwd = await settled(page, back);
    expect(same(fwd, shotB), `redo did not restore the picture it left.\n  want ${show(shotB)}\n  got  ${show(fwd)}`).toBe(true);
    expect(await codeOf(page)).toBe(codeB);
  });

  test('U2 — three rolls walk back through all three, in order', async ({ page, browserName }) => {
    await boot(page, browserName);
    // The depth that matters: the reported use is rolling repeatedly to compare,
    // so one step back is not the feature — the trail is.
    const shots: Shot[] = [await settled(page)];
    for (let i = 0; i < 3; i++) shots.push(await rollToSomethingNew(page, shots[shots.length - 1]));

    for (let i = shots.length - 2; i >= 0; i--) {
      await undoBtn(page).click();
      const got = await settled(page, shots[i + 1]);
      expect(same(got, shots[i]), `undo #${shots.length - 1 - i} landed wrong.\n  want ${show(shots[i])}\n  got  ${show(got)}`).toBe(true);
    }
    await expect(undoBtn(page), 'the stack emptied but undo is still live').toBeDisabled();
  });

  test('U3 — the buttons tell the truth, including the branch rule', async ({ page, browserName }) => {
    await boot(page, browserName);
    await expect(undoBtn(page), 'nothing has happened yet and undo is live').toBeDisabled();
    await expect(redoBtn(page), 'nothing has been undone and redo is live').toBeDisabled();

    const s0 = await settled(page);
    const s1 = await rollToSomethingNew(page, s0);
    await expect(undoBtn(page)).toBeEnabled();
    await expect(redoBtn(page), 'a roll made redo live').toBeDisabled();

    await undoBtn(page).click();
    await settled(page);
    await expect(redoBtn(page), 'an undo left nothing to redo').toBeEnabled();

    // THE BRANCH RULE, at the artifact: a NEW roll after undoing abandons the
    // one you left. A redo that survived here would jump to a picture from a
    // branch the person cannot see.
    await rollToSomethingNew(page, s1);
    await expect(redoBtn(page), 'a new roll left the abandoned branch redoable').toBeDisabled();
  });

  test('U4 — the full-bleed rail, which is where this was wished from', async ({ page, browserName }) => {
    await boot(page, browserName);
    await page.getByRole('button', { name: /Maximize the shot/i }).click();
    await expect(undoBtn(page, true)).toBeVisible();

    // Roll from the RAIL, not the dock — full bleed hides the dock entirely, and
    // this is the exact loop that used to destroy the composition with no way back.
    const before = await settled(page);
    let after = before;
    for (let i = 0; i < 8 && same(after, before); i++) {
      await page.getByTestId('rail-dice').click();
      after = await settled(page);
    }
    expect(same(after, before), 'rolling from the rail did not change the picture').toBe(false);

    await expect(undoBtn(page, true)).toBeEnabled();
    await undoBtn(page, true).click();
    const back = await settled(page, after);
    expect(same(back, before), `rail undo did not restore.\n  want ${show(before)}\n  got  ${show(back)}`).toBe(true);

    // MOBILE-WATERTIGHT, asserted where the buttons were added. Seven 44px
    // targets in one pill is the tightest row in the app.
    const overflow = await page.evaluate(() => ({
      doc: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      body: document.body.scrollWidth - document.body.clientWidth,
    }));
    expect(overflow.doc, `the page scrolls sideways by ${overflow.doc}px in full bleed`).toBeLessThanOrEqual(0);
    expect(overflow.body, `the body scrolls sideways by ${overflow.body}px in full bleed`).toBeLessThanOrEqual(0);

    for (const id of ['rail-dice', 'undo', 'redo']) {
      const box = await page.getByTestId(id).boundingBox();
      expect(box, `${id} has no box in full bleed`).not.toBeNull();
      expect(box!.width, `${id} is ${box!.width}px wide — under the 44px tap target`).toBeGreaterThanOrEqual(43.5);
      expect(box!.height, `${id} is ${box!.height}px tall — under the 44px tap target`).toBeGreaterThanOrEqual(43.5);
      // Inside the viewport, not merely rendered.
      const vw = page.viewportSize()!.width;
      expect(box!.x, `${id} starts off the left edge`).toBeGreaterThanOrEqual(-0.5);
      expect(box!.x + box!.width, `${id} runs ${(box!.x + box!.width - vw).toFixed(1)}px past the right edge`).toBeLessThanOrEqual(vw + 0.5);
    }
  });

  test('U4b — the rail holds at 320 / 360 / 390 / 430, with SEVEN 44px targets in it', async ({ page, browserName }) => {
    // THE MOBILE LAW, asserted at the width where it actually bites. Adding undo
    // and redo took the full-bleed rail from five children to seven, and seven
    // 44px targets plus a divider is 295 of the 304 usable pixels at 320 — which
    // is why the gap tightens below 360 instead of the buttons. Nine pixels of
    // headroom is not something to leave to inspection.
    await boot(page, browserName);
    await page.getByRole('button', { name: /Maximize the shot/i }).click();
    await expect(page.getByTestId('undo')).toBeVisible();

    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 760 });
      await page.waitForTimeout(350);
      const over = await page.evaluate(() => ({
        doc: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        body: document.body.scrollWidth - document.body.clientWidth,
      }));
      expect(over.doc, `${width}px: the page scrolls sideways by ${over.doc}px`).toBeLessThanOrEqual(0);
      expect(over.body, `${width}px: the body scrolls sideways by ${over.body}px`).toBeLessThanOrEqual(0);

      let prevRight = -Infinity;
      for (const id of ['rail-dice', 'undo', 'redo']) {
        const box = await page.getByTestId(id).boundingBox();
        expect(box, `${width}px: ${id} is not rendered`).not.toBeNull();
        expect(box!.width, `${width}px: ${id} is ${box!.width.toFixed(1)}px wide`).toBeGreaterThanOrEqual(43.5);
        expect(box!.height, `${width}px: ${id} is ${box!.height.toFixed(1)}px tall`).toBeGreaterThanOrEqual(43.5);
        expect(box!.x, `${width}px: ${id} starts at ${box!.x.toFixed(1)} — off the left edge`).toBeGreaterThanOrEqual(-0.5);
        expect(box!.x + box!.width,
          `${width}px: ${id} ends at ${(box!.x + box!.width).toFixed(1)} — ${(box!.x + box!.width - width).toFixed(1)}px past the right edge`)
          .toBeLessThanOrEqual(width + 0.5);
        // Laid out in a row, never wrapped or stacked on top of each other.
        expect(box!.x, `${width}px: ${id} overlaps the control before it`).toBeGreaterThanOrEqual(prevRight - 0.5);
        prevRight = box!.x + box!.width;
      }

      // Zoomed out is the operator's own wording, and it is a DIFFERENT test: it
      // widens the layout viewport without widening the window.
      await page.evaluate(() => {
        const m = document.querySelector('meta[name="viewport"]');
        m?.setAttribute('content', 'width=980, initial-scale=0.33');
      });
      await page.waitForTimeout(300);
      const zoomed = await page.evaluate(() =>
        document.documentElement.scrollWidth - document.documentElement.clientWidth);
      expect(zoomed, `${width}px zoomed out: the page scrolls sideways by ${zoomed}px`).toBeLessThanOrEqual(0);
      await page.evaluate(() => {
        const m = document.querySelector('meta[name="viewport"]');
        m?.setAttribute('content', 'width=device-width, initial-scale=1, viewport-fit=cover');
      });
      await page.waitForTimeout(200);
    }
  });

  test('U5 — the keyboard, and the caption box that must keep its own undo', async ({ page, browserName }) => {
    await boot(page, browserName);
    const s0 = await settled(page);
    const s1 = await rollToSomethingNew(page, s0);
    const s2 = await rollToSomethingNew(page, s1);

    const mod = process.platform === 'darwin' ? 'Meta' : 'Control';
    await page.keyboard.press(`${mod}+KeyZ`);
    expect(same(await settled(page, s2), s1), 'Cmd-Z did not undo').toBe(true);

    await page.keyboard.press(`Shift+${mod}+KeyZ`);
    expect(same(await settled(page, s1), s2), 'Shift-Cmd-Z did not redo').toBe(true);

    // A text field owns Cmd-Z more strongly than the app does: undo inside the
    // caption must undo the TYPING, and must not move the collage behind it.
    const caption = page.getByPlaceholder(/say what it is|title|caption/i).first();
    if (await caption.count()) {
      await caption.click();
      await caption.type('hello');
      // THE WITNESS HERE IS THE CODE, NOT THE PIXELS, and getting that wrong
      // produced a red that looked exactly like a broken guard: the caption is
      // DRAWN ON THE COLLAGE, so the browser's own field-undo removing "hello"
      // changes the picture — which is the guard WORKING. The caption is
      // deliberately not in the composition code (a code is a recipe for
      // somebody else's photographs; your words are not), so the code is
      // precisely the thing that must not move.
      const guardedCode = await codeOf(page);
      await page.keyboard.press(`${mod}+KeyZ`);
      await page.waitForTimeout(900);
      expect(await codeOf(page),
        'Cmd-Z inside the caption box stepped the COLLAGE back').toBe(guardedCode);
    }
  });

  test('U6 — a shuffle is a step too, and undo brings the deal back', async ({ page, browserName }) => {
    await boot(page, browserName);
    // Not just the dice: shuffle and remix replace the composition the same way,
    // and a person comparing deals hits exactly the same wall.
    const before = await settled(page);
    let after = before;
    for (let i = 0; i < 8 && same(after, before); i++) {
      await page.getByRole('button', { name: /Shuffle\s*images/i }).first().click();
      after = await settled(page);
    }
    expect(same(after, before), 'eight shuffles did not change the deal').toBe(false);

    await undoBtn(page).click();
    const back6 = await settled(page, after);
    expect(same(back6, before),
      `undo did not bring the deal back.\n  want ${show(before)}\n  got  ${show(back6)}`).toBe(true);
  });
});
