// Author: Aldrin Payopay · GPL-3.0-only
import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests/e2e',
  testMatch: /(?:captions|project-integrity)\.spec\.ts$/,
  timeout: 180_000,
  workers: 1,
  reporter: 'list',
  use: { baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199', trace: 'retain-on-failure', actionTimeout: 15000 },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'], channel: 'chromium' } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
  ],
});
