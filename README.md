# Voice-LLM Robot Control

An intelligent, voice-controlled robotic system powered by LLaMA 3.2 (via Ollama) running locally on a Raspberry Pi. This project moves beyond simple keyword matching by using Large Language Models to interpret natural language commands and translate them into precise motor movements.

<img src="images/robot_closeup.jpeg" alt="Robot Closeup" width="100%" height="150" style="object-fit: cover; border-radius: 8px;">

---

## 🚀 Overview

The **Voice-LLM Robot** leverages local AI to provide a fluid, conversational interface for hardware control. Users can issue complex, multi-step instructions in natural language (e.g., *"Move forward 50cm, rotate 90 degrees left, and return"*) which the system parses and executes via an Arduino-driven drivetrain.

### Key Technical Features
- **Natural Language Understanding**: Powered by `llama3.2:1b` for high-fidelity intent parsing.
- **Edge Intelligence**: Fully local execution—zero latency from cloud APIs and enhanced privacy.
- **Persistent Connectivity**: Automated mapping to `/dev/robot_nano` for reliable serial communication.
- **Audio Management**: Intelligent microphone selection with automated ALSA error mitigation.

---

## 🛠️ System Architecture

### System in Action
![Robot Demo](images/IMG_5383.gif)

| Component | Responsibility |
| :--- | :--- |
| **Raspberry Pi** | Main Controller (STT, LLM Inference, TTS). |
| **LLaMA 3.2 (1B)** | Logic Engine for natural language parsing. |
| **Arduino Nano** | Real-time motor control and actuation. |
| **L298N Driver** | Dual H-Bridge motor power management. |
| **Mecanum Wheels** | Omni-directional movement capabilities. |

---

## 🏗️ Getting Started

### 1. Repository Setup
```bash
git clone https://github.com/yaseenzj/voice-llm-robot-control.git
cd voice-llm-robot-control
```

### 2. Local LLM Configuration
This project requires **Ollama** for running the LLaMA model locally:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the optimized LLaMA 3.2 model
ollama pull llama3.2:1b
```

### 3. Firmware Deployment
1. Open `arduino/motor_control/motor_control.ino` in the Arduino IDE.
2. Upload the code to your **Arduino Nano**.
3. Connect the Arduino to the Raspberry Pi.

---

## ⚡ Execution

### Automated Launch (Recommended)
Use the bootstrap script to automatically handle environment setup and device selection:
```bash
bash run.sh
```

### Manual Launch
```bash
# Initialize environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run controller (replace [MIC_ID] with your microphone index)
python3 python/robot_encoded.py [MIC_ID]
```

---

## 🔮 Roadmap
- [ ] **Visual Perception**: Integrating OpenCV for object recognition and tracking.
- [ ] **Safety Layer**: Ultrasonic and IR sensors for autonomous collision avoidance.
- [ ] **Localization**: Basic SLAM implementation for indoor environment mapping.