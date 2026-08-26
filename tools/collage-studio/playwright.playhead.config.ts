import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for THE PLAYHEAD proof (the take's clock, on a draggable bar).
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — the repo default (playwright.config.ts) targets :5173, which on this
 * machine is Persona 500, not this app (scar: a playwright run silently reused
 * another project's dev server on 5173). Override with COLLAGE_BASE_URL to run
 * against a deployed release.
 *
 * SERIAL, one worker: both cases seek a real H.264 decoder frame by frame, and
 * two pages contending for it is exactly the stall the 400ms seek timeout
 * degrades into a stale frame — i.e. the measurement's own failure mode,
 * manufactured by the harness.
 */
export default defineConfig({
  // FAILS THE RUN if the URL is not this app. `reuseExistingServer` below
  // attaches to whatever is already listening, so without this a squatter on
  // the port takes the WHOLE suite green against a stranger. See the file.
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /playhead\.spec\.ts$/,
  timeout: 300_000,
  workers: 1,
  fullyParallel: false,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
