python3 - <<'PY'
# ==============================================================================
# INTEGRITY HEADER — KLEYNENBERG.COM / GITHUB.IO (CORPUS FACT CONSOLIDATION)
# File:       consolidate_trawled_facts.py
# Input:      /home/steve/gemini/github.io/chatGPT/trawled_corpus/corpus_manifest.json
# Output:     /home/steve/gemini/github.io/chatGPT/trawled_corpus/consolidated_facts_for_llm.md
# Standards:  RFC 1321 (MD5), RFC 8259 (JSON), YAML 1.2, W3C XML 1.0
# Toolchain:  Python 3.15 (https://www.python.org/), PyYAML 6.0.3 (https://pyyaml.org/)
# Safety:     Strictly read-only on trawled/, site2014/, papers/, icons/, .git/,
#             and repo root; excludes *.sh scripts; zero venv/pip.
# ==============================================================================
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import sys

import yaml

REPO_ROOT = Path("/home/steve/gemini/github.io")
CHATGPT_DIR = REPO_ROOT / "chatGPT"
CORPUS_DIR = CHATGPT_DIR / "trawled_corpus"
MANIFEST_PATH = CORPUS_DIR / "corpus_manifest.json"
OUT_MD_PATH = CORPUS_DIR / "consolidated_facts_for_llm.md"

if not MANIFEST_PATH.is_file():
    print(f"FOUT: Manifest ontbreekt: {MANIFEST_PATH}", file=sys.stderr)
    sys.exit(1)

if not OUT_MD_PATH.resolve().is_relative_to(CHATGPT_DIR.resolve()):
    print(f"FOUT: Uitvoerpad buiten chatGPT/: {OUT_MD_PATH}", file=sys.stderr)
    sys.exit(1)

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
raw_docs = manifest.get("documents", [])
raw_snippets = manifest.get("snippets", [])

# Sluit shell-scripts (*.sh) uit zodat code niet als biografisch feit meetelt
docs = [
    d for d in raw_docs
    if d.get("ext", "").lower() != ".sh" and not d.get("primary_name", "").lower().endswith(".sh")
]
excluded_names = {
    d["primary_name"] for d in raw_docs
    if d.get("ext", "").lower() == ".sh" or d.get("primary_name", "").lower().endswith(".sh")
}


def norm_fingerprint(text: str) -> str:
    # Verwijder Markdown-opmaaktekens en normaliseer witruimte voor cross-formaat ontdubbeling
    cleaned = re.sub(r"[#*_`>|~\-]+", " ", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


# 1. Ontdubbel snippets over .md / .txt / .pdf / .yaml / .json varianten met behoud van alle bronnen
merged_snippets = {}
for snip in raw_snippets:
    src_name = snip.get("source_file", "")
    if src_name in excluded_names or src_name.lower().endswith(".sh"):
        continue
    quote = snip.get("quote", "").strip()
    fp = norm_fingerprint(quote)
    if len(fp) < 16:
        continue

    src_ref = f"{src_name} ({snip.get('location', '?')}, md5:{snip.get('doc_md5', '')[:12]})"
    if fp not in merged_snippets:
        merged_snippets[fp] = {
            "quote": quote,
            "sources": [src_ref],
            "years": set(snip.get("years", [])),
            "dois": set(snip.get("dois", [])),
            "patents": set(snip.get("patents", [])),
            "grants": set(snip.get("eu_or_grant_signals", [])),
        }
    else:
        entry = merged_snippets[fp]
        if src_ref not in entry["sources"]:
            entry["sources"].append(src_ref)
        entry["years"].update(snip.get("years", []))
        entry["dois"].update(snip.get("dois", []))
        entry["patents"].update(snip.get("patents", []))
        entry["grants"].update(snip.get("eu_or_grant_signals", []))
        # Bewaar de rijkst geformatteerde variant (bijv. Markdown met behoud van structuur)
        if len(quote) > len(entry["quote"]):
            entry["quote"] = quote

# 2. Verzamel unieke identificatoren over het hele corpus (exclusief .sh)
all_dois = sorted({doi for d in docs for doi in d.get("dois", [])})
all_patents = sorted({pat for d in docs for pat in d.get("patents", [])})
all_grants = sorted({gr for d in docs for gr in d.get("eu_or_grant_signals", [])})
all_years = sorted({yr for d in docs for yr in d.get("years", [])})

# 3. Lees volledige tekst van alle niet-.sh documenten en filter pure cross-formaat tekstkopieën
doc_texts = {}
for d in docs:
    txt_rel = d.get("extracted_text_relpath", "")
    txt_path = REPO_ROOT / txt_rel
    if txt_path.is_file():
        doc_texts[d["md5"]] = txt_path.read_text(encoding="utf-8")

# Bepaal welke .txt/.pdf-bestanden inhoudelijk samenvallen met een reeds aanwezig .md-bestand
md_fingerprints = {
    d["md5"]: norm_fingerprint(doc_texts.get(d["md5"], ""))
    for d in docs
    if d.get("ext") == ".md"
}

redundant_variant_md5s = set()
for d in docs:
    if d.get("ext") in {".txt", ".pdf"}:
        cand_fp = norm_fingerprint(doc_texts.get(d["md5"], ""))
        if not cand_fp:
            continue
        for md_md5, md_fp in md_fingerprints.items():
            # Als >= 85% van de woorden overeenkomt met een .md-bronbestand, markeer als formaatvariant
            cand_words = set(cand_fp.split())
            md_words = set(md_fp.split())
            if cand_words and len(cand_words & md_words) / len(cand_words) >= 0.85:
                redundant_variant_md5s.add(d["md5"])
                break

lines = [
    "# Geconsolideerde Corpusfeiten — Steven E. Kleynenberg (1980–2026)",
    "",
    f"- **Gegenereerd op:** `{datetime.now(timezone.utc).astimezone().isoformat()}`",
    f"- **Actieve brondocumenten:** `{len(docs)}` (uitgesloten `.sh`: `{', '.join(sorted(excluded_names)) or 'geen'}`)",
    f"- **Unieke ontdubbelde snippets:** `{len(merged_snippets)}` (uit `{len(raw_snippets)}` ruwe snippets)",
    f"- **Jaartalbereik:** `{min(all_years) if all_years else '?'} t/m {max(all_years) if all_years else '?'}`",
    f"- **Aangetroffen DOIs:** `{', '.join(all_dois) if all_dois else 'geen'}`",
    f"- **Aangetroffen octrooien:** `{', '.join(all_patents) if all_patents else 'geen'}`",
    f"- **EU / R&D / Grant-signalen:** `{', '.join(all_grants) if all_grants else 'geen'}`",
    "",
    "## 1. Documentenindex (inclusief formaatvarianten)",
    "",
]

for d in docs:
    variant_tag = " `[FORMAATVARIANT VAN .MD]`" if d["md5"] in redundant_variant_md5s else ""
    lines.append(
        f"- **`{d['primary_name']}`** (`md5:{d['md5']}`, `{d['processing_mode']}`, `{d['text_char_count']}` chars, "
        f"jaren: `{','.join(str(y) for y in d.get('years', [])) or 'geen'}`){variant_tag} — Titel: *{d.get('detected_title', '')}*"
    )

lines.extend([
    "",
    "## 2. Integrale Tekst van Kern- & Ongedateerde Documenten (exclusief formaatduplicaten)",
    "",
])

for d in docs:
    if d["md5"] in redundant_variant_md5s:
        continue
    # Neem korte/middellange kerndocumenten (<= 14.000 chars) + XML-octrooi integraal op
    txt = doc_texts.get(d["md5"], "").strip()
    if len(txt) <= 14000 or d.get("ext") == ".xml":
        lines.append(f"### BRON: `{d['primary_name']}` (`md5:{d['md5']}`)")
        lines.append("```text")
        lines.append(txt)
        lines.append("```")
        lines.append("")

lines.extend([
    "## 3. Gestructureerde Kern uit `TREAT_AS_SOURCE.yaml`",
    "",
])
yaml_docs = [d for d in docs if d["primary_name"] == "TREAT_AS_SOURCE.yaml"]
if yaml_docs:
    yaml_raw = doc_texts.get(yaml_docs[0]["md5"], "")
    lines.append("```yaml")
    lines.append(yaml_raw.strip())
    lines.append("```")
    lines.append("")

lines.extend([
    "## 4. Chronologisch & Thematisch Ontdubbelde Tijdlijn-snippets (1980–2026)",
    "",
])

by_year = defaultdict(list)
undated_items = []
for item in merged_snippets.values():
    if item["years"]:
        for yr in sorted(item["years"]):
            by_year[yr].append(item)
    else:
        undated_items.append(item)

for yr in sorted(by_year.keys()):
    lines.append(f"### {yr}")
    for item in by_year[yr]:
        meta_parts = []
        if item["grants"]:
            meta_parts.append("Grants/EU: " + ", ".join(sorted(item["grants"])))
        if item["patents"]:
            meta_parts.append("Octrooi: " + ", ".join(sorted(item["patents"])))
        if item["dois"]:
            meta_parts.append("DOI: " + ", ".join(sorted(item["dois"])))
        meta_str = f" _[{' | '.join(meta_parts)}]_" if meta_parts else ""
        src_str = "; ".join(item["sources"][:3])
        if len(item["sources"]) > 3:
            src_str += f" (+{len(item['sources']) - 3} bronnen)"
        lines.append(f"- **[{src_str}]**{meta_str}: {item['quote']}")
    lines.append("")

if undated_items:
    lines.append("### Ongedateerde project-/octrooi-/grant-snippets")
    for item in undated_items:
        src_str = "; ".join(item["sources"][:3])
        lines.append(f"- **[{src_str}]**: {item['quote']}")
    lines.append("")

output_text = "\n".join(lines)
OUT_MD_PATH.write_text(output_text, encoding="utf-8")

print(output_text)
print(f"\n=== OPGESLAGEN NAAR: {OUT_MD_PATH} ({len(output_text)} tekens) ===")
PY