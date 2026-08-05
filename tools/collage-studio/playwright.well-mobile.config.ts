import { defineConfig, devices } from '@playwright/test';

/**
 * Mobile-watertight gate for the shared wishing well (shared/toolkit.js).
 *
 * Points at a plain static server on the REPO ROOT (the trade pages are static
 * HTML), not at the collage dev server and never at :5173 — that is Persona 500
 * on this machine. Start it first, from the repo root:
 *   python3 -m http.server 8899
 *
 * Override with WELL_BASE_URL to run the same gate against the deployed site.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /well-mobile\.spec\.ts$/,
  timeout: 60_000,
  workers: 1,
  use: {
    baseURL: process.env.WELL_BASE_URL || 'http://localhost:8899',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
