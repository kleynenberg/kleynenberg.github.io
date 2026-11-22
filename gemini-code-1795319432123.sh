# ==============================================================================
# INTEGRITY HEADER - GEMINI AI
# Script: extract_original_papers_metadata.sh
# Target: /home/steve/gemini/github.io/papers/index.html (Git history)
# Purpose: Retrieve verified DOIs, BibTeX & RIS entries from prior commit
# ==============================================================================

cd /home/steve/gemini/github.io && \
git log -n 5 --oneline -- papers/index.html && \
OLD_COMMIT=$(git log -n 2 --format="%H" -- papers/index.html | tail -n 1) && \
echo "=== EXTRACTING FROM COMMIT: $OLD_COMMIT ===" && \
git show "${OLD_COMMIT}:papers/index.html"