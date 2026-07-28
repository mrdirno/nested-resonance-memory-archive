import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  // `channel: 'chromium'` belongs HERE, per Chromium project — never at file
  // scope in a spec. Applied file-wide it is handed to the WebKit projects too,
  // and `browserType.launch` rejects it outright ("Unsupported webkit channel
  // 'chromium'"), so both WebKit projects — the only iOS-shaped coverage this
  // repo has — failed to LAUNCH on every run. Not a red assertion: no assertion
  // at all, on the engine the owner's phone actually uses.
  //
  // Why the full build rather than the default headless shell: the shell ships
  // without the media stack, so MediaRecorder, canvas.captureStream() and VP9
  // decode are all absent. Testing the video features on it proves only that
  // the shell cannot do video.
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], channel: 'chromium' },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'], channel: 'chromium' },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
    // WebKit on a desktop viewport. Not iOS — but it is the only engine here
    // that shares a lineage with it, so it catches WebKit-specific breakage
    // that Chromium never would.
    {
      name: 'webkit-desktop',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
