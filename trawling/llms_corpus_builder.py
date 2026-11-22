#!/usr/bin/env python3
# ==============================================================================
# INTEGRITY & METADATA HEADER
# File:          llms_corpus_builder.py
# Project:       steven.kleynenberg.com — INPUT => AI ==> OUTPUT Compiler
# Target Host:   https://steven.kleynenberg.com/ & https://kleynenberg.github.io/
# Runtime:       Fedora Linux 45 (https://fedoraproject.org/) / Python 3.11+
# AI Endpoint:   Google Cloud Vertex AI generateContent API
#                (https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations)
# Output Specs:  https://llmstxt.org/ | https://schema.org/
# Integrity Rules:
#   - 100% read-only on all INPUT files and local_project_trawler.py.
#   - Strictly skips any directory or file prefixed with "IGNORE." or ".".
#   - Zero localhost workstation scanning; zero dummy/fabricated data.
#   - Uses proven Vertex AI global / gemini-3.5-flash via gcloud OAuth2 token.
#   - Never overwrites live repo files without explicit --deploy + .bak backup.
# ==============================================================================

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# ------------------------------------------------------------------------------
# 1. CANONICAL PATHS & CONSTANTS
# ------------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_RAW_DIR = SCRIPT_DIR / "input" / "raw"
DEFAULT_TEXTS_DIR = SCRIPT_DIR / "input" / "texts"
DEFAULT_PAPERS_DIR = REPO_ROOT / "papers"
DEFAULT_HTML_TEMPLATE = REPO_ROOT / "index.html"
DEFAULT_KEY_FILE = SCRIPT_DIR / "gemini_key.json"
DEFAULT_OUT_DIR = SCRIPT_DIR / "output" / "llms"

DEFAULT_PROJECT = "gemini-development-hub-2026"
DEFAULT_LOCATION = "global"
DEFAULT_MODEL = "gemini-3.5-flash"

CANONICAL_BASE_URL = "https://steven.kleynenberg.com"
MIRROR_BASE_URL = "https://kleynenberg.github.io"
PUBLISHER_URL = "https://kleynenberg.com"
PODCAST_URL = "https://www.youtube.com/playlist?list=PLAN7_k5CM5ZY"
PATENT_URL = "https://patents.google.com/patent/WO2014003543A1"
MIT_LICENSE_URL = "https://opensource.org/license/mit"
GITHUB_REPO_URL = "https://github.com/kleynenberg/kleynenberg.github.io"

DISTILL_PROMPT_VERSION = "timeline-distill-v1.2"
CONSOLIDATE_PROMPT_VERSION = "timeline-consolidate-v1.2"

FALLBACK_LOCATIONS = ("global", "us-central1", "europe-west4")
FALLBACK_MODELS = ("gemini-3.5-flash", "gemini-2.5-flash")

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".tex",
    ".xml",
    ".sh",
    ".html",
    ".htm",
    ".csv",
    ".bib",
}

SECRET_LINE_RE = re.compile(
    r"(?i)(api[_-]?key|secret|token|password|passwd|private[_-]?key|"
    r"client[_-]?secret|authorization:\s*bearer)\s*[:=]\s*['\"]?"
    r"[A-Za-z0-9_\-\.\/\+]{12,}"
)
LOCAL_PATH_RE = re.compile(
    r"(/home/[A-Za-z0-9_.-]+(?:/[^\s'\"<>)]*)?|"
    r"/mnt/[A-Za-z0-9_.-]+(?:/[^\s'\"<>)]*)?|192\.168\.\d+\.\d+)"
)
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")
URL_RE = re.compile(r"https?://[^\s<>'\"\)\]]+")

VERIFIED_PUBLIC_DOMAINS = (
    "steven.kleynenberg.com",
    "kleynenberg.github.io",
    "kleynenberg.com",
    "kleynenberg.nl",
    "kleynenberg.org",
    "kleynenberg.net",
    "naaap.io",
    "innopheon.com",
    "taksie.ai",
    "axitax.nl",
    "axitax.com",
    "doi.org",
    "patents.google.com",
    "itea4.org",
    "eurekanetwork.org",
    "youtube.com",
    "github.com",
    "opensource.org",
    "link.springer.com",
    "ieeexplore.ieee.org",
    "sciencedirect.com",
)


class FatalAuthError(RuntimeError):
    """Raised immediately on unrecoverable Vertex AI auth/endpoint failure."""


def log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def is_ignored_name(name: str) -> bool:
    return name.startswith(".") or name.startswith("IGNORE.")


def sanitize_text(raw: str) -> str:
    cleaned_lines: list[str] = []
    for line in raw.splitlines():
        if SECRET_LINE_RE.search(line):
            continue
        line = LOCAL_PATH_RE.sub("[REDACTED_LOCAL_PATH]", line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def normalize_doi(raw_doi: str) -> str:
    d = raw_doi.strip()
    d = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", d, flags=re.IGNORECASE)
    d = d.rstrip(".,;:)]}>'\"")
    if not DOI_RE.match(d):
        return ""
    return f"https://doi.org/{d}"


def clean_url(raw_url: str) -> str:
    u = raw_url.strip().rstrip(".,;:)]}>'\"")
    parsed = urllib.parse.urlparse(u)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""
    if "192.168." in parsed.netloc or "localhost" in parsed.netloc:
        return ""
    return u


def extract_dois_and_urls(text: str) -> tuple[list[str], list[str]]:
    dois: set[str] = set()
    for m in DOI_RE.finditer(text):
        norm = normalize_doi(m.group(1))
        if norm:
            dois.add(norm)

    urls: set[str] = set()
    for m in URL_RE.finditer(text):
        cu = clean_url(m.group(0))
        if not cu:
            continue
        if "doi.org/" in cu.lower():
            norm = normalize_doi(cu)
            if norm:
                dois.add(norm)
            continue
        urls.add(cu)

    return sorted(dois), sorted(urls)


# ------------------------------------------------------------------------------
# 2. UNIFORM INPUT LOADER & SHA-256 DEDUPLICATION
# ------------------------------------------------------------------------------
def extract_xml_text(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
        chunks: list[str] = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                chunks.append(elem.text.strip())
            if elem.tail and elem.tail.strip():
                chunks.append(elem.tail.strip())
        return "\n".join(chunks)
    except ET.ParseError:
        return xml_bytes.decode("utf-8", errors="replace")


def extract_pdf_fallback(pdf_path: Path) -> str:
    pdftotext_bin = shutil.which("pdftotext")
    if pdftotext_bin:
        try:
            proc = subprocess.run(
                [pdftotext_bin, "-enc", "UTF-8", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout
        except Exception as exc:
            log(f"[WARN] pdftotext mislukt voor {pdf_path.name}: {exc}")
    return ""


def load_corpus_documents(
    raw_dir: Path,
    texts_dir: Path,
    papers_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """
    Leest alle niet-IGNORE. bestanden uit raw/, texts/ en inventariseert papers/.
    Koppelt companion .txt uit texts/ aan raw/ via MD5 of bestands-stem.
    """
    log(f"[INPUT] Scannen van {raw_dir}, {texts_dir} en {papers_dir} ...")

    texts_by_stem: dict[str, Path] = {}
    if texts_dir.is_dir():
        for p in sorted(texts_dir.iterdir()):
            if (
                p.is_file()
                and not is_ignored_name(p.name)
                and p.suffix.lower() == ".txt"
            ):
                texts_by_stem[p.stem.lower()] = p

    consumed_text_stems: set[str] = set()
    seen_content_hashes: set[str] = set()
    documents: list[dict[str, Any]] = []

    def register_doc(
        source_label: str,
        raw_name: str,
        text_content: str,
        companion_text_name: str | None = None,
    ) -> None:
        sanitized = sanitize_text(text_content)
        if len(sanitized.strip()) < 40:
            log(
                f"[SKIP] Te weinig bruikbare tekst in {source_label} "
                f"({len(sanitized.strip())} tekens)"
            )
            return
        norm_for_hash = re.sub(r"\s+", " ", sanitized).strip()
        content_hash = sha256_text(norm_for_hash)
        if content_hash in seen_content_hashes:
            log(
                f"[DEDUP] Identieke inhoud overgeslagen: {source_label} "
                f"(sha256={content_hash[:12]})"
            )
            return
        seen_content_hashes.add(content_hash)

        dois, urls = extract_dois_and_urls(sanitized)
        documents.append(
            {
                "doc_id": content_hash[:16],
                "sha256": content_hash,
                "source_label": source_label,
                "raw_filename": raw_name,
                "companion_text": companion_text_name or "",
                "char_count": len(sanitized),
                "text": sanitized,
                "extracted_dois": dois,
                "extracted_urls": urls,
            }
        )

    if raw_dir.is_dir():
        for p in sorted(raw_dir.iterdir()):
            if not p.is_file() or is_ignored_name(p.name):
                continue
            raw_bytes = p.read_bytes()
            file_md5 = md5_bytes(raw_bytes).lower()
            stem_lower = p.stem.lower()
            ext = p.suffix.lower()

            matched_txt_path: Path | None = None
            if file_md5 in texts_by_stem:
                matched_txt_path = texts_by_stem[file_md5]
                consumed_text_stems.add(file_md5)
            elif stem_lower in texts_by_stem:
                matched_txt_path = texts_by_stem[stem_lower]
                consumed_text_stems.add(stem_lower)

            text_data = ""
            companion_name = matched_txt_path.name if matched_txt_path else None

            if ext == ".xml":
                xml_plain = extract_xml_text(raw_bytes)
                txt_plain = (
                    matched_txt_path.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    if matched_txt_path
                    else ""
                )
                text_data = (
                    xml_plain if len(xml_plain) >= len(txt_plain) else txt_plain
                )
            elif ext in TEXT_EXTENSIONS:
                text_data = raw_bytes.decode("utf-8", errors="replace")
            elif ext == ".pdf":
                if matched_txt_path:
                    text_data = matched_txt_path.read_text(
                        encoding="utf-8", errors="replace"
                    )
                else:
                    text_data = extract_pdf_fallback(p)
                    if not text_data:
                        log(
                            f"[WARN] Geen geëxtraheerde tekst voor PDF "
                            f"{p.name} (md5={file_md5})"
                        )
            else:
                if matched_txt_path:
                    text_data = matched_txt_path.read_text(
                        encoding="utf-8", errors="replace"
                    )

            if text_data:
                register_doc(
                    f"input/raw/{p.name}", p.name, text_data, companion_name
                )

    for stem, txt_path in sorted(texts_by_stem.items()):
        if stem in consumed_text_stems:
            continue
        txt_data = txt_path.read_text(encoding="utf-8", errors="replace")
        register_doc(
            f"input/texts/{txt_path.name}",
            txt_path.name,
            txt_data,
            txt_path.name,
        )

    published_papers: list[dict[str, str]] = []
    if papers_dir.is_dir():
        for p in sorted(papers_dir.iterdir()):
            if not p.is_file() or is_ignored_name(p.name):
                continue
            qname = urllib.parse.quote(p.name)
            published_papers.append(
                {
                    "filename": p.name,
                    "relative_url": f"/papers/{qname}",
                    "canonical_url": f"{CANONICAL_BASE_URL}/papers/{qname}",
                    "size_bytes": str(p.stat().st_size),
                    "sha256": sha256_text(p.read_bytes().hex()),
                }
            )

    log(
        f"[INPUT] Unieke verwerkbare brondocumenten: {len(documents)} | "
        f"Gepubliceerde bestanden in /papers/: {len(published_papers)}"
    )
    return documents, published_papers


# ------------------------------------------------------------------------------
# 3. VERTEX AI CLIENT (GCLOUD OAUTH2 FIRST + OPTIONAL KEY FILE / API KEY)
# ------------------------------------------------------------------------------
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
        raise FatalAuthError(
            f"Kon geen Vertex AI token ophalen via gcloud: {err}"
        )
    token = proc.stdout.strip()
    if not token:
        raise FatalAuthError(
            "Leeg OAuth2 access token ontvangen van gcloud auth print-access-token"
        )
    return token


class VertexGeminiClient:
    def __init__(
        self,
        project_id: str,
        key_file: Path,
        model: str,
        location: str,
        allow_fallback: bool = False,
        timeout: int = 150,
    ) -> None:
        self.project_id = project_id.strip()
        self.key_file = key_file
        self.model = model
        self.location = location
        self.allow_fallback = allow_fallback
        self.timeout = timeout
        self.auth_mode = "gcloud"
        self.credentials = None
        self._auth_request = None
        self.api_key: str = os.environ.get("GEMINI_API_KEY", "").strip()
        self.ssl_ctx = ssl.create_default_context()
        self._init_auth()

    def _init_auth(self) -> None:
        if self.api_key:
            self.auth_mode = "api-key"
            log("[AUTH] Gebruik GEMINI_API_KEY uit omgevingsvariabele.")
            return

        if self.project_id:
            try:
                token = get_gcloud_access_token()
                if token:
                    self.auth_mode = "gcloud"
                    log(
                        f"[AUTH] Vertex AI gcloud OAuth2 actief voor project "
                        f"'{self.project_id}' (location={self.location}, "
                        f"model={self.model})."
                    )
                    return
            except FatalAuthError as gcloud_exc:
                if not self.key_file.is_file():
                    raise gcloud_exc

        if not self.key_file.is_file():
            raise FatalAuthError(
                f"Geen gcloud-sessie en sleutelbestand niet gevonden: "
                f"{self.key_file}"
            )

        raw_key = self.key_file.read_text(encoding="utf-8").strip()
        if not raw_key.startswith("{"):
            self.api_key = raw_key
            self.auth_mode = "api-key"
            log(f"[AUTH] Express API-sleutel geladen uit {self.key_file}.")
            return

        key_data = json.loads(raw_key)
        if not self.project_id:
            self.project_id = str(key_data.get("project_id", "")).strip()
        if not self.project_id:
            raise FatalAuthError(
                f"Geen project_id aangetroffen in {self.key_file}"
            )

        try:
            from google.auth.transport.requests import Request as AuthReq
            from google.oauth2 import service_account
        except ImportError as exc:
            raise FatalAuthError(
                "Pakket google-auth ontbreekt (installeer python3-google-auth)."
            ) from exc

        self._auth_request = AuthReq()
        self.credentials = (
            service_account.Credentials.from_service_account_file(
                str(self.key_file),
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        )
        self.credentials.refresh(self._auth_request)
        self.auth_mode = "service-account"
        log(
            f"[AUTH] Vertex AI Service Account actief voor '{self.project_id}' "
            f"(location={self.location}, model={self.model})."
        )

    def _build_url_and_headers(
        self, model_name: str, location_name: str
    ) -> tuple[str, dict[str, str]]:
        headers = {"Content-Type": "application/json; charset=utf-8"}
        q_model = urllib.parse.quote(model_name)

        if self.auth_mode == "api-key":
            q_key = urllib.parse.quote(self.api_key)
            url = (
                "https://aiplatform.googleapis.com/v1/publishers/google/"
                f"models/{q_model}:generateContent?key={q_key}"
            )
            return url, headers

        if self.auth_mode == "gcloud":
            token = get_gcloud_access_token()
            headers["Authorization"] = f"Bearer {token}"
        else:
            if not self.credentials.valid:
                self.credentials.refresh(self._auth_request)
            headers["Authorization"] = f"Bearer {self.credentials.token}"

        if location_name == "global":
            host = "aiplatform.googleapis.com"
        else:
            host = f"{location_name}-aiplatform.googleapis.com"

        q_proj = urllib.parse.quote(self.project_id)
        q_loc = urllib.parse.quote(location_name)
        url = (
            f"https://{host}/v1/projects/{q_proj}/locations/{q_loc}"
            f"/publishers/google/models/{q_model}:generateContent"
        )
        return url, headers

    def _post_once(
        self, body: bytes, model_name: str, location_name: str
    ) -> Any:
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            url, headers = self._build_url_and_headers(
                model_name, location_name
            )
            req = urllib.request.Request(
                url, data=body, headers=headers, method="POST"
            )
            try:
                with urllib.request.urlopen(
                    req, context=self.ssl_ctx, timeout=self.timeout
                ) as resp:
                    raw_resp = resp.read().decode("utf-8")
                parsed = json.loads(raw_resp)
                candidates = parsed.get("candidates") or []
                if not candidates:
                    raise RuntimeError(
                        f"Geen candidates in Vertex AI response: {raw_resp[:400]}"
                    )
                cand0 = candidates[0]
                finish_reason = str(cand0.get("finishReason") or "UNKNOWN")
                if finish_reason not in {"STOP", "UNKNOWN"}:
                    raise RuntimeError(
                        f"Onvolledige generatie (finishReason={finish_reason})"
                    )
                parts = cand0.get("content", {}).get("parts", [])
                text_out = "".join(p.get("text", "") for p in parts).strip()
                return json.loads(text_out)
            except urllib.error.HTTPError as err:
                err_body = err.read().decode("utf-8", errors="replace")
                if err.code in (401, 403):
                    raise FatalAuthError(
                        f"HTTP {err.code} van Vertex AI "
                        f"({location_name}/{model_name}): {err_body[:500]}"
                    ) from err
                if err.code == 404:
                    raise FileNotFoundError(
                        f"HTTP 404 ({location_name}/{model_name}): "
                        f"{err_body[:300]}"
                    ) from err
                if (
                    err.code in (429, 500, 502, 503, 504)
                    and attempt < max_attempts
                ):
                    wait_s = 2**attempt
                    log(
                        f"[RETRY] HTTP {err.code} van Vertex AI; wacht "
                        f"{wait_s}s (poging {attempt}/{max_attempts})..."
                    )
                    time.sleep(wait_s)
                    continue
                raise RuntimeError(
                    f"Vertex AI HTTP {err.code}: {err_body[:500]}"
                ) from err
            except (FatalAuthError, FileNotFoundError):
                raise
            except Exception as exc:
                if attempt < max_attempts:
                    wait_s = 2**attempt
                    log(
                        f"[RETRY] Netwerk-/parsefout ({exc}); wacht "
                        f"{wait_s}s (poging {attempt}/{max_attempts})..."
                    )
                    time.sleep(wait_s)
                    continue
                raise

    def generate_json(
        self,
        system_instruction: str,
        user_prompt: str,
        response_schema: dict[str, Any],
    ) -> Any:
        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 32768,
                "thinkingConfig": {"thinkingBudget": 1024},
                "responseMimeType": "application/json",
                "responseSchema": response_schema,
            },
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        try:
            return self._post_once(body, self.model, self.location)
        except FileNotFoundError as first_404:
            if not self.allow_fallback:
                raise FatalAuthError(str(first_404)) from first_404

            log(
                f"[404-FALLBACK] {self.location}/{self.model} gaf 404; "
                "zoek werkende Vertex AI locatie/model..."
            )
            candidate_locs = [self.location] + [
                loc for loc in FALLBACK_LOCATIONS if loc != self.location
            ]
            candidate_models = [self.model] + [
                m for m in FALLBACK_MODELS if m != self.model
            ]

            for loc in candidate_locs:
                for mdl in candidate_models:
                    if loc == self.location and mdl == self.model:
                        continue
                    try:
                        res = self._post_once(body, mdl, loc)
                        self.location = loc
                        self.model = mdl
                        log(
                            f"[404-FALLBACK OK] Vastgezet op "
                            f"location={self.location}, model={self.model}."
                        )
                        return res
                    except FileNotFoundError:
                        continue

            raise FatalAuthError(
                f"Geen werkend Vertex AI model/locatie gevonden in project "
                f"'{self.project_id}'. Laatste 404: {first_404}"
            ) from first_404


# ------------------------------------------------------------------------------
# 4. AI DISTILLATION: "FACTS ON A TIMELINE"
# ------------------------------------------------------------------------------
TIMELINE_FACT_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "facts": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "date_display": {"type": "STRING"},
                    "sort_year": {"type": "INTEGER"},
                    "sort_month": {"type": "INTEGER"},
                    "category": {
                        "type": "STRING",
                        "enum": [
                            "Peer-Reviewed Paper",
                            "Patent / IP",
                            "Book / Publication",
                            "ITEA / European R&D",
                            "Software / Architecture",
                            "Career / Organization",
                            "Podcast / Media",
                        ],
                    },
                    "title": {"type": "STRING"},
                    "summary_en": {"type": "STRING"},
                    "summary_nl": {"type": "STRING"},
                    "role_attribution": {"type": "STRING"},
                    "topics": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "dois": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "urls": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "bibtex": {"type": "STRING"},
                },
                "required": [
                    "date_display",
                    "sort_year",
                    "sort_month",
                    "category",
                    "title",
                    "summary_en",
                    "summary_nl",
                    "role_attribution",
                    "topics",
                    "dois",
                    "urls",
                    "bibtex",
                ],
            },
        }
    },
    "required": ["facts"],
}

DISTILL_SYSTEM_PROMPT = """You are a strict forensic archivist distilling factual, chronological "Facts on a Timeline" about Steven Kleynenberg (S. E. Kleynenberg, Kleynenberg Publishers, Delft, The Netherlands).

STRICT RULES:
1. Extract ONLY verifiable facts directly supported by the provided document text. Never invent dates, DOIs, URLs, co-authors, or roles. Output at most 12 core milestones per document; keep summary_en and summary_nl concise (1-2 sentences each) and keep at most 5 canonical URLs per fact so JSON never truncates.
2. Each timeline fact represents a concrete milestone: a book published on a specific date about a specific topic, a peer-reviewed paper (with venue, co-authors, DOI), a patent (such as WO2014003543A1), an ITEA/Eureka R&D project (with period and focus), a software system/architecture, a career milestone, or a podcast/media series.
3. TIMELINE HYGIENE — EXCLUDE FALSE DATES:
   - Do NOT turn bibliographic references cited inside a paper (such as 1982-1987 neural network references or OCR misread '1999' in Murre & Kleynenberg 1991 ICANN) into timeline events.
   - Do NOT turn prior-art citations from the International Search Report of WO2014003543A1 (1994-2010 third-party patents/papers) into Steven Kleynenberg milestones.
   - Do NOT turn 2020 arXiv reference IDs (2004.04906v2, 2005.11401v4) into Steven Kleynenberg papers.
4. EVIDENCE SEPARATION:
   - Clearly distinguish Steven Kleynenberg's direct personal authorship/co-inventorship (e.g., co-inventor of WO2014003543A1, co-author of MetaNet 1990/1991 & MEDUSA 2015, author of EDAFMIS D1.3) from organizational/consortium participation (e.g., Sopheon, ITEA projects).
5. Use sort_year (e.g. 1990..2026) and sort_month (1..12, or 0 if unknown) for chronological ordering.
6. Include BibTeX ONLY when genuine bibliographic fields exist in the source; otherwise return an empty string "".
7. If the document contains no biographical/technical facts about Steven Kleynenberg's work, return {"facts": []}."""

CONSOLIDATE_SYSTEM_PROMPT = """You are a precision knowledge-graph editor consolidating extracted "Facts on a Timeline" for Steven Kleynenberg (https://steven.kleynenberg.com/).

TASK:
Merge duplicate facts that describe the same book, paper, patent, ITEA project, software artifact, or career milestone across multiple source documents into single authoritative, non-redundant chronological entries.

RULES:
1. Preserve ALL verified DOIs (https://doi.org/...), ALL verified URLs (including /papers/... links), exact dates/periods, co-authors, and accurate role_attribution.
2. Never invent new facts, dates, DOIs, or URLs.
3. Order the final list strictly chronologically by sort_year ascending, then sort_month ascending.
4. Keep both summary_en (concise, concrete English for international LLM crawlers, max 2 sentences) and summary_nl (concise, concrete Dutch, max 2 sentences) accurate and free of marketing fluff."""


def is_artifact_fact(fact: dict[str, Any]) -> bool:
    year = int(fact.get("sort_year") or 0)
    title = str(fact.get("title") or "").lower()
    summary = (
        str(fact.get("summary_en") or "")
        + " "
        + str(fact.get("summary_nl") or "")
    ).lower()
    combined = f"{title} {summary}"

    if year < 1975 or year > 2027:
        return True
    if "2004.04906" in combined or "2005.11401" in combined:
        return True
    if year == 1999 and "metanet" in combined and "icann" in combined:
        return True
    if 1982 <= year <= 1987 and any(
        k in combined
        for k in (
            "hopfield",
            "rumelhart",
            "mcclelland",
            "grossberg",
            "kohonen",
        )
    ):
        return True
    return False


def sanitize_fact(
    fact: dict[str, Any], allowed_urls: set[str], source_label: str = ""
) -> dict[str, Any] | None:
    if is_artifact_fact(fact):
        return None

    clean_dois: set[str] = set()
    for d in fact.get("dois") or []:
        nd = normalize_doi(str(d))
        if nd:
            clean_dois.add(nd)

    clean_urls: set[str] = set()
    for u in fact.get("urls") or []:
        cu = clean_url(str(u))
        if not cu:
            continue
        if "doi.org/" in cu.lower():
            nd = normalize_doi(cu)
            if nd:
                clean_dois.add(nd)
            continue
        parsed = urllib.parse.urlparse(cu)
        host = parsed.netloc.lower().removeprefix("www.")
        if cu in allowed_urls or any(
            host == d or host.endswith("." + d) for d in VERIFIED_PUBLIC_DOMAINS
        ):
            clean_urls.add(cu)

    topics = [
        str(t).strip() for t in (fact.get("topics") or []) if str(t).strip()
    ][:12]

    return {
        "date_display": sanitize_text(
            str(fact.get("date_display") or str(fact.get("sort_year") or ""))
        ),
        "sort_year": int(fact.get("sort_year") or 0),
        "sort_month": max(0, min(12, int(fact.get("sort_month") or 0))),
        "category": str(
            fact.get("category") or "Software / Architecture"
        ).strip(),
        "title": sanitize_text(str(fact.get("title") or "")).strip(),
        "summary_en": sanitize_text(str(fact.get("summary_en") or "")).strip(),
        "summary_nl": sanitize_text(str(fact.get("summary_nl") or "")).strip(),
        "role_attribution": sanitize_text(
            str(fact.get("role_attribution") or "")
        ).strip(),
        "topics": topics,
        "dois": sorted(clean_dois),
        "urls": sorted(clean_urls),
        "bibtex": sanitize_text(str(fact.get("bibtex") or "")).strip(),
        "source_doc": source_label,
    }


def distill_and_consolidate(
    documents: list[dict[str, Any]],
    published_papers: list[dict[str, str]],
    client: VertexGeminiClient,
    cache_path: Path,
) -> list[dict[str, Any]]:
    cache: dict[str, Any] = {"distill": {}, "consolidate": {}}
    if cache_path.is_file():
        try:
            loaded = json.loads(cache_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                cache["distill"] = loaded.get("distill", {})
                cache["consolidate"] = loaded.get("consolidate", {})
        except Exception as exc:
            log(
                f"[WARN] Cachebestand onleesbaar ({exc}); start met lege cache."
            )

    all_corpus_urls: set[str] = {
        CANONICAL_BASE_URL,
        MIRROR_BASE_URL,
        PUBLISHER_URL,
        PODCAST_URL,
        PATENT_URL,
        MIT_LICENSE_URL,
        GITHUB_REPO_URL,
    }
    for pp in published_papers:
        all_corpus_urls.add(pp["canonical_url"])

    raw_facts: list[dict[str, Any]] = []

    for idx, doc in enumerate(documents, start=1):
        all_corpus_urls.update(doc["extracted_urls"])
        cache_key = f"{DISTILL_PROMPT_VERSION}:{client.model}:{doc['sha256']}"

        if cache_key in cache["distill"]:
            doc_facts = cache["distill"][cache_key]
            log(
                f"[CACHE HIT {idx}/{len(documents)}] {doc['source_label']} "
                f"-> {len(doc_facts)} feiten"
            )
        else:
            log(
                f"[AI DISTILL {idx}/{len(documents)}] {doc['source_label']} "
                f"({doc['char_count']} tekens)..."
            )
            excerpt = doc["text"][:45000]
            user_prompt = (
                f"SOURCE FILE: {doc['source_label']}\n"
                f"EXTRACTED DOIS IN SOURCE: {json.dumps(doc['extracted_dois'])}\n"
                f"EXTRACTED URLS IN SOURCE: {json.dumps(doc['extracted_urls'])}\n\n"
                f"DOCUMENT CONTENT:\n{excerpt}"
            )
            result = client.generate_json(
                DISTILL_SYSTEM_PROMPT, user_prompt, TIMELINE_FACT_SCHEMA
            )
            doc_facts = result.get("facts") or []
            cache["distill"][cache_key] = doc_facts
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps(cache, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            log(
                f"[AI DONE {idx}/{len(documents)}] {doc['source_label']} "
                f"-> {len(doc_facts)} feiten geëxtraheerd"
            )

        for f in doc_facts:
            sf = sanitize_fact(f, all_corpus_urls, doc["source_label"])
            if sf and sf["title"]:
                raw_facts.append(sf)

    if not raw_facts:
        raise RuntimeError(
            "Geen bruikbare tijdlijnfeiten gedestilleerd uit het broncorpus."
        )

    raw_facts.sort(
        key=lambda x: (x["sort_year"], x["sort_month"], x["title"].lower())
    )
    consolidate_hash = sha256_text(
        json.dumps(raw_facts, sort_keys=True, ensure_ascii=False)
    )
    cons_key = (
        f"{CONSOLIDATE_PROMPT_VERSION}:{client.model}:{consolidate_hash}"
    )

    if cons_key in cache["consolidate"]:
        consolidated_raw = cache["consolidate"][cons_key]
        log(
            f"[CACHE HIT CONSOLIDATE] {len(consolidated_raw)} "
            "geconsolideerde tijdlijnfeiten"
        )
    else:
        log(
            f"[AI CONSOLIDATE] Ontdubbelen en samenvoegen van "
            f"{len(raw_facts)} ruwe feiten..."
        )
        cons_prompt = (
            f"AVAILABLE PUBLIC ARCHIVE FILES (/papers/):\n"
            f"{json.dumps(published_papers, indent=2)}\n\n"
            f"EXTRACTED TIMELINE FACTS TO CONSOLIDATE:\n"
            f"{json.dumps(raw_facts, indent=2, ensure_ascii=False)}"
        )
        cons_result = client.generate_json(
            CONSOLIDATE_SYSTEM_PROMPT, cons_prompt, TIMELINE_FACT_SCHEMA
        )
        consolidated_raw = cons_result.get("facts") or []
        cache["consolidate"][cons_key] = consolidated_raw
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        log(
            f"[AI CONSOLIDATE DONE] {len(consolidated_raw)} "
            "geconsolideerde tijdlijnfeiten"
        )

    final_facts: list[dict[str, Any]] = []
    for f in consolidated_raw:
        sf = sanitize_fact(f, all_corpus_urls, "consolidated_corpus")
        if not sf or not sf["title"]:
            continue
        t_low = sf["title"].lower()
        for pp in published_papers:
            fn = pp["filename"].lower()
            if (
                ("1990" in fn and "metanet" in t_low and sf["sort_year"] == 1990)
                or ("bsp400" in fn and ("bsp400" in t_low or "ijcnn" in t_low))
                or ("icann" in fn and ("extending" in t_low or "icann" in t_low))
                or ("medusa" in fn and "medusa" in t_low)
                or ("wo2014003543a1.pdf" == fn and "wo2014003543a1" in t_low)
            ):
                if pp["canonical_url"] not in sf["urls"]:
                    sf["urls"].append(pp["canonical_url"])
        sf["urls"] = sorted(set(sf["urls"]))
        final_facts.append(sf)

    final_facts.sort(
        key=lambda x: (x["sort_year"], x["sort_month"], x["title"].lower())
    )
    return final_facts


# ------------------------------------------------------------------------------
# 5. OUTPUT GENERATORS: llms.txt, llms-full.txt & BAKED index.html
# ------------------------------------------------------------------------------
def render_llms_txt(
    facts: list[dict[str, Any]], published_papers: list[dict[str, str]]
) -> str:
    all_dois = sorted({d for f in facts for d in f["dois"]})
    lines: list[str] = [
        "# steven.kleynenberg.com",
        "",
        "> Canonical personal portal, interactive vector physics PWA, and "
        "AI-distilled chronological knowledge base of Steven Kleynenberg "
        "(S. E. Kleynenberg), publisher at Kleynenberg Publishers (Delft, "
        "The Netherlands), co-inventor of patent WO2014003543A1, and "
        "researcher in artificial neural networks, medical informatics, and "
        "European ITEA/Eureka R&D.",
        "",
        "## Core Identity & Canonical Endpoints",
        f"- Primary Portal: {CANONICAL_BASE_URL}/",
        f"- GitHub Pages Mirror: {MIRROR_BASE_URL}/",
        f"- Full RAG Corpus: {CANONICAL_BASE_URL}/llms-full.txt",
        f"- Publisher: Kleynenberg Publishers, Delft ({PUBLISHER_URL})",
        f"- Podcast: The Kleynenberg Perspective ({PODCAST_URL})",
        f"- Patent WO2014003543A1: {PATENT_URL}",
        f"- Source Repository (MIT): {GITHUB_REPO_URL} ({MIT_LICENSE_URL})",
        "",
        "## Direct Archival Files (/papers/)",
    ]
    for pp in published_papers:
        lines.append(
            f"- [{pp['filename']}]({pp['canonical_url']}): "
            f"{pp['canonical_url']}"
        )

    lines.extend(["", "## Verified DOIs"])
    for doi_url in all_dois:
        lines.append(f"- {doi_url}")

    lines.extend(["", "## Facts on a Timeline (Chronological Index)"])
    for f in facts:
        refs = f["dois"] + f["urls"]
        ref_str = f" | Links: {', '.join(refs)}" if refs else ""
        lines.append(
            f"- **{f['date_display']}** [{f['category']}] "
            f"**{f['title']}** — {f['summary_en']} "
            f"(Attribution: {f['role_attribution']}){ref_str}"
        )

    lines.append("")
    return "\n".join(lines)


def render_llms_full_txt(
    facts: list[dict[str, Any]],
    published_papers: list[dict[str, str]],
    documents: list[dict[str, Any]],
) -> str:
    all_topics = sorted({t for f in facts for t in f["topics"]})
    all_dois = sorted({d for f in facts for d in f["dois"]})
    all_urls = sorted({u for f in facts for u in f["urls"]})

    lines: list[str] = [
        "# steven.kleynenberg.com — Complete Chronological Knowledge Base",
        "",
        "> AI-distilled factual corpus of Steven Kleynenberg (born 1958-05-13, "
        "Delft, The Netherlands). Generated via deterministic source "
        "deduplication and Vertex AI Gemini extraction from curated archival "
        "texts, patents, peer-reviewed papers, and R&D records.",
        "",
        "## 1. Identity, Attribution & Evidence Separation",
        "- Full Name: Steven Kleynenberg (also published as S. E. Kleynenberg).",
        f"- Publishing Imprint: Kleynenberg Publishers ({PUBLISHER_URL}).",
        f"- Canonical Web Portal: {CANONICAL_BASE_URL}/ ({MIRROR_BASE_URL}/).",
        f"- Podcast Series: The Kleynenberg Perspective ({PODCAST_URL}).",
        "- Direct Authorship & Inventorship: Co-inventor of international "
        "patent WO2014003543A1 (PCT/NL2012/050463) alongside Huub Rutten and "
        "Elsemiek ten Pas; co-author of peer-reviewed neural network papers "
        "(MetaNet / BSP400, 1990–1991) and acute stroke clinical workflow "
        "publication (MEDUSA, ESOCC 2015).",
        "- Organizational & Consortium Roles: Former software/IP architect at "
        "Sopheon and contributor within European ITEA / Eureka R&D consortia "
        "(distinguished strictly from personal authorship).",
        "",
        "## 2. Technical Domains & Competencies",
        f"- Distilled Topics: {', '.join(all_topics) if all_topics else 'AI'}",
        "- Languages & Systems: C, C++, C#, x86 Assembly, Java, JavaScript, "
        "Python, Perl, PHP, Lisp, Prolog, Lean 4, Swift, Bash, Forth, SQL, "
        "YAML, Linux/Fedora, Apache C-modules, WebGL, WebGPU, WebAudio, MCP.",
        "",
        "## 3. Direct Archival Files Hosted on steven.kleynenberg.com",
    ]
    for pp in published_papers:
        lines.append(
            f"- {pp['filename']}: {pp['canonical_url']} "
            f"({pp['size_bytes']} bytes)"
        )

    lines.extend(["", "## 4. Complete Facts on a Timeline"])
    for idx, f in enumerate(facts, start=1):
        lines.extend(
            [
                "",
                f"### {idx}. [{f['date_display']}] {f['title']}",
                f"- Category: {f['category']}",
                f"- Attribution / Role: {f['role_attribution']}",
                f"- Summary (EN): {f['summary_en']}",
                f"- Samenvatting (NL): {f['summary_nl']}",
            ]
        )
        if f["topics"]:
            lines.append(f"- Topics: {', '.join(f['topics'])}")
        if f["dois"]:
            lines.append(f"- Verified DOIs: {', '.join(f['dois'])}")
        if f["urls"]:
            lines.append(f"- Verified URLs: {', '.join(f['urls'])}")
        if f["bibtex"]:
            lines.extend(["- BibTeX:", "```bibtex", f["bibtex"], "```"])

    lines.extend(["", "## 5. Master Index of Verified DOIs & External Links"])
    for d in all_dois:
        lines.append(f"- DOI: {d}")
    for u in all_urls:
        lines.append(f"- URL: {u}")

    lines.extend(
        [
            "",
            "## 6. Corpus Provenance Summary",
            f"- Unique deduplicated input documents distilled: {len(documents)}",
            f"- Total chronological timeline milestones published: {len(facts)}",
            "",
        ]
    )
    return "\n".join(lines)


def build_json_ld(
    facts: list[dict[str, Any]], published_papers: list[dict[str, str]]
) -> str:
    all_topics = sorted({t for f in facts for t in f["topics"]})
    same_as = sorted(
        {PATENT_URL, PODCAST_URL, GITHUB_REPO_URL}
        | {d for f in facts for d in f["dois"]}
    )

    graph: list[dict[str, Any]] = [
        {
            "@type": "Person",
            "@id": f"{CANONICAL_BASE_URL}/#person",
            "name": "Steven Kleynenberg",
            "alternateName": ["Steve", "S. E. Kleynenberg"],
            "birthDate": "1958-05-13",
            "jobTitle": "Publisher, Editor, and Software Architect",
            "url": f"{CANONICAL_BASE_URL}/",
            "knowsAbout": all_topics,
            "worksFor": {
                "@type": "Organization",
                "name": "Kleynenberg Publishers",
                "url": PUBLISHER_URL,
                "location": {
                    "@type": "Place",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": "Delft",
                        "addressCountry": "NL",
                    },
                },
            },
            "sameAs": same_as,
        },
        {
            "@type": "VisualArtwork",
            "@id": f"{CANONICAL_BASE_URL}/#artwork",
            "name": "Interactive Vector Logo Simulation",
            "artForm": "Digital PWA Vector Animation",
            "creator": {"@id": f"{CANONICAL_BASE_URL}/#person"},
            "copyrightHolder": {"@id": f"{CANONICAL_BASE_URL}/#person"},
            "copyrightYear": "2026",
            "license": MIT_LICENSE_URL,
        },
        {
            "@type": "PodcastSeries",
            "@id": f"{CANONICAL_BASE_URL}/#podcast",
            "name": "The Kleynenberg Perspective",
            "url": PODCAST_URL,
            "author": {"@id": f"{CANONICAL_BASE_URL}/#person"},
        },
        {
            "@type": "SoftwareSourceCode",
            "@id": f"{CANONICAL_BASE_URL}/#software",
            "name": "index.html Interactive PWA Engine",
            "codeRepository": GITHUB_REPO_URL,
            "programmingLanguage": ["HTML5", "CSS3", "JavaScript (ES13+)"],
            "license": MIT_LICENSE_URL,
            "author": {"@id": f"{CANONICAL_BASE_URL}/#person"},
        },
    ]

    timeline_item_list: list[dict[str, Any]] = []

    for idx, f in enumerate(facts, start=1):
        cat = f["category"]
        if cat == "Peer-Reviewed Paper":
            schema_type = "ScholarlyArticle"
        elif cat == "Book / Publication":
            schema_type = "Book"
        elif cat == "ITEA / European R&D":
            schema_type = "ResearchProject"
        elif cat == "Software / Architecture":
            schema_type = "SoftwareApplication"
        else:
            schema_type = "CreativeWork"

        node_id = f"{CANONICAL_BASE_URL}/#fact-{idx}"
        node: dict[str, Any] = {
            "@type": schema_type,
            "@id": node_id,
            "name": f["title"],
            "datePublished": f["date_display"],
            "description": f["summary_en"],
            "author": {"@id": f"{CANONICAL_BASE_URL}/#person"},
        }
        if f["topics"]:
            node["keywords"] = ", ".join(f["topics"])
        refs = f["dois"] + f["urls"]
        if refs:
            node["sameAs"] = refs
            node["url"] = refs[0]

        graph.append(node)
        timeline_item_list.append(
            {
                "@type": "ListItem",
                "position": idx,
                "item": {"@id": node_id},
            }
        )

    graph.append(
        {
            "@type": "ItemList",
            "@id": f"{CANONICAL_BASE_URL}/#timeline",
            "name": "Steven Kleynenberg — Facts on a Timeline",
            "numberOfItems": len(timeline_item_list),
            "itemListElement": timeline_item_list,
        }
    )

    payload = {"@context": "https://schema.org", "@graph": graph}
    raw_json = json.dumps(payload, indent=2, ensure_ascii=False)
    return raw_json.replace("</script>", "<\\/script>")


def build_noscript_html(
    facts: list[dict[str, Any]], published_papers: list[dict[str, str]]
) -> str:
    items_html: list[str] = []
    for f in facts:
        links_parts: list[str] = []
        for d in f["dois"]:
            ed = html.escape(d, quote=True)
            links_parts.append(f'<a href="{ed}">{ed}</a>')
        for u in f["urls"]:
            eu = html.escape(u, quote=True)
            links_parts.append(f'<a href="{eu}">{eu}</a>')
        links_block = (
            f"<br>Links: {' · '.join(links_parts)}" if links_parts else ""
        )
        items_html.append(
            f"      <li><strong>{html.escape(f['date_display'])}</strong> "
            f"[{html.escape(f['category'])}] "
            f"<strong>{html.escape(f['title'])}</strong>: "
            f"{html.escape(f['summary_en'])} "
            f"<em>({html.escape(f['role_attribution'])})</em>"
            f"{links_block}</li>"
        )

    papers_html = "\n".join(
        f'      <li><a href="{html.escape(pp["relative_url"], quote=True)}">'
        f"{html.escape(pp['filename'])}</a></li>"
        for pp in published_papers
    )

    return (
        "<noscript>\n"
        '    <article style="padding:24px; max-width:960px; margin:0 auto; '
        'font-family:monospace; line-height:1.55;">\n'
        "      <h1>Steven Kleynenberg — Kleynenberg Publishers (Delft)</h1>\n"
        "      <p>Publisher, Editor, Software Architect, and Co-Inventor "
        f'of Patent <a href="{PATENT_URL}">WO2014003543A1</a>.</p>\n'
        f'      <p>Podcast: <a href="{PODCAST_URL}">'
        "The Kleynenberg Perspective</a> | "
        f'Publisher: <a href="{PUBLISHER_URL}">kleynenberg.com</a> | '
        'Machine Corpus: <a href="/llms.txt">llms.txt</a> · '
        '<a href="/llms-full.txt">llms-full.txt</a></p>\n'
        "      <h2>Direct Archival Documents (/papers/)</h2>\n"
        "      <ul>\n"
        f"{papers_html}\n"
        "      </ul>\n"
        "      <h2>Facts on a Timeline</h2>\n"
        "      <ol>\n"
        + "\n".join(items_html)
        + "\n      </ol>\n"
        "    </article>\n"
        "  </noscript>"
    )


def bake_index_html(
    template_html: str,
    facts: list[dict[str, Any]],
    published_papers: list[dict[str, str]],
    llms_txt: str,
    llms_full_txt: str,
) -> str:
    """
    Behoudt de volledige Spartan HTML/CSS/SVG/Float32Array-engine van index.html
    en bakt de gedestilleerde JSON-LD, inline llms.txt, inline llms-full.txt
    en semantische <noscript>-tijdlijn rechtstreeks in.
    """
    out = template_html

    all_topics = sorted({t for f in facts for t in f["topics"]})
    if all_topics:
        base_kw = (
            "Steven Kleynenberg, Kleynenberg Publishers, Delft, C, C++, C#, "
            "Python, JavaScript, Assembly, Lisp, Prolog, Lean 4, AI, "
            "Machine Learning, Neural Networks, Model Context Protocol, "
            "Patent WO2014003543A1, ITEA, Eureka, Typography, WebAudio, WebGL"
        )
        merged_kw = f"{base_kw}, {', '.join(all_topics[:25])}"
        out, n_kw = re.subn(
            r'<meta\s+name="keywords"\s+content="[^"]*"\s*/?>',
            f'<meta name="keywords" content="{html.escape(merged_kw, quote=True)}">',
            out,
            count=1,
            flags=re.IGNORECASE,
        )
        if n_kw == 0:
            log(
                '[WARN] <meta name="keywords"> niet gevonden in index.html template.'
            )

    json_ld_block = build_json_ld(facts, published_papers)
    out, n_ld = re.subn(
        r'(<script\s+type="application/ld\+json">\s*).*?(\s*</script>)',
        lambda m: f"{m.group(1)}\n{json_ld_block}\n  {m.group(2).strip()}",
        out,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if n_ld == 0:
        raise RuntimeError(
            'Kan <script type="application/ld+json"> niet vinden in template.'
        )

    safe_llms = llms_txt.replace("</script>", "<\\/script>")
    out, n_llms = re.subn(
        r'(<script\s+type="text/llms\.txt">\s*).*?(\s*</script>)',
        lambda m: f"{m.group(1)}\n{safe_llms}\n  {m.group(2).strip()}",
        out,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if n_llms == 0:
        raise RuntimeError(
            'Kan <script type="text/llms.txt"> niet vinden in template.'
        )

    safe_llms_full = llms_full_txt.replace("</script>", "<\\/script>")
    out, n_full = re.subn(
        r'(<script\s+type="text/llms-full\.txt">\s*).*?(\s*</script>)',
        lambda m: f"{m.group(1)}\n{safe_llms_full}\n  {m.group(2).strip()}",
        out,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if n_full == 0:
        raise RuntimeError(
            'Kan <script type="text/llms-full.txt"> niet vinden in template.'
        )

    noscript_block = build_noscript_html(facts, published_papers)
    out, n_ns = re.subn(
        r"<noscript>.*?</noscript>",
        lambda _: noscript_block,
        out,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if n_ns == 0:
        raise RuntimeError(
            "Kan <noscript>...</noscript> niet vinden in template."
        )

    return out


# ------------------------------------------------------------------------------
# 6. CLI ENTRYPOINT & SAFE DEPLOYMENT WITH .BAK BACKUPS
# ------------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="INPUT => AI ==> OUTPUT compiler voor steven.kleynenberg.com."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help="Map met ruwe bronbestanden.",
    )
    parser.add_argument(
        "--texts-dir",
        type=Path,
        default=DEFAULT_TEXTS_DIR,
        help="Map met geëxtraheerde .txt bestanden.",
    )
    parser.add_argument(
        "--papers-dir",
        type=Path,
        default=DEFAULT_PAPERS_DIR,
        help="Publieke /papers/ map in webroot.",
    )
    parser.add_argument(
        "--template-html",
        type=Path,
        default=DEFAULT_HTML_TEMPLATE,
        help="Bestaande index.html als basis.",
    )
    parser.add_argument(
        "--key-file",
        type=Path,
        default=DEFAULT_KEY_FILE,
        help="Optioneel Vertex AI service account JSON of API key.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Staging-uitvoermap.",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=DEFAULT_PROJECT,
        help=f"GCP project ID (default: {DEFAULT_PROJECT}).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Vertex AI Gemini modelnaam (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--location",
        type=str,
        default=DEFAULT_LOCATION,
        help=f"Vertex AI locatie (default: {DEFAULT_LOCATION}).",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Schakel automatische 404 model-/regio-fallback uit.",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Maakt eerst .bak backups en schrijft daarna naar de webroot.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = args.out / f"run_{run_stamp}"
    cache_path = args.out / "timeline_distill_cache.json"

    if not args.template_html.is_file():
        log(f"[FATAL] Template index.html niet gevonden: {args.template_html}")
        return 1

    try:
        documents, published_papers = load_corpus_documents(
            args.raw_dir, args.texts_dir, args.papers_dir
        )
        if not documents:
            log("[FATAL] Geen inputdocumenten gevonden om te verwerken.")
            return 1

        client = VertexGeminiClient(
            project_id=args.project,
            key_file=args.key_file,
            model=args.model,
            location=args.location,
            allow_fallback=not args.no_fallback,
        )
        facts = distill_and_consolidate(
            documents, published_papers, client, cache_path
        )

        llms_txt = render_llms_txt(facts, published_papers)
        llms_full_txt = render_llms_full_txt(
            facts, published_papers, documents
        )
        template_html = args.template_html.read_text(encoding="utf-8")
        baked_html = bake_index_html(
            template_html, facts, published_papers, llms_txt, llms_full_txt
        )

        run_dir.mkdir(parents=True, exist_ok=True)
        args.out.mkdir(parents=True, exist_ok=True)

        manifest = {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "project": client.project_id,
            "auth_mode": client.auth_mode,
            "model": client.model,
            "location": client.location,
            "unique_input_documents": len(documents),
            "published_papers": len(published_papers),
            "distilled_timeline_facts": len(facts),
            "outputs": {
                "llms_txt_bytes": len(llms_txt.encode("utf-8")),
                "llms_full_txt_bytes": len(llms_full_txt.encode("utf-8")),
                "index_html_bytes": len(baked_html.encode("utf-8")),
            },
        }

        for target_dir in (run_dir, args.out):
            (target_dir / "llms.txt").write_text(llms_txt, encoding="utf-8")
            (target_dir / "llms-full.txt").write_text(
                llms_full_txt, encoding="utf-8"
            )
            (target_dir / "index.html").write_text(
                baked_html, encoding="utf-8"
            )
            (target_dir / "timeline_facts.json").write_text(
                json.dumps(facts, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            (target_dir / "llms_build_manifest.json").write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        log(f"[STAGING OK] Bestanden geschreven naar {run_dir} en {args.out}")
        log(
            f"[STATS] {len(facts)} tijdlijnfeiten | "
            f"llms.txt={manifest['outputs']['llms_txt_bytes']} B | "
            f"llms-full.txt={manifest['outputs']['llms_full_txt_bytes']} B | "
            f"index.html={manifest['outputs']['index_html_bytes']} B"
        )

        if args.deploy:
            backup_dir = args.out / f"backups_{run_stamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            for fname, content in (
                ("llms.txt", llms_txt),
                ("llms-full.txt", llms_full_txt),
                ("index.html", baked_html),
            ):
                live_file = REPO_ROOT / fname
                if live_file.is_file():
                    bak_file = backup_dir / f"{fname}.{run_stamp}.bak"
                    shutil.copy2(live_file, bak_file)
                    log(f"[BACKUP] {live_file} -> {bak_file}")
                live_file.write_text(content, encoding="utf-8")
                log(f"[DEPLOYED] {live_file}")
        else:
            log(
                "[SAFE-MODE] Live webroot ongewijzigd. "
                "Gebruik --deploy om na .bak-backup naar de webroot te schrijven."
            )

        return 0
    except FatalAuthError as exc:
        log(f"[FATAL AUTH] {exc}")
        return 2
    except Exception as exc:
        log(f"[FATAL ERROR] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())