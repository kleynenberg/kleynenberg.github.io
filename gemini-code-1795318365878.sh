# ==============================================================================
# INTEGRITY HEADER - GEMINI AI
# Script: update_pwa_manifest_and_sw.sh
# Target: /home/steve/gemini/github.io/manifest.webmanifest & sw.js
# Purpose: Align PWA shortcuts, Spartan palette & v5 service worker precache
# ==============================================================================

cd /home/steve/gemini/github.io && \
cat << 'EOF' > manifest.webmanifest
{
  "_integrity": "Steven Kleynenberg Sovereign Portal W3C Web Application Manifest v2.0.0 — Zero-Tracker PWA",
  "name": "Steven Kleynenberg — Sovereign AI, Systems & Publishing Portal",
  "short_name": "Kleynenberg",
  "description": "Artificial Intelligence, Systems Architecture (KSO), Academic & Patent Archive, Independent Publishing (KP), and Broadcast (TKP) — Delft, The Netherlands.",
  "id": "/",
  "start_url": "./index.html?source=pwa",
  "scope": "./",
  "display": "standalone",
  "display_override": [
    "window-controls-overlay",
    "standalone",
    "minimal-ui"
  ],
  "orientation": "any",
  "background_color": "#ffffff",
  "theme_color": "#111111",
  "lang": "en",
  "dir": "ltr",
  "categories": [
    "technology",
    "science",
    "education",
    "developer"
  ],
  "icons": [
    {
      "src": "./icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "./icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "./icons/icon-192-maskable.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "./icons/icon-512-maskable.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "./icons/icon.svg",
      "sizes": "any",
      "type": "image/svg+xml",
      "purpose": "any"
    }
  ],
  "shortcuts": [
    {
      "name": "Papers, Patents & Broadsheet",
      "short_name": "Papers",
      "description": "Peer-reviewed neural network papers (MetaNet, BSP400, MEDUSA), WO 2014/003543 A1 & De Nederlandsche Courant",
      "url": "./papers/index.html",
      "icons": [
        {
          "src": "./icons/icon-192.png",
          "sizes": "192x192",
          "type": "image/png"
        }
      ]
    },
    {
      "name": "KSO — ITEA 4 SME Profile",
      "short_name": "KSO",
      "description": "Kleynenberg Software Ontwikkeling — AI & Systems Architecture",
      "url": "./kso/index.html",
      "icons": [
        {
          "src": "./icons/icon-192.png",
          "sizes": "192x192",
          "type": "image/png"
        }
      ]
    },
    {
      "name": "Personal Projects Workbench",
      "short_name": "PP Workbench",
      "description": "AudioTap v18a WebAudio DSP, Local Project Trawler & Sovereign Tooling",
      "url": "./pp/index.html",
      "icons": [
        {
          "src": "./icons/icon-192.png",
          "sizes": "192x192",
          "type": "image/png"
        }
      ]
    },
    {
      "name": "Kleynenberg Publishers (KP)",
      "short_name": "Publishers",
      "description": "Books, monographs, broadsheets and algorithmic media",
      "url": "./kp/index.html",
      "icons": [
        {
          "src": "./icons/icon-192.png",
          "sizes": "192x192",
          "type": "image/png"
        }
      ]
    },
    {
      "name": "The Kleynenberg Perspective",
      "short_name": "TKP Podcast",
      "description": "Pure signal. Zero static. Sovereign audio broadcast",
      "url": "./tkp/index.html",
      "icons": [
        {
          "src": "./icons/icon-192.png",
          "sizes": "192x192",
          "type": "image/png"
        }
      ]
    }
  ]
}
EOF

cat << 'EOF' > sw.js
/* ==============================================================================
 * INTEGRITY & METADATA HEADER
 * File:           sw.js
 * Project:        Steven Kleynenberg Sovereign Portal — Offline-First Service Worker
 * Host Target:    https://steven.kleynenberg.com (GitHub Pages)
 * Build Version:  v5-2026-11-22
 * Standard:       W3C Service Workers / MDN Service Worker & Cache API
 * Integrity Rule: Zero tracking, deterministic offline shell, runtime PDF/API cache.
 * ============================================================================== */

const CACHE_VERSION = "kleynenberg-sovereign-v5-20261122";
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
  "./kp/logo_2.svg",
  "./tkp/",
  "./tkp/index.html",
  "./tkp/llms.txt",
  "./tkp/llms-full.txt",
  "./tkp/tkp_logo.svg"
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
EOF

git add manifest.webmanifest sw.js && \
git commit -m "Update manifest.webmanifest shortcuts and bump service worker sw.js to v5" && \
git push