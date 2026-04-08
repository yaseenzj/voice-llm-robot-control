@echo off
echo.
echo ========================================================
echo   🤖 Setting up Voice LLM Robot Control (Windows)
echo ========================================================
echo.

:: Check for python/pip
where pip >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python pip could not be found. Please install Python and add it to PATH.
    pause
    exit /b
)

echo 📦 Installing required Python libraries from requirements.txt...
pip install -r requirements.txt
echo.

:: Ensure Ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Ollama is not installed! Please install it from https://ollama.com before continuing.
    echo ⚠️ (We need it to run the LLaMA Deep Brain locally)
) else (
    echo 🧠 Ensuring local LLaMA 3.2 (1B) model is downloaded...
    ollama pull llama3.2:1b
)

echo.
echo 🚀 Setup complete! Booting up Robot Brain...
echo.
cd src
python robot_brain.py
pause
