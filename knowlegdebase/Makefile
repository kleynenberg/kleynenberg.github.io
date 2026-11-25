# ==============================================================================
# INTEGRITY HEADER
# Project : Site Assistant Knowledgebase (https://steven.kleynenberg.com/)
# Path    : /home/steve/gemini/github.io/knowlegdebase/Makefile
# Host    : hp.kleynenberg.net (Fedora / system Python3, no venv)
# Editor  : joe
# Rule    : No dummy data, no silent overwrites, explicit checks & logging
# ==============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

PARENT_DIR := ..
KB_DIR := .
MANIFEST_FILE := $(KB_DIR)/sources.manifest
INVENTORY_FILE := $(KB_DIR)/inventory.txt
HASHES_FILE := $(KB_DIR)/sha256.sum
CHUNKS_FILE := $(KB_DIR)/chunks.jsonl
EXTRACT_LOG := $(KB_DIR)/extract.log
EXTRACTOR_SCRIPT := $(KB_DIR)/extract_kb.py

# Standard selection from parent site tree (kp/ intentionally excluded by default)
# Adjust targets or edit with: joe Makefile
TARGET_PATHS := \
	$(PARENT_DIR)/llms.txt \
	$(PARENT_DIR)/llms-full.txt \
	$(PARENT_DIR)/index.html \
	$(PARENT_DIR)/CITATION.cff \
	$(PARENT_DIR)/steven-kleynenberg-identity.jsonld \
	$(PARENT_DIR)/robots.txt \
	$(PARENT_DIR)/sitemap.xml \
	$(PARENT_DIR)/kso \
	$(PARENT_DIR)/papers \
	$(PARENT_DIR)/pp \
	$(PARENT_DIR)/tkp

.PHONY: help edit status manifest inventory hash extract clean

help:
	@echo "Site Assistant Knowledgebase Makefile — /home/steve/gemini/github.io/knowlegdebase"
	@echo "Targets:"
	@echo "  make edit       Open Makefile in joe"
	@echo "  make status     Show environment, parent files, and current kb artifacts"
	@echo "  make manifest   Write active source paths to sources.manifest"
	@echo "  make inventory  List existing files under TARGET_PATHS into inventory.txt (excluding .git)"
	@echo "  make hash       Compute SHA-256 checksums for inventoried regular files"
	@echo "  make extract    Extract text and generate chunks.jsonl from inventory.txt"
	@echo "  make clean      Remove generated kb artifacts (manifest, inventory, sha256, chunks, log)"

edit:
	@joe $(KB_DIR)/Makefile

status:
	@echo "=== Host & Python Environment ==="
	@hostname
	@python3 --version
	@command -v pdftotext jq joe make sha256sum || true
	@python3 -c "import bs4; print('bs4 version:', bs4.__version__)"
	@echo "=== Parent Repository Check ($(PARENT_DIR)) ==="
	@ls -la $(PARENT_DIR)
	@echo "=== Knowledgebase Directory Check ($(KB_DIR)) ==="
	@ls -la $(KB_DIR)

manifest:
	@echo "[manifest] Writing source manifest to $(MANIFEST_FILE)..."
	@printf "%s\n" $(TARGET_PATHS) > $(MANIFEST_FILE)
	@wc -l $(MANIFEST_FILE)

inventory: manifest
	@echo "[inventory] Scanning existing files from $(MANIFEST_FILE) (excluding .git)..."
	@: > $(INVENTORY_FILE)
	@while IFS= read -r entry; do \
		if [ ! -e "$$entry" ]; then \
			echo "[inventory][MISSING] $$entry" >&2; \
		elif [ -f "$$entry" ]; then \
			printf "%s\n" "$$entry" >> $(INVENTORY_FILE); \
		elif [ -d "$$entry" ]; then \
			find "$$entry" -path '*/.git' -prune -o -type f -print >> $(INVENTORY_FILE); \
		fi; \
	done < $(MANIFEST_FILE)
	@sort -u -o $(INVENTORY_FILE) $(INVENTORY_FILE)
	@echo "[inventory] Total files indexed: $$(wc -l < $(INVENTORY_FILE))"

hash: inventory
	@echo "[hash] Computing SHA-256 checksums into $(HASHES_FILE)..."
	@if [ ! -s $(INVENTORY_FILE) ]; then \
		echo "[hash][ERROR] $(INVENTORY_FILE) is empty; aborting." >&2; \
		exit 1; \
	fi
	@xargs -r sha256sum < $(INVENTORY_FILE) > $(HASHES_FILE)
	@echo "[hash] Checksums written: $$(wc -l < $(HASHES_FILE))"

extract: hash
	@echo "[extract] Running $(EXTRACTOR_SCRIPT) into $(CHUNKS_FILE)..."
	@if [ ! -f $(EXTRACTOR_SCRIPT) ]; then \
		echo "[extract][ERROR] Missing $(EXTRACTOR_SCRIPT); aborting." >&2; \
		exit 1; \
	fi
	@python3 $(EXTRACTOR_SCRIPT) \
		--inventory $(INVENTORY_FILE) \
		--hashes $(HASHES_FILE) \
		--output $(CHUNKS_FILE) \
		2>&1 | tee $(EXTRACT_LOG)
	@echo "[extract] Chunk lines written: $$(wc -l < $(CHUNKS_FILE))"

clean:
	@echo "[clean] Removing generated artifacts in $(KB_DIR)..."
	@rm -f $(MANIFEST_FILE) $(INVENTORY_FILE) $(HASHES_FILE) $(CHUNKS_FILE) $(EXTRACT_LOG)
	@echo "[clean] Done."