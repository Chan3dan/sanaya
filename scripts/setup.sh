#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

command -v python3 >/dev/null || { echo "Python 3.12+ is required."; exit 1; }
command -v node >/dev/null || { echo "Node.js 20+ is required."; exit 1; }
command -v redis-cli >/dev/null || echo "Redis CLI not found; ensure Redis is installed and running."
command -v ollama >/dev/null || echo "Ollama not found; install Ollama before voice AI testing."

python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

(cd api && npm install)
(cd dashboard && npm install)
test -f .env || cp .env.example .env
python scripts/download_models.py
python -c "import asyncio; from core.db.session import create_all_tables; asyncio.run(create_all_tables())"

echo "Sanaya setup complete. Run start.bat or the three dev commands to launch."
