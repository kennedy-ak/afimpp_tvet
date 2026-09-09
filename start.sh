#!/usr/bin/env bash
# Deploy and run the AfIMMP Django app under Gunicorn, in the background.
#
# Usage:
#   ./start.sh            pull, sync deps, migrate, collectstatic, restart
#                         Gunicorn in the background, then health-check
#   ./start.sh stop       stop Gunicorn (pid file, then anything on $PORT,
#                         then any gunicorn running afimpp_config.wsgi)
#   ./start.sh status     is Gunicorn running?
#   ./start.sh fg         run in the foreground (for systemd); no pull
#
# Tunables (environment or .env):
#   PORT         port Gunicorn binds on               (default: 8015)
#   HOST         interface Gunicorn binds on          (default: 0.0.0.0)
#   WORKERS      Gunicorn worker processes            (default: 2*CPUs+1, max 4)
#   SKIP_PULL=1  restart what is on disk without git pull
#   SKIP_SETUP=1 skip uv sync / migrate / collectstatic
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

LOG_DIR="$APP_DIR/logs"
PID_FILE="$LOG_DIR/pids/gunicorn.pid"
LOG_FILE="$LOG_DIR/gunicorn.log"
ACCESS_LOG="$LOG_DIR/gunicorn-access.log"
ERROR_LOG="$LOG_DIR/gunicorn-error.log"

# Read PORT/HOST/WORKERS from .env if present. Only these keys are read (the
# file is not sourced, because values like SECRET_KEY contain characters the
# shell would choke on).
env_value() {
    [[ -f .env ]] || return 0
    sed -n "s/^[[:space:]]*$1=[[:space:]]*//p" .env | tail -n 1 | sed -e 's/[[:space:]]*$//' -e "s/^['\"]//" -e "s/['\"]$//"
}
PORT="${PORT:-$(env_value PORT)}"
HOST="${HOST:-$(env_value HOST)}"
WORKERS="${WORKERS:-$(env_value WORKERS)}"

PORT="${PORT:-8015}"
HOST="${HOST:-0.0.0.0}"
if [[ -z "$WORKERS" ]]; then
    WORKERS=$(( 2 * $(nproc 2>/dev/null || echo 1) + 1 ))
    (( WORKERS > 4 )) && WORKERS=4
fi

# Prefer the project virtualenv; fall back to whatever python is on PATH.
if [[ -x .venv/bin/python ]]; then
    PYTHON="$APP_DIR/.venv/bin/python"
elif [[ -x .venv/Scripts/python.exe ]]; then
    PYTHON="$APP_DIR/.venv/Scripts/python.exe"
else
    PYTHON="$(command -v python3 || command -v python)"
fi

# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------
is_running() {
    [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

# PIDs of whatever is listening on $PORT. Always exits 0: an empty result
# (port free) is not an error, and under `set -e -o pipefail` a failing grep
# here would abort the whole script.
port_pids() {
    if command -v ss >/dev/null; then
        ss -ltnpH "sport = :$PORT" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2 | sort -u || true
    elif command -v lsof >/dev/null; then
        lsof -ti "tcp:$PORT" -sTCP:LISTEN 2>/dev/null | sort -u || true
    elif command -v fuser >/dev/null; then
        fuser "$PORT/tcp" 2>/dev/null | tr ' ' '\n' | grep -E '^[0-9]+$' | sort -u || true
    fi
    return 0
}

# PIDs of gunicorn processes serving this app (pid file or not).
app_pids() {
    pgrep -f 'gunicorn.*afimpp_config\.wsgi' 2>/dev/null | sort -u || true
}

# Send TERM to a list of pids, wait up to 30s, then KILL any survivors.
terminate() {
    local pids=("$@") pid
    [[ ${#pids[@]} -eq 0 ]] && return 0
    echo "=== Stopping pid(s): ${pids[*]} ==="
    for pid in "${pids[@]}"; do kill -TERM "$pid" 2>/dev/null || true; done
    for _ in $(seq 1 30); do
        local alive=0
        for pid in "${pids[@]}"; do kill -0 "$pid" 2>/dev/null && alive=1; done
        (( alive )) || return 0
        sleep 1
    done
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "    pid $pid did not exit, killing"
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
}

stop_all() {
    local pids=() pid
    if is_running; then pids+=("$(cat "$PID_FILE")"); fi
    while read -r pid; do [[ -n "$pid" ]] && pids+=("$pid"); done < <(port_pids)
    while read -r pid; do [[ -n "$pid" ]] && pids+=("$pid"); done < <(app_pids)

    # Never target ourselves; de-duplicate.
    local unique=() seen=" "
    for pid in "${pids[@]}"; do
        [[ "$pid" == "$$" ]] && continue
        [[ "$seen" == *" $pid "* ]] && continue
        seen="$seen$pid "
        unique+=("$pid")
    done

    if [[ ${#unique[@]} -eq 0 ]]; then
        echo "=== Nothing running on port $PORT ==="
    else
        terminate "${unique[@]}"
        echo "=== Stopped ==="
    fi
    rm -f "$PID_FILE"
}

# ---------------------------------------------------------------------------
# Deploy steps
# ---------------------------------------------------------------------------
pull_code() {
    if [[ "${SKIP_PULL:-0}" == "1" ]]; then
        echo "=== Skipping git pull (SKIP_PULL=1) ==="
    elif git pull --ff-only; then
        echo "=== Code pulled ==="
    else
        echo "" >&2
        echo "!!! git pull failed - deploy aborted, site still running. !!!" >&2
        echo "    Usually a local change conflicts with the repo." >&2
        echo "    Resolve it, or restart without pulling: SKIP_PULL=1 ./start.sh" >&2
        exit 1
    fi
}

# Runs BEFORE touching the running site: old code keeps serving until
# everything here has succeeded.
setup() {
    if [[ "${SKIP_SETUP:-0}" == "1" ]]; then
        echo "=== Skipping setup (SKIP_SETUP=1) ==="
        return
    fi
    if command -v uv >/dev/null 2>&1; then
        echo "=== Syncing dependencies (uv) ==="
        # --inexact so manually installed extras are never surprise-removed.
        uv sync --inexact
    elif ! "$PYTHON" -c "import gunicorn" 2>/dev/null; then
        echo "=== Installing gunicorn ==="
        "$PYTHON" -m pip install --quiet gunicorn
    fi
    echo "=== Applying database migrations ==="
    "$PYTHON" manage.py migrate --noinput
    echo "=== Collecting static files ==="
    "$PYTHON" manage.py collectstatic --noinput >/dev/null
}

health_check() {
    sleep 3
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/" || echo "000")
    echo "Local health check: HTTP $code"
    case "$code" in
        200|301|302) echo "Site is up." ;;
        *) echo "WARNING: unexpected status - check $LOG_FILE" ;;
    esac
}

cmd_deploy() {
    pull_code
    setup
    stop_all
    mkdir -p "$LOG_DIR/pids"
    echo "=== Starting Gunicorn on $HOST:$PORT with $WORKERS workers ==="
    nohup "$PYTHON" -m gunicorn afimpp_config.wsgi:application \
        --bind "$HOST:$PORT" \
        --workers "$WORKERS" \
        --timeout 120 \
        --access-logfile "$ACCESS_LOG" \
        --error-logfile "$ERROR_LOG" \
        --pid "$PID_FILE" \
        > "$LOG_FILE" 2>&1 &
    echo "Gunicorn PID: $!"
    echo ""
    echo "=== All services started ==="
    echo "  Gunicorn: http://$HOST:$PORT"
    echo "  Logs:     $LOG_DIR/"
    echo ""
    echo "To stop:       ./stop.sh"
    echo "To check logs: tail -f $LOG_FILE"
    health_check
}

cmd_foreground() {
    setup
    stop_all
    echo "=== Starting Gunicorn on $HOST:$PORT with $WORKERS workers (foreground) ==="
    exec "$PYTHON" -m gunicorn afimpp_config.wsgi:application \
        --bind "$HOST:$PORT" \
        --workers "$WORKERS" \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
}

cmd_status() {
    if is_running; then
        echo "Running, pid $(cat "$PID_FILE") on $HOST:$PORT"
    else
        local pids
        pids="$(port_pids | tr '\n' ' ')"
        if [[ -n "$pids" ]]; then
            echo "Not started by this script, but port $PORT is held by pid(s): $pids"
        else
            echo "Not running"
        fi
        return 1
    fi
}

case "${1:-}" in
    ""|start|deploy|restart) cmd_deploy ;;
    stop)                    stop_all ;;
    status)                  cmd_status ;;
    fg|--foreground)         cmd_foreground ;;
    -h|--help)               sed -n '2,18p' "$0" ;;
    *) echo "Unknown command: $1" >&2; sed -n '2,18p' "$0"; exit 2 ;;
esac
