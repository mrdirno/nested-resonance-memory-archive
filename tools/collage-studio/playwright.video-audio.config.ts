import { defineConfig, devices } from '@playwright/test';

/**
 * Standalone config for the EXPORT-CARRIES-THE-SOUND proof.
 *
 * `video-audio-export.spec.ts` had no config of its own, so the only way to run
 * it was the repo default — which points at :5173, i.e. Persona 500 on this
 * machine, not this app. A proof that cannot be run is a proof that rots, and
 * this one guards `offlineAudio.ts`: the module the trim window now flows
 * through. Same shape as every other config here — an ALREADY-RUNNING collage
 * dev server on :5199, no webServer block, `COLLAGE_BASE_URL` to point it at a
 * deployed release instead.
 */
export default defineConfig({
  testDir: './tests/e2e',
  testMatch: /video-audio-export\.spec\.ts$/,
  timeout: 420_000,
  workers: 1,
  use: {
    baseURL: process.env.COLLAGE_BASE_URL || 'http://localhost:5199',
    trace: 'off',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chromium' } },
  ],
});
