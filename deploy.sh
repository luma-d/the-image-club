#!/usr/bin/env bash
# One-command deploy: rebuild from content/*.md, push source + publish Pages.
# Usage: ./deploy.sh "what changed"
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py
git add -A
git commit -m "${1:-content update}" || echo "(nothing to commit)"
git push origin master
COMMIT=$(git commit-tree "$(git rev-parse HEAD:docs)" -m "GitHub Pages site")
git push -f origin "$COMMIT:refs/heads/gh-pages"
echo "Deployed: https://luma-d.github.io/the-image-club/"
