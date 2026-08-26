/**
 * IS THE THING ON THE OTHER END OF THE URL ACTUALLY THIS APP?
 *
 * WHY THIS FILE EXISTS — SCAR, 2026-08-26.
 *   `playwright.config.ts` already carries a long comment about :5173 belonging
 *   to Persona 500 and about `reuseExistingServer` being the mechanism that
 *   makes a wrong-app run SILENT. The port was moved to :5199 and `--strictPort`
 *   was added, and the hole was declared closed.
 *
 *   It was not. `--strictPort` only protects the run that starts the server
 *   FIRST. `reuseExistingServer: !process.env.CI` means that when something else
 *   is already listening on :5199, Playwright does not start vite at all — it
 *   attaches to the squatter and every spec in the suite drives a stranger.
 *   Measured, not theorised: a run of the swap spec against :5199 spent four
 *   minutes per test waiting for a file input that does not exist, because
 *   `/Volumes/dual/persona500` had vite on :5199 with `--host`. The title on the
 *   other end read "Persona 500 | 1,022 AI Mentors & 1,070+ Tools".
 *
 *   A timeout is the LUCKY version of that failure. The dangerous version is a
 *   spec whose assertions happen to pass against the other app — or, far more
 *   likely here, one that goes GREEN because its `toHaveCount(0)` and
 *   `not.toBeVisible()` assertions are all trivially true on a page that has
 *   none of this app's furniture. That is a whole suite reporting green about
 *   software it never loaded.
 *
 * WHAT IT DOES. One fetch, before any browser starts, and it throws with the
 * name of whatever answered. Cheap enough to be unconditional, and it covers
 * every spec at once rather than asking 39 files to remember a guard.
 *
 * It also covers the deployed target: `COLLAGE_BASE_URL` pointed at a Pages URL
 * that 404s, or at the wrong path under the same origin, fails here instead of
 * thirty minutes later.
 */
import type { FullConfig } from '@playwright/test';

/** The <title> this app's index.html has carried since it was named. */
const MARK = 'Smart Crop GenArt Studio';

export default async function globalSetup(config: FullConfig) {
  const base =
    process.env.COLLAGE_BASE_URL ||
    config.projects[0]?.use?.baseURL ||
    'http://localhost:5199';

  let html = '';
  try {
    const res = await fetch(base, { redirect: 'follow' });
    if (!res.ok) {
      throw new Error(`${base} answered ${res.status} ${res.statusText}`);
    }
    html = await res.text();
  } catch (e) {
    throw new Error(
      `E2E TARGET UNREACHABLE — ${base}\n` +
        `  ${(e as Error).message}\n` +
        `  Start this app's dev server (npx vite --port <port> --strictPort) or fix COLLAGE_BASE_URL.`,
    );
  }

  if (!html.includes(MARK)) {
    const title = /<title>([^<]*)<\/title>/i.exec(html)?.[1]?.trim() ?? '(no <title>)';
    throw new Error(
      `E2E TARGET IS NOT COLLAGE STUDIO — ${base}\n` +
        `  expected a page containing "${MARK}"\n` +
        `  got: "${title}"\n` +
        `  Something else is serving that port. Playwright's reuseExistingServer attaches to\n` +
        `  whatever is already listening, so the whole suite would have run against it.\n` +
        `  Start this app on a free port and pass COLLAGE_BASE_URL=http://localhost:<port>/`,
    );
  }
}
