#!/usr/bin/env bash
# Stop the AfIMMP Gunicorn server. Thin wrapper around `start.sh stop`:
# kills the pid-file server (logs/pids/gunicorn.pid), anything else bound to
# $PORT (default 8015),
# and any stray gunicorn running afimpp_config.wsgi.
set -euo pipefail
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/start.sh" stop
