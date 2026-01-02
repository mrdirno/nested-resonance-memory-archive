// public/sw.js
// Service Worker for Offline Support & Periodic Sync

const CACHE_NAME = 'genart-v2-cache';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((res) => res || fetch(e.request))
  );
});

// Periodic Sync for Templates (Experimental)
self.addEventListener('periodicsync', (e) => {
  if (e.tag === 'update-templates') {
    // e.waitUntil(fetchAndCacheTemplates());
    console.log("Periodic sync: Updating templates...");
  }
});
