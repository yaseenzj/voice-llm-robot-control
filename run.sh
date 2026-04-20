#!/bin/bash
echo "Setting up Voice LLM Robot Control..."


# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "python3 could not be found. Please install Python 3."
    exit 1
fi


# 1. Virtual Environment Setup
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
echo "🔌 Activating virtual environment..."
source .venv/bin/activate


# 2. System Dependencies Check (For Linux/WSL)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! dpkg -l | grep -q libespeak1; then
        echo "Missing system dependency: libespeak1"
        echo "Please run: sudo apt-get update && sudo apt-get install -y libespeak1 portaudio19-dev python3-pyaudio"
    fi
fi
echo "📦 Installing/Updating Python libraries..."
pip install --upgrade pip
pip install -r requirements.txt


# 3. Ollama Check
if command -v ollama &> /dev/null; then
    echo "Ensuring local LLaMA model is ready..."
    ollama pull llama3.2:1b
else
    echo "Ollama not detected. Please install it for natural language support."
fi
echo "Setup complete! Booting up Robot Brain..."
cd python
python3 robot_brain.py
