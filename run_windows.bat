@echo off
setlocal
if not exist venv\Scripts\python.exe (
  echo Virtual environment not found. Run setup_windows.bat first.
  pause
  exit /b 1
)

start "TraceFake Backend" cmd /k "venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
start "TraceFake Frontend" cmd /k "cd frontend && npm run dev"

echo TraceFake is starting.
echo Frontend: http://localhost:5173
echo Backend:  http://127.0.0.1:8000
