#!/bin/bash
# Q-SMEC Command Center — Production build + deploy
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Q-SMEC Command Center — Production Build ==="

# Build frontend
echo "Building frontend..."
cd "$ROOT/frontend"
npm run build
echo "  → Built to backend/static/"

# Start production server
echo "Starting production server on :8000..."
cd "$ROOT"
source .venv/bin/activate 2>/dev/null || true
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
