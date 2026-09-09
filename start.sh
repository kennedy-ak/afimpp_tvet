#!/usr/bin/env bash
# Start the AfIMMP Django app with Gunicorn.
#
# Usage:
#   ./start.sh            run in the foreground (use this under systemd)
#   ./start.sh -d         run detached in the background (nohup-style)
#   ./start.sh stop       stop the server (pid file, then anything on $PORT,
#                         then any gunicorn running afimpp_config.wsgi)
#   ./start.sh restart    stop, then start detached
#   ./start.sh status     report whether a detached server is running
#
# Tunables (override via environment or .env):
#   PORT      port Gunicorn binds on              (default: 8015)
#   HOST      interface Gunicorn binds on         (default: 0.0.0.0)
#   WORKERS   number of Gunicorn worker processes (default: 2 * CPUs + 1, capped at 4)
#   SKIP_SETUP=1  skip migrate/collectstatic on start
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

PID_FILE="$APP_DIR/gunicorn.pid"
LOG_FILE="$APP_DIR/gunicorn.log"

# Read PORT/HOST/WORKERS from .env if present, so they can live alongside the
# Django settings. Only these keys are read (the file is not sourced, because
# values like SECRET_KEY contain characters the shell would choke on).
env_value() {
    [[ -f .env ]] || return 0
    sed -n "s/^[[:space:]]*$1=[[:space:]]*//p" .env | tail -n 1 | sed -e 's/[[:space:]]*$//' -e "s/^['\"]//" -e "s/['\"]$//"
}
PORT="${PORT:-$(env_value PORT)}"
HOST="${HOST:-$(env_value HOST)}"
WORKERS="${WORKERS:-$(env_value WORKERS)}"

PORT="${PORT:-8015}"
HOST="${HOST:-0.0.0.0}"
if [[ -z "${WORKERS:-}" ]]; then
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

is_running() {
    [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

# PIDs of whatever is listening on $PORT (any of ss / lsof / fuser that exists).
port_pids() {
    if command -v ss >/dev/null; then
        ss -ltnpH "sport = :$PORT" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2 | sort -u
    elif command -v lsof >/dev/null; then
        lsof -ti "tcp:$PORT" -sTCP:LISTEN 2>/dev/null | sort -u
    elif command -v fuser >/dev/null; then
        fuser "$PORT/tcp" 2>/dev/null | tr ' ' '\n' | grep -E '^[0-9]+$' | sort -u
    fi
}

# PIDs of gunicorn master processes serving this app (pid file or not).
app_pids() {
    pgrep -f 'gunicorn.*afimpp_config\.wsgi' 2>/dev/null | sort -u || true
}

# Send TERM to a list of pids, wait up to 30s, then KILL any survivors.
terminate() {
    local pids=("$@") pid
    [[ ${#pids[@]} -eq 0 ]] && return 0
    echo "[start.sh] Stopping pid(s): ${pids[*]}"
    for pid in "${pids[@]}"; do kill -TERM "$pid" 2>/dev/null || true; done
    for _ in $(seq 1 30); do
        local alive=0
        for pid in "${pids[@]}"; do kill -0 "$pid" 2>/dev/null && alive=1; done
        (( alive )) || return 0
        sleep 1
    done
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "[start.sh] pid $pid did not exit, killing"
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
}

require_port_free() {
    local pids
    pids="$(port_pids)"
    if [[ -n "$pids" ]]; then
        echo "[start.sh] Port $PORT is already in use by pid(s): $(echo "$pids" | tr '
' ' ')" >&2
        echo "[start.sh] Run './start.sh stop' (or ./stop.sh) first, or set PORT to a free port." >&2
        exit 1
    fi
}

setup() {
    if [[ "${SKIP_SETUP:-0}" == "1" ]]; then
        return
    fi
    if ! "$PYTHON" -c "import gunicorn" 2>/dev/null; then
        echo "[start.sh] gunicorn not installed, installing..."
        "$PYTHON" -m pip install --quiet gunicorn
    fi
    echo "[start.sh] Applying migrations..."
    "$PYTHON" manage.py migrate --noinput
    echo "[start.sh] Collecting static files..."
    "$PYTHON" manage.py collectstatic --noinput --clear >/dev/null
}

gunicorn_cmd() {
    "$PYTHON" -m gunicorn afimpp_config.wsgi:application \
        --bind "$HOST:$PORT" \
        --workers "$WORKERS" \
        --timeout 120 \
        --access-logfile "$LOG_FILE" \
        --error-logfile "$LOG_FILE" \
        --capture-output \
        "$@"
}

cmd_start_fg() {
    require_port_free
    setup
    echo "[start.sh] Starting Gunicorn on $HOST:$PORT with $WORKERS workers (foreground)"
    exec "$PYTHON" -m gunicorn afimpp_config.wsgi:application \
        --bind "$HOST:$PORT" \
        --workers "$WORKERS" \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
}

cmd_start_bg() {
    if is_running; then
        echo "[start.sh] Already running (pid $(cat "$PID_FILE"))"
        return 0
    fi
    require_port_free
    setup
    echo "[start.sh] Starting Gunicorn on $HOST:$PORT with $WORKERS workers (background)"
    gunicorn_cmd --daemon --pid "$PID_FILE"
    sleep 1
    if is_running; then
        echo "[start.sh] Started, pid $(cat "$PID_FILE"). Logs: $LOG_FILE"
    else
        echo "[start.sh] Failed to start. Check $LOG_FILE" >&2
        exit 1
    fi
}

cmd_stop() {
    local pids=()
    # 1. The server we started (pid file).
    if is_running; then
        pids+=("$(cat "$PID_FILE")")
    fi
    # 2. Anything else bound to our port (e.g. an old nohup gunicorn).
    while read -r pid; do
        [[ -n "$pid" ]] && pids+=("$pid")
    done < <(port_pids)
    # 3. Any gunicorn master still running this app on another port.
    while read -r pid; do
        [[ -n "$pid" ]] && pids+=("$pid")
    done < <(app_pids)

    # Never target ourselves; de-duplicate.
    local unique=() seen=" " pid
    for pid in "${pids[@]}"; do
        [[ "$pid" == "$$" ]] && continue
        [[ "$seen" == *" $pid "* ]] && continue
        seen="$seen$pid "
        unique+=("$pid")
    done

    if [[ ${#unique[@]} -eq 0 ]]; then
        echo "[start.sh] Nothing running on port $PORT"
    else
        terminate "${unique[@]}"
        echo "[start.sh] Stopped"
    fi
    rm -f "$PID_FILE"
}

cmd_status() {
    if is_running; then
        echo "[start.sh] Running, pid $(cat "$PID_FILE") on $HOST:$PORT"
    else
        echo "[start.sh] Not running"
        return 1
    fi
}

case "${1:-}" in
    ""|start)     cmd_start_fg ;;
    -d|--daemon)  cmd_start_bg ;;
    stop)         cmd_stop ;;
    restart)      cmd_stop; cmd_start_bg ;;
    status)       cmd_status ;;
    -h|--help)    sed -n '2,15p' "$0" ;;
    *)            echo "Unknown command: $1" >&2; sed -n '2,15p' "$0"; exit 2 ;;
esac
