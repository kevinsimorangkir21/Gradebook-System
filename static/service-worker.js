const CACHE_NAME = 'gradebook-cache-v1';
const CACHE_URLS = [
  '/', 
  '/static/style.css', 
  '/static/script.js'
];

// Install event: caching essential resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CACHE_URLS);
    })
  );
});

// Activate event: clean up old caches if needed
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName); // Remove old caches
          }
        })
      );
    })
  );
});

// Fetch event: respond with cached resources or fetch from the network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // If there's a cached response, return it; otherwise, fetch from the network
      return cachedResponse || fetch(event.request).then((response) => {
        // If we got a valid response, clone it and update the cache
        if (response && response.status === 200 && response.type === 'basic') {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      });
    }).catch(() => {
      // Handle errors (optional)
      console.error('Fetching failed; returning offline page instead.');
      // You could return a fallback offline page if desired
    })
  );
});
