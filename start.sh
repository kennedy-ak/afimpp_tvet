#!/usr/bin/env bash
# Start the AfIMMP Django app with Gunicorn.
#
# Usage:
#   ./start.sh            run in the foreground (use this under systemd)
#   ./start.sh -d         run detached in the background (nohup-style)
#   ./start.sh stop       stop a detached server
#   ./start.sh restart    stop, then start detached
#   ./start.sh status     report whether a detached server is running
#
# Tunables (override via environment or .env):
#   PORT      port Gunicorn binds on              (default: 8015)
#   HOST      interface Gunicorn binds on         (default: 0.0.0.0)
#   WORKERS   number of Gunicorn worker processes (default: 2 * CPUs + 1)
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
WORKERS="${WORKERS:-$(( 2 * $(nproc 2>/dev/null || echo 1) + 1 ))}"

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
    if ! is_running; then
        echo "[start.sh] Not running"
        rm -f "$PID_FILE"
        return 0
    fi
    local pid
    pid="$(cat "$PID_FILE")"
    echo "[start.sh] Stopping pid $pid..."
    kill -TERM "$pid"
    for _ in $(seq 1 30); do
        kill -0 "$pid" 2>/dev/null || break
        sleep 1
    done
    if kill -0 "$pid" 2>/dev/null; then
        echo "[start.sh] Did not exit, killing"
        kill -KILL "$pid"
    fi
    rm -f "$PID_FILE"
    echo "[start.sh] Stopped"
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
