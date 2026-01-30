@echo off
SET PORT=8089
SET VENV_DIR=venv

echo Checking for process on port %PORT%...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":%PORT%" ^| find "LISTENING"') do (
    echo Killing process %%a
    taskkill /F /PID %%a
)

if not exist %VENV_DIR% (
    echo Creating virtual environment...
    py -m venv %VENV_DIR% 2>nul || python -m venv %VENV_DIR%
)

if not exist %VENV_DIR% (
    echo Errors creating virtual environment. Please check Python installation.
    pause
    exit /b 1
)

echo Installing dependencies...
%VENV_DIR%\Scripts\pip install -r requirements.txt

echo Starting app...
%VENV_DIR%\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port %PORT%

pause
