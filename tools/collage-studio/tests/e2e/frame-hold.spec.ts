/**
 * THE FRAME HOLD, AT THE ARTIFACT.
 *
 * Wished for (wishing well, collage): *"Tide pool is sick I like them. Maybe
 * good idea to lock aspect ratio too as a toggle."*
 *
 * WHAT WAS BROKEN
 *   Chasing a recipe means pressing the dice again and again, and every press
 *   re-dealt the shape of frame too: `handleDice` applied `roll.aspect`
 *   unconditionally, and `rollDice` draws from a roster of seven — so the
 *   canvas changed shape on ~6 of 7 presses. Measured on the pre-fix build:
 *   12 presses, 12 frame-shape changes, 6 distinct aspects. The engine had
 *   carried the answer since the locks shipped (`RollLock`, "the slot-machine
 *   hold" in diceRoll.ts) but no caller ever passed it — the machinery was
 *   dark, and no surface offered a toggle.
 *
 * THE PROMISE, in two halves that fail in opposite directions:
 *
 *   HELD, THE FRAME MUST NOT MOVE — else the toggle is a lie.
 *   HELD, THE DICE MUST STILL ROLL — else the hold killed the button.
 *
 * And the hold pins WHAT IS ON SCREEN, not the last roll: the Canvas chips can
 * re-set the frame after a roll, and a lock that snapped back to the rolled
 * aspect on its next press would be a broken lock (that is why the fix reads
 * the `aspect` state instead of `rollDice({ locks, previous })` — `previous`
 * only knows the last ROLL).
 *
 * The witness for the frame is the composition CODE read off the page — its
 * aspect field is the one character at mid[0], a roster index no browser is
 * free to perturb (field layout asserted in tests/unit/rollCode.invariants.mjs)
 * — plus the stage frame's own box ratio, which is the thing the wisher can
 * see. The witness for "still rolls" is the rest of the code changing.
 *
 * Run against the running collage dev server (:5199, never :5173 — that is
 * Persona 500 on this machine):
 *   npx playwright test --config playwright.frame-hold.config.ts
 * or against a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.frame-hold.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

// A valid solid-colour PNG built in-process — any number of DISTINCT photos with
// no fixture files. Distinct colours because the app colour-analyses every image.
function makePng(r: number, g: number, b: number, size = 64): Buffer {
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

const distinctPhotos = (n: number) =>
  Array.from({ length: n }, (_, i) => ({
    name: `photo_${i}.png`,
    mimeType: 'image/png',
    buffer: makePng((i * 28) % 255, (i * 97) % 255, (i * 51) % 255),
  }));

const codeOf = (page: Page) => page.getByTestId('composition-code').innerText();

/** The frame's aspect, read from the code — mid[0] is the roster index. */
const aspectChar = async (page: Page) => (await codeOf(page)).trim().split('-')[1][0];

/**
 * The frame's aspect as the wisher sees it: the stage frame's own box. The
 * selector is the one stage-room.spec.ts already measures with. Read as a
 * ratio, not the inline style — once `artFit` lands the style is measured
 * pixels and the aspect only survives in the box.
 */
const frameRatio = (page: Page) =>
  page.evaluate(() => {
    const el = document.querySelector('div.relative.shadow-2xl');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return r.height ? r.width / r.height : null;
  });

/** Two ratios agree when they are the same roster entry — the closest pair on
    the roster is 20% apart, and the measured box wobbles well under 1%. */
const sameShape = (a: number, b: number) => Math.abs(a - b) / b < 0.02;

async function boot(page: Page, photos = 9) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(distinctPhotos(photos));
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  await expect(page.getByTestId('composition-code')).toBeVisible({ timeout: 30_000 });
  // The commit after upload, not a layout worker — same wait dice-count uses.
  await page.waitForTimeout(400);
}

/** Press a dice and give React its commit plus the artFit re-measure. */
async function press(page: Page, testId: string) {
  await page.getByTestId(testId).click();
  await page.waitForTimeout(250);
}

test.describe('the frame hold', () => {

  test('F1: held, twelve rolls keep the frame — and the dice still rolls', async ({ page }) => {
    await boot(page);
    await press(page, 'dock-dice'); // land somewhere first, like the wisher mid-chase

    const chip = page.getByTestId('dock-hold-frame');
    await expect(chip).toBeVisible();
    await chip.click();
    await expect(chip).toHaveAttribute('aria-pressed', 'true');

    const heldChar = await aspectChar(page);
    const heldRatio = (await frameRatio(page))!;
    expect(heldRatio, 'the stage frame is not measurable').not.toBeNull();

    const codes: string[] = [];
    for (let i = 0; i < 12; i++) {
      await press(page, 'dock-dice');
      expect(await aspectChar(page), `press ${i + 1} moved the held frame (code)`).toBe(heldChar);
      const r = (await frameRatio(page))!;
      expect(sameShape(r, heldRatio), `press ${i + 1} moved the held frame (box ${r} vs ${heldRatio})`).toBe(true);
      codes.push((await codeOf(page)).trim());
    }
    // The other half of the promise: with the frame pinned, everything else
    // must still be a dice — identical codes would mean the hold froze the roll.
    expect(new Set(codes).size, `the dice went dead under the hold: ${codes[0]}`).toBeGreaterThan(1);

    // Undo of a held roll: the frame must not jump (the pre-roll aspect IS the
    // held aspect), and the hold itself must survive the step back — it rides
    // preference, not history.
    await press(page, 'undo-dock');
    expect(await aspectChar(page), 'undo after a held roll moved the frame').toBe(heldChar);
    await expect(chip).toHaveAttribute('aria-pressed', 'true');
  });

  test('F2: OFF by default, and off means exactly the old dice', async ({ page }) => {
    await boot(page);
    const chip = page.getByTestId('dock-hold-frame');
    await expect(chip).toBeVisible();
    await expect(chip, 'the hold must ship OFF — current behaviour unchanged').toHaveAttribute('aria-pressed', 'false');

    // Free-rolling, the frame must still change shape. Twenty presses: a
    // no-change run is (1/7)^20 under the roster draw — a probability, but not
    // a flake. Pre-fix this is 12-for-12 (the probe this spec was built from).
    const start = await aspectChar(page);
    const seen: string[] = [start];
    let moved = false;
    for (let i = 0; i < 20 && !moved; i++) {
      await press(page, 'dock-dice');
      seen.push(await aspectChar(page));
      moved = seen[seen.length - 1] !== start;
    }
    expect(moved, `20 free rolls never re-shaped the frame: ${seen.join(' ')}`).toBe(true);
  });

  test('F3: one hold, both surfaces — the rail button and the dock chip are the same state', async ({ page }) => {
    await boot(page);
    const heldChar = await aspectChar(page);

    await page.getByRole('button', { name: 'Maximize the shot' }).click();
    const rail = page.getByTestId('rail-hold-frame');
    await expect(rail).toBeVisible();
    await expect(rail).toHaveAttribute('aria-pressed', 'false');

    // 44px is a law, in both rows of a wrapped rail.
    const box = await rail.boundingBox();
    expect(box!.width, 'the rail hold is under the 44px tap target').toBeGreaterThanOrEqual(43.5);
    expect(box!.height, 'the rail hold is under the 44px tap target').toBeGreaterThanOrEqual(43.5);

    await rail.click();
    await expect(rail).toHaveAttribute('aria-pressed', 'true');

    const ratio0 = (await frameRatio(page))!;
    for (let i = 0; i < 6; i++) {
      await press(page, 'rail-dice');
      const r = (await frameRatio(page))!;
      expect(sameShape(r, ratio0), `rail press ${i + 1} moved the held frame (${r} vs ${ratio0})`).toBe(true);
    }

    await page.getByRole('button', { name: 'Exit full bleed' }).click();
    // Same state, read from the other surface — and the frame the rail held is
    // the frame the code still carries.
    await expect(page.getByTestId('dock-hold-frame')).toHaveAttribute('aria-pressed', 'true');
    expect(await aspectChar(page), 'the rail rolls moved the frame the code carries').toBe(heldChar);

    await page.getByTestId('dock-hold-frame').click();
    await page.getByRole('button', { name: 'Maximize the shot' }).click();
    await expect(page.getByTestId('rail-hold-frame')).toHaveAttribute('aria-pressed', 'false');
  });

  test('F3b: the widened rail is watertight where the phones are', async ({ page }) => {
    await boot(page);
    await page.getByRole('button', { name: 'Maximize the shot' }).click();
    await expect(page.getByTestId('rail-hold-frame')).toBeVisible();

    // The eighth button re-derived the wrap: five makers + hold on one row,
    // three navigators on the next, one row again from 430. Same bar the
    // seventh button was held to in colour-dice.spec.ts.
    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 720 });
      await page.waitForTimeout(250);
      const overflow = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollW, `${w}px: the page scrolls sideways`).toBeLessThanOrEqual(overflow.clientW);
      for (const id of ['rail-dice', 'rail-hold-frame', 'rail-colour-dice', 'rail-shuffle', 'rail-remix', 'undo', 'redo']) {
        const b = await page.getByTestId(id).boundingBox();
        expect(b, `${w}px: ${id} is not laid out`).not.toBeNull();
        expect(b!.width, `${w}px: ${id} is under the 44px tap target`).toBeGreaterThanOrEqual(43.5);
        expect(b!.height, `${w}px: ${id} is under the 44px tap target`).toBeGreaterThanOrEqual(43.5);
        expect(b!.x, `${w}px: ${id} starts off the left edge`).toBeGreaterThanOrEqual(-0.5);
        expect(b!.x + b!.width, `${w}px: ${id} runs off the right edge`).toBeLessThanOrEqual(w + 0.5);
      }

      // The geometry the change actually CLAIMS, not just the tap law: the
      // hold rides the makers' row beside the dice; below 430 the navigators
      // wrap to a second row; from 430 the rail is one row again. Without
      // this, a silent regression to a 4/4 split passes every assert above.
      const yOf = async (id: string) => (await page.getByTestId(id).boundingBox())!.y;
      const diceY = await yOf('rail-dice');
      expect(Math.abs((await yOf('rail-hold-frame')) - diceY), `${w}px: the hold left the dice's row`).toBeLessThan(2);
      if (w < 430) {
        expect(Math.abs((await yOf('rail-remix')) - diceY), `${w}px: the makers' row split`).toBeLessThan(2);
        expect((await yOf('undo')) - diceY, `${w}px: undo did not wrap to the second row`).toBeGreaterThan(40);
      } else {
        expect(Math.abs((await yOf('undo')) - diceY), '430px: the rail is not one row').toBeLessThan(2);
      }
    }
  });

  test('F4: the hold pins what is ON SCREEN, not the last roll', async ({ page }) => {
    await boot(page);
    await press(page, 'dock-dice');
    const chip = page.getByTestId('dock-hold-frame');
    await chip.click();
    await expect(chip).toHaveAttribute('aria-pressed', 'true');
    const rolledChar = await aspectChar(page);

    // Re-set the frame by hand AFTER engaging the hold — the Canvas chips must
    // keep working (the hold is about the dice, not about you), and what they
    // set becomes the held value.
    await page.getByRole('button', { name: 'Settings' }).click();
    const story = page.getByTitle('Story — 9:16');
    const portrait = page.getByTitle('Portrait — 2:3');
    // '6' is Story's roster index; when the roll already landed there, pull the
    // frame somewhere else instead so the hand-set value is always a CHANGE.
    await (rolledChar === '6' ? portrait : story).click();
    await page.getByRole('button', { name: 'Layout' }).click();
    await page.waitForTimeout(250);

    const handChar = await aspectChar(page);
    expect(handChar, 'the Canvas chip stopped working under the hold').not.toBe(rolledChar);

    // A hold that reads `previous.aspect` — the last ROLL — snaps back to
    // rolledChar on this press. The state on screen is the only truth.
    for (let i = 0; i < 3; i++) {
      await press(page, 'dock-dice');
      expect(await aspectChar(page), `press ${i + 1} snapped back to the rolled frame`).toBe(handChar);
    }
  });
});
