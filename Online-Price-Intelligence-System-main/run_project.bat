@echo off
setlocal

echo ====================================================
echo   Online Price Intelligence System - Quick Start
echo ====================================================
echo.

set ROOT=%~dp0

echo [1/4] Initializing Database...
python init_db.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Database initialization failed. Ensure PostgreSQL is running.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/4] Starting Express Backend (Auth)...
start "PriceIntel-Express" cmd /k "cd /d %ROOT%backend-express && node server.js"

echo [3/4] Starting Python Backend (AI/Scraping)...
start "PriceIntel-Python" cmd /k "cd /d %ROOT% && set PYTHONPATH=. && python -m uvicorn backend.app.main_optimized:app --port 8001"

echo [4/4] Starting Frontend (UI)...
start "PriceIntel-Frontend" cmd /k "cd /d %ROOT%frontend && npm run dev"

echo.
echo ====================================================
echo   SYSTEM IS STARTING UP
echo ====================================================
echo   Frontend:        http://localhost:5173
echo   Express Health:  http://localhost:5001/health
echo   Python Docs:     http://localhost:8000/docs
echo ====================================================
echo.
echo Keep these windows open while using the system.
pause
endlocal
