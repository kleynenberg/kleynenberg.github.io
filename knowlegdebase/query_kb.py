# ==============================================================================
# INTEGRITY HEADER
# Project : Site Assistant Knowledgebase (https://steven.kleynenberg.com/)
# Path    : /home/steve/gemini/github.io/knowlegdebase/query_kb.py
# Host    : hp.kleynenberg.net (Fedora / system Python3, no venv)
# Editor  : joe
# Rule    : No dummy data, no lambdas, explicit checks & logging
# ==============================================================================

import argparse
import json
import math
import os
import re
import sys


def log_info(message):
    sys.stdout.write(f"[query] {message}\n")


def log_error(message):
    sys.stderr.write(f"[query][ERROR] {message}\n")


def tokenize(text):
    lowered = text.lower()
    return re.findall(r"[a-z0-9_./-]{2,}", lowered)


def load_chunks(chunks_path):
    if not os.path.isfile(chunks_path):
        raise FileNotFoundError(f"Chunks file not found: {chunks_path}")

    records = []
    with open(chunks_path, "r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                log_error(f"Invalid JSON at line {line_number} in {chunks_path}: {exc}")
                continue
            text = item.get("text", "")
            tokens = tokenize(text)
            records.append({
                "chunk_id": item.get("chunk_id", f"line-{line_number}"),
                "source_path": item.get("source_path", "<unknown>"),
                "doc_type": item.get("doc_type", "<unknown>"),
                "sha256": item.get("sha256", ""),
                "text": text,
                "tokens": tokens,
            })
    return records


def build_idf(records):
    doc_count = len(records)
    if doc_count == 0:
        return {}

    df = {}
    for record in records:
        unique_tokens = set(record["tokens"])
        for tok in unique_tokens:
            df[tok] = df.get(tok, 0) + 1

    idf = {}
    for tok, freq in df.items():
        idf[tok] = math.log((1.0 + doc_count) / (1.0 + freq)) + 1.0
    return idf


def score_record(record, query_tokens, idf):
    if not query_tokens or not record["tokens"]:
        return 0.0

    token_counts = {}
    for tok in record["tokens"]:
        token_counts[tok] = token_counts.get(tok, 0) + 1

    doc_len = float(len(record["tokens"]))
    score = 0.0
    matched_terms = 0

    for qtok in query_tokens:
        tf = token_counts.get(qtok, 0)
        if tf > 0:
            matched_terms += 1
            term_weight = idf.get(qtok, 1.0)
            tf_norm = tf / (tf + 1.5)
            score += term_weight * tf_norm

    if matched_terms == 0:
        return 0.0

    coverage_bonus = (matched_terms / float(len(query_tokens))) * 0.5
    length_penalty = 1.0 / (1.0 + 0.0005 * doc_len)
    return (score + coverage_bonus) * length_penalty


def compare_scored_items(item_a, item_b):
    if item_a["score"] > item_b["score"]:
        return -1
    if item_a["score"] < item_b["score"]:
        return 1
    if item_a["chunk_id"] < item_b["chunk_id"]:
        return -1
    if item_a["chunk_id"] > item_b["chunk_id"]:
        return 1
    return 0


def sort_scored_items(scored_items):
    ordered = list(scored_items)
    n = len(ordered)
    for i in range(n):
        for j in range(0, n - i - 1):
            if compare_scored_items(ordered[j], ordered[j + 1]) > 0:
                temp = ordered[j]
                ordered[j] = ordered[j + 1]
                ordered[j + 1] = temp
    return ordered


def make_snippet(text, query_tokens, max_len):
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= max_len:
        return compact

    lower_compact = compact.lower()
    hit_index = -1
    for qtok in query_tokens:
        pos = lower_compact.find(qtok)
        if pos != -1 and (hit_index == -1 or pos < hit_index):
            hit_index = pos

    if hit_index == -1:
        return compact[:max_len].rstrip() + "..."

    start = max(0, hit_index - int(max_len * 0.25))
    end = min(len(compact), start + max_len)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(compact) else ""
    return prefix + compact[start:end].strip() + suffix


def parse_args():
    parser = argparse.ArgumentParser(description="Search local chunks.jsonl knowledgebase.")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--chunks", default="chunks.jsonl", help="Path to chunks.jsonl")
    parser.add_argument("--doc-type", default="", help="Optional filter on doc_type (e.g. xml, pdf, html, txt)")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top matching chunks to display")
    parser.add_argument("--snippet-len", type=int, default=260, help="Maximum snippet length in characters")
    parser.add_argument("--json", action="store_true", help="Output matching results as JSON")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.top_k < 1:
        log_error("--top-k must be at least 1.")
        return 1

    try:
        all_records = load_chunks(args.chunks)
    except FileNotFoundError as exc:
        log_error(str(exc))
        return 1

    doc_type_filter = args.doc_type.strip().lower()
    if doc_type_filter:
        filtered_records = []
        for rec in all_records:
            if rec["doc_type"].lower() == doc_type_filter:
                filtered_records.append(rec)
        records = filtered_records
    else:
        records = all_records

    if not records:
        log_info(f"No chunks available in {args.chunks} (filter={doc_type_filter or 'none'}).")
        return 0

    query_tokens = tokenize(args.query)
    if not query_tokens:
        log_error("Query produced no searchable tokens.")
        return 1

    idf = build_idf(records)
    scored = []
    for rec in records:
        value = score_record(rec, query_tokens, idf)
        if value > 0.0:
            scored.append({
                "score": round(value, 6),
                "chunk_id": rec["chunk_id"],
                "source_path": rec["source_path"],
                "doc_type": rec["doc_type"],
                "snippet": make_snippet(rec["text"], query_tokens, args.snippet_len),
            })

    if not scored:
        log_info(f"No matching chunks for query: {args.query!r}")
        return 0

    ordered = sort_scored_items(scored)
    top_matches = ordered[: args.top_k]

    if args.json:
        sys.stdout.write(json.dumps(top_matches, ensure_ascii=False, indent=2) + "\n")
        return 0

    log_info(f"Matches={len(scored)} (showing top {len(top_matches)}) for query={args.query!r}")
    for rank, match in enumerate(top_matches, start=1):
        sys.stdout.write(
            f"[{rank}] score={match['score']:.4f} | id={match['chunk_id']} | "
            f"type={match['doc_type']} | src={match['source_path']}\n"
            f"    {match['snippet']}\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())