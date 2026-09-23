import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for THE GRAB — press any fragment, drag its picture, let go.
 *
 * Points at the ALREADY-RUNNING collage dev server on :5199 and has NO webServer
 * block — Vite's default 5173 belongs to another project on this machine
 * (Persona 500), and `reuseExistingServer` would attach to it silently.
 * `globalSetup` fails the run if the URL is not this app.
 *
 * Mobile Chrome carries the touch tests (real touch through CDP, which only
 * Chromium has); desktop Chromium carries the mouse test. Serial, because every
 * assertion reads a colour off an asynchronously produced preview.
 */
export default defineConfig({
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /grab\.spec\.ts$/,
  timeout: 240_000,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium', launchOptions: { args: ['--mute-audio'] } } },
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium', launchOptions: { args: ['--mute-audio'] } } },
  ],
});
