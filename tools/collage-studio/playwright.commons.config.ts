import { defineConfig, devices } from '@playwright/test';

/**
 * Ship gate for THE COMMONS (commons/index.html + commons/gear.js).
 *
 * Points at a plain static server on the REPO ROOT — the commons is static HTML,
 * not the collage app — and never at :5173, which is Persona 500 on this
 * machine. Start it first, from the repo root:
 *   python3 -m http.server 8765
 *
 * Override with COMMONS_BASE_URL to run the same gate against the deployed site.
 */
export default defineConfig({
  // FAILS THE RUN if the URL is not this app. `reuseExistingServer` below
  // attaches to whatever is already listening, so without this a squatter on
  // the port takes the WHOLE suite green against a stranger. See the file.
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /commons-mobile\.spec\.ts$/,
  timeout: 60_000,
  workers: 1,
  use: {
    // Trailing slash is load-bearing: spec paths are relative so the deployed
    // repo-path prefix survives resolution.
    baseURL: process.env.COMMONS_BASE_URL || 'http://localhost:8765/',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
