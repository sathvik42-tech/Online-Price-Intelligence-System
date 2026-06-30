@echo off
echo Starting Online Price Intelligence System...

start cmd /k "set PYTHONPATH=. && uvicorn backend.app.main:app --reload"
start cmd /k "cd frontend && npm run dev"

echo Backend running at http://localhost:8000
echo Frontend running at http://localhost:5173
start http://localhost:5173
pause
