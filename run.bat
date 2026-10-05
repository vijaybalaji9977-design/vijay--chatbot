@echo off
title Intelligent Multi-Functional AI Chatbot
echo ========================================================
echo   Intelligent Multi-Functional AI Chatbot Launcher
echo ========================================================
echo.

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

:: Install dependencies if needed
echo [INFO] Verifying dependencies...
python -m pip install -r requirements.txt --quiet

:: Start server
echo.
echo [INFO] Starting FastAPI application on http://127.0.0.1:8000 ...
echo [INFO] Press Ctrl+C in this terminal to stop the server.
echo.

python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause
