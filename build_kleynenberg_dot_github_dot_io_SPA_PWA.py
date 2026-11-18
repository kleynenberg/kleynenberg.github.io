#!/usr/bin/env python3
# ==============================================================================
# INTEGRITY & METADATA HEADER
# File:          build_kleynenberg_dot_github_dot_io_SPA_PWA.py
# Project:       Project UnLinked — Sovereign Static SPA / PWA Compiler
# Host Target:   https://kleynenberg.github.io (GitHub Pages)
# Workstation:   hp.kleynenberg.net (Fedora Linux / JOE Editor)
# Author:        Steven (S.E.) Kleynenberg
# Version:       1.0.0
# Standards:     HTML5, CSS3, ES7+, W3C Web App Manifest, Service Worker API,
#                Schema.org JSON-LD 1.1, Open Graph Protocol, Dublin Core, llms.txt
# License/Legal: Independent Sovereign Portal & Parody-Exception Implementation
#                (Dutch Copyright Act Art. 18b / EU InfoSoc Directive 2001/29/EC)
# Integrity Rule: Zero dummy data, zero trackers, zero third-party runtime CDNs,
#                zero mandatory third-party Python dependencies (built-in YAML 1.2
#                subset parser + optional PyYAML acceleration).
# ==============================================================================

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml  # Optional PyYAML (python3-pyyaml on Fedora)
except ImportError:
    yaml = None


def esc(val: object) -> str:
    return html.escape(str(val or ""), quote=True)


# ------------------------------------------------------------------------------
# Zero-Dependency Pure-Python YAML 1.2 Subset Parser (Fallback when PyYAML absent)
# Supports mappings, sequences, inline arrays [...], inline maps {...},
# literal block scalars (|), booleans, integers, and quoted/unquoted strings.
# ------------------------------------------------------------------------------
def _strip_yaml_comment(line: str) -> str:
    in_single = False
    in_double = False
    for idx, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single and (idx == 0 or line[idx - 1] != "\\"):
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if idx == 0 or line[idx - 1].isspace():
                return line[:idx].rstrip()
    return line.rstrip()


def _split_top_level(text: str, sep: str = ",") -> list:
    parts = []
    buf = []
    depth_sq = 0
    depth_cu = 0
    in_single = False
    in_double = False
    for idx, ch in enumerate(text):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single and (idx == 0 or text[idx - 1] != "\\"):
            in_double = not in_double
        elif not in_single and not in_double:
            if ch == "[":
                depth_sq += 1
            elif ch == "]":
                depth_sq -= 1
            elif ch == "{":
                depth_cu += 1
            elif ch == "}":
                depth_cu -= 1
            elif ch == sep and depth_sq == 0 and depth_cu == 0:
                parts.append("".join(buf).strip())
                buf = []
                continue
        buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return [p for p in parts if p != ""]


def _parse_yaml_scalar(raw: str):
    val = raw.strip()
    if val == "" or val in ("null", "Null", "NULL", "~"):
        return None
    if val in ("true", "True", "TRUE"):
        return True
    if val in ("false", "False", "FALSE"):
        return False
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        inner = val[1:-1]
        if val.startswith('"'):
            inner = inner.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
        else:
            inner = inner.replace("''", "'")
        return inner
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [_parse_yaml_scalar(item) for item in _split_top_level(inner, ",")]
    if val.startswith("{") and val.endswith("}"):
        inner = val[1:-1].strip()
        if not inner:
            return {}
        obj = {}
        for pair in _split_top_level(inner, ","):
            if ":" not in pair:
                continue
            k, v = pair.split(":", 1)
            obj[str(_parse_yaml_scalar(k.strip()))] = _parse_yaml_scalar(v.strip())
        return obj
    if re.fullmatch(r"-?\d+", val):
        return int(val)
    if re.fullmatch(r"-?\d+\.\d+", val):
        return float(val)
    return val


def parse_yaml_lite(text: str):
    raw_lines = text.splitlines()
    entries = []
    idx = 0
    while idx < len(raw_lines):
        raw = raw_lines[idx]
        cleaned = _strip_yaml_comment(raw)
        if cleaned.strip() == "":
            idx += 1
            continue
        indent = len(cleaned) - len(cleaned.lstrip(" "))
        content = cleaned.strip()
        # Handle literal block scalar '|'
        if content.endswith(": |") or content == "|":
            base_indent = indent
            idx += 1
            block_lines = []
            block_indent = None
            while idx < len(raw_lines):
                nxt = raw_lines[idx]
                if nxt.strip() == "":
                    block_lines.append("")
                    idx += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                if nxt_indent <= base_indent:
                    break
                if block_indent is None:
                    block_indent = nxt_indent
                block_lines.append(nxt[block_indent:])
                idx += 1
            entries.append((indent, content[:-1].rstrip(), "\n".join(block_lines).rstrip("\n")))
            continue
        entries.append((indent, content, None))
        idx += 1

    def parse_block(pos: int, expected_indent: int):
        if pos >= len(entries):
            return None, pos
        indent, content, block_val = entries[pos]
        if indent < expected_indent:
            return None, pos

        if content.startswith("- ") or content == "-":
            result_list = []
            while pos < len(entries):
                ind, cont, bval = entries[pos]
                if ind != expected_indent or not (cont.startswith("- ") or cont == "-"):
                    break
                rest = cont[1:].strip()
                if rest == "":
                    item, pos = parse_block(pos + 1, expected_indent + 2)
                    result_list.append(item)
                elif rest.startswith("{") and rest.endswith("}"):
                    result_list.append(_parse_yaml_scalar(rest))
                    pos += 1
                elif ":" in rest:
                    k, v = rest.split(":", 1)
                    k = str(_parse_yaml_scalar(k.strip()))
                    v_str = v.strip()
                    item_dict = {}
                    if bval is not None:
                        item_dict[k] = bval
                        pos += 1
                    elif v_str == "":
                        nested, pos = parse_block(pos + 1, expected_indent + 2)
                        item_dict[k] = nested
                    else:
                        item_dict[k] = _parse_yaml_scalar(v_str)
                        pos += 1
                    # Read remaining keys belonging to this list-item mapping
                    if pos < len(entries) and entries[pos][0] > expected_indent:
                        sub_indent = entries[pos][0]
                        more, pos = parse_block(pos, sub_indent)
                        if isinstance(more, dict):
                            item_dict.update(more)
                    result_list.append(item_dict)
                else:
                    result_list.append(_parse_yaml_scalar(rest))
                    pos += 1
            return result_list, pos

        result_dict = {}
        while pos < len(entries):
            ind, cont, bval = entries[pos]
            if ind != expected_indent or cont.startswith("- ") or cont == "-":
                break
            if ":" not in cont:
                pos += 1
                continue
            k, v = cont.split(":", 1)
            key = str(_parse_yaml_scalar(k.strip()))
            v_str = v.strip()
            if bval is not None:
                result_dict[key] = bval
                pos += 1
            elif v_str == "":
                if pos + 1 < len(entries) and entries[pos + 1][0] > expected_indent:
                    child, pos = parse_block(pos + 1, entries[pos + 1][0])
                    result_dict[key] = child
                else:
                    result_dict[key] = None
                    pos += 1
            else:
                result_dict[key] = _parse_yaml_scalar(v_str)
                pos += 1
        return result_dict, pos

    parsed, _ = parse_block(0, 0)
    return parsed


def load_portal_config(yaml_path: Path) -> dict:
    if not yaml_path.exists():
        raise FileNotFoundError(f"Required configuration file not found: {yaml_path}")
    raw_text = yaml_path.read_text(encoding="utf-8")
    if yaml is not None:
        loaded = yaml.safe_load(raw_text)
    else:
        loaded = parse_yaml_lite(raw_text)
    if not isinstance(loaded, dict) or "meta" not in loaded:
        raise ValueError(f"Invalid YAML root structure in {yaml_path}")
    return loaded


def extract_pwa_icons(root_dir: Path, svg_name: str, icon_192: str, icon_512: str) -> dict:
    svg_path = root_dir / svg_name
    out_192 = root_dir / icon_192
    out_512 = root_dir / icon_512
    status = {"svg_exists": svg_path.exists(), "192_ready": out_192.exists(), "512_ready": out_512.exists()}

    if not svg_path.exists():
        print(f"[WARN] Primary SVG '{svg_name}' not found in {root_dir}. Place it there and re-run to extract PNG icons.")
        return status

    converters = []
    if shutil.which("rsvg-convert"):
        converters.append(("rsvg-convert", lambda size, dst: ["rsvg-convert", "-w", str(size), "-h", str(size), str(svg_path), "-o", str(dst)]))
    if shutil.which("inkscape"):
        converters.append(("inkscape", lambda size, dst: ["inkscape", str(svg_path), f"--export-filename={dst}", f"--export-width={size}", f"--export-height={size}"]))
    if shutil.which("magick"):
        converters.append(("magick", lambda size, dst: ["magick", "-background", "none", str(svg_path), "-resize", f"{size}x{size}", str(dst)]))
    elif shutil.which("convert"):
        converters.append(("convert", lambda size, dst: ["convert", "-background", "none", str(svg_path), "-resize", f"{size}x{size}", str(dst)]))

    if not converters:
        print("[WARN] No SVG rasterizer found (rsvg-convert, inkscape, or magick). Install librsvg2-tools on Fedora.")
        return status

    tool_name, cmd_fn = converters[0]
    for size, target in [(192, out_192), (512, out_512)]:
        try:
            subprocess.run(cmd_fn(size, target), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[OK]   Extracted {target.name} ({size}x{size}) via {tool_name}")
        except subprocess.CalledProcessError as exc:
            print(f"[ERR]  Failed extracting {target.name} via {tool_name}: {exc}")

    status["192_ready"] = out_192.exists()
    status["512_ready"] = out_512.exists()
    return status


def reconcile_papers(root_dir: Path, config: dict) -> None:
    papers_cfg = config.get("scientific_papers", {})
    storage_rel = papers_cfg.get("storage_directory", "papers/")
    papers_dir = root_dir / storage_rel
    papers_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = papers_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("# Keep papers directory tracked in Git for local PDF uploads.\n", encoding="utf-8")

    for entry in papers_cfg.get("entries", []):
        rel_pdf = entry.get("pdf_path", "")
        if not rel_pdf:
            entry["pdf_available"] = False
            continue
        candidate = root_dir / rel_pdf
        if not candidate.exists() and entry.get("id") == "paper_esocc_2015":
            alt = papers_dir / "chp3A10.10072F978-3-319-24072-5_15.pdf"
            if alt.exists():
                entry["pdf_path"] = f"{storage_rel.rstrip('/')}/{alt.name}"
                candidate = alt
        entry["pdf_available"] = candidate.exists()
        if entry["pdf_available"]:
            print(f"[OK]   Detected local paper PDF: {entry['pdf_path']}")


def build_manifest(config: dict) -> str:
    meta = config["meta"]
    branding = meta["branding"]
    manifest = {
        "_integrity": "Project UnLinked W3C Web Application Manifest v1.0.0 — Zero-Tracker Sovereign PWA",
        "name": meta["site_title"],
        "short_name": meta["short_name"],
        "description": config["hero"]["bio_headline"],
        "id": "/",
        "start_url": "./index.html?source=pwa",
        "scope": "./",
        "display": "standalone",
        "display_override": ["window-controls-overlay", "standalone", "minimal-ui"],
        "orientation": "any",
        "background_color": "#f4f2ee",
        "theme_color": "#0a66c2",
        "lang": meta["language"],
        "dir": "ltr",
        "categories": ["technology", "science", "education", "developer"],
        "icons": [
            {
                "src": f"./{branding['pwa_icon_192']}",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"./{branding['pwa_icon_512']}",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"./{branding['primary_svg_icon']}",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any",
            },
        ],
        "shortcuts": [
            {
                "name": "Pillar #1: 1985–2020 Foundation",
                "short_name": "Timeline",
                "description": "Chronological academic, defence and enterprise R&D timeline",
                "url": "./index.html#pillar-1-timeline",
                "icons": [{"src": f"./{branding['pwa_icon_192']}", "sizes": "192x192", "type": "image/png"}],
            },
            {
                "name": "Scientific Publications Archive",
                "short_name": "Papers",
                "description": "Peer-reviewed proceedings, abstracts, PDFs and BibTeX",
                "url": "./index.html#scientific-papers",
                "icons": [{"src": f"./{branding['pwa_icon_192']}", "sizes": "192x192", "type": "image/png"}],
            },
            {
                "name": "Public GitHub Repositories",
                "short_name": "GitHub",
                "description": "Live public repositories under github.com/kleynenberg",
                "url": "./index.html#github-repositories",
                "icons": [{"src": f"./{branding['pwa_icon_192']}", "sizes": "192x192", "type": "image/png"}],
            },
            {
                "name": "Pillar #2: Living R&D Sandbox",
                "short_name": "R&D Sandbox",
                "description": "Active AI systems and the 20 KSA architectural codenames",
                "url": "./index.html#pillar-2-sandbox",
                "icons": [{"src": f"./{branding['pwa_icon_192']}", "sizes": "192x192", "type": "image/png"}],
            },
        ],
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def build_service_worker(config: dict, build_hash: str) -> str:
    branding = config["meta"]["branding"]
    precache_assets = [
        "./",
        "./index.html",
        "./style.css",
        "./app.js",
        "./portal.json",
        "./manifest.webmanifest",
        "./llms.txt",
        f"./{branding['primary_svg_icon']}",
        f"./{branding['pwa_icon_192']}",
        f"./{branding['pwa_icon_512']}",
    ]
    for paper in config.get("scientific_papers", {}).get("entries", []):
        if paper.get("enabled") and paper.get("pdf_available") and paper.get("pdf_path"):
            precache_assets.append(f"./{paper['pdf_path'].lstrip('./')}")

    assets_json = json.dumps(precache_assets, indent=2)
    return f'''/* ==============================================================================
 * INTEGRITY & METADATA HEADER
 * File:          sw.js
 * Project:       Project UnLinked — Offline-First Service Worker
 * Host Target:   https://kleynenberg.github.io (GitHub Pages)
 * Build Hash:    {build_hash}
 * Standard:      W3C Service Workers / MDN Service Worker & Cache API
 * Integrity Rule: Zero tracking, deterministic offline shell, runtime PDF/API cache.
 * ============================================================================== */

const CACHE_VERSION = "unlinked-sovereign-v1-{build_hash}";
const RUNTIME_CACHE = "unlinked-runtime-v1-{build_hash}";

const PRECACHE_URLS = {assets_json};

self.addEventListener("install", (event) => {{
  event.waitUntil(
    caches.open(CACHE_VERSION).then(async (cache) => {{
      for (const url of PRECACHE_URLS) {{
        try {{
          await cache.add(url);
        }} catch (err) {{
          console.warn("[UnLinked SW] Precache skipped optional asset:", url);
        }}
      }}
    }}).then(() => self.skipWaiting())
  );
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION && key !== RUNTIME_CACHE)
          .map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
}});

self.addEventListener("fetch", (event) => {{
  const {{ request }} = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);

  if (url.hostname === "api.github.com") {{
    event.respondWith(
      fetch(request)
        .then((networkResp) => {{
          if (networkResp && networkResp.ok) {{
            const clone = networkResp.clone();
            caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, clone));
          }}
          return networkResp;
        }})
        .catch(() => caches.match(request))
    );
    return;
  }}

  if (url.origin === self.location.origin) {{
    event.respondWith(
      caches.match(request).then((cachedResp) => {{
        const networkFetch = fetch(request)
          .then((networkResp) => {{
            if (networkResp && networkResp.ok) {{
              const clone = networkResp.clone();
              caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
            }}
            return networkResp;
          }})
          .catch(() => cachedResp);

        return cachedResp || networkFetch;
      }})
    );
  }}
}});
'''


def build_json_ld(config: dict) -> str:
    meta = config["meta"]
    person = meta["person"]
    branding = meta["branding"]
    base_url = meta["canonical_url"].rstrip("/")

    person_id = f"{base_url}/#steven-kleynenberg"
    website_id = f"{base_url}/#website"
    unlinked_app_id = f"{base_url}/#project-unlinked"

    graph = [
        {
            "@type": "WebSite",
            "@id": website_id,
            "url": f"{base_url}/",
            "name": meta["site_title"],
            "description": config["hero"]["bio_headline"],
            "inLanguage": meta["language"],
            "publisher": {"@id": f"{base_url}/#kleynenberg-publishers"},
            "author": {"@id": person_id},
        },
        {
            "@type": "Person",
            "@id": person_id,
            "name": person["full_name"],
            "alternateName": person["formal_name"],
            "givenName": person["given_name"],
            "familyName": person["family_name"],
            "jobTitle": person["role_summary"],
            "url": f"{base_url}/",
            "image": f"{base_url}/{branding['primary_svg_icon']}",
            "homeLocation": {
                "@type": "Place",
                "name": person["location"],
            },
            "sameAs": [
                "https://github.com/kleynenberg",
                "https://kleynenberg.com",
                "https://taksie.ai",
                "https://innopheon.com",
                "https://naaap.io",
                "https://www.researchgate.net/profile/Steven-Kleynenberg",
                "https://patents.google.com/patent/WO2014003543A1/en",
            ],
            "alumniOf": [
                {
                    "@type": "CollegeOrUniversity",
                    "name": "Leiden University",
                    "url": "https://www.universiteitleiden.nl",
                },
                {
                    "@type": "CollegeOrUniversity",
                    "name": "Delft University of Technology",
                    "url": "https://www.tudelft.nl",
                },
            ],
            "worksFor": {
                "@type": "Organization",
                "@id": f"{base_url}/#kleynenberg-publishers",
                "name": "Kleynenberg Publishers",
                "url": "https://kleynenberg.com",
            },
            "knowsAbout": [
                "Artificial Intelligence",
                "Natural Language Processing",
                "Part-of-Speech Tagging Document Retrieval",
                "Modular Neural Networks",
                "CALM Architecture",
                "Massively Parallel Computing",
                "Connection Machine Supercomputing",
                "Model-Based Reasoning Diagnostic Systems",
                "Cellular Automata Simulation",
                "Enterprise Innovation Management",
                "Medical High-Performance Computing",
                "WebGPU and Browser-Native AI",
                "Progressive Web Applications",
                "Operating System Kernel Engineering",
            ],
        },
        {
            "@type": "SoftwareApplication",
            "@id": unlinked_app_id,
            "name": config["project_unlinked_spotlight"]["working_title"],
            "applicationCategory": "WebApplication",
            "operatingSystem": "All (Progressive Web App)",
            "url": f"{base_url}/",
            "codeRepository": config["project_unlinked_spotlight"]["repository_url"],
            "author": {"@id": person_id},
            "description": config["project_unlinked_spotlight"]["summary"],
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        },
        {
            "@type": "Patent",
            "@id": f"{base_url}/#patent-wo2014003543a1",
            "name": "WO2014003543A1 — Automated Document Retrieval and Linguistic Text Mining via Part-of-Speech Tagging",
            "patentNumber": "WO2014003543A1",
            "url": "https://patents.google.com/patent/WO2014003543A1/en",
            "inventor": [
                {"@id": person_id},
                {"@type": "Person", "name": "Elsemiek ten Pas"},
                {"@type": "Person", "name": "Huub Rutten"},
            ],
            "assignee": {
                "@type": "Organization",
                "name": "Sopheon N.V.",
                "url": "https://www.sopheon.com",
            },
        },
    ]

    for paper in config.get("scientific_papers", {}).get("entries", []):
        if not paper.get("enabled") or paper.get("is_placeholder"):
            continue
        article_node = {
            "@type": "ScholarlyArticle",
            "@id": f"{base_url}/#{paper['id']}",
            "identifier": paper["archive_id"],
            "name": paper["title"],
            "headline": paper["title"],
            "datePublished": str(paper["year"]),
            "abstract": paper["abstract"],
            "keywords": ", ".join(paper.get("keywords", [])),
            "author": [{"@type": "Person", "name": a} for a in paper.get("authors", [])],
            "isPartOf": {"@type": "PublicationEvent", "name": paper["venue"]},
        }
        if paper.get("doi"):
            article_node["sameAs"] = f"https://doi.org/{paper['doi']}"
        elif paper.get("external_url"):
            article_node["url"] = paper["external_url"]
        graph.append(article_node)

    for proj in config.get("pillar_2_sandbox", {}).get("projects", []):
        if not proj.get("enabled") or proj.get("is_placeholder"):
            continue
        if proj.get("url"):
            graph.append(
                {
                    "@type": "SoftwareApplication",
                    "@id": f"{base_url}/#{proj['id']}",
                    "name": proj["title"],
                    "url": proj["url"],
                    "description": proj["summary"],
                    "creator": {"@id": person_id},
                }
            )

    payload = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(payload, indent=2, ensure_ascii=False)


def build_llms_txt(config: dict) -> str:
    meta = config["meta"]
    person = meta["person"]
    hero = config["hero"]
    spotlight = config["project_unlinked_spotlight"]

    lines = [
        "# ==============================================================================",
        "# INTEGRITY & METADATA HEADER",
        "# File:          llms.txt",
        "# Project:       Project UnLinked — Sovereign Static PWA Portal",
        "# Canonical URL: https://kleynenberg.github.io/",
        "# Specification: https://llmstxt.org/",
        "# ==============================================================================",
        "",
        f"# {person['full_name']} — {meta['short_name']}",
        "",
        f"> {hero['bio_headline']}",
        "",
        f"- **Canonical Portal**: {meta['canonical_url']}",
        f"- **Location**: {person['location']}",
        f"- **Role**: {person['role_summary']}",
        f"- **Active Flagship**: {spotlight['working_title']} ({spotlight['live_url']})",
        "",
        "## Core Ecosystem Links",
        "",
    ]
    for link in hero.get("bio_links", []):
        if link.get("enabled"):
            lines.append(f"- [{link['label']}]({link['url']}): {link['subtitle']}")

    lines.extend(["", "## Flagship Initiative: Project UnLinked", "", spotlight["summary"], ""])

    lines.extend(["## Pillar #1 — Chronological Academic, Defence & Enterprise Foundation (1985–2020)", ""])
    for item in config.get("pillar_1_timeline", {}).get("milestones", []):
        if not item.get("enabled") or item.get("is_placeholder"):
            continue
        lines.append(f"### {item['period']} — {item['title']}")
        lines.append(f"- **Organization**: {item['organization']}")
        lines.append(f"- **Summary**: {item['summary']}")
        for d in item.get("details", []):
            lines.append(f"  - {d}")
        for ext in item.get("external_links", []):
            lines.append(f"  - Reference: [{ext['label']}]({ext['url']})")
        lines.append("")

    lines.extend(["## Scientific Publications Archive", ""])
    for paper in config.get("scientific_papers", {}).get("entries", []):
        if not paper.get("enabled") or paper.get("is_placeholder"):
            continue
        authors_str = ", ".join(paper.get("authors", []))
        lines.append(f"- **{paper['archive_id']} ({paper['year']})**: *{paper['title']}* — {authors_str}. {paper['venue']}.")
        if paper.get("doi"):
            lines.append(f"  - DOI: https://doi.org/{paper['doi']}")
        if paper.get("external_url"):
            lines.append(f"  - Archive URL: {paper['external_url']}")
        lines.append(f"  - Abstract: {paper['abstract']}")

    lines.extend(["", "## Pillar #2 — Living R&D Sandbox (2020–Present)", ""])
    for proj in config.get("pillar_2_sandbox", {}).get("projects", []):
        if not proj.get("enabled") or proj.get("is_placeholder"):
            continue
        url_part = f" ({proj['url']})" if proj.get("url") else ""
        lines.append(f"- **{proj['title']}**{url_part} [{proj['status']}]: {proj['summary']}")

    lines.extend(["", "## Strategic R&D Roadmap — The 20 KSA Codenames", ""])
    for ksa in config.get("ksa_roadmap", {}).get("codenames", []):
        if not ksa.get("enabled") or ksa.get("is_placeholder"):
            continue
        lines.append(f"- **{ksa['code']} — {ksa['name']}**: {ksa['focus']}")

    lines.extend(["", "## Pillar #3 — Sovereign Publishing & Audiovisual Media", ""])
    for eco in config.get("pillar_3_media", {}).get("ecosystems", []):
        if not eco.get("enabled") or eco.get("is_placeholder"):
            continue
        lines.append(f"- **{eco['title']}** ({eco['url']}): {eco['summary']}")

    lines.extend(
        [
            "",
            "## Legal & Colophon",
            "",
            meta["legal"]["non_affiliation_notice"],
            f"© {meta['legal']['copyright_year_roman']} {meta['legal']['copyright_holder']} ({meta['legal']['copyright_url']}). All rights reserved.",
            "",
        ]
    )
    return "\n".join(lines)


def build_index_html(config: dict) -> str:
    meta = config["meta"]
    person = meta["person"]
    branding = meta["branding"]
    legal = meta["legal"]
    sections = config["sections"]
    hero = config["hero"]
    spotlight = config["project_unlinked_spotlight"]
    p1 = config["pillar_1_timeline"]
    papers_cfg = config["scientific_papers"]
    gh_cfg = config["github_repos"]
    p2 = config["pillar_2_sandbox"]
    ksa_cfg = config["ksa_roadmap"]
    p3 = config["pillar_3_media"]

    canonical = meta["canonical_url"]
    svg_icon = branding["primary_svg_icon"]
    png_192 = branding["pwa_icon_192"]
    png_512 = branding["pwa_icon_512"]
    json_ld_str = build_json_ld(config)

    telemetry_html = "\n".join(
        f'<span class="telemetry-pill">{esc(b)}</span>' for b in branding.get("telemetry_badges", [])
    )

    bio_links_html = "\n".join(
        f'''<a class="bio-link-chip" data-feature-id="{esc(item['id'])}" href="{esc(item['url'])}" target="_blank" rel="noopener noreferrer">
              <span class="bio-link-label">{esc(item['label'])}</span>
              <span class="bio-link-sub">{esc(item['subtitle'])}</span>
            </a>'''
        for item in hero.get("bio_links", [])
        if item.get("enabled")
    )

    featured_html = []
    for cta in config.get("featured_ctas", []):
        if not cta.get("enabled"):
            continue
        is_ext = cta["target_url"].startswith("http")
        rel_attr = ' target="_blank" rel="noopener noreferrer"' if is_ext else ""
        featured_html.append(
            f'''<article class="featured-card" data-feature-id="{esc(cta['id'])}">
                  <span class="badge-subtle">{esc(cta['badge'])}</span>
                  <h3>{esc(cta['title'])}</h3>
                  <p>{esc(cta['description'])}</p>
                  <a class="btn-secondary" href="{esc(cta['target_url'])}"{rel_attr}>{esc(cta['action_label'])} &rarr;</a>
                </article>'''
        )

    spotlight_pillars_html = "\n".join(
        f'''<div class="spotlight-pillar" data-feature-id="{esc(sp['id'])}">
              <h4>{esc(sp['heading'])}</h4>
              <p>{esc(sp['detail'])}</p>
            </div>'''
        for sp in spotlight.get("pillars_of_design", [])
        if sp.get("enabled")
    )

    era_tabs_html = ['<button class="filter-chip is-active" type="button" data-era-filter="all">All eras (1985–2020)</button>']
    for era in p1.get("eras", []):
        if era.get("enabled"):
            era_tabs_html.append(
                f'<button class="filter-chip" type="button" data-era-filter="{esc(era["id"])}">{esc(era["period"])}</button>'
            )

    milestones_html = []
    for m in p1.get("milestones", []):
        is_ph = bool(m.get("is_placeholder"))
        if not m.get("enabled") and not is_ph:
            continue
        ph_attr = ' data-placeholder="true"' if is_ph else ""
        ph_class = " is-placeholder" if is_ph else ""
        hidden_style = ' hidden' if (is_ph and not m.get("enabled")) else ""

        details_li = "\n".join(f"<li>{esc(d)}</li>" for d in m.get("details", []))
        code_block = ""
        if m.get("code_artifact"):
            ca = m["code_artifact"]
            code_block = f'''<div class="code-artifact">
                <div class="code-artifact-header">
                  <span>{esc(ca.get('language', 'Code'))}</span>
                  <span>{esc(ca.get('caption', ''))}</span>
                </div>
                <pre><code>{esc(ca.get('snippet', ''))}</code></pre>
              </div>'''

        links_html = ""
        if m.get("external_links"):
            anchors = " ".join(
                f'<a class="inline-ext-link" href="{esc(lk["url"])}" target="_blank" rel="noopener noreferrer">{esc(lk["label"])} &nearr;</a>'
                for lk in m["external_links"]
            )
            links_html = f'<div class="milestone-links">{anchors}</div>'

        milestones_html.append(
            f'''<article class="timeline-card{ph_class}" data-feature-id="{esc(m['id'])}" data-era="{esc(m['era'])}"{ph_attr}{hidden_style}>
                  <div class="timeline-meta">
                    <span class="period-tag">{esc(m['period'])}</span>
                    <span class="category-tag">{esc(m['category'])}</span>
                  </div>
                  <h3>{esc(m['title'])}</h3>
                  <p class="org-line">{esc(m['organization'])}</p>
                  <p class="summary-line">{esc(m['summary'])}</p>
                  <details class="proof-details">
                    <summary>Inspect technical architecture and primary evidence</summary>
                    <div class="proof-body">
                      <ul>{details_li}</ul>
                      {code_block}
                      {links_html}
                    </div>
                  </details>
                </article>'''
        )

    papers_html = []
    for paper in papers_cfg.get("entries", []):
        is_ph = bool(paper.get("is_placeholder"))
        if not paper.get("enabled") and not is_ph:
            continue
        ph_attr = ' data-placeholder="true"' if is_ph else ""
        ph_class = " is-placeholder" if is_ph else ""
        hidden_style = ' hidden' if (is_ph and not paper.get("enabled")) else ""

        authors_str = ", ".join(paper.get("authors", []))
        kw_html = " ".join(f'<span class="kw-chip">{esc(k)}</span>' for k in paper.get("keywords", []))
        doi_html = ""
        if paper.get("doi"):
            doi_html = f'<a class="meta-link" href="https://doi.org/{esc(paper["doi"])}" target="_blank" rel="noopener noreferrer">DOI: {esc(paper["doi"])} &nearr;</a>'

        if paper.get("pdf_available"):
            pdf_btn = f'<a class="btn-primary-sm" href="./{esc(paper["pdf_path"])}" target="_blank" rel="noopener">Download PDF</a>'
        else:
            pdf_btn = f'<span class="pdf-slot-badge" title="Upload PDF to {esc(paper["pdf_path"])}">PDF slot: {esc(paper["pdf_path"])}</span>'

        ext_btn = ""
        if paper.get("external_url"):
            ext_btn = f'<a class="btn-secondary-sm" href="{esc(paper["external_url"])}" target="_blank" rel="noopener noreferrer">Publisher / Archive &nearr;</a>'

        papers_html.append(
            f'''<article class="paper-card{ph_class}" data-feature-id="{esc(paper['id'])}"{ph_attr}{hidden_style}>
                  <div class="paper-header-row">
                    <span class="archive-id">{esc(paper['archive_id'])}</span>
                    <span class="paper-year">{esc(paper['year'])}</span>
                    {doi_html}
                  </div>
                  <h3>{esc(paper['title'])}</h3>
                  <p class="paper-authors">{esc(authors_str)}</p>
                  <p class="paper-venue">{esc(paper['venue'])}</p>
                  <p class="paper-abstract">{esc(paper['abstract'])}</p>
                  <div class="paper-keywords">{kw_html}</div>
                  <div class="paper-actions">
                    {pdf_btn}
                    {ext_btn}
                    <button class="btn-secondary-sm copy-bibtex-btn" type="button" data-bibtex="{esc(paper.get('bibtex', ''))}">Copy BibTeX</button>
                  </div>
                </article>'''
        )

    domain_tabs_html = ['<button class="filter-chip is-active" type="button" data-domain-filter="all">All domains</button>']
    for dom in p2.get("domains", []):
        if dom.get("enabled"):
            domain_tabs_html.append(
                f'<button class="filter-chip" type="button" data-domain-filter="{esc(dom["id"])}">{esc(dom["label"])}</button>'
            )

    p2_projects_html = []
    for proj in p2.get("projects", []):
        is_ph = bool(proj.get("is_placeholder"))
        if not proj.get("enabled") and not is_ph:
            continue
        ph_attr = ' data-placeholder="true"' if is_ph else ""
        ph_class = " is-placeholder" if is_ph else ""
        hidden_style = ' hidden' if (is_ph and not proj.get("enabled")) else ""

        stack_html = " ".join(f'<span class="stack-chip">{esc(s)}</span>' for s in proj.get("stack", []))
        title_html = (
            f'<a href="{esc(proj["url"])}" target="_blank" rel="noopener noreferrer">{esc(proj["title"])} &nearr;</a>'
            if proj.get("url")
            else esc(proj["title"])
        )
        p2_projects_html.append(
            f'''<article class="sandbox-card{ph_class}" data-feature-id="{esc(proj['id'])}" data-domain="{esc(proj['domain'])}"{ph_attr}{hidden_style}>
                  <div class="sandbox-top">
                    <span class="status-pill">{esc(proj['status'])}</span>
                  </div>
                  <h3>{title_html}</h3>
                  <p>{esc(proj['summary'])}</p>
                  <div class="stack-row">{stack_html}</div>
                </article>'''
        )

    ksa_tabs_html = ['<button class="filter-chip is-active" type="button" data-ksa-filter="all">All 20 codenames</button>']
    for s in ksa_cfg.get("series", []):
        is_ph_s = s["id"] == "series_reserved"
        if s.get("enabled") or is_ph_s:
            ph_s_attr = ' data-placeholder="true" hidden' if (is_ph_s and not s.get("enabled")) else ""
            ksa_tabs_html.append(
                f'<button class="filter-chip" type="button" data-ksa-filter="{esc(s["id"])}"{ph_s_attr}>{esc(s["label"])}</button>'
            )

    ksa_cards_html = []
    for ksa in ksa_cfg.get("codenames", []):
        is_ph = bool(ksa.get("is_placeholder"))
        if not ksa.get("enabled") and not is_ph:
            continue
        ph_attr = ' data-placeholder="true"' if is_ph else ""
        ph_class = " is-placeholder" if is_ph else ""
        hidden_style = ' hidden' if (is_ph and not ksa.get("enabled")) else ""
        ksa_cards_html.append(
            f'''<div class="ksa-card{ph_class}" data-feature-id="{esc(ksa['id'])}" data-ksa-series="{esc(ksa['series'])}"{ph_attr}{hidden_style}>
                  <div class="ksa-head">
                    <span class="ksa-code">{esc(ksa['code'])}</span>
                    <span class="ksa-name">{esc(ksa['name'])}</span>
                  </div>
                  <p class="ksa-focus">{esc(ksa['focus'])}</p>
                </div>'''
        )

    p3_cards_html = []
    p3_rail_html = []
    for eco in p3.get("ecosystems", []):
        is_ph = bool(eco.get("is_placeholder"))
        if not eco.get("enabled") and not is_ph:
            continue
        ph_attr = ' data-placeholder="true"' if is_ph else ""
        ph_class = " is-placeholder" if is_ph else ""
        hidden_style = ' hidden' if (is_ph and not eco.get("enabled")) else ""
        hl_li = "\n".join(f"<li>{esc(h)}</li>" for h in eco.get("highlights", []))
        p3_cards_html.append(
            f'''<article class="media-card{ph_class}" data-feature-id="{esc(eco['id'])}"{ph_attr}{hidden_style}>
                  <div class="media-head">
                    <h3><a href="{esc(eco['url'])}" target="_blank" rel="noopener noreferrer">{esc(eco['title'])} &nearr;</a></h3>
                    <span class="location-tag">{esc(eco['location'])}</span>
                  </div>
                  <p>{esc(eco['summary'])}</p>
                  <ul>{hl_li}</ul>
                </article>'''
        )
        if not is_ph:
            p3_rail_html.append(
                f'''<div class="rail-ecosystem" data-feature-id="{esc(eco['id'])}_rail">
                      <a class="rail-eco-title" href="{esc(eco['url'])}" target="_blank" rel="noopener noreferrer">{esc(eco['title'])} &nearr;</a>
                      <p>{esc(eco['summary'])}</p>
                    </div>'''
            )

    return f'''<!DOCTYPE html>
<!-- ==============================================================================
     INTEGRITY & METADATA HEADER
     File:          index.html
     Project:       Project UnLinked — Sovereign Static Progressive Web App
     Host Target:   https://kleynenberg.github.io (GitHub Pages)
     Workstation:   hp.kleynenberg.net (Fedora Linux / JOE Editor)
     Author:        Steven (S.E.) Kleynenberg
     Standards:     HTML5, Schema.org JSON-LD 1.1, Open Graph Protocol, Dublin Core,
                    W3C Web App Manifest, Service Worker API
     License/Legal: Independent Sovereign Portal & Parody-Exception Implementation
                    (Dutch Copyright Act Art. 18b / EU InfoSoc Directive 2001/29/EC)
     ============================================================================== -->
<html lang="{esc(meta['language'])}" data-theme="{esc(meta.get('default_theme', 'daylight'))}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(meta['site_title'])}</title>
  <meta name="description" content="{esc(hero['bio_headline'])}">
  <meta name="author" content="{esc(person['full_name'])}">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
  <meta name="theme-color" content="#0a66c2">
  <meta name="color-scheme" content="light dark">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="alternate" type="text/plain" title="LLM Knowledge Graph Index (llms.txt)" href="./llms.txt">

  <!-- PWA Manifest & Icons (Derived from user-supplied primary vector emblem) -->
  <link rel="manifest" href="./manifest.webmanifest">
  <link rel="icon" type="image/svg+xml" href="./{esc(svg_icon)}">
  <link rel="icon" type="image/png" sizes="192x192" href="./{esc(png_192)}">
  <link rel="apple-touch-icon" sizes="192x192" href="./{esc(png_192)}">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-title" content="{esc(meta['short_name'])}">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">

  <!-- Open Graph Protocol (https://ogp.me) -->
  <meta property="og:type" content="profile">
  <meta property="og:site_name" content="Project UnLinked — Steven Kleynenberg">
  <meta property="og:title" content="{esc(meta['site_title'])}">
  <meta property="og:description" content="{esc(hero['bio_headline'])}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:locale" content="{esc(meta['locale'])}">
  <meta property="profile:first_name" content="{esc(person['given_name'])}">
  <meta property="profile:last_name" content="{esc(person['family_name'])}">
  <meta property="profile:username" content="kleynenberg">
  <meta property="og:image" content="{esc(canonical)}{esc(png_512)}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="512">
  <meta property="og:image:height" content="512">
  <meta property="og:image:alt" content="Steven Kleynenberg — Project UnLinked Sovereign Emblem">
  <meta property="og:image" content="{esc(canonical)}{esc(svg_icon)}">
  <meta property="og:image:type" content="image/svg+xml">

  <!-- X / Twitter Card Metadata -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(meta['site_title'])}">
  <meta name="twitter:description" content="{esc(hero['bio_headline'])}">
  <meta name="twitter:image" content="{esc(canonical)}{esc(png_512)}">
  <meta name="twitter:image:alt" content="Steven Kleynenberg — Project UnLinked Sovereign Emblem">

  <!-- Dublin Core Metadata Terms (DCMI) -->
  <meta name="DC.title" content="{esc(meta['site_title'])}">
  <meta name="DC.creator" content="{esc(person['full_name'])}">
  <meta name="DC.publisher" content="{esc(legal['copyright_holder'])}">
  <meta name="DC.subject" content="Artificial Intelligence, NLP, Parallel Computing, Patent WO2014003543A1, Systems Architecture">
  <meta name="DC.language" content="{esc(meta['language'])}">
  <meta name="DC.rights" content="Copyright {esc(legal['copyright_year_roman'])} {esc(legal['copyright_holder'])}. All rights reserved.">

  <!-- Schema.org JSON-LD 1.1 Knowledge Graph for AI Crawlers -->
  <script type="application/ld+json">
{json_ld_str}
  </script>

  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to primary content</a>

  <!-- Floating UnLinked Sovereign Header (User SVG Icon as Primary UnLinked Emblem) -->
  <header class="topbar" role="banner">
    <div class="topbar-inner">
      <div class="brand-cluster">
        <a class="brand-mark" href="#top" aria-label="UnLinked — Steven Kleynenberg Home">
          <img class="brand-emblem" src="./{esc(svg_icon)}" alt="UnLinked Emblem" width="36" height="36">
          <span class="brand-wordmark">UnLinked</span>
        </a>
        <div class="search-box" role="search">
          <label class="sr-only" for="global-search">Filter timeline, papers, KSA codenames and repositories</label>
          <input id="global-search" type="search" placeholder="Search 1985–2026 graph, papers, KSA, repos… ( / )" autocomplete="off">
        </div>
      </div>

      <nav class="topbar-nav" aria-label="Primary portal sections">
        <a href="#project-unlinked">UnLinked</a>
        <a href="#pillar-1-timeline">1985–2020</a>
        <a href="#scientific-papers">Papers</a>
        <a href="#github-repositories">GitHub</a>
        <a href="#pillar-2-sandbox">R&amp;D Sandbox</a>
        <a href="#ksa-roadmap">20 KSA</a>
      </nav>

      <div class="topbar-actions">
        <span id="pwa-status-badge" class="status-telemetry" title="Progressive Web App &amp; Offline Cache Status">PWA initializing</span>
        <button id="install-pwa-btn" class="btn-install" type="button" hidden>+ Install app</button>
        <button id="toggle-slots-btn" class="btn-ghost" type="button" aria-pressed="false" title="Show or hide reserved archival and future expansion slots">Slots: off</button>
        <button id="theme-toggle-btn" class="btn-ghost" type="button" aria-label="Switch between Daylight Glass and Future Dark themes">Future dark</button>
      </div>
    </div>
  </header>

  <div id="top" class="page-shell">
    <main id="main-content" class="main-column">

      <!-- 1. EXECUTIVE PROFILE HERO (PromiseClick High-Signal Architecture) -->
      <section class="card hero-card" data-feature-id="hero_profile" aria-labelledby="profile-name">
        <div class="hero-banner">
          <div class="banner-hook-grid">
            <div class="hook-block hook-stop">
              <span class="hook-kicker">Legacy platforms</span>
              <p>{esc(hero['banner_hook']['stop_statement'])}</p>
            </div>
            <div class="hook-block hook-start">
              <span class="hook-kicker">Sovereign architecture</span>
              <p>{esc(hero['banner_hook']['start_statement'])}</p>
            </div>
          </div>
        </div>

        <div class="hero-body">
          <div class="avatar-row">
            <div class="avatar-ring" title="{esc(branding['status_ring_badge'])}">
              <img src="./{esc(svg_icon)}" alt="{esc(person['full_name'])} sovereign vector emblem" width="116" height="116">
              <span class="ring-badge">{esc(branding['status_ring_badge'])}</span>
            </div>
            <div class="telemetry-strip" aria-label="Sovereign architecture guarantees">
              {telemetry_html}
            </div>
          </div>

          <div class="identity-block">
            <div class="name-line">
              <h1 id="profile-name">{esc(person['full_name'])}</h1>
              <span class="formal-tag">{esc(person['formal_name'])}</span>
            </div>
            <p class="bio-headline">{esc(hero['bio_headline'])}</p>
            <p class="location-line">{esc(person['location'])} &middot; {esc(person['role_summary'])}</p>
          </div>

          <!-- Sovereign Bio-Link Hub ("One hub that leads to many") -->
          <div class="bio-link-hub" aria-label="Sovereign ecosystem links">
            {bio_links_html}
          </div>

          <!-- PAIS-Structured About Section (Pain -> Agitation -> Ideal Situation -> Solution) -->
          <div class="about-pais">
            <h2>About — first-principles career architecture</h2>
            <div class="pais-grid">
              <div class="pais-step">
                <span class="pais-label">01 &middot; The constraint</span>
                <p>{esc(hero['about_pais']['pain'])}</p>
              </div>
              <div class="pais-step">
                <span class="pais-label">02 &middot; Structural cost</span>
                <p>{esc(hero['about_pais']['agitation'])}</p>
              </div>
              <div class="pais-step">
                <span class="pais-label">03 &middot; Architectural standard</span>
                <p>{esc(hero['about_pais']['ideal_situation'])}</p>
              </div>
              <div class="pais-step pais-solution">
                <span class="pais-label">04 &middot; Sovereign implementation</span>
                <p>{esc(hero['about_pais']['solution'])}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. FEATURED SECTION (Strictly 3 Zero-Friction CTA Cards) -->
      <section class="card" data-feature-id="featured_ctas" aria-labelledby="featured-heading">
        <div class="section-header">
          <h2 id="featured-heading">{esc(sections['featured_ctas']['title'])}</h2>
          <span class="section-sub">Three direct entry points &middot; zero feed clutter</span>
        </div>
        <div class="featured-grid">
          {''.join(featured_html)}
        </div>
      </section>

      <!-- 3. ACTIVE FLAGSHIP SPOTLIGHT: PROJECT UNLINKED -->
      <section id="project-unlinked" class="card spotlight-card" data-feature-id="project_unlinked_spotlight" aria-labelledby="spotlight-heading">
        <div class="section-header">
          <div>
            <span class="badge-accent">{esc(spotlight['status'])}</span>
            <h2 id="spotlight-heading">{esc(spotlight['working_title'])}</h2>
          </div>
          <div class="spotlight-links">
            <a class="btn-secondary-sm" href="{esc(spotlight['live_url'])}" target="_blank" rel="noopener noreferrer">Live origin &nearr;</a>
            <a class="btn-secondary-sm" href="{esc(spotlight['repository_url'])}" target="_blank" rel="noopener noreferrer">Source repository &nearr;</a>
          </div>
        </div>
        <p class="lead-paragraph">{esc(spotlight['summary'])}</p>
        <div class="spotlight-pillars-grid">
          {spotlight_pillars_html}
        </div>
      </section>

      <!-- 4. PILLAR #1: CHRONOLOGICAL FOUNDATION (1985–2020) -->
      <section id="pillar-1-timeline" class="card" data-feature-id="pillar_1_timeline" aria-labelledby="pillar1-heading">
        <div class="section-header">
          <div>
            <h2 id="pillar1-heading">{esc(sections['pillar_1_timeline']['title'])}</h2>
            <p class="section-desc">Verified progression from early commercial systems and parallel neurocomputing to WIPO-patented NLP and European medical HPC consortia.</p>
          </div>
        </div>
        <div class="filter-bar" role="tablist" aria-label="Filter timeline by era">
          {''.join(era_tabs_html)}
        </div>
        <div class="timeline-list">
          {''.join(milestones_html)}
        </div>
      </section>

      <!-- 5. SCIENTIFIC PUBLICATIONS ARCHIVE (ResearchGate / arXiv / Academia Hybrid) -->
      <section id="scientific-papers" class="card" data-feature-id="scientific_papers" aria-labelledby="papers-heading">
        <div class="section-header">
          <div>
            <h2 id="papers-heading">{esc(sections['scientific_papers']['title'])}</h2>
            <p class="section-desc">Canonical archive identifiers, structured abstracts, one-click BibTeX citations, and local PDF ingestion slots ({esc(papers_cfg['storage_directory'])}).</p>
          </div>
          <a class="btn-secondary-sm" href="https://www.researchgate.net/profile/Steven-Kleynenberg" target="_blank" rel="noopener noreferrer">ResearchGate profile &nearr;</a>
        </div>
        <div class="papers-list">
          {''.join(papers_html)}
        </div>
      </section>

      <!-- 6. DYNAMIC PUBLIC GITHUB REPOSITORIES -->
      <section id="github-repositories" class="card" data-feature-id="github_repositories" aria-labelledby="github-heading">
        <div class="section-header">
          <div>
            <h2 id="github-heading">{esc(sections['github_repositories']['title'])}</h2>
            <p class="section-desc">Dynamically queried from the public GitHub REST API for <a href="{esc(gh_cfg['profile_url'])}" target="_blank" rel="noopener noreferrer">github.com/{esc(gh_cfg['username'])}</a>, highlighting <a href="https://github.com/kleynenberg/public-test-repos/" target="_blank" rel="noopener noreferrer">public-test-repos</a>.</p>
          </div>
          <span id="github-sync-status" class="status-telemetry">Syncing repositories…</span>
        </div>
        <div id="github-lang-filters" class="filter-bar" aria-label="Filter GitHub repositories by language">
          <button class="filter-chip is-active" type="button" data-repo-lang="all">All languages</button>
        </div>
        <div id="github-repos-grid" class="repos-grid" aria-live="polite"></div>
      </section>

      <!-- 7. PILLAR #2: LIVING R&D SANDBOX (2020–PRESENT) -->
      <section id="pillar-2-sandbox" class="card" data-feature-id="pillar_2_sandbox" aria-labelledby="pillar2-heading">
        <div class="section-header">
          <div>
            <h2 id="pillar2-heading">{esc(sections['pillar_2_sandbox']['title'])}</h2>
            <p class="section-desc">First-principles software engineering across fiscal AI, WebGPU compute kernels, serverless virtual worlds, audio DSP, and bare-metal OS development.</p>
          </div>
        </div>
        <div class="filter-bar" role="tablist" aria-label="Filter R&D projects by engineering domain">
          {''.join(domain_tabs_html)}
        </div>
        <div class="sandbox-grid">
          {''.join(p2_projects_html)}
        </div>
      </section>

      <!-- 8. STRATEGIC R&D ROADMAP: THE 20 KSA CODENAMES -->
      <section id="ksa-roadmap" class="card" data-feature-id="ksa_roadmap" aria-labelledby="ksa-heading">
        <div class="section-header">
          <div>
            <h2 id="ksa-heading">{esc(sections['ksa_roadmap']['title'])}</h2>
            <p class="section-desc">Twenty structured architectural tracks spanning tactical enterprise AI (Series I) and next-generation cognitive compute engines (Series II).</p>
          </div>
        </div>
        <div class="filter-bar" role="tablist" aria-label="Filter KSA roadmap by series">
          {''.join(ksa_tabs_html)}
        </div>
        <div class="ksa-grid">
          {''.join(ksa_cards_html)}
        </div>
      </section>

      <!-- 9. PILLAR #3: SOVEREIGN PUBLISHING & AUDIOVISUAL MEDIA -->
      <section id="pillar-3-media" class="card" data-feature-id="pillar_3_media" aria-labelledby="pillar3-heading">
        <div class="section-header">
          <div>
            <h2 id="pillar3-heading">{esc(sections['pillar_3_media']['title'])}</h2>
            <p class="section-desc">Independent book conservation, deterministic typographic pipelines, podcasts, and instrumental music production.</p>
          </div>
        </div>
        <div class="media-grid">
          {''.join(p3_cards_html)}
        </div>
      </section>

    </main>

    <!-- RIGHT SIDEBAR RAIL (Executive Knowledge Graph Summary & Ecosystems) -->
    <aside class="side-column" aria-label="Knowledge graph telemetry and publishing ecosystems">
      <section class="card side-card">
        <h2>Sovereign graph telemetry</h2>
        <dl class="telemetry-dl">
          <div><dt>Canonical origin</dt><dd><a href="{esc(canonical)}">kleynenberg.github.io</a></dd></div>
          <div><dt>Configuration source</dt><dd><code>portal.yaml &rarr; portal.json</code></dd></div>
          <div><dt>Machine index</dt><dd><a href="./llms.txt">llms.txt</a> &middot; JSON-LD 1.1</dd></div>
          <div><dt>WIPO patent</dt><dd><a href="https://patents.google.com/patent/WO2014003543A1/en" target="_blank" rel="noopener noreferrer">WO2014003543A1</a></dd></div>
          <div><dt>External trackers</dt><dd>0 (zero third-party scripts)</dd></div>
        </dl>
      </section>

      <section class="card side-card">
        <h2>Autonomous ecosystems</h2>
        {''.join(p3_rail_html)}
      </section>

      <section class="card side-card">
        <h2>Primary domains</h2>
        <ul class="domain-list">
          <li><a href="https://kleynenberg.com" target="_blank" rel="noopener noreferrer">kleynenberg.com</a><span>Publishing &amp; conservation</span></li>
          <li><a href="https://taksie.ai" target="_blank" rel="noopener noreferrer">taksie.ai</a><span>Fiscal AI pre-processor</span></li>
          <li><a href="https://innopheon.com" target="_blank" rel="noopener noreferrer">innopheon.com</a><span>Patent &amp; NLP intelligence</span></li>
          <li><a href="https://naaap.io" target="_blank" rel="noopener noreferrer">naaap.io</a><span>Audiovisual media network</span></li>
          <li><a href="https://moo.demetro.nl" target="_blank" rel="noopener noreferrer">moo.demetro.nl</a><span>Cloud-native MetroMoo</span></li>
        </ul>
      </section>
    </aside>
  </div>

  <!-- MANDATORY COLOPHON & NON-AFFILIATION FOOTER -->
  <footer class="site-footer" role="contentinfo">
    <div class="footer-inner">
      <p class="legal-notice">{esc(legal['non_affiliation_notice'])}</p>
      <p>&copy; {esc(legal['copyright_year_roman'])} <a href="{esc(legal['copyright_url'])}">{esc(legal['copyright_holder'])}</a>. All rights reserved.</p>
    </div>
  </footer>

  <script src="./app.js" defer></script>
</body>
</html>
'''


def build_style_css() -> str:
    return r'''/* ==============================================================================
 * INTEGRITY & METADATA HEADER
 * File:          style.css
 * Project:       Project UnLinked — Editorial Zero-Dependency Design System
 * Host Target:   https://kleynenberg.github.io (GitHub Pages)
 * Typography:    Curated local system font stacks (zero external font CDNs)
 * Themes:        Daylight Glass (default) & Future Dark
 * ============================================================================== */

:root {
  --font-sans: Inter, "SF Pro Text", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-serif: "Newsreader", "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  --font-mono: "JetBrains Mono", "SF Mono", "Fira Code", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

  --bg-canvas: #f4f2ee;
  --bg-surface: #ffffff;
  --bg-surface-elevated: rgba(255, 255, 255, 0.88);
  --bg-subtle: #f8f7f4;
  --bg-code: #141820;
  --fg-code: #e6edf3;

  --fg-primary: #191919;
  --fg-secondary: #4a4f55;
  --fg-muted: #666b73;

  --accent: #0a66c2;
  --accent-hover: #004182;
  --accent-soft: rgba(10, 102, 194, 0.09);
  --border-subtle: rgba(25, 25, 25, 0.11);
  --border-strong: rgba(25, 25, 25, 0.22);

  --banner-gradient: linear-gradient(125deg, #0f172a 0%, #1e293b 52%, #0a4a8f 100%);
  --shadow-card: 0 1px 3px rgba(15, 23, 42, 0.06), 0 8px 24px rgba(15, 23, 42, 0.04);
  --radius-card: 12px;
  --radius-pill: 999px;
}

html[data-theme="future-dark"] {
  --bg-canvas: #0b0e14;
  --bg-surface: #121722;
  --bg-surface-elevated: rgba(18, 23, 34, 0.88);
  --bg-subtle: #181f2e;
  --bg-code: #080b10;
  --fg-code: #e2e8f0;

  --fg-primary: #eef2f6;
  --fg-secondary: #b4becb;
  --fg-muted: #8895a7;

  --accent: #4da3ff;
  --accent-hover: #82bfff;
  --accent-soft: rgba(77, 163, 255, 0.14);
  --border-subtle: rgba(226, 232, 240, 0.11);
  --border-strong: rgba(226, 232, 240, 0.24);

  --banner-gradient: linear-gradient(125deg, #060911 0%, #0f1c33 55%, #123866 100%);
  --shadow-card: 0 2px 6px rgba(0, 0, 0, 0.35), 0 12px 32px rgba(0, 0, 0, 0.28);
}

*, *::before, *::after {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  scroll-padding-top: 76px;
}

body {
  margin: 0;
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.62;
  color: var(--fg-primary);
  background: var(--bg-canvas);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

code, pre {
  font-family: var(--font-mono);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.skip-link {
  position: absolute;
  left: -9999px;
  top: 8px;
  background: var(--accent);
  color: #ffffff;
  padding: 8px 14px;
  border-radius: 6px;
  z-index: 1000;
}

.skip-link:focus {
  left: 12px;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-surface-elevated);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--border-subtle);
  padding-top: env(titlebar-area-height, 0px);
}

.topbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.brand-cluster {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1 1 280px;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  color: var(--fg-primary);
  font-weight: 700;
  letter-spacing: -0.02em;
  text-decoration: none;
}

.brand-mark:hover {
  text-decoration: none;
  color: var(--accent);
}

.brand-emblem {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #ffffff;
  padding: 2px;
  border: 1px solid var(--border-subtle);
  object-fit: contain;
}

.brand-wordmark {
  font-size: 1.05rem;
}

.search-box {
  flex: 1 1 200px;
  max-width: 320px;
}

.search-box input {
  width: 100%;
  padding: 7px 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-subtle);
  background: var(--bg-subtle);
  color: var(--fg-primary);
  font-family: var(--font-sans);
  font-size: 0.86rem;
}

.search-box input:focus {
  outline: 2px solid var(--accent);
  border-color: transparent;
}

.topbar-nav {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 0.86rem;
}

.topbar-nav a {
  color: var(--fg-secondary);
  font-weight: 500;
}

.topbar-nav a:hover {
  color: var(--accent);
  text-decoration: none;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-telemetry {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--fg-muted);
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
}

.btn-ghost, .btn-install, .btn-secondary, .btn-secondary-sm, .btn-primary-sm {
  font-family: var(--font-sans);
  font-size: 0.82rem;
  font-weight: 600;
  border-radius: var(--radius-pill);
  cursor: pointer;
  transition: background-color 0.16s ease, border-color 0.16s ease, color 0.16s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-ghost {
  background: transparent;
  color: var(--fg-secondary);
  border: 1px solid var(--border-subtle);
  padding: 6px 12px;
}

.btn-ghost:hover {
  background: var(--bg-subtle);
  color: var(--fg-primary);
}

.btn-install, .btn-primary-sm {
  background: var(--accent);
  color: #ffffff;
  border: 1px solid var(--accent);
  padding: 6px 14px;
  text-decoration: none;
}

.btn-install:hover, .btn-primary-sm:hover {
  background: var(--accent-hover);
  color: #ffffff;
  text-decoration: none;
}

.btn-secondary, .btn-secondary-sm {
  background: var(--bg-subtle);
  color: var(--fg-primary);
  border: 1px solid var(--border-subtle);
  padding: 7px 14px;
  text-decoration: none;
}

.btn-secondary-sm {
  padding: 5px 11px;
  font-size: 0.8rem;
}

.btn-secondary:hover, .btn-secondary-sm:hover {
  border-color: var(--accent);
  color: var(--accent);
  text-decoration: none;
}

.page-shell {
  max-width: 1200px;
  margin: 22px auto 44px;
  padding: 0 20px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 310px;
  gap: 22px;
  align-items: start;
}

.main-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.side-column {
  position: sticky;
  top: 74px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: 24px 26px;
}

.side-card {
  padding: 20px;
}

h1, h2, h3, h4 {
  margin: 0;
  letter-spacing: -0.018em;
  line-height: 1.28;
  color: var(--fg-primary);
}

h1 { font-size: 1.65rem; font-weight: 700; }
h2 { font-size: 1.2rem; font-weight: 650; }
h3 { font-size: 1.02rem; font-weight: 620; }
h4 { font-size: 0.94rem; font-weight: 620; }

.hero-card {
  padding: 0;
  overflow: hidden;
}

.hero-banner {
  background: var(--banner-gradient);
  color: #f8fafc;
  padding: 26px 28px 54px;
}

.banner-hook-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.hook-block {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 10px;
  padding: 12px 15px;
}

.hook-start {
  background: rgba(10, 102, 194, 0.28);
  border-color: rgba(147, 197, 253, 0.35);
}

.hook-kicker {
  display: block;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: #cbd5e1;
  margin-bottom: 4px;
}

.hook-block p {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.48;
  color: #f8fafc;
}

.hero-body {
  padding: 0 28px 28px;
}

.avatar-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-top: -44px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.avatar-ring {
  position: relative;
  width: 112px;
  height: 112px;
  border-radius: 50%;
  background: #ffffff;
  padding: 6px;
  border: 3px solid var(--accent);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.14);
}

.avatar-ring img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: contain;
  display: block;
}

.ring-badge {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--accent);
  color: #ffffff;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: var(--radius-pill);
  border: 2px solid var(--bg-surface);
  white-space: nowrap;
}

.telemetry-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.telemetry-pill {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--fg-secondary);
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
}

.name-line {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.formal-tag {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--fg-muted);
}

.bio-headline {
  margin: 8px 0 6px;
  font-size: 1.03rem;
  font-weight: 500;
  color: var(--fg-primary);
}

.location-line {
  margin: 0;
  font-size: 0.88rem;
  color: var(--fg-muted);
}

.bio-link-hub {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.bio-link-chip {
  display: flex;
  flex-direction: column;
  padding: 10px 12px;
  border-radius: 9px;
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  text-decoration: none;
  transition: border-color 0.16s ease, transform 0.16s ease;
}

.bio-link-chip:hover {
  border-color: var(--accent);
  transform: translateY(-1px);
  text-decoration: none;
}

.bio-link-label {
  font-weight: 650;
  font-size: 0.88rem;
  color: var(--accent);
}

.bio-link-sub {
  font-size: 0.77rem;
  color: var(--fg-muted);
}

.about-pais {
  margin-top: 22px;
  padding-top: 20px;
  border-top: 1px solid var(--border-subtle);
}

.about-pais h2 {
  margin-bottom: 12px;
}

.pais-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.pais-step {
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: 9px;
  padding: 13px 15px;
}

.pais-solution {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.pais-label {
  display: block;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: var(--accent);
  margin-bottom: 4px;
}

.pais-step p {
  margin: 0;
  font-size: 0.88rem;
  color: var(--fg-secondary);
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.section-desc, .section-sub {
  margin: 4px 0 0;
  font-size: 0.88rem;
  color: var(--fg-muted);
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.featured-card {
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 10px;
}

.featured-card p {
  margin: 0;
  font-size: 0.86rem;
  color: var(--fg-secondary);
  flex-grow: 1;
}

.badge-subtle, .badge-accent, .period-tag, .category-tag, .status-pill, .archive-id {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  padding: 2px 8px;
  border-radius: 6px;
}

.badge-subtle, .category-tag, .status-pill {
  background: var(--bg-surface);
  color: var(--fg-secondary);
  border: 1px solid var(--border-subtle);
}

.badge-accent, .period-tag, .archive-id {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}

.spotlight-card {
  border-left: 4px solid var(--accent);
}

.lead-paragraph {
  margin: 0 0 16px;
  font-size: 0.95rem;
  color: var(--fg-secondary);
}

.spotlight-pillars-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.spotlight-pillar {
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: 9px;
  padding: 14px;
}

.spotlight-pillar p {
  margin: 6px 0 0;
  font-size: 0.85rem;
  color: var(--fg-secondary);
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.filter-chip {
  font-family: var(--font-sans);
  font-size: 0.81rem;
  font-weight: 500;
  padding: 5px 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-subtle);
  background: var(--bg-subtle);
  color: var(--fg-secondary);
  cursor: pointer;
}

.filter-chip:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.filter-chip.is-active {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.timeline-card {
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 16px 18px;
}

.timeline-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.org-line {
  margin: 3px 0 8px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--fg-muted);
}

.summary-line {
  margin: 0 0 10px;
  font-size: 0.9rem;
  color: var(--fg-secondary);
}

.proof-details summary {
  font-size: 0.83rem;
  font-weight: 600;
  color: var(--accent);
  cursor: pointer;
  user-select: none;
}

.proof-body {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border-subtle);
  font-size: 0.87rem;
  color: var(--fg-secondary);
}

.proof-body ul {
  margin: 0;
  padding-left: 18px;
}

.proof-body li {
  margin-bottom: 5px;
}

.code-artifact {
  margin-top: 10px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-code);
  color: var(--fg-code);
}

.code-artifact-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 6px 12px;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
}

.code-artifact pre {
  margin: 0;
  padding: 12px;
  font-size: 0.82rem;
  overflow-x: auto;
}

.milestone-links {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.inline-ext-link {
  font-size: 0.82rem;
  font-weight: 600;
}

.papers-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.paper-card {
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 18px;
}

.paper-header-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.paper-year, .meta-link {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--fg-muted);
}

.paper-authors {
  margin: 4px 0 2px;
  font-size: 0.86rem;
  font-weight: 500;
  color: var(--fg-primary);
}

.paper-venue {
  margin: 0 0 10px;
  font-size: 0.83rem;
  color: var(--fg-muted);
}

.paper-abstract {
  margin: 0 0 12px;
  font-family: var(--font-serif);
  font-size: 0.96rem;
  line-height: 1.58;
  color: var(--fg-secondary);
}

.paper-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.kw-chip, .stack-chip {
  font-family: var(--font-mono);
  font-size: 0.73rem;
  background: var(--bg-surface);
  color: var(--fg-secondary);
  border: 1px solid var(--border-subtle);
  padding: 2px 8px;
  border-radius: 5px;
}

.paper-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.pdf-slot-badge {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--fg-muted);
  background: var(--bg-surface);
  border: 1px dashed var(--border-strong);
  padding: 4px 10px;
  border-radius: 6px;
}

.repos-grid, .sandbox-grid, .media-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.repo-card, .sandbox-card, .media-card {
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 8px;
}

.repo-card.is-featured-repo {
  border-color: var(--accent);
}

.repo-meta-row, .sandbox-top, .media-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}

.repo-card p, .sandbox-card p, .media-card p {
  margin: 0;
  font-size: 0.87rem;
  color: var(--fg-secondary);
}

.stack-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.ksa-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(215px, 1fr));
  gap: 10px;
}

.ksa-card {
  background: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: 9px;
  padding: 12px;
}

.ksa-head {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 4px;
}

.ksa-code {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--accent);
}

.ksa-name {
  font-weight: 650;
  font-size: 0.9rem;
}

.ksa-focus {
  margin: 0;
  font-size: 0.81rem;
  color: var(--fg-secondary);
}

.media-card ul {
  margin: 4px 0 0;
  padding-left: 18px;
  font-size: 0.84rem;
  color: var(--fg-secondary);
}

.location-tag {
  font-size: 0.78rem;
  color: var(--fg-muted);
}

.is-placeholder {
  border-style: dashed;
  border-color: var(--border-strong);
  opacity: 0.88;
}

.telemetry-dl {
  margin: 12px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 0.84rem;
}

.telemetry-dl dt {
  font-size: 0.75rem;
  color: var(--fg-muted);
}

.telemetry-dl dd {
  margin: 1px 0 0;
  font-weight: 500;
}

.rail-ecosystem {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
}

.rail-ecosystem:first-of-type {
  border-top: none;
  padding-top: 0;
}

.rail-eco-title {
  font-weight: 650;
  font-size: 0.9rem;
}

.rail-ecosystem p {
  margin: 4px 0 0;
  font-size: 0.82rem;
  color: var(--fg-secondary);
}

.domain-list {
  list-style: none;
  margin: 12px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.domain-list li {
  display: flex;
  flex-direction: column;
  font-size: 0.84rem;
}

.domain-list span {
  font-size: 0.76rem;
  color: var(--fg-muted);
}

.site-footer {
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  padding: 24px 20px 32px;
  margin-top: 32px;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  font-size: 0.82rem;
  color: var(--fg-muted);
}

.footer-inner p {
  margin: 0 0 8px;
}

.footer-inner p:last-child {
  margin-bottom: 0;
  color: var(--fg-secondary);
}

@media (max-width: 960px) {
  .page-shell {
    grid-template-columns: 1fr;
  }
  .side-column {
    position: static;
  }
  .featured-grid, .spotlight-pillars-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .banner-hook-grid, .pais-grid, .repos-grid, .sandbox-grid, .media-grid {
    grid-template-columns: 1fr;
  }
  .topbar-nav {
    display: none;
  }
}
'''


def build_app_js() -> str:
    return r'''/* ==============================================================================
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
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile portal.yaml into the Project UnLinked sovereign static SPA/PWA.")
    parser.add_argument("--root", default=".", help="Repository root directory (default: current directory)")
    parser.add_argument("--yaml", default="portal.yaml", help="Path to portal.yaml relative to --root")
    args = parser.parse_args()

    root_dir = Path(args.root).resolve()
    yaml_path = root_dir / args.yaml

    config = load_portal_config(yaml_path)
    branding = config["meta"]["branding"]

    extract_pwa_icons(
        root_dir=root_dir,
        svg_name=branding["primary_svg_icon"],
        icon_192=branding["pwa_icon_192"],
        icon_512=branding["pwa_icon_512"],
    )
    reconcile_papers(root_dir, config)

    portal_json_str = json.dumps(config, indent=2, ensure_ascii=False) + "\n"
    manifest_str = build_manifest(config)
    index_html_str = build_index_html(config)
    style_css_str = build_style_css()
    app_js_str = build_app_js()
    llms_txt_str = build_llms_txt(config)

    digest = hashlib.sha256()
    for blob in (portal_json_str, manifest_str, index_html_str, style_css_str, app_js_str, llms_txt_str):
        digest.update(blob.encode("utf-8"))
    build_hash = digest.hexdigest()[:12]

    sw_js_str = build_service_worker(config, build_hash)

    outputs = {
        "portal.json": portal_json_str,
        "manifest.webmanifest": manifest_str,
        "index.html": index_html_str,
        "style.css": style_css_str,
        "app.js": app_js_str,
        "sw.js": sw_js_str,
        "llms.txt": llms_txt_str,
    }

    for filename, content in outputs.items():
        out_path = root_dir / filename
        out_path.write_text(content, encoding="utf-8")
        print(f"[OK]   Wrote {out_path.name} ({len(content.encode('utf-8'))} bytes)")

    print(f"[DONE] Sovereign PWA build complete (hash={build_hash}) at {datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
