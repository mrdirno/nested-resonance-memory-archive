import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for the concurrency proof (every imported video plays at
 * once — the wish "Multiple videos should play back at the same time").
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — the repo default (playwright.config.ts) targets :5173, which on this
 * machine is Persona 500, not this app (scar: a run silently reused another
 * project's dev server on 5173). Override with COLLAGE_BASE_URL to run against a
 * deployed release.
 *
 * Chromium only, on purpose: the spec itself sets the iPhone UA for the phone
 * shape (the caps are chosen off the UA + coarse pointer, not the engine), and
 * the WebKit build on this machine has no VP9 decode for the hue-keyed fixtures.
 */
export default defineConfig({
  // FAILS THE RUN if the URL is not this app. `reuseExistingServer` below
  // attaches to whatever is already listening, so without this a squatter on
  // the port takes the WHOLE suite green against a stranger. See the file.
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /concurrency\.spec\.ts$/,
  timeout: 240_000,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
