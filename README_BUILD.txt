# Project UnLinked — Sovereign Static SPA / PWA Build Kit

Workstation: `hp.kleynenberg.net` (Fedora Linux / JOE editor / GNU Make)
Target origin: `https://kleynenberg.github.io/`

## Quick Start in `/home/steve/gemini/github.io`

1. Extract this archive into `/home/steve/gemini/github.io`.
2. Ensure your vector emblem `google_logo_image_of_steven_klenenberg_at_gmail_dot_com.svg` is present in `/home/steve/gemini/github.io/`.
3. Run the compiler:
   ```bash
   chmod +x build_kleynenberg_dot_github_dot_io_SPA_PWA.py
   ./build_kleynenberg_dot_github_dot_io_SPA_PWA.py
   ```
   *(Or run `make build` and `make serve` to preview at `http://127.0.0.1:8080/`.)*

4. Drop scientific paper PDFs (such as `chp3A10.10072F978-3-319-24072-5_15.pdf` or `medusa-2015-acute-stroke-esocc.pdf`) into `papers/` and re-run `./build_kleynenberg_dot_github_dot_io_SPA_PWA.py` — the compiler automatically detects available PDFs and activates their download buttons and Service Worker precaching.
