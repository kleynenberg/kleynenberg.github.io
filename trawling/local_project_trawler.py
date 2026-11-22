#!/usr/bin/env python3
# ==============================================================================
# INTEGRITY HEADER — PROJECT UNLINKED (https://steven.kleynenberg.com/)
# File:        /home/steve/dump/trawler/local_project_trawler.py (v3.1.1)
# Owner:       Steven Kleynenberg — KSO (Kleynenberg Software Ontwikkeling)
# Purpose:     Discreet, 100% read-only, content-driven local project inventory
#              with static project_dna extraction and sandboxed Vertex AI
#              (OAuth2 global/regional or Express API key) Gemini synthesis +
#              SHA-256 caching.
# Output Base: /home/steve/dump/trawler/results/local_projects_corpus/run_<YYYYMMDD_HHMMSS>/
# Standards:   Python 3.11+ Standard Library (https://docs.python.org/3/),
#              RFC 8259 JSON (https://www.rfc-editor.org/rfc/rfc8259),
#              Vertex AI generateContent API (https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference)
# Environment: Fedora Linux 45 (https://fedoraproject.org/) / hp.kleynenberg.net
# Safety:      100% read-only on all input paths; zero writes outside --out;
#              strict exclusion of sensitive/private paths and key files;
#              automatic secret redaction; privacy sandbox sends metadata only.
# ==============================================================================

from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

# ==============================================================================
# TOP INPUT PATHS & CONFIGURATION (EDIT OR OVERRIDE VIA --paths / --out)
# ==============================================================================
REPO_ROOT = Path("/home/steve/gemini/github.io/trawling")
RESULTS_DIR = REPO_ROOT / "output"
BASE_OUT_DIR = RESULTS_DIR / "localhost"

TOP_INPUT_PATHS: list[tuple[str, Path]] = [
    ("local_gemini", Path("/home/steve/gemini")),
    ("fedora44_gemini", Path("/mnt/fedora44/home/steve/gemini")),
    ("local_extensions", Path("/home/steve/extensions")),
    ("fedora44_extensions", Path("/mnt/fedora44/home/steve/extensions")),
    ("antigravity", Path("/home/steve/AntiGravityWorkspace")),
    ("fedora44_python", Path("/mnt/fedora44/home/steve/python")),
]

# Harde pad-substrings die onder geen beding gelezen of betreden mogen worden
BLOCKED_PATH_SUBSTRINGS: tuple[str, ...] = (
    "medisch",
    "medical",
    "prive",
    "private",
)

# Top-level mapnamen die worden overgeslagen (osint, android_forensics, bookmarks zijn WEL toegestaan)
SKIP_TOP_DIRS: set[str] = {
    "github.io",
    "XXXXX",
    "OOPSIE",
    "gmail",
    "poor",
    "00backup.audiotap",
    "01backup.audiotap",
    "02backup.audiotap",
    "03backup.audiotap",
    "04backup.audiotap",
    "backup_working_autoingest",
    "archive",
    "loss",
}

# Standaard technische ruis-mappen binnen projecten
SKIP_WALK_DIRS: set[str] = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".cache",
    ".idea",
    ".vscode",
    "target",
    "vendor",
    "tmp",
    "temp",
    ".mypy_cache",
    ".pytest_cache",
}

# Submap-prefixen met lage prioriteit (oude/backup-subtrees binnen een project)
LOW_PRIO_PREFIXES: tuple[str, ...] = (
    "bad",
    "old",
    "backup",
    "00backup",
    "01backup",
    "02backup",
    "deprecated",
    "trash",
)

# Bestanden met mogelijke credentials/sleutels/databases overslaan tijdens scan
SKIP_FILE_PATTERNS = re.compile(
    r"(\.env|secret|credential|token|password|passwd|id_rsa|service[_-]?account.*json$|.*_key\.(json|txt)$|\.pem$|\.key$|\.keystore$|\.jks$|\.p12$|\.pfx$|\.sqlite3?$|\.db$)",
    re.IGNORECASE,
)

# Regels met mogelijke secrets redigeren vóór tekstextractie
SECRET_LINE_RE = re.compile(
    r"(api[_-]?key|secret|token|password|passwd|private_key|bearer\s+[a-zA-Z0-9._-]+|sk-[a-zA-Z0-9]{20,}|AIza[0-9A-Za-z_-]{30,})",
    re.IGNORECASE,
)

CODE_EXT_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript/React",
    ".jsx": "React",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".java": "Java",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".hpp": "C++ Header",
    ".ino": "Arduino/Embedded C++",
    ".rs": "Rust",
    ".go": "Go",
    ".cs": "C#",
    ".swift": "Swift",
    ".lean": "Lean 4",
    ".lisp": "Lisp",
    ".pl": "Perl/Prolog",
    ".php": "PHP",
    ".rb": "Ruby",
    ".sh": "Shell/Bash",
    ".wgsl": "WebGPU (WGSL)",
    ".glsl": "OpenGL/WebGL (GLSL)",
    ".html": "HTML5",
    ".css": "CSS3",
    ".sql": "SQL",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".gs": "Google Apps Script",
    ".fth": "Forth",
    ".forth": "Forth",
    ".asm": "Assembly",
    ".s": "Assembly",
}

ASSET_EXTS: set[str] = {
    ".ttf", ".otf", ".woff", ".woff2", ".eot", ".pfb", ".pfm", ".afm",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".svg", ".ico",
    ".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac",
    ".mp4", ".mkv", ".avi", ".mov", ".webm",
    ".zip", ".tar", ".gz", ".xz", ".7z", ".rar",
    ".apk", ".dex", ".class", ".jar", ".so", ".dll",
    ".bin", ".dat", ".pak", ".iso", ".img", ".safetensors", ".gguf", ".pt",
}

PROJECT_MARKER_NAMES: set[str] = {
    "readme", "readme.md", "readme.txt", "readme.rst",
    "manifest.json", "androidmanifest.xml", "package.json",
    "pyproject.toml", "setup.py", "cargo.toml", "go.mod",
    "makefile", "cmakelists.txt", "dockerfile", "build.gradle",
}

TECH_SIGNATURES: dict[str, re.Pattern[str]] = {
    "WebGPU": re.compile(r"\b(navigator\.gpu|GPUDevice|WGSL|createShaderModule)\b"),
    "WebGL": re.compile(r"\b(webgl2?|gl\.createShader|THREE\.)\b"),
    "Web Audio / DSP": re.compile(r"\b(AudioContext|webkitAudioContext|createBiquadFilter|AudioWorklet)\b"),
    "Chrome Extension MV3": re.compile(r'"manifest_version"\s*:\s*3'),
    "Android SDK / WebView": re.compile(r"\b(android\.webkit\.WebView|MediaSession|FOREGROUND_SERVICE|com\.android\.build)\b"),
    "GTK4 / Libadwaita": re.compile(r"\b(gi\.require_version\(['\"]Gtk['\"],\s*['\"]4\.0['\"]\)|Adw\.|Gtk\.Application)\b"),
    "Ollama / Local LLM": re.compile(r"\b(ollama|11434|llama\.cpp|gguf)\b", re.IGNORECASE),
    "ONNX Runtime": re.compile(r"\b(onnxruntime|InferenceSession|\.onnx)\b", re.IGNORECASE),
    "TFLite / WebNN": re.compile(r"\b(tflite|navigator\.ml|MLGraphBuilder|Interpreter\()\b", re.IGNORECASE),
    "Apache Solr / Lucene": re.compile(r"\b(pysolr|solr|8983|lucene)\b", re.IGNORECASE),
    "Bluetooth Classic / BLE": re.compile(
        r"\b(bleak|bluez|gatt|BluetoothSocket|RFCOMM|heart_rate|00001101-0000-1000-8000-00805F9B34FB)\b",
        re.IGNORECASE,
    ),
    "LoRa / IoT": re.compile(r"\b(lorawan|ttn|thethingsnetwork|rn2483)\b", re.IGNORECASE),
    "PipeWire / Audio DSP": re.compile(r"\b(pipewire|pw-cat|jack|reaper|sounddevice|pyaudio)\b", re.IGNORECASE),
    "Google Cloud / BigQuery": re.compile(r"\b(bigquery|cloud\.run|firestore|google-cloud)\b", re.IGNORECASE),
    "MCP (Model Context Protocol)": re.compile(r"\b(modelcontextprotocol|mcp\.server|FastMCP|jsonrpc)\b", re.IGNORECASE),
    "PDF / Typography Pipeline": re.compile(r"\b(weasyprint|reportlab|fontTools|fontforge|pypdf)\b", re.IGNORECASE),
    "Docker / Podman": re.compile(r"\b(FROM |docker-compose|podman)\b"),
}

STDLIB_MODS: set[str] = {
    "os", "sys", "re", "json", "math", "time", "datetime", "pathlib",
    "collections", "itertools", "functools", "subprocess", "shutil",
    "typing", "argparse", "logging", "hashlib", "base64", "io",
    "threading", "multiprocessing", "random", "string", "copy", "ast",
    "html", "xml", "urllib", "http", "socket", "struct", "glob", "tempfile",
}

JAVA_SYMBOL_RE = re.compile(
    r"\b(?:public|final|abstract)?\s*(?:class|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+extends\s+([A-Za-z0-9_.<>]+))?"
)
JS_SYMBOL_RE = re.compile(
    r"\b(?:export\s+)?(?:async\s+)?(?:function\s+([A-Za-z_$][A-Za-z0-9_$]*)|class\s+([A-Za-z_$][A-Za-z0-9_$]*))"
)

DOMAIN_CATEGORIES: tuple[str, ...] = (
    "Enterprise intelligence and fiscal AI",
    "Browser-native AI and WebGPU engines",
    "Cloud-native virtual worlds",
    "Audio DSP, edge-AI and telemetry",
    "Low-level OS, flashing and forensics",
    "Publishing and typographic pipelines",
    "Internal utility / maintenance",
)

CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


class FatalAuthError(RuntimeError):
    """Wordt geworpen bij HTTP 401/403/404 zodat het script direct stopt (fail-fast)."""


# ==============================================================================
# HTML & CODE METADATA EXTRACTORS
# ==============================================================================
class HTMLSignalParser(HTMLParser):
    """Extraheert veilige UI-structuursignalen (<title>, headings, knoppen/labels)."""

    def __init__(self) -> None:
        super().__init__()
        self.current_tag: str | None = None
        self.titles: list[str] = []
        self.headings: list[str] = []
        self.ui_labels: list[str] = []
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        low = tag.lower()
        if low in {"title", "h1", "h2", "h3", "button", "label"}:
            self.current_tag = low
            self._buf = []

    def handle_data(self, data: str) -> None:
        if self.current_tag:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == self.current_tag:
            cleaned = " ".join("".join(self._buf).split()).strip()
            if cleaned and len(cleaned) <= 120:
                if self.current_tag == "title" and cleaned not in self.titles:
                    self.titles.append(cleaned)
                elif self.current_tag in {"h1", "h2", "h3"} and cleaned not in self.headings:
                    self.headings.append(cleaned)
                elif self.current_tag in {"button", "label"} and len(cleaned) >= 2 and cleaned not in self.ui_labels:
                    self.ui_labels.append(cleaned)
            self.current_tag = None
            self._buf = []


def is_blocked_path(path: Path) -> bool:
    low = path.as_posix().lower()
    if any(token in low for token in BLOCKED_PATH_SUBSTRINGS):
        return True
    if any(part in SKIP_TOP_DIRS for part in path.parts):
        return True
    return False


def is_low_prio(rel_path: Path) -> bool:
    for part in rel_path.parts[:-1]:
        low = part.lower()
        if any(tok == low or low.startswith(tok + "_") or low.startswith(tok + "-") for tok in LOW_PRIO_PREFIXES):
            return True
    return False


def redact_secrets(text: str) -> str:
    clean_lines: list[str] = []
    for line in text.splitlines():
        if SECRET_LINE_RE.search(line):
            clean_lines.append("[REDACTED_SENSITIVE_LINE]")
        else:
            clean_lines.append(line)
    return "\n".join(clean_lines)


def safe_read_text(path: Path, max_bytes: int = 24576) -> str:
    try:
        raw = path.read_bytes()[:max_bytes]
        txt = raw.decode("utf-8", errors="ignore")
        return redact_secrets(txt)
    except OSError:
        return ""


def clean_readme(raw_md: str) -> str:
    lines: list[str] = []
    for raw_line in raw_md.splitlines():
        s = raw_line.strip()
        if not s or set(s) <= {"=", "-", "#", "*", "`", "~"} or s.startswith(("![", "[![")):
            continue
        lines.append(re.sub(r"^#+\s*", "", s))
        if sum(len(x) for x in lines) >= 420:
            break
    return " ".join(lines)[:450]


def extract_html_signals(html_text: str) -> dict:
    parser = HTMLSignalParser()
    try:
        parser.feed(html_text)
    except Exception:
        pass
    out: dict = {}
    if parser.titles:
        out["title"] = parser.titles[0]
    if parser.headings:
        out["headings"] = parser.headings[:6]
    if parser.ui_labels:
        out["ui_labels"] = parser.ui_labels[:10]
    return out


def extract_python_ast(py_text: str) -> dict:
    res: dict = {"docstring": "", "classes": [], "functions": [], "imports": []}
    try:
        tree = ast.parse(py_text)
    except Exception:
        return res

    doc = ast.get_docstring(tree)
    if doc:
        res["docstring"] = " ".join(doc.split())[:300]

    imports_found: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            res["classes"].append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            res["functions"].append(f"{node.name}()")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                top_mod = alias.name.split(".")[0]
                if top_mod not in STDLIB_MODS:
                    imports_found.add(top_mod)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top_mod = node.module.split(".")[0]
            if top_mod not in STDLIB_MODS:
                imports_found.add(top_mod)

    res["classes"] = res["classes"][:8]
    res["functions"] = res["functions"][:10]
    res["imports"] = sorted(imports_found)[:12]
    return res


def extract_android_manifest(xml_text: str) -> dict:
    info: dict = {}
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return info

    pkg = root.attrib.get("package")
    if pkg:
        info["android_package"] = pkg

    activities: list[str] = []
    services: list[str] = []
    permissions: list[str] = []
    ns = "{http://schemas.android.com/apk/res/android}"

    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        raw_name = elem.attrib.get(f"{ns}name") or elem.attrib.get("name") or ""
        short_name = raw_name.split(".")[-1] if raw_name else ""
        if tag == "activity" and short_name and short_name not in activities:
            activities.append(short_name)
        elif tag == "service" and short_name and short_name not in services:
            services.append(short_name)
        elif tag == "uses-permission" and short_name and short_name not in permissions:
            permissions.append(short_name)

    if activities:
        info["activities"] = activities[:6]
    if services:
        info["services"] = services[:6]
    if permissions:
        info["permissions"] = permissions[:8]
    return info


def build_synthesized_topic(name: str, dna: dict, tech: set[str], langs: Counter[str]) -> str:
    parts: list[str] = []
    if dna.get("android", {}).get("android_package"):
        parts.append(f"Android: {dna['android']['android_package']}")
    titles = [h["title"] for h in dna.get("html_ui", []) if h.get("title")]
    if titles:
        parts.append(f"UI Title: '{titles[0]}'")
    if dna.get("readme_summary"):
        parts.append(dna["readme_summary"])
    elif dna.get("manifest", {}).get("description"):
        parts.append(str(dna["manifest"]["description"]))
    elif dna.get("manifest", {}).get("pkg_desc"):
        parts.append(str(dna["manifest"]["pkg_desc"]))
    elif dna.get("python_docstrings"):
        parts.append(dna["python_docstrings"][0])

    if dna.get("code_symbols"):
        parts.append(f"Symbols: {', '.join(dna['code_symbols'][:6])}")

    tail = ""
    if tech:
        tail = f"Stack: {', '.join(sorted(tech))}"
    elif langs:
        tail = f"Langs: {', '.join(k for k, _ in langs.most_common(4))}"

    body = " | ".join(parts)
    if body and tail:
        return f"{body} | {tail}"
    return body or tail or name


# ==============================================================================
# DIRECTORY CLASSIFICATION & READ-ONLY PROJECT INSPECTION
# ==============================================================================
def classify_subdir(subdir_path: Path) -> tuple[bool, str]:
    if is_blocked_path(subdir_path):
        return False, "blocked_sensitive_path"

    try:
        children = list(subdir_path.iterdir())
    except OSError as exc:
        return False, f"unreadable ({exc.strerror or 'os_error'})"

    if not children:
        return False, "empty_dir"

    sub_dirs = [c for c in children if c.is_dir() and not c.is_symlink() and not c.name.startswith(".")]
    files = [c for c in children if c.is_file() and not c.is_symlink()]

    code_files = 0
    asset_files = 0
    has_marker = False

    for f in files:
        low = f.name.lower()
        ext = f.suffix.lower()
        if low in PROJECT_MARKER_NAMES or low.startswith("readme"):
            has_marker = True
        if ext in CODE_EXT_MAP:
            code_files += 1
        elif ext in ASSET_EXTS:
            asset_files += 1

    if has_marker or code_files > 0:
        return True, "code_or_marker_present"

    if len(files) >= 15 and (asset_files / max(len(files), 1)) >= 0.70:
        return False, f"asset_sink ({len(files)} files, {asset_files} binary/media/font assets)"

    if len(sub_dirs) >= 12 and len(files) <= 2:
        sample_names = ", ".join(sorted(d.name for d in sub_dirs)[:8])
        return False, f"high_fanout_no_code ({len(sub_dirs)} subdirs: {sample_names}...)"

    return True, "inspect_deeper"


def inspect_item(source_label: str, item_path: Path, max_depth: int) -> dict | None:
    if is_blocked_path(item_path):
        return None

    if item_path.is_file() and not item_path.is_symlink():
        if SKIP_FILE_PATTERNS.search(item_path.name) or item_path.name.endswith("~"):
            return None
        try:
            st = item_path.stat()
        except OSError:
            return None

        ext = item_path.suffix.lower()
        lang = CODE_EXT_MAP.get(ext, ext or "file")
        dna: dict = {}
        tech: set[str] = set()

        if ext in CODE_EXT_MAP and st.st_size <= 300_000:
            txt = safe_read_text(item_path, 24_576)
            for tech_name, pat in TECH_SIGNATURES.items():
                if pat.search(txt):
                    tech.add(tech_name)
            if ext == ".py":
                py_info = extract_python_ast(txt)
                if py_info["docstring"]:
                    dna["python_docstrings"] = [f"{item_path.name}: {py_info['docstring']}"]
                symbols = py_info["classes"] + py_info["functions"]
                if symbols:
                    dna["code_symbols"] = symbols
                if py_info["imports"]:
                    dna["python_imports"] = py_info["imports"]

        lang_counter = Counter({lang: 1})
        return {
            "source_root": source_label,
            "name": item_path.name,
            "kind": "standalone_file",
            "path": item_path.as_posix(),
            "last_modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).strftime("%Y-%m-%d"),
            "inspected_files": 1,
            "languages": {lang: 1},
            "asset_summary": {},
            "detected_tech": sorted(tech),
            "synthesized_topic": build_synthesized_topic(item_path.name, dna, tech, lang_counter),
            "project_dna": dna,
            "active_code_files": [item_path.name],
            "pruned_subtrees": [],
        }

    if not item_path.is_dir() or item_path.is_symlink():
        return None

    lang_counter: Counter[str] = Counter()
    asset_counter: Counter[str] = Counter()
    tech_hits: set[str] = set()
    latest_mtime = 0.0
    inspected_files = 0
    pruned_subtrees: list[dict[str, str]] = []
    candidates: list[tuple[int, float, int, Path, Path]] = []

    for root, dirs, files in os.walk(item_path, followlinks=False):
        root_path = Path(root)
        if is_blocked_path(root_path):
            dirs[:] = []
            continue

        rel_root = root_path.relative_to(item_path)
        depth = len(rel_root.parts)

        if depth >= max_depth:
            if dirs:
                pruned_subtrees.append({
                    "subpath": rel_root.as_posix(),
                    "reason": f"max_depth_reached ({max_depth})",
                })
            dirs[:] = []

        kept_dirs: list[str] = []
        for dname in sorted(dirs):
            if dname in SKIP_WALK_DIRS or dname.startswith(".") or dname in SKIP_TOP_DIRS:
                continue
            sub_p = root_path / dname
            if is_blocked_path(sub_p):
                continue
            should_descend, reason = classify_subdir(sub_p)
            if should_descend:
                kept_dirs.append(dname)
            else:
                rel_sub = (rel_root / dname).as_posix()
                pruned_subtrees.append({"subpath": rel_sub, "reason": reason})
        dirs[:] = kept_dirs

        for fname in sorted(files):
            if SKIP_FILE_PATTERNS.search(fname) or fname.endswith("~"):
                continue
            fpath = root_path / fname
            if fpath.is_symlink():
                continue
            try:
                st = fpath.stat()
            except OSError:
                continue

            inspected_files += 1
            if st.st_mtime > latest_mtime:
                latest_mtime = st.st_mtime

            ext = fpath.suffix.lower()
            if ext in CODE_EXT_MAP:
                lang_counter[CODE_EXT_MAP[ext]] += 1
            elif ext in ASSET_EXTS:
                asset_counter[ext] += 1

            rel_file = rel_root / fname
            low_prio_flag = 1 if is_low_prio(rel_file) else 0
            if ext in CODE_EXT_MAP or fname.lower() in PROJECT_MARKER_NAMES or fname.lower().startswith("readme"):
                candidates.append((low_prio_flag, -st.st_mtime, -st.st_size, rel_file, fpath))

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))

    dna: dict = {}
    readme_summary = ""
    manifest_info: dict = {}
    android_info: dict = {}
    html_list: list[dict] = []
    code_symbols: list[str] = []
    python_imports: set[str] = set()
    python_docstrings: list[str] = []
    active_code_files: list[str] = []

    for low_prio_flag, _, neg_size, rel_file, fpath in candidates[:45]:
        rel_str = rel_file.as_posix()
        fname = fpath.name
        low_name = fname.lower()
        ext = fpath.suffix.lower()

        if len(active_code_files) < 12 and low_prio_flag == 0 and fname != "R.java":
            active_code_files.append(rel_str)

        if abs(neg_size) > 300_000:
            continue

        txt = safe_read_text(fpath, 24_576)
        if not txt:
            continue

        for tech_name, pat in TECH_SIGNATURES.items():
            if pat.search(txt):
                tech_hits.add(tech_name)

        if low_name.startswith("readme") and not readme_summary and low_prio_flag == 0:
            readme_summary = clean_readme(txt)

        elif low_name == "androidmanifest.xml" and not android_info and low_prio_flag == 0:
            android_info = extract_android_manifest(txt)
            tech_hits.add("Android SDK / WebView")

        elif low_name == "manifest.json" and not manifest_info and low_prio_flag == 0:
            try:
                mdata = json.loads(txt)
                if isinstance(mdata, dict):
                    manifest_info = {
                        k: v
                        for k, v in {
                            "name": mdata.get("name"),
                            "description": mdata.get("description"),
                            "version": mdata.get("version"),
                            "manifest_version": mdata.get("manifest_version"),
                        }.items()
                        if v
                    }
                    if mdata.get("manifest_version") == 3:
                        tech_hits.add("Chrome Extension MV3")
            except Exception:
                pass

        elif low_name == "package.json" and not manifest_info.get("pkg_name") and low_prio_flag == 0:
            try:
                pdata = json.loads(txt)
                if isinstance(pdata, dict):
                    if pdata.get("name"):
                        manifest_info["pkg_name"] = pdata["name"]
                    if pdata.get("description"):
                        manifest_info["pkg_desc"] = pdata["description"]
                    deps = list((pdata.get("dependencies") or {}).keys())[:10]
                    if deps:
                        manifest_info["dependencies"] = deps
            except Exception:
                pass

        elif low_name == "dockerfile":
            tech_hits.add("Docker / Podman")

        elif ext == ".html" and len(html_list) < 3 and low_prio_flag == 0:
            hs = extract_html_signals(txt)
            if hs:
                hs["file"] = rel_str
                html_list.append(hs)

        elif ext == ".py" and low_prio_flag == 0:
            py_info = extract_python_ast(txt)
            if py_info["docstring"] and len(python_docstrings) < 2:
                python_docstrings.append(f"{fname}: {py_info['docstring']}")
            for sym in py_info["classes"] + py_info["functions"]:
                if sym not in code_symbols and len(code_symbols) < 15:
                    code_symbols.append(sym)
            python_imports.update(py_info["imports"])

        elif ext in {".java", ".kt", ".cs"} and fname != "R.java" and low_prio_flag == 0:
            for m in JAVA_SYMBOL_RE.finditer(txt):
                cls_name, ext_name = m.groups()
                lbl = f"{cls_name} extends {ext_name}" if ext_name else cls_name
                if lbl not in code_symbols and len(code_symbols) < 15:
                    code_symbols.append(lbl)

        elif ext in {".js", ".ts", ".mjs"} and low_prio_flag == 0:
            for m in JS_SYMBOL_RE.finditer(txt):
                sym = m.group(1) or m.group(2)
                if sym and len(sym) > 2 and sym not in code_symbols and len(code_symbols) < 15:
                    code_symbols.append(sym)

    if readme_summary:
        dna["readme_summary"] = readme_summary
    if manifest_info:
        dna["manifest"] = manifest_info
    if android_info:
        dna["android"] = android_info
    if html_list:
        dna["html_ui"] = html_list
    if code_symbols:
        dna["code_symbols"] = code_symbols
    if python_imports:
        dna["python_imports"] = sorted(python_imports)[:12]
    if python_docstrings:
        dna["python_docstrings"] = python_docstrings

    last_mod_str = (
        datetime.fromtimestamp(latest_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
        if latest_mtime > 0
        else "unknown"
    )

    return {
        "source_root": source_label,
        "name": item_path.name,
        "kind": "directory",
        "path": item_path.as_posix(),
        "last_modified": last_mod_str,
        "inspected_files": inspected_files,
        "languages": dict(lang_counter.most_common(8)),
        "asset_summary": dict(asset_counter.most_common(6)),
        "detected_tech": sorted(tech_hits),
        "synthesized_topic": build_synthesized_topic(item_path.name, dna, tech_hits, lang_counter),
        "project_dna": dna,
        "active_code_files": active_code_files,
        "pruned_subtrees": pruned_subtrees,
    }


# ==============================================================================
# SANDBOXED VERTEX AI (OAUTH2 GLOBAL/REGIONAL OR EXPRESS API KEY) + CACHE
# ==============================================================================
def resolve_gemini_credentials(cli_key: str, offline: bool) -> tuple[str, str] | None:
    """Detecteert automatisch Service Account JSON of AIza API-sleutel.

    Returns ("api_key", raw_key_str) | ("service_account", resolved_json_path) | None.
    """
    if offline:
        return None

    explicit = (cli_key or "").strip()
    if explicit:
        if explicit.startswith("AIza"):
            return ("api_key", explicit)
        p = Path(explicit).expanduser().resolve()
        if p.is_file() and p.suffix.lower() == ".txt":
            txt_key = p.read_text(encoding="utf-8").strip()
            if txt_key.startswith("AIza"):
                return ("api_key", txt_key)
        return ("service_account", str(p))

    env_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_api_key.startswith("AIza"):
        return ("api_key", env_api_key)

    env_sa_key = os.environ.get("GEMINI_SERVICE_ACCOUNT_KEY", "").strip()
    if env_sa_key:
        if env_sa_key.startswith("AIza"):
            return ("api_key", env_sa_key)
        return ("service_account", str(Path(env_sa_key).expanduser().resolve()))

    script_dir = Path(__file__).resolve().parent

    # 1. Controleer eerst op een eventuele Express API-sleutel (gemini_api_key.txt)
    txt_candidates = [
        script_dir / "gemini_api_key.txt",
        REPO_ROOT / "gemini_api_key.txt",
    ]
    for tc in txt_candidates:
        if tc.is_file():
            raw_val = tc.read_text(encoding="utf-8").strip()
            if raw_val.startswith("AIza"):
                return ("api_key", raw_val)

    # 2. Controleer standaardlocaties voor Service Account JSON (gemini_key.json)
    json_candidates = [
        script_dir / "gemini_key.json",
        REPO_ROOT / "gemini_key.json",
        script_dir.parent / "gemini_key.json",
    ]
    for jc in json_candidates:
        if jc.is_file():
            return ("service_account", str(jc.resolve()))

    return None


class VertexOAuthSession:
    """Beheert OAuth2 Service Account credentials en bouwt de Vertex AI endpoint-URL (global of regionaal)."""

    def __init__(self, key_path: Path, location: str = "global") -> None:
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
        except ImportError as exc:
            print(f"[ERROR] Pakket 'google-auth' ontbreekt ({exc}). Installeer via systeembeheer.", file=sys.stderr)
            sys.exit(1)

        if not key_path.is_file():
            print(f"[ERROR] Service Account JSON-sleutel niet gevonden: {key_path}", file=sys.stderr)
            sys.exit(1)

        try:
            key_meta = json.loads(key_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[ERROR] Kan Service Account JSON niet lezen ({key_path}): {exc}", file=sys.stderr)
            sys.exit(1)

        self.project_id = str(key_meta.get("project_id") or "").strip()
        if not self.project_id:
            print(f"[ERROR] Veld 'project_id' ontbreekt in {key_path}", file=sys.stderr)
            sys.exit(1)

        self.location = (location or "global").strip() or "global"
        self.key_path = key_path
        self.backend_label = "vertex_ai_oauth"

        self._request = Request()
        self._creds = service_account.Credentials.from_service_account_file(
            str(key_path),
            scopes=[CLOUD_PLATFORM_SCOPE],
        )
        self._creds.refresh(self._request)

    def get_token(self) -> str:
        if not self._creds.valid or not self._creds.token:
            self._creds.refresh(self._request)
        return str(self._creds.token)

    def build_generate_url(self, model: str) -> str:
        if self.location == "global":
            host = "https://aiplatform.googleapis.com"
        else:
            host = f"https://{self.location}-aiplatform.googleapis.com"
        return (
            f"{host}/v1/projects/{self.project_id}"
            f"/locations/{self.location}/publishers/google/models/{model}:generateContent"
        )

    def build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
        }


class VertexExpressApiKeySession:
    """Gebruikt een Google Cloud Vertex AI Express API-sleutel (AIza...) zonder OAuth2-projectpad."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key.strip()
        self.project_id = "vertex-express-mode"
        self.location = "global"
        self.backend_label = "vertex_ai_express_key"

    def build_generate_url(self, model: str) -> str:
        return f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent"

    def build_headers(self) -> dict[str, str]:
        return {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }


def build_sandbox_metadata(project: dict) -> dict:
    """Stelt het strikt geschoonde, compacte metadata-object samen voor externe AI-synthese."""
    return {
        "name": project.get("name", ""),
        "last_modified": project.get("last_modified", "unknown"),
        "languages": project.get("languages", {}),
        "detected_tech": project.get("detected_tech", []),
        "project_dna": project.get("project_dna", {}),
        "active_code_files": project.get("active_code_files", []),
    }


def compute_dna_hash(project: dict) -> str:
    """Berekent deterministische SHA-256 fingerprint op basis van project_dna en technische kernvelden."""
    canonical_subject = {
        "name": project.get("name", ""),
        "languages": project.get("languages", {}),
        "detected_tech": project.get("detected_tech", []),
        "project_dna": project.get("project_dna", {}),
        "active_code_files": project.get("active_code_files", []),
    }
    raw_bytes = json.dumps(canonical_subject, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw_bytes).hexdigest()


def load_synthesis_cache(cache_path: Path) -> dict[str, dict]:
    if not cache_path.is_file():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception as exc:
        print(f"[WARN] Kon AI-cache niet uitlezen ({cache_path}): {exc}", file=sys.stderr)
    return {}


def save_synthesis_cache(cache_path: Path, cache_data: dict[str, dict]) -> None:
    tmp_path = cache_path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(cache_data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(cache_path)


def normalize_synthesis_result(raw_obj: dict) -> dict:
    onderwerp = str(raw_obj.get("onderwerp_kort") or "").strip()
    architectuur = str(raw_obj.get("architectuur_samenvatting") or "").strip()
    categorie = str(raw_obj.get("domein_categorie") or "Internal utility / maintenance").strip()
    if categorie not in DOMAIN_CATEGORIES:
        categorie = "Internal utility / maintenance"
    publiek = bool(raw_obj.get("geschikt_voor_publiek_portaal", False))
    return {
        "onderwerp_kort": onderwerp,
        "architectuur_samenvatting": architectuur,
        "domein_categorie": categorie,
        "geschikt_voor_publiek_portaal": publiek,
    }


def query_vertex_synthesis(
    session: VertexOAuthSession | VertexExpressApiKeySession,
    model: str,
    project: dict,
) -> tuple[dict, bool]:
    """Stuurt uitsluitend geschoonde project_dna metadata naar Vertex AI generateContent.

    Returns (result_dict, ok_to_cache). Raises FatalAuthError op HTTP 401/403/404.
    """
    sandbox_meta = build_sandbox_metadata(project)
    categories_str = " | ".join(DOMAIN_CATEGORIES)
    prompt = (
        "Analyseer uitsluitend deze geschoonde metadata van een lokaal softwareproject. "
        "Baseer je strikt op de aangeleverde velden en verzin GEEN feiten of functionaliteit die niet uit de metadata blijkt.\n"
        "Geef een JSON-object terug met exact deze 4 velden:\n"
        "1. 'onderwerp_kort': Eén beknopte, feitelijke Nederlandse zin die beschrijft wat het project daadwerkelijk doet.\n"
        "2. 'architectuur_samenvatting': Technische architectuursamenvatting (maximaal 2 zinnen in het Nederlands), "
        "geschikt voor een R&D-portfolio.\n"
        f"3. 'domein_categorie': Kies exact één best passende categorie uit: {categories_str}.\n"
        "4. 'geschikt_voor_publiek_portaal': Boolean (true voor volwaardige R&D- of engineeringprojecten; "
        "false voor lokale opschoonscripts, testjes of eenmalige hulpscripts).\n\n"
        "Metadata:\n"
        + json.dumps(sandbox_meta, ensure_ascii=False)
    )

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "onderwerp_kort": {"type": "STRING"},
                    "architectuur_samenvatting": {"type": "STRING"},
                    "domein_categorie": {
                        "type": "STRING",
                        "enum": list(DOMAIN_CATEGORIES),
                    },
                    "geschikt_voor_publiek_portaal": {"type": "BOOLEAN"},
                },
                "required": [
                    "onderwerp_kort",
                    "architectuur_samenvatting",
                    "domein_categorie",
                    "geschikt_voor_publiek_portaal",
                ],
            },
            "temperature": 0.1,
        },
    }

    url = session.build_generate_url(model)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=session.build_headers(),
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            cand = resp_data["candidates"][0]["content"]
            parts = cand.get("parts") or []
            raw_text = parts[0]["text"].strip()
            parsed = json.loads(raw_text)
            return normalize_synthesis_result(parsed), True
    except urllib.error.HTTPError as exc:
        err_body = ""
        try:
            err_body = exc.read().decode("utf-8", errors="ignore")[:360]
        except Exception:
            pass
        msg = f"[API HTTP {exc.code}: {exc.reason} {err_body}]".strip()
        if exc.code in (401, 403, 404):
            raise FatalAuthError(msg) from exc
        print(f"[API-ERROR] {project.get('name')}: {msg}", file=sys.stderr)
        return {
            "onderwerp_kort": msg,
            "architectuur_samenvatting": "",
            "domein_categorie": "Internal utility / maintenance",
            "geschikt_voor_publiek_portaal": False,
        }, False
    except Exception as exc:
        msg = f"[API fout: {exc}]"
        print(f"[API-ERROR] {project.get('name')}: {msg}", file=sys.stderr)
        return {
            "onderwerp_kort": msg,
            "architectuur_samenvatting": "",
            "domein_categorie": "Internal utility / maintenance",
            "geschikt_voor_publiek_portaal": False,
        }, False


# ==============================================================================
# CLI & MAIN ORCHESTRATION
# ==============================================================================
def resolve_input_roots(cli_paths: list[str] | None) -> list[tuple[str, Path]]:
    if not cli_paths:
        return TOP_INPUT_PATHS
    resolved: list[tuple[str, Path]] = []
    for idx, raw in enumerate(cli_paths, start=1):
        p = Path(raw).expanduser().resolve()
        label = f"custom_{idx}_{p.name}"
        resolved.append((label, p))
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discreet, read-only, content-driven local project trawler v3.1.1 with sandboxed Vertex AI Gemini synthesis."
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        help="Optionele lijst van top-inputpaden (overschrijft standaard TOP_INPUT_PATHS).",
    )
    parser.add_argument(
        "--out",
        default=str(BASE_OUT_DIR),
        help="Basismap voor uitvoer (standaard: /home/steve/dump/trawler/results/local_projects_corpus).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=10,
        help="Maximale scandiepte binnen code-projecten (standaard: 10).",
    )
    parser.add_argument(
        "--gemini-key",
        default="",
        help="Pad naar Service Account JSON-sleutel, pad naar .txt met AIza-sleutel, of directe AIza...-sleutel.",
    )
    parser.add_argument(
        "--gemini-model",
        default="gemini-2.5-flash",
        help="Vertex AI Gemini model-ID voor synthese (standaard: gemini-2.5-flash).",
    )
    parser.add_argument(
        "--gcp-location",
        default="global",
        help="Google Cloud Vertex AI locatie (standaard: global; bijv. ook us-central1 of europe-west4).",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Negeer bestaande AI-synthese cache en bevraag Vertex AI opnieuw.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Forceer 100%% offline uitvoering zonder API-aanroepen, ook als een sleutel aanwezig is.",
    )
    args = parser.parse_args()

    cred_info = resolve_gemini_credentials(args.gemini_key, args.offline)
    ai_enabled = cred_info is not None
    ai_session: VertexOAuthSession | VertexExpressApiKeySession | None = None

    base_out = Path(args.out).expanduser().resolve()
    base_out.mkdir(parents=True, exist_ok=True)
    cache_path = base_out / "ai_synthesis_cache.json"
    synthesis_cache: dict[str, dict] = {}
    cache_hits = 0
    api_calls = 0

    if ai_enabled and cred_info is not None:
        cred_kind, cred_val = cred_info
        synthesis_cache = load_synthesis_cache(cache_path)
        if cred_kind == "api_key":
            ai_session = VertexExpressApiKeySession(cred_val)
            print(
                f"[AI-MODE] Vertex AI Express API-sleutel actief "
                f"(model: {args.gemini_model}, endpoint: global, cache-items: {len(synthesis_cache)})"
            )
        else:
            key_path = Path(cred_val)
            ai_session = VertexOAuthSession(key_path, location=args.gcp_location)
            print(
                f"[AI-MODE] Vertex AI OAuth2 geauthenticeerd "
                f"(project: {ai_session.project_id}, locatie: {ai_session.location}, "
                f"model: {args.gemini_model}, key: {key_path}, cache-items: {len(synthesis_cache)})"
            )
    else:
        print("[OFFLINE-MODE] Geen actieve sleutel gevonden (--offline of niet aanwezig); draait 100% deterministisch.")

    run_stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    run_dir = base_out / f"run_{run_stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    out_json = run_dir / "local_projects_manifest.json"
    out_md = run_dir / "local_projects_summary.md"

    active_roots = resolve_input_roots(args.paths)
    projects: list[dict] = []

    try:
        for label, root_path in active_roots:
            if is_blocked_path(root_path):
                print(f"[BLOCKED] Gevoelig pad overgeslagen: {root_path}")
                continue
            if not root_path.exists() or not root_path.is_dir():
                print(f"[SKIP] Pad niet gevonden of geen map: {root_path}")
                continue

            entries = sorted(
                [
                    p for p in root_path.iterdir()
                    if not p.name.startswith(".") and not is_blocked_path(p)
                ],
                key=lambda p: p.name.lower(),
            )
            print(f"=== SCANNING {label} ({root_path}) — {len(entries)} items ===")
            for entry in entries:
                info = inspect_item(label, entry, max_depth=args.max_depth)
                if info is None:
                    continue

                if ai_enabled and ai_session is not None:
                    dna_sha = compute_dna_hash(info)
                    cache_key = f"{args.gemini_model}:{dna_sha}"
                    if not args.no_cache and cache_key in synthesis_cache:
                        info["ai_synthesis"] = synthesis_cache[cache_key]
                        cache_hits += 1
                    else:
                        print(f"  [VERTEX-GEMINI] Synthese voor: {info['name']} ({dna_sha[:12]})...")
                        synth_res, ok_to_cache = query_vertex_synthesis(ai_session, args.gemini_model, info)
                        info["ai_synthesis"] = synth_res
                        api_calls += 1
                        if ok_to_cache:
                            synthesis_cache[cache_key] = synth_res
                            save_synthesis_cache(cache_path, synthesis_cache)

                projects.append(info)
    except FatalAuthError as exc:
        print(
            f"\n[FATAL-AUTH/MODEL] Afgebroken na HTTP 401/403/404 van Vertex AI:\n{exc}\n\n"
            "Controleer één van deze twee stappen in Google Cloud Console:\n"
            "1. Open Vertex AI Studio (https://console.cloud.google.com/vertex-ai/studio?project=gemini-development-hub-2026) "
            "en verstuur eenmalig een testprompt om modeltoegang vrij te geven.\n"
            "2. Of klik in de zijbalk op 'Get API key' (https://console.cloud.google.com/apis/credentials?project=gemini-development-hub-2026) "
            "en sla de AIza...-sleutel op in /home/steve/dump/trawler/gemini_api_key.txt.",
            file=sys.stderr,
        )
        sys.exit(1)

    generated_iso = datetime.now(timezone.utc).astimezone().isoformat()
    manifest = {
        "schema_version": "3.1.1",
        "generated_at": generated_iso,
        "run_id": f"run_{run_stamp}",
        "run_dir": run_dir.as_posix(),
        "ai_synthesis_enabled": ai_enabled,
        "ai_backend": ai_session.backend_label if ai_session else None,
        "gcp_project_id": ai_session.project_id if ai_session else None,
        "gcp_location": ai_session.location if ai_session else None,
        "gemini_model": args.gemini_model if ai_enabled else None,
        "input_roots": [{"label": lbl, "path": rp.as_posix()} for lbl, rp in active_roots],
        "total_items": len(projects),
        "projects": projects,
    }
    out_json.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        f"# Discreet R&D Project Inventory — {manifest['run_id']}",
        "",
        f"- **Schema-versie:** `3.1.1`",
        f"- **Gegenereerd op:** `{generated_iso}`",
        f"- **Run-map:** `{run_dir.as_posix()}`",
        f"- **AI-synthese:** `{'actief via ' + ai_session.backend_label + ' (' + args.gemini_model + ' @ ' + ai_session.location + ')' if ai_enabled and ai_session else 'uitgeschakeld (offline)'}`",
        f"- **Totaal geïnspecteerde projecten/items:** `{len(projects)}`",
        "",
    ]

    by_root: dict[str, list[dict]] = {}
    for p in projects:
        by_root.setdefault(p["source_root"], []).append(p)

    for label, items in by_root.items():
        md.append(f"## Bron: `{label}` ({len(items)} items)")
        md.append("")
        for p in items:
            langs = ", ".join(f"{k} ({v})" for k, v in p["languages"].items()) or "geen code gedetecteerd"
            tech = ", ".join(p["detected_tech"]) if p["detected_tech"] else "-"
            md.append(f"### `{p['name']}` (`{p['last_modified']}`, {p['inspected_files']} bestanden)")

            ai_syn = p.get("ai_synthesis")
            if isinstance(ai_syn, dict):
                pub_label = "JA (Geschikt voor R&D-portaal)" if ai_syn.get("geschikt_voor_publiek_portaal") else "NEE (Intern / utility)"
                md.append(f"> **Domein:** {ai_syn.get('domein_categorie', '-')} | **Publiek portaal:** {pub_label}")
                if ai_syn.get("onderwerp_kort"):
                    md.append(f"> **Onderwerp:** {ai_syn['onderwerp_kort']}")
                if ai_syn.get("architectuur_samenvatting"):
                    md.append(f"> **Architectuur:** {ai_syn['architectuur_samenvatting']}")

            md.append(f"- **Talen:** {langs}")
            if p["asset_summary"]:
                assets = ", ".join(f"{k} ({v})" for k, v in p["asset_summary"].items())
                md.append(f"- **Assets:** {assets}")
            md.append(f"- **Gedetecteerde stack:** {tech}")
            if p.get("synthesized_topic"):
                md.append(f"- **Statische DNA-synthese:** {p['synthesized_topic']}")
            files_list = p.get("active_code_files") or []
            if files_list:
                md.append(f"- **Actieve codebestanden:** `{', '.join(files_list[:8])}`")
            if p["pruned_subtrees"]:
                pruned_str = "; ".join(f"{x['subpath']} ({x['reason']})" for x in p["pruned_subtrees"][:5])
                md.append(f"- **Slim gesnoeide submappen:** {pruned_str}")
            md.append("")

    out_md.write_text("\n".join(md), encoding="utf-8")

    print("\n=== RUN VOLTOOID ===")
    print(f"Run-map       : {run_dir}")
    print(f"JSON manifest : {out_json}")
    print(f"Markdown dump : {out_md} ({out_md.stat().st_size} bytes)")
    if ai_enabled:
        print(f"AI-synthese   : {api_calls} API-aanroepen, {cache_hits} cache-hits ({cache_path})")


if __name__ == "__main__":
    main()