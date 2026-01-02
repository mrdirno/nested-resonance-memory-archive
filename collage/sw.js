/**
 * SERVICE WORKER
 * Section 18: Advanced PWA Architecture
 *
 * Features:
 * - Offline-first caching strategy
 * - Periodic Background Sync for template updates
 * - Push notifications for export completion
 * - Compute sharing via message channels
 */

const CACHE_NAME = 'smart-collage-v3';
// Don't cache static assets - let the browser handle them
// This avoids path issues with subdirectory deployments
const STATIC_ASSETS = [];

// External dependencies to cache
const CDN_ASSETS = [
  'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.11.0/dist/tf.min.js',
  'https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js',
];

// Template/layout presets endpoint (for periodic sync)
const TEMPLATES_ENDPOINT = '/api/templates';

// ============================================================================
// INSTALL EVENT
// ============================================================================

self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');

  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      console.log('[SW] Caching static assets');

      // Cache static assets
      await cache.addAll(STATIC_ASSETS);

      // Try to cache CDN assets (may fail due to CORS)
      for (const url of CDN_ASSETS) {
        try {
          await cache.add(url);
          console.log(`[SW] Cached: ${url}`);
        } catch (e) {
          console.warn(`[SW] Failed to cache: ${url}`);
        }
      }

      console.log('[SW] Installation complete');
    })
  );

  // Activate immediately
  self.skipWaiting();
});

// ============================================================================
// ACTIVATE EVENT
// ============================================================================

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');

  event.waitUntil(
    (async () => {
      // Clean old caches
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );

      // Take control immediately
      await self.clients.claim();

      // Register for periodic sync if supported
      if ('periodicSync' in self.registration) {
        try {
          await self.registration.periodicSync.register('template-sync', {
            minInterval: 24 * 60 * 60 * 1000, // 24 hours
          });
          console.log('[SW] Periodic sync registered');
        } catch (e) {
          console.warn('[SW] Periodic sync not available:', e);
        }
      }

      console.log('[SW] Activation complete');
    })()
  );
});

// ============================================================================
// FETCH EVENT (Stale-While-Revalidate)
// ============================================================================

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) return;

  // Network-first strategy for app files to avoid stale cache issues
  event.respondWith(
    (async () => {
      try {
        // Always try network first
        const networkResponse = await fetch(request);

        // Cache successful responses
        if (networkResponse.ok) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(request, networkResponse.clone());
        }

        return networkResponse;
      } catch (e) {
        // Network failed, try cache
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(request);

        if (cachedResponse) {
          return cachedResponse;
        }

        // No cache either
        return new Response('Offline', { status: 503 });
      }
    })()
  );
});

// ============================================================================
// PERIODIC BACKGROUND SYNC
// ============================================================================

self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'template-sync') {
    console.log('[SW] Periodic sync: template-sync');

    event.waitUntil(
      (async () => {
        try {
          // Fetch new templates
          const response = await fetch(TEMPLATES_ENDPOINT);
          if (response.ok) {
            const templates = await response.json();

            // Store in IndexedDB or cache
            const cache = await caches.open(CACHE_NAME);
            await cache.put(
              new Request('/templates.json'),
              new Response(JSON.stringify(templates))
            );

            console.log('[SW] Templates updated:', templates.length);

            // Notify clients
            const clients = await self.clients.matchAll();
            for (const client of clients) {
              client.postMessage({
                type: 'TEMPLATES_UPDATED',
                count: templates.length,
              });
            }
          }
        } catch (e) {
          console.warn('[SW] Template sync failed:', e);
        }
      })()
    );
  }
});

// ============================================================================
// MESSAGE HANDLER (Compute Sharing)
// ============================================================================

self.addEventListener('message', (event) => {
  const { type, payload } = event.data || {};

  switch (type) {
    case 'COMPUTE_LAYOUT':
      // Offload layout computation to service worker
      handleComputeLayout(event, payload);
      break;

    case 'RENDER_TILE':
      // Render a tile of large image in background
      handleRenderTile(event, payload);
      break;

    case 'SKIP_WAITING':
      self.skipWaiting();
      break;

    case 'GET_CACHE_STATUS':
      handleCacheStatus(event);
      break;
  }
});

/**
 * Compute layout in service worker thread
 */
function handleComputeLayout(event, payload) {
  const { width, height, count, seed, mode, gutter } = payload;

  const createRng = (s) => {
    let t = s + 0x6D2B79F5;
    return () => {
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  const rng = createRng(seed);
  const gap = Math.max(2, width * (gutter || 0.005));

  // BSP layout (minimal mode)
  let nodes = [{ x: 0, y: 0, w: width, h: height }];
  let safety = 0;

  while (nodes.length < count && safety < 1000) {
    safety++;
    let idx = -1, maxScore = -1;

    for (let i = 0; i < nodes.length; i++) {
      const score = nodes[i].w * nodes[i].h * (0.8 + rng() * 0.4);
      if (score > maxScore) {
        maxScore = score;
        idx = i;
      }
    }

    if (idx === -1) break;

    const p = nodes[idx];
    nodes.splice(idx, 1);

    const isVert = p.w > p.h;
    const splitBase = 0.382 + rng() * 0.236;

    if (isVert) {
      const w1 = p.w * splitBase;
      nodes.push(
        { x: p.x, y: p.y, w: w1, h: p.h },
        { x: p.x + w1, y: p.y, w: p.w - w1, h: p.h }
      );
    } else {
      const h1 = p.h * splitBase;
      nodes.push(
        { x: p.x, y: p.y, w: p.w, h: h1 },
        { x: p.x, y: p.y + h1, w: p.w, h: p.h - h1 }
      );
    }
  }

  const result = nodes.map((n, i) => ({
    id: `cell-${i}`,
    path: [
      { x: n.x + gap, y: n.y + gap },
      { x: n.x + n.w - gap, y: n.y + gap },
      { x: n.x + n.w - gap, y: n.y + n.h - gap },
      { x: n.x + gap, y: n.y + n.h - gap },
    ],
    bounds: { x: n.x + gap, y: n.y + gap, w: n.w - gap * 2, h: n.h - gap * 2 },
  }));

  event.source.postMessage({
    type: 'LAYOUT_RESULT',
    payload: result,
  });
}

/**
 * Render a tile for large image export
 */
async function handleRenderTile(event, payload) {
  const { tileIndex, totalTiles, tileWidth, tileHeight, offsetX, offsetY } = payload;

  // In a real implementation, we'd use OffscreenCanvas here
  // For now, just acknowledge the request
  event.source.postMessage({
    type: 'TILE_READY',
    payload: {
      tileIndex,
      totalTiles,
      status: 'acknowledged',
    },
  });
}

/**
 * Report cache status
 */
async function handleCacheStatus(event) {
  const cache = await caches.open(CACHE_NAME);
  const keys = await cache.keys();

  let totalSize = 0;
  for (const request of keys) {
    const response = await cache.match(request);
    if (response) {
      const blob = await response.blob();
      totalSize += blob.size;
    }
  }

  event.source.postMessage({
    type: 'CACHE_STATUS',
    payload: {
      entries: keys.length,
      sizeBytes: totalSize,
      sizeMB: (totalSize / (1024 * 1024)).toFixed(2),
    },
  });
}

// ============================================================================
// PUSH NOTIFICATIONS (Export Complete)
// ============================================================================

self.addEventListener('push', (event) => {
  const data = event.data?.json() || {};

  const options = {
    body: data.body || 'Your collage is ready!',
    icon: '/icons/icon-192.png',
    badge: '/icons/badge-72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/',
    },
    actions: [
      { action: 'download', title: 'Download' },
      { action: 'dismiss', title: 'Dismiss' },
    ],
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'Smart Collage', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'download') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  }
});

console.log('[SW] Service Worker loaded');
