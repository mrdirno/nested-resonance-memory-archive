// Author: Aldrin Payopay · GPL-3.0-only
// Real native dialog and keyboard behavior. Clipboard is the only mocked boundary.
// Run: npx playwright test tests/e2e/lyric-help.spec.ts --project=chromium --project='Mobile Chrome' --project='Mobile Safari' --workers=1
import { test, expect, type Locator, type Page } from '@playwright/test';
import path from 'node:path';

test.use({ actionTimeout: 15_000 });

const DRAFT = 'A draft still waiting for its melody\nKeep this second line';
const SRT = '1\n00:00:00,000 --> 00:00:02,000\nORIGINAL WORDS\n';
const HELP = 'Need lyrics? Start with your song';
const LINKS = [
  ['Open Gemini', 'https://gemini.google.com/'],
  ['Current upload limits', 'https://support.google.com/gemini/answer/14903178?hl=en'],
  ['Open Whisper Web', 'https://huggingface.co/spaces/Xenova/whisper-web'],
  ['Open-source project', 'https://github.com/xenova/whisper-web'],
  ['Apple Silicon setup guide', 'https://github.com/ml-explore/mlx-examples/tree/main/whisper'],
] as const;

async function prepareDraft(page: Page) {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles(path.resolve('tests/fixtures/img_a.jpg'));
  await page.getByRole('button', { name: 'Text', exact: true }).click();
  await page.getByLabel('Import caption file', { exact: true }).setInputFiles({ name: 'help-check.srt', mimeType: 'application/x-subrip', buffer: Buffer.from(SRT) });
  await page.getByRole('button', { name: 'Edit caption 1: ORIGINAL WORDS', exact: true }).click();
  await page.getByLabel('Caption text', { exact: true }).fill('UNSAVED CUE WORDS');
  await page.getByLabel('Start (seconds)', { exact: true }).fill('0.25');
  await page.getByLabel('End (seconds)', { exact: true }).fill('1.75');
  await page.getByLabel('Lyrics, one line per cue', { exact: true }).fill(DRAFT);
}

async function expectDraft(page: Page) {
  // Read the rendered fields directly: native showModal correctly makes the
  // underlying editor inert, so it has no accessible labels until dismissal.
  await expect(page.locator('textarea[placeholder="Paste the lines you want in this take"]')).toHaveValue(DRAFT);
  await expect(page.locator('textarea[aria-label="Caption text"]')).toHaveValue('UNSAVED CUE WORDS');
  await expect(page.getByTestId('caption-cue-form').locator('input[type=number]').nth(0)).toHaveValue('0.25');
  await expect(page.getByTestId('caption-cue-form').locator('input[type=number]').nth(1)).toHaveValue('1.75');
  await expect(page.getByTestId('caption-editor')).toContainText('1 timed cues');
  await expect(page.locator('button[aria-label="Edit caption 1: ORIGINAL WORDS"]')).toHaveCount(1);
}

async function expectHitTarget(control: Locator) {
  await control.scrollIntoViewIfNeeded();
  const result = await control.evaluate(element => {
    const box = element.getBoundingClientRect();
    const hit = document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2);
    return { width: box.width, height: box.height, left: box.left, right: box.right, top: box.top, bottom: box.bottom,
      viewportWidth: innerWidth, viewportHeight: innerHeight, reachable: hit === element || element.contains(hit) };
  });
  expect(result.width, JSON.stringify(result)).toBeGreaterThanOrEqual(43.5);
  expect(result.height, JSON.stringify(result)).toBeGreaterThanOrEqual(43.5);
  expect(result.left, JSON.stringify(result)).toBeGreaterThanOrEqual(0);
  expect(result.right, JSON.stringify(result)).toBeLessThanOrEqual(result.viewportWidth + 1);
  expect(result.top, JSON.stringify(result)).toBeGreaterThanOrEqual(0);
  expect(result.bottom, JSON.stringify(result)).toBeLessThanOrEqual(result.viewportHeight + 1);
  expect(result.reachable, JSON.stringify(result)).toBe(true);
}

for (const width of [320, 390]) {
  test(`lyric guide fits ${width}px, isolates shortcuts and returns to the unsaved draft`, async ({ page }, info) => {
    test.setTimeout(90_000);
    await page.setViewportSize({ width, height: 664 });
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await prepareDraft(page);
    const trigger = page.getByRole('button', { name: HELP, exact: true });
    await trigger.click();
    const dialog = page.getByRole('dialog', { name: 'Get lyrics from your song', exact: true });
    await expect(dialog).toBeVisible();
    await expect(dialog).toHaveJSProperty('open', true);
    const close = dialog.getByRole('button', { name: 'Close guide', exact: true });
    await expect(close).toBeFocused();
    const geometry = await dialog.evaluate(element => {
      const box = element.getBoundingClientRect();
      return { top: box.top, bottom: box.bottom, left: box.left, right: box.right,
        innerHeight, innerWidth, scrollable: element.scrollHeight > element.clientHeight,
        overflow: element.scrollWidth > element.clientWidth + 1,
        pageOverflow: document.documentElement.scrollWidth > innerWidth + 1 };
    });
    expect(geometry.left).toBeGreaterThanOrEqual(0);
    expect(geometry.top).toBeGreaterThanOrEqual(0);
    expect(geometry.right).toBeLessThanOrEqual(geometry.innerWidth + 1);
    expect(geometry.bottom).toBeLessThanOrEqual(geometry.innerHeight + 1);
    expect(geometry.scrollable).toBe(true);
    expect(geometry.overflow).toBe(false);
    expect(geometry.pageOverflow).toBe(false);
    await expectHitTarget(close);
    await page.screenshot({ path: info.outputPath(`lyric-guide-${width}-top.png`) });

    // These are live Studio shortcuts when focus is on a button. Native dialog
    // inertness plus its key boundary must keep them from reaching the canvas.
    let downloads = 0, fileChoosers = 0;
    page.on('download', () => { downloads++; });
    page.on('filechooser', () => { fileChoosers++; });
    const beforeUrl = page.url();
    for (const key of ['f', 'Control+z', 'Control+Shift+z', 'Control+s', 'Control+e', 'Control+o', 'Meta+z', 'Meta+s', 'Meta+e', 'Meta+o']) {
      await close.focus();
      await page.keyboard.press(key);
      await expect(dialog).toBeVisible();
      await expect(page.getByRole('dialog')).toHaveCount(1);
    }
    await expect(page.locator('[role="toolbar"][aria-label="Full bleed tools"]')).toHaveCount(0);
    await expectDraft(page);
    expect(downloads).toBe(0);
    expect(fileChoosers).toBe(0);
    expect(page.url()).toBe(beforeUrl);

    await expectHitTarget(dialog.getByRole('textbox', { name: 'Lyric transcription prompt', exact: true }));
    await expectHitTarget(dialog.getByRole('button', { name: 'Copy lyric prompt', exact: true }));
    await expect(dialog.getByRole('link')).toHaveCount(LINKS.length);
    for (const [name, href] of LINKS) {
      const link = dialog.getByRole('link', { name, exact: true });
      await expect(link).toHaveAttribute('href', href);
      await expect(link).toHaveAttribute('target', '_blank');
      await expect(link).toHaveAttribute('rel', /noopener/);
      await expect(link).toHaveAttribute('rel', /noreferrer/);
      await expectHitTarget(link);
    }
    await page.screenshot({ path: info.outputPath(`lyric-guide-${width}-options.png`) });
    // Native tab order cannot enter the Studio underneath the modal. WebKit
    // also cycles through browser chrome: body is active there but hasFocus is
    // false, which is different from focusing an underlying app control.
    await close.focus();
    for (let step = 0; step < 10; step++) {
      await page.keyboard.press('Tab');
      const focus = await dialog.evaluate(element => ({ inside: element.contains(document.activeElement),
        documentFocused: document.hasFocus(), body: document.activeElement === document.body }));
      expect(focus.inside || (!focus.documentFocused && focus.body), JSON.stringify(focus)).toBe(true);
    }
    await close.click();
    await expect(dialog).not.toBeVisible();
    await expect(trigger).toBeFocused();
    await expectDraft(page);

    await trigger.click();
    await expect(dialog).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(dialog).not.toBeVisible();
    await expect(trigger).toBeFocused();
    await expectDraft(page);
    await page.getByRole('button', { name: 'Save cue', exact: true }).click();
    await expect(page.getByRole('button', { name: 'Edit caption 1: UNSAVED CUE WORDS', exact: true })).toBeVisible();
    expect(errors).toEqual([]);
  });
}

test('lyric prompt copies and selects the same complete text when clipboard access is denied', async ({ page }) => {
  test.setTimeout(60_000);
  // Stub permission-dependent I/O, not the component's copy/fallback behavior.
  await page.addInitScript(() => {
    const state = window as typeof window & { lyricClipboardDenied: boolean; lyricCopiedText: string };
    state.lyricClipboardDenied = false;
    state.lyricCopiedText = '';
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async (value: string) => {
      if (state.lyricClipboardDenied) throw new DOMException('Permission denied', 'NotAllowedError');
      state.lyricCopiedText = value;
    } } });
  });
  await prepareDraft(page);
  const trigger = page.getByRole('button', { name: HELP, exact: true });
  await trigger.click();
  const dialog = page.getByRole('dialog', { name: 'Get lyrics from your song', exact: true });
  const prompt = dialog.getByRole('textbox', { name: 'Lyric transcription prompt', exact: true });
  const expected = await prompt.inputValue();
  expect(expected).toContain('If you cannot access or listen to the audio');
  expect(expected).toContain('[unclear]');
  await expect(prompt).toHaveJSProperty('readOnly', true);
  await dialog.getByRole('button', { name: 'Copy lyric prompt', exact: true }).click();
  await expect(dialog.getByRole('status')).toContainText('Prompt copied');
  expect(await page.evaluate(() => (window as any).lyricCopiedText)).toBe(expected);
  await page.evaluate(() => { (window as any).lyricClipboardDenied = true; });
  await dialog.getByRole('button', { name: 'Copy lyric prompt', exact: true }).click();
  await expect(dialog.getByRole('status')).toContainText('The prompt is selected');
  await expect(prompt).toBeFocused();
  expect(await prompt.evaluate(element => {
    const input = element as HTMLTextAreaElement;
    return input.value.slice(input.selectionStart, input.selectionEnd);
  })).toBe(expected);
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();
  await expect(trigger).toBeFocused();
  await expectDraft(page);
});
