#!/bin/bash
# Q-SMEC Command Center — Start server (called by Windows Task Scheduler)
# Ensures only one instance runs at a time

PIDFILE="/tmp/qsmec-command-center.pid"
TUNNEL_PIDFILE="/tmp/qsmec-tunnel.pid"
LOGFILE="/mnt/e/Data1/Q-SMEC-Command-Center/server.log"
TUNNEL_LOG="/mnt/e/Data1/Q-SMEC-Command-Center/tunnel.log"
ROOT="/mnt/e/Data1/Q-SMEC-Command-Center"

# Check if server already running
if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "$(date) Server already running (PID $OLD_PID)" >> "$LOGFILE"
    else
        rm -f "$PIDFILE"
    fi
fi

# Start server if not running
if [ ! -f "$PIDFILE" ]; then
    cd "$ROOT"
    source .venv/bin/activate 2>/dev/null || true
    echo "$(date) Starting Q-SMEC Command Center on :8000" >> "$LOGFILE"
    nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 >> "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "$(date) Server started (PID $!)" >> "$LOGFILE"
    sleep 3
fi

echo "$(date) Ready at http://niket-hv-01:8000" >> "$LOGFILE"
