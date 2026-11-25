# ==============================================================================
# INTEGRITY HEADER
# Project : Site Assistant Knowledgebase (https://steven.kleynenberg.com/)
# Path    : /home/steve/gemini/github.io/knowlegdebase/extract_kb.py
# Host    : hp.kleynenberg.net (Fedora / system Python3, no venv)
# Editor  : joe
# Rule    : No dummy data, no lambdas, explicit checks & logging
# ==============================================================================

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

SKIP_FILENAMES = {
    ".gitkeep",
    ".ds_store",
}

SKIP_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".mp4",
    ".webm",
    ".mp3",
    ".wav",
    ".ogg",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".gitkeep",
}

DIRECT_TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".tex",
    ".json",
    ".jsonld",
    ".cff",
    ".py",
    ".sh",
    ".js",
    ".css",
    ".url",
    ".csv",
    ".tsv",
    ".yaml",
    ".yml",
    ".toml",
}


def log_info(message):
    sys.stdout.write(f"[extract] {message}\n")


def log_warn(message):
    sys.stderr.write(f"[extract][WARN] {message}\n")


def log_error(message):
    sys.stderr.write(f"[extract][ERROR] {message}\n")


def load_checksums(hash_path):
    hashes = {}
    if not os.path.isfile(hash_path):
        log_warn(f"Checksum file not found: {hash_path}; computing live SHA-256 per file.")
        return hashes

    with open(hash_path, "r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            parts = stripped.split(None, 1)
            if len(parts) != 2:
                log_warn(f"Malformed hash line {line_number} in {hash_path}: {stripped}")
                continue
            digest, file_path = parts[0].strip(), parts[1].strip()
            hashes[file_path] = digest
            hashes[os.path.normpath(file_path)] = digest
    return hashes


def compute_sha256(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as handle:
        while True:
            block = handle.read(65536)
            if not block:
                break
            hasher.update(block)
    return hasher.hexdigest()


def normalize_whitespace(text):
    collapsed_spaces = re.sub(r"[ \t\r\f\v]+", " ", text)
    collapsed_newlines = re.sub(r"\n{3,}", "\n\n", collapsed_spaces)
    lines = [line.strip() for line in collapsed_newlines.splitlines()]
    non_empty_lines = [line for line in lines if line]
    return "\n\n".join(non_empty_lines).strip()


def extract_html_text(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as handle:
        raw_html = handle.read()
    soup = BeautifulSoup(raw_html, "html.parser")
    for unwanted in soup(["script", "style", "noscript"]):
        unwanted.decompose()
    text = soup.get_text(separator="\n")
    return normalize_whitespace(text)


def extract_xml_text(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as handle:
        raw_xml = handle.read()
    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as exc:
        log_warn(f"XML parse error in {file_path} ({exc}); falling back to BeautifulSoup XML/HTML extraction.")
        soup = BeautifulSoup(raw_xml, "html.parser")
        for unwanted in soup(["script", "style", "noscript"]):
            unwanted.decompose()
        return normalize_whitespace(soup.get_text(separator="\n"))

    fragments = []
    for text_piece in root.itertext():
        cleaned = text_piece.strip()
        if cleaned:
            fragments.append(cleaned)
    joined = "\n".join(fragments)
    return normalize_whitespace(joined)


def extract_pdf_text(file_path):
    completed = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", file_path, "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr_msg = completed.stderr.strip() if completed.stderr else "unknown pdftotext error"
        raise RuntimeError(f"pdftotext failed on {file_path} (rc={completed.returncode}): {stderr_msg}")
    return normalize_whitespace(completed.stdout)


def extract_plain_text(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as handle:
        raw_text = handle.read()
    return normalize_whitespace(raw_text)


def classify_and_extract(file_path):
    base_name = os.path.basename(file_path)
    _, ext = os.path.splitext(base_name)
    ext_lower = ext.lower()
    base_lower = base_name.lower()

    if base_lower in SKIP_FILENAMES:
        return "skipped_binary", ""

    if base_lower == "cname":
        return "cname", extract_plain_text(file_path)

    if ext_lower in SKIP_EXTENSIONS:
        return "skipped_binary", ""

    if ext_lower in {".html", ".htm"}:
        return "html", extract_html_text(file_path)

    if ext_lower == ".xml":
        return "xml", extract_xml_text(file_path)

    if ext_lower == ".pdf":
        return "pdf", extract_pdf_text(file_path)

    if ext_lower in DIRECT_TEXT_EXTENSIONS:
        doc_type = ext_lower.lstrip(".") if ext_lower else "text"
        return doc_type, extract_plain_text(file_path)

    log_warn(f"Unclassified extension '{ext_lower or '<none>'}' for {file_path}; attempting plain text read.")
    return "other_text", extract_plain_text(file_path)


def split_into_chunks(text, max_chars, overlap_chars):
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)
    step = max(1, max_chars - overlap_chars)

    while start < text_len:
        end = min(start + max_chars, text_len)
        if end < text_len:
            newline_pos = text.rfind("\n\n", start + int(max_chars * 0.5), end)
            space_pos = text.rfind(" ", start + int(max_chars * 0.5), end)
            if newline_pos != -1:
                end = newline_pos
            elif space_pos != -1:
                end = space_pos
        segment = text[start:end].strip()
        if segment:
            chunks.append(segment)
        if end >= text_len:
            break
        next_start = end - overlap_chars
        if next_start <= start:
            next_start = start + step
        start = next_start

    return chunks


def read_inventory(inventory_path):
    if not os.path.isfile(inventory_path):
        raise FileNotFoundError(f"Inventory file not found: {inventory_path}")
    paths = []
    with open(inventory_path, "r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            entry = raw_line.strip()
            if entry:
                paths.append(entry)
    return paths


def parse_args():
    parser = argparse.ArgumentParser(description="Extract text chunks from inventory.txt into JSONL.")
    parser.add_argument("--inventory", default="inventory.txt", help="Path to inventory.txt")
    parser.add_argument("--hashes", default="sha256.sum", help="Path to sha256.sum")
    parser.add_argument("--output", default="chunks.jsonl", help="Output JSONL path")
    parser.add_argument("--max-chars", type=int, default=1200, help="Maximum characters per chunk")
    parser.add_argument("--overlap-chars", type=int, default=150, help="Overlap characters between chunks")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.max_chars < 200:
        log_error("--max-chars must be at least 200.")
        return 1
    if args.overlap_chars < 0 or args.overlap_chars >= args.max_chars:
        log_error("--overlap-chars must be >= 0 and smaller than --max-chars.")
        return 1

    try:
        entries = read_inventory(args.inventory)
    except FileNotFoundError as exc:
        log_error(str(exc))
        return 1

    checksums = load_checksums(args.hashes)

    counts = {
        "total_entries": len(entries),
        "processed_files": 0,
        "skipped_files": 0,
        "empty_files": 0,
        "error_files": 0,
        "total_chunks": 0,
    }

    with open(args.output, "w", encoding="utf-8") as out_handle:
        for entry in entries:
            norm_entry = os.path.normpath(entry)
            if not os.path.isfile(entry):
                log_warn(f"Missing file from inventory: {entry}")
                counts["error_files"] += 1
                continue

            digest = checksums.get(entry) or checksums.get(norm_entry) or compute_sha256(entry)

            try:
                doc_type, extracted_text = classify_and_extract(entry)
            except Exception as exc:
                log_error(f"Failed extracting {entry}: {exc}")
                counts["error_files"] += 1
                continue

            if doc_type == "skipped_binary":
                counts["skipped_files"] += 1
                continue

            if not extracted_text:
                log_warn(f"No text extracted ({doc_type}) from {entry}")
                counts["empty_files"] += 1
                continue

            chunk_texts = split_into_chunks(extracted_text, args.max_chars, args.overlap_chars)
            counts["processed_files"] += 1

            for idx, chunk_text in enumerate(chunk_texts):
                record = {
                    "chunk_id": f"{digest[:12]}:{idx:04d}",
                    "source_path": norm_entry,
                    "doc_type": doc_type,
                    "sha256": digest,
                    "chunk_index": idx,
                    "chunk_total": len(chunk_texts),
                    "char_count": len(chunk_text),
                    "text": chunk_text,
                }
                out_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                counts["total_chunks"] += 1

    log_info(
        "Summary: "
        f"inventory={counts['total_entries']}, "
        f"processed={counts['processed_files']}, "
        f"skipped={counts['skipped_files']}, "
        f"empty={counts['empty_files']}, "
        f"errors={counts['error_files']}, "
        f"chunks={counts['total_chunks']} -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())