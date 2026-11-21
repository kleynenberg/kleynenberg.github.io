/* ==============================================================================
 * INTEGRITY & METADATA HEADER
 * File:           sw.js
 * Project:        Project UnLinked — Offline-First Service Worker
 * Host Target:    https://kleynenberg.com (GitHub Pages)
 * Build Hash:     583016a9d6a9-v4
 * Standard:       W3C Service Workers / MDN Service Worker & Cache API
 * Integrity Rule: Zero tracking, deterministic offline shell, runtime PDF/API cache.
 * ============================================================================== */

const CACHE_VERSION = "unlinked-sovereign-v4-583016a9d6a9";
const RUNTIME_CACHE = "unlinked-runtime-v4-583016a9d6a9";

const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./krant.html",
  "./papers/De-Nederlandsche-Courant-Steven-Kleynenberg-2026-11-19.pdf",
  "./manifest.webmanifest",
  "./llms.txt",
  "./llms-full.txt",
  "./favicon.ico",
  "./apple-touch-icon.png",
  "./google_logo_image_of_steven_kleynenberg_at_gmail_dot_com.svg",
  "./icons/icon.svg",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-192-maskable.png",
  "./icons/icon-512-maskable.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(async (cache) => {
      for (const url of PRECACHE_URLS) {
        try {
          await cache.add(url);
        } catch (err) {
          console.warn("[UnLinked SW] Precache skipped optional asset:", url);
        }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION && key !== RUNTIME_CACHE)
          .map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);

  if (url.hostname === "://github.com") {
    event.respondWith(
      fetch(request)
        .then((networkResp) => {
          if (networkResp && networkResp.ok) {
            const clone = networkResp.clone();
            caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, clone));
          }
          return networkResp;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(request).then((cachedResp) => {
        const networkFetch = fetch(request)
          .then((networkResp) => {
            if (networkResp && networkResp.ok) {
              const clone = networkResp.clone();
              caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
            }
            return networkResp;
          })
          .catch(() => cachedResp);

        return cachedResp || networkFetch;
      })
    );
  }
});
