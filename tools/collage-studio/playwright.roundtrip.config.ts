import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for the project save/load round trip.
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 — the repo default
 * (playwright.config.ts) targets :5173, which on this machine is Persona 500,
 * not this app (scar: a playwright run silently reused another project's dev
 * server on 5173). Override with COLLAGE_BASE_URL to run against a release.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /project-roundtrip\.spec\.ts$/,
  timeout: 180_000,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    acceptDownloads: true,
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
