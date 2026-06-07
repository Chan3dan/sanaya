@echo off
setlocal
cd /d "%~dp0\.."

where python >nul 2>nul || (echo Python 3.12+ is required. && exit /b 1)
where node >nul 2>nul || (echo Node.js 20+ is required. && exit /b 1)
where redis-cli >nul 2>nul || echo Redis CLI not found; ensure Redis is installed and running.
where ollama >nul 2>nul || echo Ollama not found; install Ollama before voice AI testing.

if not exist venv python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist data\ollama\models mkdir data\ollama\models
set OLLAMA_MODELS=%CD%\data\ollama\models

cd api
npm install
cd ..\dashboard
npm install
cd ..

if not exist .env copy .env.example .env
python scripts\download_models.py
python -c "import asyncio; from core.db.session import create_all_tables; asyncio.run(create_all_tables())"

echo Sanaya setup complete. Run start.bat to launch.
