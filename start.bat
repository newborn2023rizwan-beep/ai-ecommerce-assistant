@echo off
title ShopMitra BD - AI E-Commerce Assistant
color 0A

echo.
echo  ============================================
echo   ShopMitra BD - AI E-Commerce Assistant
echo  ============================================
echo.

:: ── Force correct working directory ──────────────────────────────────────
D:
cd /d "D:\Ai Engineering\PythonProject\ai-ecommerce-assistant"

echo Current directory:
cd
echo.

:: ── Check Python ──────────────────────────────────────────────────────────
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    pause
    exit /b 1
)
python --version
echo  OK

:: ── Check Ollama ─────────────────────────────────────────────────────────
echo.
echo [2/4] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo  WARNING: Ollama not running. Starting...
    start /min "" ollama serve
    timeout /t 3 /nobreak >nul
) else (
    echo  OK - Ollama is running
)

:: ── Install / verify dependencies ────────────────────────────────────────
echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo  OK

:: ── Launch Streamlit ─────────────────────────────────────────────────────
echo.
echo [4/4] Launching ShopMitra BD...
echo  App will open at: http://localhost:8501
echo  Press Ctrl+C to stop.
echo  ============================================
echo.

start "" http://localhost:8501
streamlit run app.py --server.port 8501 --server.headless false

echo.
echo  Server stopped.
pause
