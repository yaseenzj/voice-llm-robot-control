#!/bin/bash
echo "=========================================="
echo "   🤖 Voice LLM Robot Control Setup 🤖   "
echo "=========================================="

if ! command -v python3 &> /dev/null; then
    echo "❌ python3 could not be found. Please install Python 3."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "🔌 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "🔌 Activating virtual environment..."
source .venv/bin/activate

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Checking system dependencies..."
    
    MISSING_DEPS=""
    if ! dpkg -l | grep -q libespeak1; then MISSING_DEPS="$MISSING_DEPS libespeak1"; fi
    if ! dpkg -l | grep -q portaudio19-dev; then MISSING_DEPS="$MISSING_DEPS portaudio19-dev"; fi
    if ! dpkg -l | grep -q python3-pyaudio; then MISSING_DEPS="$MISSING_DEPS python3-pyaudio"; fi
    
    if [ ! -z "$MISSING_DEPS" ]; then
        echo "Installing missing dependencies: $MISSING_DEPS"
        sudo apt-get update && sudo apt-get install -y $MISSING_DEPS
    fi

    if ! pgrep -x "pulseaudio" > /dev/null; then
        echo "🔊 Starting PulseAudio to prevent ALSA conflicts..."
        pulseaudio --start --exit-idle-time=-1
    fi
fi

echo "📦 Installing/Updating Python libraries..."
pip install --upgrade pip
pip install -r requirements.txt

if command -v ollama &> /dev/null; then
    echo "🧠 Ensuring local LLaMA model is ready..."
    ollama pull llama3.2:1b
else
    echo "⚠️ Ollama not detected. Natural language features might be limited."
fi

echo ""
echo "🔍 Detecting Microphones..."
while true; do
    MICS=$(python3 -c "import speech_recognition as sr; [print(f'{i}: {n}') for i, n in enumerate(sr.Microphone.list_microphone_names())]" 2>/dev/null)
    
    if [ -z "$MICS" ]; then
        echo "❌ NO MICROPHONES DETECTED!"
        echo "------------------------------------------"
        read -p "👉 Please connect a microphone and press [ENTER] to reload, or 'q' to quit: " choice
        if [[ "$choice" == "q" ]]; then
            echo "Exiting..."
            exit 1
        fi
    else
        echo "------------------------------------------"
        echo "ID  |  Microphone Name"
        echo "------------------------------------------"
        echo "$MICS"
        echo "------------------------------------------"
        read -p "🎤 Enter the ID of the mic you want to use (or 'r' to reload): " mic_choice
        
        if [[ "$mic_choice" == "r" ]]; then
            continue
        fi
        
        # Validate if input is a number
        if [[ "$mic_choice" =~ ^[0-9]+$ ]]; then
            echo "✅ Selected Mic ID: $mic_choice"
            echo "🚀 Booting up Robot Encoded..."
            python3 python/robot_encoded.py "$mic_choice"
            break
        else
            echo "⚠️ Invalid input. Please enter a number ID."
        fi
    fi
done
