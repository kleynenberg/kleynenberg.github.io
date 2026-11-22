#!/usr/bin/env python3

# ==============================================================================
# INTEGRITY HEADER
# File: llms_corpus_builder.py
# Target: /home/steve/gemini/github.io/trawling/llms_corpus_builder.py
# Host: hp.kleynenberg.net (Fedora Linux 45, Python 3.11+)
# Mode: Deterministic --no-ai support + Vertex AI (global / gemini-3.5-flash)
# Policy: No fabricated/dummy data; no hidden paths/IGNORE files; .bak on deploy
# ==============================================================================
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

CANONICAL_ORIGIN = "https://steven.kleynenberg.com/"
MIRROR_ORIGIN = "https://kleynenberg.github.io/"
DEFAULT_PROJECT = "gemini-development-hub-2026"
DEFAULT_LOCATION = "global"
DEFAULT_MODEL = "gemini-3.5-flash"
DEFAULT_TIMEOUT = 90
DEFAULT_MAX_OUTPUT_TOKENS = 4096

IGNORED_NAMES = {
    "IGNORE.",
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}
PRIVILEGED_STEMS = {
    "timeline_distill_cache",
    "portal",
    "secrets",
    "credentials",
    "service_account",
}

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")
URL_RE = re.compile(r"https?://[^\s<>()\"'\]]+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")

RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING"},
        "year": {"type": "STRING"},
        "summary": {"type": "STRING"},
        "dois": {"type": "ARRAY", "items": {"type": "STRING"}},
        "urls": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["title", "year", "summary", "dois", "urls"],
}


def log_msg(level: str, msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def should_skip_path(path: Path) -> bool:
    for part in path.parts:
        if (
            part.startswith(".")
            or part.startswith("IGNORE.")
            or part in IGNORED_NAMES
        ):
            return True
    return False


def is_privileged_source_file(path: Path) -> bool:
    stem = path.stem.lower()
    if (
        stem in PRIVILEGED_STEMS
        or stem.startswith("ignore.")
        or stem.startswith(".")
    ):
        return True
    return False


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def read_text_strict(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Kan tekst niet decoderen voor {path.name}")


def extract_primary_year(title_or_name: str, text: str) -> str:
    for source in (title_or_name, text[:4000]):
        years = YEAR_RE.findall(source)
        if years:
            return years[0]
    return ""


def clean_label_title(label: str) -> str:
    base = Path(label).name
    stem = Path(base).stem
    if re.fullmatch(r"[0-9a-fA-F]{16,}", stem):
        return f"Document {stem[:12]}"
    cleaned = re.sub(r"[_-]+", " ", stem).strip()
    return cleaned if cleaned else base


def scan_sources(
    trawling_dir: Path, papers_dir: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scan_roots = [
        trawling_dir / "input" / "raw",
        trawling_dir / "input" / "texts",
        papers_dir,
    ]
    roots_display = ", ".join(str(p) for p in scan_roots)
    log_msg("INPUT", f"Scannen van {roots_display} ...")

    seen_hashes: set[str] = set()
    docs: list[dict[str, Any]] = []
    published_papers: list[dict[str, Any]] = []
    allowed_suffixes = {
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".html",
        ".htm",
        ".csv",
    }

    for root in scan_roots:
        if not root.exists():
            continue
        for current_root, dirnames, filenames in os.walk(root):
            cur_path = Path(current_root)
            if should_skip_path(cur_path):
                dirnames[:] = []
                continue
            dirnames[:] = [
                d
                for d in sorted(dirnames)
                if not d.startswith(".")
                and not d.startswith("IGNORE.")
                and d not in IGNORED_NAMES
            ]
            for fname in sorted(filenames):
                if fname.startswith(".") or fname.startswith("IGNORE."):
                    continue
                fpath = cur_path / fname
                if should_skip_path(fpath) or not fpath.is_file():
                    continue
                if root != papers_dir and is_privileged_source_file(fpath):
                    continue

                digest = sha256_file(fpath)
                if digest in seen_hashes:
                    rel_label = (
                        str(fpath.relative_to(trawling_dir))
                        if fpath.is_relative_to(trawling_dir)
                        else fpath.name
                    )
                    log_msg(
                        "DEDUP",
                        f"Identieke inhoud overgeslagen: {rel_label} "
                        f"(sha256={digest[:12]})",
                    )
                    continue
                seen_hashes.add(digest)

                if root == papers_dir:
                    published_papers.append(
                        {
                            "filename": fpath.name,
                            "sha256": digest,
                            "size_bytes": fpath.stat().st_size,
                            "year": extract_primary_year(fpath.name, ""),
                        }
                    )
                    continue

                if fpath.suffix.lower() not in allowed_suffixes:
                    continue

                text = read_text_strict(fpath)
                rel_label = (
                    str(fpath.relative_to(trawling_dir))
                    if fpath.is_relative_to(trawling_dir)
                    else fpath.name
                )
                docs.append(
                    {
                        "id": digest[:16],
                        "sha256": digest,
                        "label": rel_label,
                        "filename": fpath.name,
                        "text": text,
                        "chars": len(text),
                    }
                )

    log_msg(
        "INPUT",
        f"Unieke verwerkbare brondocumenten: {len(docs)} | "
        f"Gepubliceerde bestanden in /papers/: {len(published_papers)}",
    )
    return docs, published_papers


def extract_deterministic_fact(doc: dict[str, Any]) -> dict[str, Any]:
    text = doc["text"]
    label = doc["label"]
    title = clean_label_title(label)
    year = extract_primary_year(label, text)

    dois = sorted(
        set(m.group(0).rstrip(".,);]") for m in DOI_RE.finditer(text))
    )
    urls = sorted(
        set(m.group(0).rstrip(".,);]") for m in URL_RE.finditer(text))
    )

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    heading = ""
    for ln in lines[:25]:
        if ln.startswith("#"):
            heading = ln.lstrip("#").strip()
            break

    snippet_source = " ".join(lines[:12])
    snippet = re.sub(r"\s+", " ", snippet_source).strip()[:280]
    fallback_summary = f"Bronbestand {title} ({doc['chars']} tekens)"
    summary = heading if heading else (snippet if snippet else fallback_summary)

    return {
        "source_id": doc["id"],
        "sha256": doc["sha256"],
        "source_label": label,
        "title": title,
        "year": year,
        "summary": summary,
        "dois": dois[:25],
        "urls": urls[:25],
        "chars": doc["chars"],
        "mode": "deterministic-no-ai",
    }


def get_gcloud_access_token() -> str:
    env_token = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN", "").strip()
    if env_token:
        return env_token

    proc = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = proc.stderr.strip()
        raise RuntimeError(
            f"Kon geen Vertex AI OAuth2 token ophalen via gcloud: {err}"
        )
    token = proc.stdout.strip()
    if not token:
        raise RuntimeError(
            "Leeg OAuth2 access token ontvangen van gcloud auth print-access-token"
        )
    return token


class VertexGeminiClient:
    def __init__(
        self,
        project: str,
        location: str,
        model: str,
        timeout: int,
        max_output_tokens: int,
    ) -> None:
        self.project = project
        self.location = location
        self.model = model
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens
        self.access_token = get_gcloud_access_token()

    def endpoint_url(self) -> str:
        if self.location == "global":
            host = "aiplatform.googleapis.com"
        else:
            host = f"{self.location}-aiplatform.googleapis.com"
        return (
            f"https://{host}/v1/projects/{self.project}"
            f"/locations/{self.location}/publishers/google"
            f"/models/{self.model}:generateContent"
        )

    def generate_json(self, doc: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "Extract structured metadata from the provided source text as "
            "strict valid JSON. Keep string fields concise so JSON is never "
            'truncated. Return JSON object with keys: "title" (string), '
            '"year" (string), "summary" (string, max 2 sentences), '
            '"dois" (array of strings), "urls" (array of strings).\n\n'
            f"Source label: {doc['label']}\n"
            f"Source text:\n{doc['text']}"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": self.max_output_tokens,
                "responseMimeType": "application/json",
                "responseSchema": RESPONSE_SCHEMA,
            },
        }
        body = json.dumps(payload).encode("utf-8")
        req = urlrequest.Request(
            self.endpoint_url(),
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                raw_resp = resp.read().decode("utf-8")
        except TimeoutError as exc:
            raise RuntimeError("The read operation timed out") from exc
        except urlerror.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {detail[:500]}") from exc
        except urlerror.URLError as exc:
            reason_str = str(exc.reason)
            if "timed out" in reason_str.lower():
                raise RuntimeError("The read operation timed out") from exc
            raise RuntimeError(f"Netwerkfout: {reason_str}") from exc

        envelope = json.loads(raw_resp)
        candidates = envelope.get("candidates") or []
        if not candidates:
            raise RuntimeError("Geen candidates in Vertex AI response")

        cand0 = candidates[0]
        finish_reason = str(cand0.get("finishReason") or "UNKNOWN")
        if finish_reason not in {"STOP", "UNKNOWN"}:
            raise RuntimeError(
                f"Onvolledige generatie (finishReason={finish_reason})"
            )

        parts = ((cand0.get("content") or {}).get("parts")) or []
        text_out = "".join(
            p.get("text", "") for p in parts if isinstance(p, dict)
        ).strip()
        if not text_out:
            raise RuntimeError("Lege tekst in Vertex AI candidate response")

        parsed = json.loads(text_out)
        if not isinstance(parsed, dict):
            raise RuntimeError("Modeluitvoer is geen JSON-object")

        raw_title = parsed.get("title") or clean_label_title(doc["label"])
        raw_year = parsed.get("year") or extract_primary_year(
            doc["label"], doc["text"]
        )
        dois = [
            str(x).strip()
            for x in (parsed.get("dois") or [])
            if str(x).strip()
        ]
        urls = [
            str(x).strip()
            for x in (parsed.get("urls") or [])
            if str(x).strip()
        ]

        return {
            "source_id": doc["id"],
            "sha256": doc["sha256"],
            "source_label": doc["label"],
            "title": str(raw_title).strip(),
            "year": str(raw_year).strip(),
            "summary": str(parsed.get("summary") or "").strip(),
            "dois": dois,
            "urls": urls,
            "chars": doc["chars"],
            "mode": f"vertex-ai:{self.model}",
        }


def load_cache(cache_path: Path) -> dict[str, dict[str, Any]]:
    if not cache_path.exists():
        return {}
    data = json.loads(read_text_strict(cache_path))
    if not isinstance(data, dict):
        return {}
    entries = data.get("entries")
    if isinstance(entries, dict):
        return entries
    return {}


def save_cache(cache_path: Path, entries: dict[str, dict[str, Any]]) -> None:
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }
    cache_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def distill_documents(
    docs: list[dict[str, Any]],
    no_ai: bool,
    cache_path: Path,
    client: VertexGeminiClient | None,
    retries: int = 2,
) -> list[dict[str, Any]]:
    if no_ai:
        log_msg(
            "MODE",
            "--no-ai actief: deterministische lokale extractie zonder Vertex AI.",
        )
        facts: list[dict[str, Any]] = []
        total = len(docs)
        for idx, doc in enumerate(docs, start=1):
            fact = extract_deterministic_fact(doc)
            facts.append(fact)
            log_msg("NO-AI", f"[{idx}/{total}] {doc['label']} -> {fact['title']}")
        return facts

    assert client is not None
    log_msg(
        "AUTH",
        f"Vertex AI OAuth2 actief voor project '{client.project}' "
        f"(location={client.location}, model={client.model}).",
    )
    cache_entries = load_cache(cache_path)
    facts = []
    total = len(docs)

    for idx, doc in enumerate(docs, start=1):
        cache_key = f"{doc['sha256']}:{client.model}"
        if cache_key in cache_entries:
            facts.append(cache_entries[cache_key])
            log_msg(
                "CACHE", f"[{idx}/{total}] {doc['label']} geladen uit cache."
            )
            continue

        log_msg(
            "AI DISTILL",
            f"[{idx}/{total}] {doc['label']} ({doc['chars']} tekens)...",
        )
        attempt = 0
        while True:
            try:
                fact = client.generate_json(doc)
                cache_entries[cache_key] = fact
                save_cache(cache_path, cache_entries)
                facts.append(fact)
                log_msg(
                    "AI DONE",
                    f"[{idx}/{total}] {doc['label']} -> {fact['title']}",
                )
                break
            except Exception as exc:
                if attempt < retries:
                    attempt += 1
                    wait_s = min(2 ** (attempt - 1), 8)
                    log_msg(
                        "RETRY",
                        f"Netwerk-/parsefout ({exc}); wacht {wait_s}s "
                        f"(poging {attempt}/{retries})...",
                    )
                    time.sleep(wait_s)
                else:
                    log_msg("FATAL ERROR", str(exc))
                    raise RuntimeError(str(exc)) from exc

    return facts


def build_consolidated_corpus(
    facts: list[dict[str, Any]],
    published_papers: list[dict[str, Any]],
    no_ai: bool,
) -> dict[str, Any]:
    all_dois: list[str] = []
    all_urls: list[str] = []
    seen_dois: set[str] = set()
    seen_urls: set[str] = set()

    for f in facts:
        for d in f.get("dois", []):
            if d not in seen_dois:
                seen_dois.add(d)
                all_dois.append(d)
        for u in f.get("urls", []):
            if u not in seen_urls:
                seen_urls.add(u)
                all_urls.append(u)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_origin": CANONICAL_ORIGIN,
        "mirror_origin": MIRROR_ORIGIN,
        "mode": "no-ai-deterministic" if no_ai else "vertex-ai",
        "document_count": len(facts),
        "published_papers_count": len(published_papers),
        "dois": all_dois,
        "urls": all_urls,
        "facts": facts,
        "published_papers": published_papers,
    }


def render_llms_txt(corpus: dict[str, Any]) -> str:
    lines = [
        "# Steven Kleynenberg — Corpus & Publications",
        f"> Generated in {corpus['mode']} mode from local sources and /papers/.",
        f"- Canonical URL: {CANONICAL_ORIGIN}",
        f"- Mirror URL: {MIRROR_ORIGIN}",
        "- llms.txt specification: https://llmstxt.org/",
        "",
        "## Published Papers (/papers/)",
    ]
    for p in corpus["published_papers"]:
        yr = f" ({p['year']})" if p.get("year") else ""
        lines.append(f"- {p['filename']}{yr}")
    if not corpus["published_papers"]:
        lines.append("- Geen gepubliceerde bestanden gevonden in /papers/.")

    lines.extend(["", "## Source Entries"])
    for f in corpus["facts"]:
        yr = f" [{f['year']}]" if f.get("year") else ""
        lines.append(f"- {f['title']}{yr}: {f['summary']}")

    if corpus["dois"]:
        lines.extend(["", "## DOIs"])
        for d in corpus["dois"]:
            lines.append(f"- https://doi.org/{d}")

    return "\n".join(lines).strip() + "\n"


def render_llms_full_txt(corpus: dict[str, Any]) -> str:
    sections = [
        "# Steven Kleynenberg — Full Deterministic & Curated Corpus",
        f"Generated-At: {corpus['generated_at']}",
        f"Mode: {corpus['mode']}",
        f"Canonical: {CANONICAL_ORIGIN}",
        f"Mirror: {MIRROR_ORIGIN}",
        f"Source-Documents: {corpus['document_count']}",
        f"Published-Papers: {corpus['published_papers_count']}",
        "",
        "## Published Papers",
    ]
    for p in corpus["published_papers"]:
        yr = p.get("year") or "n/a"
        sections.append(
            f"- File: {p['filename']} | Year: {yr} | SHA256: {p['sha256']}"
        )

    sections.append("\n## Extracted Source Records")
    for f in corpus["facts"]:
        sections.append(f"### {f['title']}")
        sections.append(f"- Source: {f['source_label']}")
        sections.append(f"- Year: {f.get('year') or 'n/a'}")
        sections.append(f"- Summary: {f['summary']}")
        if f.get("dois"):
            sections.append(f"- DOIs: {', '.join(f['dois'])}")
        if f.get("urls"):
            sections.append(f"- URLs: {', '.join(f['urls'])}")
        sections.append("")

    return "\n".join(sections).strip() + "\n"


def render_index_html(corpus: dict[str, Any], llms_txt_content: str) -> str:
    json_ld = {
        "@context": "https://schema.org/",
        "@type": "WebSite",
        "name": "Steven Kleynenberg",
        "url": CANONICAL_ORIGIN,
        "sameAs": [MIRROR_ORIGIN],
        "dateModified": corpus["generated_at"],
    }
    json_ld_str = json.dumps(json_ld, indent=2, ensure_ascii=False)

    paper_items = []
    for p in corpus["published_papers"]:
        fname_esc = html.escape(p["filename"])
        yr_esc = html.escape(p.get("year") or "")
        yr_part = f" ({yr_esc})" if yr_esc else ""
        paper_items.append(
            f'      <li><a href="papers/{fname_esc}">{fname_esc}</a>'
            f"{yr_part}</li>"
        )
    papers_html = (
        "\n".join(paper_items)
        if paper_items
        else "      <li>Geen bestanden in /papers/</li>"
    )

    fact_items = []
    for f in corpus["facts"]:
        title_esc = html.escape(f["title"])
        sum_esc = html.escape(f["summary"])
        yr_esc = html.escape(f.get("year") or "")
        yr_badge = f" <span>[{yr_esc}]</span>" if yr_esc else ""
        fact_items.append(
            f"      <li><strong>{title_esc}</strong>{yr_badge}: "
            f"{sum_esc}</li>"
        )
    facts_html = (
        "\n".join(fact_items)
        if fact_items
        else "      <li>Geen brondocumenten verwerkt</li>"
    )

    llms_pre_esc = html.escape(llms_txt_content)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Steven Kleynenberg — Publications &amp; Corpus</title>
  <link rel="canonical" href="{CANONICAL_ORIGIN}">
  <script type="application/ld+json">
{json_ld_str}
  </script>
</head>
<body>
  <main>
    <h1>Steven Kleynenberg</h1>
    <p>Mode: {html.escape(corpus['mode'])} | Documenten: {corpus['document_count']} | Papers: {corpus['published_papers_count']}</p>
    <section id="papers">
      <h2>Gepubliceerde bestanden (/papers/)</h2>
      <ul>
{papers_html}
      </ul>
    </section>
    <section id="sources">
      <h2>Verwerkte bronnen</h2>
      <ul>
{facts_html}
      </ul>
    </section>
    <section id="llms-txt">
      <h2>llms.txt</h2>
      <pre>{llms_pre_esc}</pre>
    </section>
  </main>
</body>
</html>
"""


def write_file_with_optional_backup(
    target: Path, content: str, make_backup: bool
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if make_backup and target.exists():
        bak_path = target.with_name(target.name + ".bak")
        shutil.copy2(target, bak_path)
        log_msg("BACKUP", f"Backup gemaakt: {bak_path}")
    target.write_text(content, encoding="utf-8")
    log_msg("WRITE", f"Geschreven: {target}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build llms.txt, llms-full.txt, and index.html."
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Draai volledig zonder Vertex AI-aanroepen.",
    )
    parser.add_argument(
        "--project",
        default=DEFAULT_PROJECT,
        help=f"GCP project ID (default: {DEFAULT_PROJECT})",
    )
    parser.add_argument(
        "--location",
        default=DEFAULT_LOCATION,
        help=f"Vertex AI location (default: {DEFAULT_LOCATION})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model ID (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Read timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=DEFAULT_MAX_OUTPUT_TOKENS,
        help=f"Max output tokens per request (default: {DEFAULT_MAX_OUTPUT_TOKENS})",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Schakel eventuele model-fallbacks expliciet uit.",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Schrijf direct naar live doelbestanden (met .bak backup).",
    )
    parser.add_argument(
        "--trawling-dir",
        type=Path,
        default=None,
        help="Pad naar trawling-directory.",
    )
    parser.add_argument(
        "--papers-dir",
        type=Path,
        default=None,
        help="Pad naar papers-directory.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Pad naar uitvoerdirectory.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    script_dir = Path(__file__).resolve().parent
    trawling_dir = (
        args.trawling_dir.resolve() if args.trawling_dir else script_dir
    )
    repo_root = trawling_dir.parent
    papers_dir = (
        args.papers_dir.resolve()
        if args.papers_dir
        else (repo_root / "papers")
    )

    if args.out_dir:
        out_dir = args.out_dir.resolve()
    elif args.deploy:
        out_dir = repo_root
    else:
        out_dir = trawling_dir / "stage"

    docs, published_papers = scan_sources(trawling_dir, papers_dir)
    cache_path = trawling_dir / "timeline_distill_cache.json"

    client: VertexGeminiClient | None = None
    if not args.no_ai:
        client = VertexGeminiClient(
            project=args.project,
            location=args.location,
            model=args.model,
            timeout=args.timeout,
            max_output_tokens=args.max_output_tokens,
        )

    facts = distill_documents(
        docs=docs,
        no_ai=args.no_ai,
        cache_path=cache_path,
        client=client,
        retries=2,
    )

    corpus = build_consolidated_corpus(
        facts=facts,
        published_papers=published_papers,
        no_ai=args.no_ai,
    )

    llms_txt = render_llms_txt(corpus)
    llms_full_txt = render_llms_full_txt(corpus)
    index_html = render_index_html(corpus, llms_txt)

    write_file_with_optional_backup(
        out_dir / "llms.txt", llms_txt, make_backup=args.deploy
    )
    write_file_with_optional_backup(
        out_dir / "llms-full.txt", llms_full_txt, make_backup=args.deploy
    )
    write_file_with_optional_backup(
        out_dir / "index.html", index_html, make_backup=args.deploy
    )

    log_msg("DONE", f"Voltooid in {out_dir}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log_msg("FATAL ERROR", str(exc))
        sys.exit(1)