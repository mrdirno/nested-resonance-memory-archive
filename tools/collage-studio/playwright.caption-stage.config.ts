import { defineConfig, devices } from '@playwright/test';

/** Local module seam only. The production UI/export proof lives in captions.spec.ts. */
export default defineConfig({
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /caption-stage\.spec\.ts$/,
  timeout: 60_000,
  workers: 1,
  outputDir: 'test-results/caption-stage',
  reporter: 'list',
  use: { baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199', trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } }],
});
