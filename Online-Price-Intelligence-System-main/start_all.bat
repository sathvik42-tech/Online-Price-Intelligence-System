@echo off
setlocal

echo Starting Online Price Intelligence System...

set ROOT=%~dp0

REM Python backend (FastAPI)
start "Python Backend" cmd /k "cd /d %ROOT% && set PYTHONPATH=. && python -m uvicorn backend.app.main:app --reload --port 8000"

REM Express backend
start "Express Backend" cmd /k "cd /d %ROOT%backend-express && node server.js"

REM Frontend (Vite)
start "Frontend" cmd /k "cd /d %ROOT%frontend && npm run dev"

echo.
echo Python backend:  http://localhost:8000
echo Express backend: http://localhost:5001
echo Frontend:        http://localhost:5173
echo.
pause
endlocal
