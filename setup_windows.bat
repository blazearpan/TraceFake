@echo off
setlocal
echo ========================================
echo TRACEFAKE - Windows Setup
echo ========================================

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.11+ and try again.
  pause
  exit /b 1
)

python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

if not exist frontend\node_modules (
  echo Installing frontend dependencies...
  cd frontend
  call npm install
  cd ..
)

echo.
echo Setup complete.
echo Next:
echo 1. venv\Scripts\python.exe ml\training\download_dataset.py
echo 2. venv\Scripts\python.exe ml\training\train.py
echo 3. run_windows.bat
pause
