/* ==============================================================================
 * INTEGRITY & METADATA HEADER
 * File:          app.js
 * Project:       Project UnLinked — Sovereign Static PWA Runtime
 * Host Target:   https://kleynenberg.github.io (GitHub Pages)
 * Standard:      Vanilla ES7+ / MDN Web Docs Service Worker & Fetch APIs
 * Integrity Rule: Zero tracking, zero cookies, deterministic runtime toggles.
 * ============================================================================== */

(() => {
  "use strict";

  const rootEl = document.documentElement;
  const themeBtn = document.getElementById("theme-toggle-btn");
  const slotsBtn = document.getElementById("toggle-slots-btn");
  const installBtn = document.getElementById("install-pwa-btn");
  const pwaBadge = document.getElementById("pwa-status-badge");
  const searchInput = document.getElementById("global-search");

  let deferredInstallPrompt = null;
  let slotsVisible = false;

  function applyTheme(theme) {
    const resolved = theme === "future-dark" ? "future-dark" : "daylight";
    rootEl.setAttribute("data-theme", resolved);
    if (themeBtn) {
      themeBtn.textContent = resolved === "future-dark" ? "Daylight glass" : "Future dark";
    }
    try {
      localStorage.setItem("unlinked_theme", resolved);
    } catch (_) {}
  }

  try {
    const savedTheme = localStorage.getItem("unlinked_theme");
    if (savedTheme) applyTheme(savedTheme);
  } catch (_) {}

  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const current = rootEl.getAttribute("data-theme");
      applyTheme(current === "future-dark" ? "daylight" : "future-dark");
    });
  }

  function updatePlaceholderVisibility(show) {
    slotsVisible = Boolean(show);
    document.querySelectorAll("[data-placeholder='true']").forEach((el) => {
      el.hidden = !slotsVisible;
    });
    if (slotsBtn) {
      slotsBtn.setAttribute("aria-pressed", String(slotsVisible));
      slotsBtn.textContent = slotsVisible ? "Slots: on" : "Slots: off";
    }
  }

  if (slotsBtn) {
    slotsBtn.addEventListener("click", () => {
      updatePlaceholderVisibility(!slotsVisible);
    });
  }

  async function syncPortalConfig() {
    try {
      const resp = await fetch("./portal.json", { cache: "no-cache" });
      if (!resp.ok) return;
      const cfg = await resp.json();

      if (cfg.sections) {
        Object.entries(cfg.sections).forEach(([secKey, secVal]) => {
          if (secVal && secVal.enabled === false) {
            document.querySelectorAll(`[data-feature-id="${secKey}"]`).forEach((el) => {
              el.hidden = true;
            });
          }
        });
      }

      const toggleMap = new Map();
      const collect = (items) => {
        if (!Array.isArray(items)) return;
        items.forEach((item) => {
          if (item && item.id) toggleMap.set(item.id, Boolean(item.enabled));
        });
      };

      collect(cfg.hero?.bio_links);
      collect(cfg.featured_ctas);
      collect(cfg.project_unlinked_spotlight?.pillars_of_design);
      collect(cfg.pillar_1_timeline?.milestones);
      collect(cfg.scientific_papers?.entries);
      collect(cfg.pillar_2_sandbox?.projects);
      collect(cfg.ksa_roadmap?.codenames);
      collect(cfg.pillar_3_media?.ecosystems);

      toggleMap.forEach((enabled, featureId) => {
        document.querySelectorAll(`[data-feature-id="${featureId}"]`).forEach((el) => {
          if (!enabled) {
            el.hidden = true;
          } else if (el.dataset.placeholder !== "true") {
            el.hidden = false;
          }
        });
      });

      if (cfg.sections?.archival_slots?.enabled) {
        updatePlaceholderVisibility(true);
      }

      if (cfg.github_repos) {
        loadGitHubRepositories(cfg.github_repos);
      }
    } catch (err) {
      console.warn("[UnLinked] portal.json runtime sync skipped:", err);
      loadGitHubRepositories({
        username: "kleynenberg",
        api_endpoint: "https://api.github.com/users/kleynenberg/repos?sort=updated&per_page=100",
        cache_ttl_seconds: 900,
        featured_repo_names: ["public-test-repos", "kleynenberg.github.io"],
        fallback_repos: [
          {
            name: "public-test-repos",
            html_url: "https://github.com/kleynenberg/public-test-repos/",
            description: "Public experimental repository collection and verification sandbox.",
            language: "Shell / C / Web",
          },
        ],
      });
    }
  }

  function updateNetworkBadge() {
    if (!pwaBadge) return;
    pwaBadge.textContent = navigator.onLine ? "PWA ready · online" : "PWA offline cached";
  }

  window.addEventListener("online", updateNetworkBadge);
  window.addEventListener("offline", updateNetworkBadge);
  updateNetworkBadge();

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("./sw.js", { scope: "./" })
        .then(() => {
          if (pwaBadge && navigator.onLine) {
            pwaBadge.textContent = "PWA offline ready";
          }
        })
        .catch((err) => console.warn("[UnLinked] Service Worker registration failed:", err));
    });
  }

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    if (installBtn) installBtn.hidden = false;
  });

  if (installBtn) {
    installBtn.addEventListener("click", async () => {
      if (!deferredInstallPrompt) return;
      deferredInstallPrompt.prompt();
      await deferredInstallPrompt.userChoice;
      deferredInstallPrompt = null;
      installBtn.hidden = true;
    });
  }

  window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
    if (installBtn) installBtn.hidden = true;
    if (pwaBadge) pwaBadge.textContent = "Installed standalone PWA";
  });

  function bindFilterGroup(buttonAttr, targetAttr) {
    const buttons = document.querySelectorAll(`[${buttonAttr}]`);
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const value = btn.getAttribute(buttonAttr);
        buttons.forEach((b) => b.classList.toggle("is-active", b === btn));
        document.querySelectorAll(`[${targetAttr}]`).forEach((card) => {
          if (card.dataset.placeholder === "true" && !slotsVisible) {
            card.hidden = true;
            return;
          }
          const matches = value === "all" || card.getAttribute(targetAttr) === value;
          card.hidden = !matches;
        });
      });
    });
  }

  bindFilterGroup("data-era-filter", "data-era");
  bindFilterGroup("data-domain-filter", "data-domain");
  bindFilterGroup("data-ksa-filter", "data-ksa-series");

  document.querySelectorAll(".copy-bibtex-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const bibtex = btn.getAttribute("data-bibtex") || "";
      if (!bibtex) return;
      const orig = btn.textContent;
      try {
        await navigator.clipboard.writeText(bibtex);
        btn.textContent = "Copied BibTeX";
      } catch (_) {
        btn.textContent = "Clipboard unavailable";
      }
      setTimeout(() => {
        btn.textContent = orig;
      }, 1800);
    });
  });

  function renderGitHubRepos(repos, featuredNames) {
    const grid = document.getElementById("github-repos-grid");
    const langBar = document.getElementById("github-lang-filters");
    if (!grid || !langBar) return;

    const featuredSet = new Set((featuredNames || []).map((n) => n.toLowerCase()));
    const sorted = [...repos].sort((a, b) => {
      const aFeat = featuredSet.has((a.name || "").toLowerCase()) ? 1 : 0;
      const bFeat = featuredSet.has((b.name || "").toLowerCase()) ? 1 : 0;
      if (aFeat !== bFeat) return bFeat - aFeat;
      return String(b.updated_at || "").localeCompare(String(a.updated_at || ""));
    });

    const languages = new Set();
    sorted.forEach((r) => {
      if (r.language) languages.add(r.language);
    });

    langBar.innerHTML = '<button class="filter-chip is-active" type="button" data-repo-lang="all">All languages</button>';
    languages.forEach((lang) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "filter-chip";
      chip.setAttribute("data-repo-lang", lang);
      chip.textContent = lang;
      langBar.appendChild(chip);
    });

    grid.innerHTML = "";
    sorted.forEach((repo) => {
      const isFeat = featuredSet.has((repo.name || "").toLowerCase());
      const card = document.createElement("article");
      card.className = `repo-card${isFeat ? " is-featured-repo" : ""}`;
      card.setAttribute("data-repo-language", repo.language || "Other");

      const topRow = document.createElement("div");
      topRow.className = "repo-meta-row";

      const title = document.createElement("h3");
      const link = document.createElement("a");
      link.href = repo.html_url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = `${repo.name} ↗`;
      title.appendChild(link);
      topRow.appendChild(title);

      if (repo.language) {
        const langBadge = document.createElement("span");
        langBadge.className = "badge-subtle";
        langBadge.textContent = repo.language;
        topRow.appendChild(langBadge);
      }

      const desc = document.createElement("p");
      desc.textContent = repo.description || "Public source repository under github.com/kleynenberg.";

      const foot = document.createElement("div");
      foot.className = "repo-meta-row";
      const stats = document.createElement("span");
      stats.className = "location-tag";
      const stars = typeof repo.stargazers_count === "number" ? `★ ${repo.stargazers_count} · ` : "";
      const updated = repo.updated_at ? `Updated ${repo.updated_at.slice(0, 10)}` : "Public repository";
      stats.textContent = `${stars}${updated}`;
      foot.appendChild(stats);

      if (isFeat) {
        const featTag = document.createElement("span");
        featTag.className = "badge-accent";
        featTag.textContent = "Featured";
        foot.appendChild(featTag);
      }

      card.appendChild(topRow);
      card.appendChild(desc);
      card.appendChild(foot);
      grid.appendChild(card);
    });

    langBar.querySelectorAll("[data-repo-lang]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const lang = btn.getAttribute("data-repo-lang");
        langBar.querySelectorAll("[data-repo-lang]").forEach((b) => b.classList.toggle("is-active", b === btn));
        grid.querySelectorAll(".repo-card").forEach((card) => {
          card.hidden = lang !== "all" && card.getAttribute("data-repo-language") !== lang;
        });
      });
    });
  }

  async function loadGitHubRepositories(ghCfg) {
    const statusEl = document.getElementById("github-sync-status");
    const cacheKey = `unlinked_gh_repos_${ghCfg.username || "kleynenberg"}`;
    const ttlMs = (ghCfg.cache_ttl_seconds || 900) * 1000;

    try {
      const cachedRaw = sessionStorage.getItem(cacheKey);
      if (cachedRaw) {
        const cached = JSON.parse(cachedRaw);
        if (Date.now() - cached.timestamp < ttlMs && Array.isArray(cached.repos)) {
          renderGitHubRepos(cached.repos, ghCfg.featured_repo_names);
          if (statusEl) statusEl.textContent = `${cached.repos.length} public repos (cached)`;
          return;
        }
      }
    } catch (_) {}

    try {
      const resp = await fetch(ghCfg.api_endpoint, {
        headers: { Accept: "application/vnd.github+json" },
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const repos = await resp.json();
      if (!Array.isArray(repos)) throw new Error("Unexpected GitHub API response");

      try {
        sessionStorage.setItem(cacheKey, JSON.stringify({ timestamp: Date.now(), repos }));
      } catch (_) {}

      renderGitHubRepos(repos, ghCfg.featured_repo_names);
      if (statusEl) statusEl.textContent = `${repos.length} public repos · live`;
    } catch (err) {
      console.warn("[UnLinked] GitHub API fallback activated:", err);
      const fallback = ghCfg.fallback_repos || [];
      renderGitHubRepos(fallback, ghCfg.featured_repo_names);
      if (statusEl) statusEl.textContent = "Offline / rate-limit fallback";
    }
  }

  if (searchInput) {
    document.addEventListener("keydown", (e) => {
      if (e.key === "/" && document.activeElement !== searchInput && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
        e.preventDefault();
        searchInput.focus();
      }
    });

    searchInput.addEventListener("input", () => {
      const q = searchInput.value.trim().toLowerCase();
      const searchableCards = document.querySelectorAll(
        ".timeline-card, .paper-card, .repo-card, .sandbox-card, .ksa-card, .media-card"
      );
      searchableCards.forEach((card) => {
        if (card.dataset.placeholder === "true" && !slotsVisible) {
          card.hidden = true;
          return;
        }
        if (!q) {
          card.hidden = false;
          return;
        }
        const hay = card.textContent.toLowerCase();
        card.hidden = !hay.includes(q);
      });
    });
  }

  syncPortalConfig();
})();
