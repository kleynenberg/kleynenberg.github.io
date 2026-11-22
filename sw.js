/* ==============================================================================
 * INTEGRITY & METADATA HEADER
 * File:           sw.js
 * Project:        Steven Kleynenberg Sovereign Portal — Offline-First Service Worker
 * Host Target:    https://steven.kleynenberg.com (GitHub Pages)
 * Build Version:  v5-2026-11-22
 * Standard:       W3C Service Workers / MDN Service Worker & Cache API
 * Integrity Rule: Zero tracking, deterministic offline shell, runtime PDF/API cache.
 * ============================================================================== */

const CACHE_VERSION = "kleynenberg-sovereign-v6-20261122";
const RUNTIME_CACHE = "kleynenberg-runtime-v5-20261122";

const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./llms.txt",
  "./llms-full.txt",
  "./manifest.webmanifest",
  "./favicon.ico",
  "./apple-touch-icon.png",
  "./icons/icon.svg",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-192-maskable.png",
  "./icons/icon-512-maskable.png",
  "./papers/",
  "./papers/index.html",
  "./papers/llms.txt",
  "./papers/llms-full.txt",
  "./papers/De-Nederlandsche-Courant-Steven-Kleynenberg-2026-11-19.pdf",
  "./kso/",
  "./kso/index.html",
  "./kso/llms.txt",
  "./kso/llms-full.txt",
  "./kso/KSO_logo.jpg",
  "./pp/",
  "./pp/index.html",
  "./pp/llms.txt",
  "./pp/llms-full.txt",
  "./kp/",
  "./kp/index.html",
  "./kp/llms.txt",
  "./kp/llms-full.txt",
  "./kp/logo.svg",
  "./tkp/",
  "./tkp/index.html",
  "./tkp/llms.txt",
  "./tkp/llms-full.txt",
  "./tkp/tkp_logo.svg",
  './papers/font_taxonomy.pdf',
  './papers/font_taxonomy.tex',
  './CITATION.cff'
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(async (cache) => {
      for (const url of PRECACHE_URLS) {
        try {
          await cache.add(url);
        } catch (err) {
          console.warn("[Kleynenberg SW] Precache skipped optional asset:", url);
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

  if (url.hostname === "github.com") {
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
