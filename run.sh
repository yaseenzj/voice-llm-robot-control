#!/bin/bash
echo "🤖 Setting up Voice LLM Robot Control..."

# Check if pip is available
if ! command -v pip &> /dev/null
then
    echo "❌ pip could not be found. Please ensure Python is installed with pip."
    exit
fi

echo "📦 Installing required Python libraries from requirements.txt..."
pip install -r requirements.txt

# Try to pull the Ollama model
if command -v ollama &> /dev/null
then
    echo "🧠 Ensuring local LLaMA 3.2 (1B) model is downloaded..."
    ollama pull llama3.2:1b
else
    echo "⚠️ Ollama is not installed! Please install it from https://ollama.com before continuing."
fi

echo "🚀 Setup complete! Booting up Robot Brain..."
cd python
python3 robot_brain.py
