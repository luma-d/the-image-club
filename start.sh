#!/usr/bin/env bash
# Start The Image Club site locally + a public demo URL.
# Rebuilds docs/ from content/, then serves docs/ on 127.0.0.1:8000.
# Usage: ./start.sh   (run from anywhere; safe to re-run)
set -euo pipefail
cd "$(dirname "$0")"
PORT=8000

# Rebuild docs/ from the markdown content
python3 build.py

# Static server (serves docs/)
if ! curl -s -o /dev/null http://127.0.0.1:$PORT/; then
  setsid -f sh -c "exec python3 -m http.server $PORT --bind 127.0.0.1 --directory docs > /tmp/image-club-web.log 2>&1"
  sleep 1
fi
echo "Local:  http://127.0.0.1:$PORT/"

# Public demo tunnel (URL changes on every run)
if ! pgrep -f "cloudflared tunnel --no-autoupdate --url http://127.0.0.1:$PORT" >/dev/null; then
  setsid -f sh -c "exec ~/bin/cloudflared tunnel --no-autoupdate --url http://127.0.0.1:$PORT > /tmp/cloudflared-$PORT.log 2>&1"
fi
for i in $(seq 1 15); do
  URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared-$PORT.log 2>/dev/null | head -1)
  [ -n "${URL:-}" ] && break
  sleep 2
done
echo "Public: ${URL:-<not up yet, check /tmp/cloudflared-$PORT.log>}"
