import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for the TRIM proof.
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO
 * webServer block — the repo default (playwright.config.ts) targets :5173, which
 * on this machine is Persona 500, not this app (scar: a playwright run silently
 * reused another project's dev server on 5173). Override with COLLAGE_BASE_URL
 * to run the same spec against the deployed release.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /trim\.spec\.ts$/,
  timeout: 420_000,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
