import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for THE POST (the exported SVG as the project file).
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — the repo default (playwright.config.ts) targets :5173, which on this
 * machine is Persona 500, not this app (scar: a playwright run silently reused
 * another project's dev server on 5173). Override with COLLAGE_BASE_URL to run
 * against a deployed release.
 *
 * `acceptDownloads` is explicit: S1 IS a download, saved and fed back in.
 */
export default defineConfig({
  // FAILS THE RUN if the URL is not this app. `reuseExistingServer` below
  // attaches to whatever is already listening, so without this a squatter on
  // the port takes the WHOLE suite green against a stranger. See the file.
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /svg-project\.spec\.ts$/,
  timeout: 240_000,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    acceptDownloads: true,
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
    // The phone the pages actually get used on. Same assertions, 393px wide.
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium' } },
  ],
});
