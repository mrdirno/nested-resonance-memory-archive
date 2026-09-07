import { defineConfig, devices } from '@playwright/test';

/**
 * REACHABLE-CONTROLS gate: the wishing well, Add music and the frame's shape
 * are ON SCREEN in the loaded state, at every phone size, without scrolling a
 * pane nobody can see is scrollable. Points at the ALREADY-RUNNING collage dev
 * server on :5199 — never :5173, which on this machine is Persona 500.
 * Override with COLLAGE_BASE_URL to gate a deployed release.
 */
export default defineConfig({
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /reachable\.spec\.ts$/,
  timeout: 120_000,
  fullyParallel: true,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium' } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
  ],
});
