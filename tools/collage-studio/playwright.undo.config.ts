import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for the UNDO proof.
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — the repo default (playwright.config.ts) targets :5173, which on this
 * machine is Persona 500, not this app (scar: a playwright run silently reused
 * another project's dev server on 5173). Override with COLLAGE_BASE_URL to run
 * against a deployed release.
 *
 * Serial, not parallel: the assertion is a pixel fingerprint of the shared
 * preview pipeline, so a machine under load is the only thing that could make
 * two identical compositions disagree.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /undo\.spec\.ts$/,
  timeout: 240_000,
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
    // The phone this was wished from — full bleed is a phone gesture.
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium' } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
  ],
});
