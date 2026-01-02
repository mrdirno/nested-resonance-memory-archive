// public/sw.js
// Service Worker for Offline Support & Periodic Sync

const CACHE_NAME = 'genart-v2-cache';
const MODEL_CACHE = 'genart-model-cache';

const ASSETS = [
  './',
  './index.html',
  './manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  
  // 1. Cache AI Models (CDN)
  if (url.hostname === 'cdn.jsdelivr.net') {
     e.respondWith(
       caches.open(MODEL_CACHE).then(async (cache) => {
         const cached = await cache.match(e.request);
         if (cached) return cached;
         try {
             const net = await fetch(e.request);
             if (net.status === 200) {
                 cache.put(e.request, net.clone());
             }
             return net;
         } catch (err) {
             console.error("Model fetch failed", err);
             return new Response("Network error", { status: 408 });
         }
       })
     );
     return;
  }

  // 2. Standard App Assets
  e.respondWith(
    caches.match(e.request).then((res) => res || fetch(e.request))
  );
});

// Periodic Sync for Templates
self.addEventListener('periodicsync', (e) => {
  if (e.tag === 'update-templates') {
    console.log("Periodic sync: Updating templates...");
  }
});