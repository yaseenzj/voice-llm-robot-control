# Voice LLM Robot - Week 1 Documentation

**Arduino Voice-Controlled Chassis**  
*Temporary implementation for Week 1 testing. Primary target: Raspberry Pi LLM integration (Week 2-3).*

## Features
- [x] Real-time voice command recognition (forward/back/left/right/stop)
- [x] L298N motor driver PWM control (slow speed: 80/255)
- [x] Clean serial communication (/dev/ttyACM0, 9600 baud)
- [x] Tested on Ubuntu 24.04 + Arduino Mega 2560

## Hardware Requirements
- Arduino Mega 2560
- L298N dual motor driver
- 2x DC motors (6-12V, 100RPM)
- 4-wheel robot chassis
- Jumper wires
- USB cable (Arduino to laptop)
- Power: 7.4V-11.1V LiPo battery

## Wiring Diagram

L298N Motor Driver → Arduino Mega
├── IN1 → Pin 8 (Left motor forward)
├── IN2 → Pin 9 (Left motor reverse)
├── IN3 → Pin 10 (Right motor forward)
├── IN4 → Pin 11 (Right motor reverse)
├── ENA → Pin 7 (Left PWM)
├── ENB → Pin 6 (Right PWM)
├── VCC → 5V
└── GND → GND

Motors:
├── Left → L298N OUT1/OUT2
└── Right → L298N OUT3/OUT4

text

## Installation

### 1. Arduino Setup

    Install Arduino IDE 2.x from arduino.cc

    Connect Arduino Mega via USB

    Open src/chassis_controller.ino

    Tools → Board → "Arduino Mega or Mega 2560"

    Tools → Port → "/dev/ttyACM0" (Linux)

    Upload sketch (Ctrl+U)

text

### 2. Python Voice Setup
```bash
pip3 install SpeechRecognition pyserial
python3 src/voice_controller.py

Usage
Arduino Test

text
1. Upload `chassis_controller.ino`
2. Open Serial Monitor (9600 baud)
3. Type: F/B/L/R/S + Enter
4. Verify: Motors move slow (PWM 80)
5. **CLOSE Serial Monitor** (blocks Python)

Voice Control Demo

text
Terminal shows:
👂 Speak...
"forward" → FORWARD ✓
👂 Speak...
"left" → LEFT ✓  
👂 Speak...
"stop" → STOP ✓

Voice Commands: forward/back/left/right/stop/f/b/l/r/s
Example Serial Output

text
✅ SLOW Chassis Ready
Cmd: F → Moving
Cmd: L → Moving  
Cmd: S → STOPPED

Python Terminal Output

text
🎤 VOICE READY
👂 Speak... "forward"
FORWARD ✓
👂 Speak... "back" 
BACK ✓
👂 Speak... "stop"
STOP ✓

Troubleshooting
Issue	Solution
/dev/ttyACM0 busy	sudo killall arduino + unplug/replug
No motor movement	Check L298N wiring (pins 6-11), test with 9V battery
ALSA warnings	Normal - add os.environ['AUDIODEV'] = 'null'
Voice not detected	Run find_mic.py, update device_index=12
File Structure

text
voice-llm-robot/
├── src/
│   ├── chassis_controller.ino     # Arduino firmware
│   ├── voice_controller.py        # Python voice system
│   └── find_mic.py               # Microphone detection
├── docs/
│   └── wiring_diagram.jpg        # Visual connections
└── README.md

Performance Metrics

text
Voice latency: ~0.5s end-to-end
Motor response: <50ms
Command accuracy: 95%
Tested: Ubuntu 24.04 + Arduino Mega 2560
