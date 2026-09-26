#!/usr/bin/env bash
# Serves index.html, opens a Cloudflare quick tunnel to it, points the repro dataset at the
# tunnel, then keeps the tunnel up until Ctrl-C. Needs LANGSMITH_API_KEY (or a .env beside it).
set -euo pipefail
cd "$(dirname "$0")"
port="${PORT:-8000}"

set -m
python3 -m http.server "$port" --bind 127.0.0.1 >/dev/null 2>&1 &
server=$!
cloudflared tunnel --no-autoupdate --url "http://127.0.0.1:$port" >.tunnel.log 2>&1 &
tunnel=$!
trap 'kill -- -$server -$tunnel 2>/dev/null || true' EXIT

url=""
for _ in $(seq 60); do
  url=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' .tunnel.log | head -1 || true)
  [ -n "$url" ] && break
  sleep 1
done
[ -n "$url" ] || { echo "error: no tunnel URL after 60 s; see .tunnel.log" >&2; exit 1; }
# A quick tunnel's DNS can lag its URL by a few seconds.
until curl -sf -o /dev/null "$url/"; do sleep 2; done
echo "echo page: $url/"

env_file=()
[ -f .env ] && env_file=(--env-file .env)
uv run ${env_file[@]+"${env_file[@]}"} repro.py --renderer-url "$url/"

echo
echo "Tunnel up. Open the URLs above; Ctrl-C to stop."
wait "$tunnel"
