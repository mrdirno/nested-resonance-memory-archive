import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for the source-count / duplicate-free-fill proof.
 *
 * It points at the ALREADY-RUNNING collage dev server on :5199 and has NO
 * webServer block — the repo default (playwright.config.ts) targets :5173, which
 * on this machine is Persona 500, not this app (scar: a playwright run silently
 * reused another project's dev server on 5173). Reuse the live collage server;
 * never spawn or hit 5173 here. Override with COLLAGE_BASE_URL to run against a
 * deployed release.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /(source-count|video-length-sync)\.spec\.ts$/,
  timeout: 120_000,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
