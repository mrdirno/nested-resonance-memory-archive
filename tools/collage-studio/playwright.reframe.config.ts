import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for THE REFRAME and THE FRAME TRAVELS.
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — Vite's default 5173 belongs to another project on this machine
 * (Persona 500), and `reuseExistingServer` would attach to it silently.
 * `globalSetup` fails the run if the URL is not this app.
 *
 * `acceptDownloads` is explicit because T4/T5 ARE downloads: the file is
 * exported, saved and fed back in through the real Open button.
 * Serial, because every assertion in this spec reads a colour off an
 * asynchronously produced preview — parallel workers lose that race (see the
 * `stableColour` comment in the spec).
 */
export default defineConfig({
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /reframe\.spec\.ts$/,
  timeout: 300_000,
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
