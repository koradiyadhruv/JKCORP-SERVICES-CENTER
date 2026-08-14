// Basic service worker - cache-first for app shell, network-first for API/form submissions if desired.
// NOTE: This is minimal. Adjust cache names and strategies as needed for your site.

const CACHE_NAME = 'jkcorp-shell-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/assets/css/styles.min.css',
  '/manifest.json',
  // add any critical images or icons here
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  const req = event.request;
  // Network-first for navigation (ensures content updates), fallback to cache
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() => caches.match('/index.html'))
    );
    return;
  }

  // For other static assets: try cache first, then network
  event.respondWith(
    caches.match(req).then(cached => cached || fetch(req).then(res => {
      // Optionally cache fetched assets
      return res;
    }))
  );
});
