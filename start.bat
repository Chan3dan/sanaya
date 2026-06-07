@echo off
setlocal
cd /d "%~dp0"

if not exist .env copy .env.example .env

where redis-server >nul 2>nul && start "Sanaya Redis" redis-server
where ollama >nul 2>nul && start "Sanaya Ollama" ollama serve

start "Sanaya Core" cmd /k "call venv\Scripts\activate.bat && python -m core.main"
start "Sanaya API" cmd /k "cd api && npm run dev"
start "Sanaya Dashboard" cmd /k "cd dashboard && npm run dev"

timeout /t 5 >nul
start http://localhost:3000
