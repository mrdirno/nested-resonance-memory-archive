import { defineConfig, devices } from '@playwright/test';

/**
 * The MOBILE-WATERTIGHT ship gate. Points at the ALREADY-RUNNING collage dev
 * server on :5199 — never :5173, which on this machine is Persona 500.
 * Override with COLLAGE_BASE_URL to gate a deployed release.
 */
export default defineConfig({
  // FAILS THE RUN if the URL is not this app. `reuseExistingServer` below
  // attaches to whatever is already listening, so without this a squatter on
  // the port takes the WHOLE suite green against a stranger. See the file.
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /mobile-watertight\.spec\.ts$/,
  timeout: 150_000,
  fullyParallel: true,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
    hasTouch: true,
    isMobile: true,
  },
  projects: [
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium' } },
  ],
});
