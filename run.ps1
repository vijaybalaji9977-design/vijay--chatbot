# AI-Powered Multi-Functional Chatbot PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   AI-Powered Multi-Functional Chatbot Launcher" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Verify Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "[OK] Detected: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH!" -ForegroundColor Red
    pause
    exit 1
}

# Verify / install dependencies
Write-Host "[INFO] Verifying dependencies..." -ForegroundColor Cyan
python -m pip install -r requirements.txt --quiet

# Launch Uvicorn
Write-Host ""
Write-Host "[INFO] Starting FastAPI application on http://localhost:8000 ..." -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C in this terminal to stop the server." -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
