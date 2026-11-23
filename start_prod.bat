@echo off
cd /d "%~dp0"

set "VENV_PY=%~dp0fastapi\venv\Scripts\python.exe"
set "LOGDIR=%~dp0logs"
set "LOGFILE=%LOGDIR%\backend.log"
REM default port 8002, override with arg: start_prod.bat 8003
set "PORT=8002"
if not "%~1"=="" set "PORT=%~1"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

if not exist "%VENV_PY%" (
    echo [ERROR] venv python not found: %VENV_PY% >> "%LOGFILE%"
    echo [ERROR] venv python not found: %VENV_PY%
    echo         step1: python -m venv fastapi\venv
    echo         step2: fastapi\venv\Scripts\pip install -r fastapi\requirements.txt
    pause
    exit /b 1
)

echo. >> "%LOGFILE%"
echo ================== %date% %time% Reimbursement service start (port %PORT%) ================== >> "%LOGFILE%"

REM skip if port already in use
netstat -ano | findstr "LISTENING" | findstr /R ":%PORT% " >nul
if not errorlevel 1 (
    echo [%time%] port %PORT% already in use, skip start >> "%LOGFILE%"
    exit /b 0
)

cd /d "%~dp0fastapi"
"%VENV_PY%" -m uvicorn main:app --host 0.0.0.0 --port %PORT% >> "%LOGFILE%" 2>&1
