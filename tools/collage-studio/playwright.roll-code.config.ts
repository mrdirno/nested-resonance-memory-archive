import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for the composition-code proof.
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — the repo default (playwright.config.ts) targets :5173, which on this
 * machine is Persona 500, not this app (scar: a playwright run silently reused
 * another project's dev server on 5173). Override with COLLAGE_BASE_URL to run
 * against a deployed release.
 *
 * Serial, not parallel: every test drives the SAME preview pipeline and the
 * pixel fingerprints are the assertion, so a shared machine under load is the
 * only thing that could make them disagree.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /roll-code\.spec\.ts$/,
  timeout: 240_000,
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
    // The phone these pages actually get used on. Same assertions, 393px wide.
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium' } },
  ],
});
