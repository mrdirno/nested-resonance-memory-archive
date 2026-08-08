import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for "the artwork gets the room".
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO
 * webServer block — the repo default (playwright.config.ts) targets :5173,
 * which on this machine is Persona 500, not this app (scar: a playwright run
 * silently reused another project's dev server on 5173). Override with
 * COLLAGE_BASE_URL to run against a deployed release.
 *
 * Each test sets its own viewport, so there is one project and no device size.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /stage-room\.spec\.ts$/,
  timeout: 180_000,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
    launchOptions: { args: ['--autoplay-policy=no-user-gesture-required'] },
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
