import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { createHash } from 'node:crypto'
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { join, relative, resolve, sep } from 'node:path'

const OUT_DIR = 'dist'
const SW_FILE = 'sw.js'

const STAMP_TOKEN = "const RAW_STAMP = '__SW_BUILD_STAMP__';"
const PRECACHE_TOKEN = "const RAW_PRECACHE = '__SW_PRECACHE__';"

function listFiles(dir: string, root = dir): string[] {
  const out: string[] = []
  for (const entry of readdirSync(dir)) {
    const abs = join(dir, entry)
    if (statSync(abs).isDirectory()) out.push(...listFiles(abs, root))
    else out.push(relative(root, abs).split(sep).join('/'))
  }
  return out.sort()
}

/**
 * Substitutes the two build-time placeholders in dist/sw.js.
 *
 * WHY THIS EXISTS: public/ files are copied byte-for-byte, so the service
 * worker cannot see anything vite knows -- not `base`, not the content-hashed
 * asset names, not a version. Shipping a cache-first SW with a FROZEN cache
 * name is worse than shipping no SW at all: the first visit pins index.html,
 * and every later deploy hands returning users an index.html that points at
 * deleted hashes. This plugin is what makes the per-release cache bump
 * mechanical instead of a thing someone has to remember.
 *
 * The stamp is a hash of the emitted tree, not a timestamp: identical output
 * yields an identical cache name (no pointless re-download), and any code
 * change reaches it through vite's content-hashed filenames.
 *
 * Fails the build loudly if a placeholder is missing -- a silently un-stamped
 * SW is exactly the failure mode this plugin was written to prevent.
 */
function stampServiceWorker(): Plugin {
  return {
    name: 'stamp-service-worker',
    apply: 'build',
    enforce: 'post',
    closeBundle() {
      const outDir = resolve(process.cwd(), OUT_DIR)
      const swPath = join(outDir, SW_FILE)

      const files = listFiles(outDir).filter((f) => f !== SW_FILE)
      const precache = ['./', ...files.map((f) => './' + f)]

      const stamp = createHash('sha256')
        .update(files.join('\n'))
        .digest('hex')
        .slice(0, 12)

      let src = readFileSync(swPath, 'utf8')
      for (const token of [STAMP_TOKEN, PRECACHE_TOKEN]) {
        if (!src.includes(token)) {
          this.error(
            `[stamp-service-worker] placeholder not found in ${OUT_DIR}/${SW_FILE}: ${token}\n` +
              'public/sw.js and vite.config.ts have drifted apart; the shipped SW would ' +
              'keep a frozen cache name and permanently stale returning users.'
          )
        }
      }
      src = src
        .replace(STAMP_TOKEN, `const RAW_STAMP = ${JSON.stringify(stamp)};`)
        .replace(PRECACHE_TOKEN, `const RAW_PRECACHE = ${JSON.stringify(precache)};`)
      writeFileSync(swPath, src)

      this.info?.(
        `[stamp-service-worker] cache=genart-v3-${stamp} precache=${precache.length} entries`
      )
    },
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), stampServiceWorker()],
  // Relative base. This is what lets the same build work at the site root, at
  // /nested-resonance-memory-archive/collage/, and under `vite preview` without
  // hardcoding the repo name a second time. Do not replace it with an absolute
  // base: it also produces the import.meta.url-relative worker URL that keeps
  // src/workers/render.worker.ts loadable from a subdirectory.
  base: './',
  worker: {
    format: 'es',
  },
  build: {
    outDir: OUT_DIR,
    target: 'esnext'
  }
})
