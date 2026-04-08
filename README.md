# Voice-LLM Robot

### **Stop talking to walls. Talk to your hardware.**
Most "voice-controlled" robots are just glorified remote controls with a limited vocabulary. This one has a local LLaMA 3.2 brain running on a Raspberry Pi 4, meaning it actually understands what you want, even if you don't say it perfectly. It's the difference between a scripted NPC and a physical agent that thinks.

---

## The Actual Experience
Forget memorizing "Move Forward 5 Seconds." Just tell it what to do like a normal person.
> *"Yo, cruise forward for a bit, then pull a sharp left and wait there."*



### **Why this isn't just another tutorial project:**
* **Privacy by Default:** Everything runs on-device via Ollama on your Pi 4. No data is leaving your room, and no big-tech company is listening to your conversations.
* **Conversational Logic:** It handles intent. If you're vague, the LLM fills the gaps. If you're specific, it executes perfectly.
* **Hybrid Engine:** We use heuristics for the simple stuff (instant response) and the LLM for the complex maneuvers.
* **Hardware Combo:** Uses the Raspberry Pi 4 for high-level reasoning and the Arduino Uno for rock-solid motor execution.

---

## The Hardware Stack


| Component | The Job |
| :--- | :--- |
| **Raspberry Pi 4B** | The Pre-frontal Cortex. Handles the mic input and the LLaMA 3.2 brain. |
| **Arduino Uno** | The muscles. Handles the real-time PWM and motor pulses via Serial. |
| **L298N Driver** | The nervous system. Keeps the motors from frying your boards. |
| **12V LiPo** | The heart. Providing the juice to actually move. |

---

## Getting Started (The 1-Click Version)
I hate manual setup as much as you do. Use the scripts.

1. **Windows:** Double-click `run.bat`
2. **Linux/macOS:** `bash run.sh`

### **The "I want to do it myself" Way**
```bash
# Set up the environment on your Pi
python -m venv .venv
source .venv/bin/activate 

# Get the dependencies and the brain
pip install -r requirements.txt
ollama pull llama3.2:1b

# Wake it up
python python/robot_brain.py
