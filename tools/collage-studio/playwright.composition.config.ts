import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for the composition (arrangement + crop focus) proof.
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — the repo default (playwright.config.ts) targets :5173, which on this
 * machine is Persona 500, not this app (scar: a playwright run silently reused
 * another project's dev server on 5173). Override with COLLAGE_BASE_URL to run
 * against a deployed release.
 */
export default defineConfig({
  // FAILS THE RUN if the URL is not this app. `reuseExistingServer` below
  // attaches to whatever is already listening, so without this a squatter on
  // the port takes the WHOLE suite green against a stranger. See the file.
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /composition\.spec\.ts$/,
  timeout: 180_000,
  // SERIAL, like playwright.roll-code.config.ts. Both projects here render a
  // FULL-RESOLUTION export through a worker, and two of those at once on one
  // machine time each other out — a false red that costs a cycle to diagnose
  // (it did: chromium alone 5/5, Mobile Chrome alone 2/2, both in parallel 2
  // failed, both serial 10/10).
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
    // The phone the pages actually get used on. Same assertions, 393px wide.
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium' } },
  ],
});
