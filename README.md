# Voice-LLM Robot 

### **Stop talking to walls. Talk to your hardware.**
Most "voice-controlled" robots are just glorified remote controls with a limited vocabulary. This one has a local **LLaMA 3.2** brain running on a Jetson Nano (or Raspberry Pi), meaning it actually understands what you want, even if you don't say it perfectly. It's the difference between a scripted NPC and a physical agent that thinks.

---

## 🎬 The Actual Experience
Forget memorizing "Move Forward 5 Seconds." Just tell it what to do like a normal person.
> *"Yo, go forward 50 cm, then turn left and go forward for 30cm then turn left and go forward for 1 second then turn 90 degree to the ;eft.."*

### **Why this isn't just another tutorial project:**
* **Privacy by Default:** Everything runs on-device. No data leaves your room, and no big-tech company is listening.
* **Smart Intent Recognition:** It handles unit conversions (meters, cm, seconds) and slang naturally.
* **Robust Hardware Setup:** Optimized for **Arduino Nano** for real-time motor control and **Jetson Nano/Pi** for the AI brain.
* **Zero-Config Setup:** A smart script handles system dependencies, audio drivers, and microphone selection for you.

---

## 🏗️ The Hardware Stack

| Component | The Job |
| :--- | :--- |
| **Raspberry Pi 4B** | The Pre-frontal Cortex. Handles mic input, speech-to-text, and the AI brain. |
| **Arduino Nano** | The muscles. Handles high-frequency PWM and encoder feedback via Serial. |
| **L298N Driver** | The nervous system. Bridges the logic power to the high-current motors. |
| **12V LiPo** | The heart. Providing the juice to actually move. |
| **Microphone** | The ears. Captures your voice commands. |

**Recommended Microphone:** [Digitek Wireless Microphone (DWM 101)](https://amzn.in/d/0imarqwx)

---

## 🚀 Getting Started

### **1. The Easy Way (One-Click Setup)**
I've automated the headache. The `run.sh` script installs requirements, fixes common Linux audio errors (Error 524), and helps you select your microphone.
```bash
bash run.sh
```

### **2. The Manual Way**
```bash
# Set up the environment
python3 -m venv .venv
source .venv/bin/activate 

# Install dependencies
pip install -r requirements.txt

# Start the brain (Select your mic ID when prompted)
python3 python/robot_encoded.py [MIC_ID]
```

### **3. Arduino Setup**
1. Open `arduino/motor_control/motor_control.ino` in the Arduino IDE.
2. Select **Arduino Nano** (Old Bootloader often required) or your specific board.
3. Upload and connect the USB cable to your AI controller.

---

## 🛠️ Key Features
* **Microphone Auto-Detection:** No more hardcoding device IDs. The script detects and lets you choose on launch.
* **Audio Conflict Fix:** Built-in `pulseaudio` management to prevent the "ALSA busy" errors during simultaneous listening and speaking.
* **Calibrated Movement:** Uses encoder feedback (ticks) for precise distance (CM) and rotation (Degrees).

---

## 🔮 Future Upgrades:
* **Computer Vision:** Mount a camera for Multimodal AI. Say *"Find the red ball"* or *"Follow me."*
* **SLAM & Mapping:** Use RP-Lidar for Global Navigation. Ask the robot to *"Go to the kitchen."*
* **Obstacle Avoidance:** Add ultrasonic sensors for a "Reflex Layer" to prevent crashes.
* **Semantic Memory:** Use a Vector Database (RAG) so it remembers landmarks like *"my charger."*