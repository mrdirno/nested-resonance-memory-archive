/* Bounded read-only Wish audit. Aldrin Payopay · GPL-3.0-only.
 * Five isolated browser pages; synthetic draft text is never submitted.
 * Usage: node live_sample.cjs [absolute-source-root] [base-url]
 */
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const root = path.resolve(process.argv[2] || '/Volumes/dual/nested-resonance-memory-archive');
const base = new URL(process.argv[3] || 'https://mrdirno.github.io/nested-resonance-memory-archive/');
if (!/^https?:$/.test(base.protocol) || !base.pathname.endsWith('/')) {
  throw new Error('Provide an http(s) base URL ending in /');
}
const fromApp = createRequire(path.join(root, 'tools/collage-studio/package.json'));
const { chromium } = fromApp('playwright');
const cases = [
  { path: 'av/consumables.html', lifecycle: 'maintained', runtime: 'toolkit', surface: 'av', trigger: '.av-req-btn', sheet: '.av-sheet', close: '.av-x' },
  { path: 'commons/index.html', lifecycle: 'maintained', runtime: 'feedback', surface: 'commons', trigger: '#addbtn', sheet: '.fb-sheet', close: '.fb-x' },
  { path: 'collage/', lifecycle: 'maintained', runtime: 'feedback', surface: 'collage', trigger: '.studio-header-wish', sheet: '.fb-sheet', close: '.fb-x' },
  { path: 'archive/HELIOS-V045-amethyst-interference.html', lifecycle: 'legacy_or_archived' },
  { path: 'collage-beta/', lifecycle: 'legacy_or_archived' },
];

(async () => {
  const browser = await chromium.launch();
  const started = new Date().toISOString();
  const screenshots = path.join(__dirname, 'screenshots');
  fs.mkdirSync(screenshots, { recursive: true });
  const results = await Promise.all(cases.map(async c => {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, colorScheme: 'dark' });
    const page = await context.newPage();
    const errors = [], preventedWrites = [];
    page.on('pageerror', e => errors.push(e.message));
    // No test action may write to the production server. GET/HEAD/OPTIONS only.
    await context.route('**/*', route => {
      const request = route.request();
      if (!['GET', 'HEAD', 'OPTIONS'].includes(request.method())) {
        preventedWrites.push({ method: request.method(), origin: new URL(request.url()).origin });
        return route.abort();
      }
      return route.continue();
    });
    const result = { path: c.path, url: new URL(c.path, base).href, lifecycle: c.lifecycle, submission_accepted: 'not_tested', draft_close_reopen: 'not_tested', draft_reload: 'not_tested' };
    try {
      const response = await page.goto(result.url, { waitUntil: 'networkidle', timeout: 20000 });
      result.http_status = response.status();
      if (response.status() !== 200) throw new Error(`Expected HTTP 200, received ${response.status()}`);
      Object.assign(result, await page.evaluate(config => {
        const handles = { feedback: !!window.Feedback, toolkit: !!window.Toolkit };
        const selector = config.trigger || '.av-req-btn,.fb-btn,#btn-wish,button[data-wish-well],a[data-wish-well]';
        const element = document.querySelector(selector);
        const rect = element?.getBoundingClientRect();
        const style = element && getComputedStyle(element);
        const visible = !!(rect?.width && rect?.height && style.visibility !== 'hidden' && style.display !== 'none');
        const cx = rect && rect.left + rect.width / 2, cy = rect && rect.top + rect.height / 2;
        const onGlass = visible && rect.left >= 0 && rect.top >= 0 && rect.right <= innerWidth && rect.bottom <= innerHeight;
        const top = onGlass ? document.elementFromPoint(cx, cy) : null;
        const reachable = !!(onGlass && top && (top === element || element.contains(top)));
        const label = element?.getAttribute('aria-label') || element?.textContent?.trim() || null;
        return {
          title: document.title,
          runtime_handles: handles,
          runtime_loaded: config.runtime ? handles[config.runtime] : (handles.feedback || handles.toolkit),
          feedback_config_ready: window.Feedback?.ready ?? null,
          feedback_surface: window.Feedback?.surface ?? null,
          toolkit_surface: window.Toolkit?.trade?.slug ?? null,
          trigger: { selector, found: !!element, has_visible_box: visible, in_initial_viewport: !!onGlass, center_hit_in_initial_viewport: reachable, accessible_name: label, named_wish_or_feedback: !!(label && /wish|feedback/i.test(label)) },
          opens_correct_modal: 'not_tested',
          theme_attribute: document.documentElement.dataset.theme || null,
          body_background: getComputedStyle(document.body).backgroundColor,
          horizontal_overflow_px: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        };
      }, c));
      const id = c.path.replace(/[^a-z0-9]+/gi, '-').replace(/-$/, '');
      const closed = `screenshots/${id}-page.png`;
      await page.screenshot({ path: path.join(__dirname, closed) });
      result.screenshots = [closed];
      if (c.trigger) {
        if (!result.runtime_loaded) throw new Error(`Expected ${c.runtime} runtime did not load`);
        await page.locator(c.trigger).scrollIntoViewIfNeeded();
        result.trigger.center_hit_after_scroll = await page.locator(c.trigger).evaluate(element => {
          const box = element.getBoundingClientRect();
          const top = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
          return !!top && (top === element || element.contains(top));
        });
        await page.locator(c.trigger).click({ timeout: 4000 });
        result.trigger.opened_by_real_click = true;
        const sheet = page.locator(c.sheet);
        await sheet.waitFor({ state: 'visible', timeout: 4000 });
        const title = sheet.locator('[name=tool_title]');
        result.modal_surface_matches = (c.runtime === 'feedback' ? result.feedback_surface : result.toolkit_surface) === c.surface;
        result.opens_correct_modal = await sheet.isVisible() && await title.count() === 1 && result.modal_surface_matches;
        const modal = `screenshots/${id}-modal.png`;
        await page.screenshot({ path: path.join(__dirname, modal) });
        result.screenshots.push(modal);
        const draft = 'Local audit draft — never submitted';
        await title.fill(draft);
        await sheet.locator(c.close).click();
        await page.locator(c.trigger).click();
        result.draft_close_reopen = await title.inputValue() === draft ? 'retained' : 'lost';
        await page.reload({ waitUntil: 'networkidle', timeout: 20000 });
        await page.locator(c.trigger).click({ timeout: 4000 });
        result.draft_reload = await page.locator(c.sheet).locator('[name=tool_title]').inputValue() === draft ? 'retained' : 'lost';
      }
    } catch (error) {
      result.audit_error = error.message;
    } finally {
      result.page_errors = errors;
      result.prevented_network_writes = preventedWrites;
      await context.close();
    }
    return result;
  }));
  await browser.close();
  const report = {
    schema: 'wish-live-sample/v1',
    started_at: started,
    finished_at: new Date().toISOString(),
    browser: 'Playwright Chromium, isolated contexts',
    viewport: { width: 390, height: 844, mobile: true, touch: true, color_scheme: 'dark' },
    scope: 'Five URL samples only. No full-site coverage, login persistence, server acceptance, theme schedule, or real-device conclusion is implied.',
    write_policy: 'All non-GET/HEAD/OPTIONS network requests blocked. Synthetic text was filled, closed, reopened and reloaded; no submit action was taken.',
    results,
  };
  fs.writeFileSync(path.join(__dirname, 'live-observations.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ output: path.join(__dirname, 'live-observations.json'), sampled: results.length, audit_errors: results.filter(r => r.audit_error), results }, null, 2));
  // Missing named triggers and lost drafts are recorded findings. Infrastructure
  // errors/missing required runtime on a maintained sample fail the audit run.
  if (results.some(r => r.audit_error || (r.lifecycle === 'maintained' && !r.opens_correct_modal))) process.exitCode = 1;
})().catch(error => { console.error(error.stack); process.exitCode = 2; });
