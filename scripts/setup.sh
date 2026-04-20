#!/bin/bash
# Q-SMEC Command Center — First-time setup
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Q-SMEC Command Center Setup ==="

# Python venv
echo "Creating Python virtual environment..."
cd "$ROOT"
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Frontend deps (NODE_ENV=development ensures devDeps install)
echo "Installing frontend dependencies..."
cd "$ROOT/frontend"
NODE_ENV=development npm install

# .env
if [ ! -f "$ROOT/.env" ]; then
    echo "Creating .env from .env.example..."
    cp "$ROOT/.env.example" "$ROOT/.env"
    echo "  → Edit .env with your API keys before running!"
fi

# Init DB
echo "Initializing database..."
cd "$ROOT"
python -c "from backend.database import init_db; init_db()"

# Static dir
mkdir -p "$ROOT/backend/static"
touch "$ROOT/backend/static/.gitkeep"

echo ""
echo "=== Setup complete ==="
echo "  Backend: cd $ROOT && source .venv/bin/activate && uvicorn backend.main:app --reload"
echo "  Frontend: cd $ROOT/frontend && npm run dev"
echo "  Or use: bash scripts/dev.sh"
