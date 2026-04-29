#!/bin/bash
echo "------------------------------------------------"
echo "RUN: Voice LLM Robot Control - Setup & Boot"
echo "------------------------------------------------"

# Check for Python
if command -v python3 &> /dev/null; then
    PY_CMD="python3"
elif command -v python &> /dev/null; then
    PY_CMD="python"
else
    echo "ERROR: Python could not be found. Please install Python 3."
    exit 1
fi

# 1. Virtual Environment Setup
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PY_CMD -m venv .venv
fi

echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# 2. Dependencies
echo "Installing/Updating Python libraries..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Microphone Setup
echo ""
echo "Microphone Check..."
python python/list_mics.py
echo ""
read -p "Enter the Index of your EXTERNAL microphone (from the list above): " MIC_INDEX

# 4. Ollama Check
if command -v ollama &> /dev/null; then
    echo "Ensuring local LLaMA model (llama3.2:1b) is ready..."
    ollama pull llama3.2:1b
else
    echo "WARNING: Ollama not detected. Please install it from https://ollama.com"
fi

echo "DONE: Setup complete! Booting up Robot Brain..."
cd python
python robot_encoded.py $MIC_INDEX
