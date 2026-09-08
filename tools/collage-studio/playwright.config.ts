import { defineConfig, devices } from '@playwright/test';

/**
 * TESTS DO NOT COME OUT OF THE SPEAKERS.
 *
 * WHY THIS EXISTS — 2026-09-07, reported by the owner mid-run: *"you're playing
 * loud pure tones what's the deal i'm trying to make music"*. This suite's audio
 * fixtures are literal sine tones, and a growing share of its specs exist
 * precisely to prove that sound gets UNMUTED — the cut audition, the levels, the
 * window fade, and now solo. Every one of them was therefore playing tones out
 * of the machine's output while somebody was working on that machine.
 *
 * `--mute-audio` silences the OUTPUT DEVICE only. Decoding, WebAudio graphs,
 * `OfflineAudioContext`, MediaRecorder capture and every `el.muted` / `paused` /
 * `currentTime` fact these specs assert are untouched — which is why it can be
 * unconditional rather than a flag somebody has to remember.
 *
 * IT COVERS CHROMIUM ONLY. WebKit and Firefox have no equivalent launch switch,
 * so the two WebKit projects below still make noise: run them when the machine
 * is not also being used to listen to something.
 */
const MUTED = ['--mute-audio'];

/**
 * SERIAL REMOTE CHECKS KEEP THE VERIFICATION LOAD BOUNDED.
 *
 * Observations — 2026-09-07 (C3720): the owner reported 4 failed / 6 passed
 * when `tests/e2e/solo.spec.ts` ran against Pages with the default parallelism;
 * the failures waited for video elements. The same owner reported that a
 * single-browser manual intake decoded the clip in about two seconds.
 * Retained `biudjcirz.output` records the ten Chromium + Mobile Chrome cases
 * passing with one worker in 19.7s (exit 0). The owner identifies this as the
 * production rerun; that output does not itself print the target URL.
 *
 * Decoder/resource pressure is a hypothesis, not an established cause of the
 * parallel failures: these observations do not isolate network, scheduling or
 * decoder admission. Preserve the failed run as evidence. Serial success is
 * bounded functional coverage, not a concurrent-load guarantee.
 *
 * A remote base URL therefore pins workers to 1 and starts no local dev server.
 * This avoids unnecessary local load and attaching the webServer block to
 * whatever holds :5199 when the tests are aimed at an external deployment.
 */
const REMOTE = /^https?:\/\/(?!localhost|127\.0\.0\.1)/i.test(process.env.COLLAGE_BASE_URL || '');

export default defineConfig({
  // FAILS THE RUN if the URL is not this app. `reuseExistingServer` below
  // attaches to whatever is already listening, so without this a squatter on
  // the port takes the WHOLE suite green against a stranger. See the file.
  globalSetup: './tests/globalSetup.ts',
  testDir: './tests',
  timeout: 30000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI || REMOTE ? 1 : undefined,
  reporter: 'html',
  use: {
    // :5199, NOT :5173. Vite's default port belongs to another project on this
    // machine (Persona 500), and `reuseExistingServer` below means a run that
    // aims at 5173 will happily attach to whatever is already listening there —
    // so the whole suite goes green or red against an app that is not this one,
    // silently, with no error to notice. Every spec here already documents
    // `COLLAGE_BASE_URL=http://localhost:5199/`; the config is what made that an
    // instruction people had to remember instead of the default.
    baseURL: 'http://localhost:5199',
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
      use: {
        ...devices['Desktop Chrome'], channel: 'chromium',
        launchOptions: { args: MUTED },
      },
    },
    {
      name: 'Mobile Chrome',
      use: {
        ...devices['Pixel 5'], channel: 'chromium',
        launchOptions: { args: MUTED },
      },
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
  webServer: REMOTE ? undefined : {
    // `--strictPort` so a busy 5199 FAILS the run instead of quietly sliding to
    // the next free port while `url` waits on one nothing will ever serve.
    command: 'npx vite --port 5199 --strictPort',
    url: 'http://localhost:5199',
    reuseExistingServer: !process.env.CI,
  },
});
