# ==============================================================================
# INTEGRITY & METADATA HEADER
# File:          Makefile
# Project:       Project UnLinked — Sovereign Static PWA Build Pipeline
# Host Target:   https://kleynenberg.github.io (GitHub Pages)
# Workstation:   hp.kleynenberg.net (Fedora Linux / GNU Make / JOE Editor)
# ==============================================================================

PYTHON := python3
BUILDER := ./build_kleynenberg_dot_github_dot_io_SPA_PWA.py
YAML_SRC := portal.yaml
SVG_ICON := google_logo_image_of_steven_klenenberg_at_gmail_dot_com.svg

.PHONY: all build icons serve check clean

all: build

build: $(YAML_SRC) $(BUILDER)
	$(PYTHON) $(BUILDER) --root . --yaml $(YAML_SRC)

icons: $(SVG_ICON)
	@if command -v rsvg-convert >/dev/null 2>&1; then \
		rsvg-convert -w 192 -h 192 "$(SVG_ICON)" -o icon-192.png; \
		rsvg-convert -w 512 -h 512 "$(SVG_ICON)" -o icon-512.png; \
		echo "[OK] Generated icon-192.png and icon-512.png via rsvg-convert"; \
	elif command -v inkscape >/dev/null 2>&1; then \
		inkscape "$(SVG_ICON)" --export-filename=icon-192.png --export-width=192 --export-height=192; \
		inkscape "$(SVG_ICON)" --export-filename=icon-512.png --export-width=512 --export-height=512; \
		echo "[OK] Generated icon-192.png and icon-512.png via inkscape"; \
	else \
		echo "[ERR] Install librsvg2-tools or inkscape on Fedora to extract PNG icons."; \
		exit 1; \
	fi

serve: build
	@echo "Serving Project UnLinked PWA locally at http://127.0.0.1:8080/"
	$(PYTHON) -m http.server 8080 --bind 127.0.0.1

check:
	$(PYTHON) -m json.tool portal.json >/dev/null && echo "[OK] portal.json valid"
	$(PYTHON) -m json.tool manifest.webmanifest >/dev/null && echo "[OK] manifest.webmanifest valid"

clean:
	rm -f index.html style.css app.js portal.json manifest.webmanifest sw.js llms.txt
