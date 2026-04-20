#!/bin/bash
# Q-SMEC Command Center — Stop server and tunnel

PIDFILE="/tmp/qsmec-command-center.pid"
TUNNEL_PIDFILE="/tmp/qsmec-tunnel.pid"
LOGFILE="/mnt/e/Data1/Q-SMEC-Command-Center/server.log"

# Stop tunnel
if [ -f "$TUNNEL_PIDFILE" ]; then
    T_PID=$(cat "$TUNNEL_PIDFILE")
    if kill -0 "$T_PID" 2>/dev/null; then
        kill "$T_PID"
        echo "$(date) Tunnel stopped (PID $T_PID)" >> "$LOGFILE"
    fi
    rm -f "$TUNNEL_PIDFILE"
fi
pkill -f "cloudflared tunnel" 2>/dev/null

# Stop server
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "$(date) Server stopped (PID $PID)" >> "$LOGFILE"
    fi
    rm -f "$PIDFILE"
else
    kill $(lsof -ti:8000) 2>/dev/null
fi
