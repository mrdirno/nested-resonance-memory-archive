// public/sw.js
// Service worker for the Smart Crop GenArt Studio.
//
// DEPLOY CONTEXT: this app is served from a SUBDIRECTORY of a GitHub Pages
// project site (https://<user>.github.io/<repo>/collage/). Files in public/ are
// copied byte-for-byte by vite -- `base: './'` does NOT rewrite them. So every
// URL in this file must be relative to the SW script itself. A root-anchored
// index.html path resolves to the origin root, which 404s here, and
// cache.addAll() is atomic, so one bad entry used to kill install() outright.
//
// The two placeholders below are substituted at build time by the
// `stamp-service-worker` plugin in vite.config.ts:
//   __SW_BUILD_STAMP__ -> a hash of the emitted dist tree (changes iff the
//                         build changes, so the cache name changes per release)
//   __SW_PRECACHE__    -> the real list of emitted files, relative to this file
// In `vite dev` the placeholders stay literal; the fallbacks below keep the SW
// valid and harmless there.

const RAW_STAMP = '__SW_BUILD_STAMP__';
const RAW_PRECACHE = '__SW_PRECACHE__';

const CACHE_PREFIX = 'genart-v3-';
const CACHE_NAME = CACHE_PREFIX + (RAW_STAMP.indexOf('__SW_') === 0 ? 'dev' : RAW_STAMP);

// './' resolves against the SW script URL -> the app directory, never the origin
// root. A SW can only claim a scope at or below its own directory, so this is
// structurally incapable of intercepting a sibling app.
const FALLBACK_PRECACHE = ['./', './index.html', './manifest.json', './favicon.svg'];
const PRECACHE = Array.isArray(RAW_PRECACHE) ? RAW_PRECACHE : FALLBACK_PRECACHE;

const SHELL_URL = './index.html';

// Vite emits content-hashed filenames into assets/. A hashed name is immutable,
// so cache-first is safe there and only there.
function isImmutableAsset(url) {
  return url.pathname.indexOf(new URL('./assets/', self.location).pathname) === 0;
}

function isSameOrigin(url) {
  return url.origin === self.location.origin;
}

// ---------------------------------------------------------------- install ---
// Best-effort precache: cache.addAll() rejects the WHOLE install if any single
// entry fails, which would leave the app with no service worker at all. Cache
// each entry independently so a transient failure costs one file, not the SW.
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      Promise.all(
        PRECACHE.map((url) =>
          cache.add(new Request(url, { cache: 'reload' })).catch(() => undefined)
        )
      )
    )
  );
  // NOTE: deliberately NO skipWaiting(). Taking over a page that is already
  // running the previous build's chunks is the classic way to hand a live tab a
  // cache that no longer contains the chunks it is about to lazy-load. The new
  // SW activates on the next navigation once old tabs are gone; until then the
  // old SW serves navigations network-first, so content is never stale anyway.
});

// --------------------------------------------------------------- activate ---
// Evict every previous generation of OUR cache. Without this the old code's
// frozen CACHE_NAME meant a first visit pinned index.html forever, and every
// later deploy handed returning users an index.html pointing at deleted hashes:
// a white screen no reload could clear.
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((k) => k.indexOf(CACHE_PREFIX) === 0 && k !== CACHE_NAME)
            .map((k) => caches.delete(k))
        )
      )
      .then(() => self.clients.claim())
  );
});

// ------------------------------------------------------------------ fetch ---
self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Never touch non-GET (no cache semantics) ...
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // ... and never touch cross-origin. The app pulls tfjs + blazeface from
  // jsdelivr at runtime; those must go straight to the network, opaque and
  // uncached, or a stale/opaque copy can silently break smart-crop.
  if (!isSameOrigin(url)) return;

  // Navigations: NETWORK-FIRST. The app shell must never be pinned -- this is
  // the single rule that makes a bad deploy recoverable with a reload.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(SHELL_URL, copy)).catch(() => {});
          return res;
        })
        .catch(() =>
          caches
            .match(SHELL_URL, { cacheName: CACHE_NAME })
            .then((hit) => hit || caches.match(SHELL_URL))
            .then(
              (hit) =>
                hit ||
                new Response('<h1>Offline</h1>', {
                  status: 503,
                  headers: { 'Content-Type': 'text/html; charset=utf-8' }
                })
            )
        )
    );
    return;
  }

  // Content-hashed assets: cache-first (the hash guarantees freshness).
  if (isImmutableAsset(url)) {
    event.respondWith(
      caches.match(req).then(
        (hit) =>
          hit ||
          fetch(req).then((res) => {
            if (res && res.ok) {
              const copy = res.clone();
              caches.open(CACHE_NAME).then((c) => c.put(req, copy)).catch(() => {});
            }
            return res;
          })
      )
    );
    return;
  }

  // Everything else same-origin (manifest, favicon, unhashed extras):
  // stale-while-revalidate.
  event.respondWith(
    caches.match(req).then((hit) => {
      const network = fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(req, copy)).catch(() => {});
          }
          return res;
        })
        .catch(() => hit);
      return hit || network;
    })
  );
});

// ---------------------------------------------------------------- message ---
// Lets the page opt into an immediate takeover ("Update now" affordance) without
// making skipWaiting the unconditional default.
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});

// Periodic Sync for Templates (Experimental)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'update-templates') {
    // event.waitUntil(fetchAndCacheTemplates());
    console.log('Periodic sync: Updating templates...');
  }
});
