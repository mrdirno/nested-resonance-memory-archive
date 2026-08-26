import { defineConfig, devices } from '@playwright/test';

/**
 * Ship gate for the kit switcher (shared/toolkit.js) — the one control that
 * moves a tradesperson between kits, on all six trades at once.
 *
 * Points at a plain static server on the REPO ROOT (the trade pages are static
 * HTML), not at the collage dev server and never at :5173 — that is Persona 500
 * on this machine. Start it first, from the repo root:
 *   python3 -m http.server 8899
 *
 * Override with KIT_BASE_URL to run the same gate against the deployed site.
 */
export default defineConfig({
  // FAILS THE RUN if the URL is not this app. `reuseExistingServer` below
  // attaches to whatever is already listening, so without this a squatter on
  // the port takes the WHOLE suite green against a stranger. See the file.
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /kit-switcher\.spec\.ts$/,
  timeout: 60_000,
  workers: 1,
  use: {
    // Trailing slash is load-bearing: spec paths are relative so the deployed
    // repo-path prefix survives resolution.
    baseURL: process.env.KIT_BASE_URL || 'http://localhost:8899/',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
