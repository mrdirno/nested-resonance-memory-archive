import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for THE COLOUR DICE proof.
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — the repo default (playwright.config.ts) targets :5173, which on this
 * machine is Persona 500, not this app (scar: a playwright run silently reused
 * another project's dev server on 5173). Override with COLLAGE_BASE_URL to run
 * against a deployed release.
 *
 * Serial: two of the three assertions are pixel fingerprints of the shared
 * preview pipeline, so a machine under load is the only thing that could make
 * two identical compositions disagree.
 *
 * Mobile Chrome is not optional here. The wish came from full bleed on a phone,
 * and the rail this adds a seventh button to had nine spare pixels at 320.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /colour-dice\.spec\.ts$/,
  timeout: 240_000,
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium' } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
  ],
});
