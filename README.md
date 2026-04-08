# Voice LLM Robot - Week 4 Documentation

**Arduino Voice-Controlled Chassis**  
Temporary implementation on Arduino Mega for testing.  
Primary target: Raspberry Pi LLM integration (Week 4-5).

## Features

- Real‑time voice command recognition: `forward` / `back` / `left` / `right` / `stop`
- L298N motor driver PWM control (slow speed: 80/255)
- Clean serial communication (`/dev/ttyACM0`, 9600 baud)
- Tested on Ubuntu 22.04 + Arduino Mega 2560

## Hardware Requirements

- Arduino Mega 2560
- L298N dual motor driver
- 2× DC motors (6–12 V, 100 RPM)
- 4‑wheel robot chassis
- Jumper wires
- USB cable (Arduino → laptop)
- Power: 12 V LiPo battery


## Wiring Diagram

| L298N Pin | Connected to        | Purpose |
|-----------|---------------------|---------|
| IN1       | Arduino pin 8       | Left motor forward |
| IN2       | Arduino pin 9       | Left motor reverse |
| IN3       | Arduino pin 10      | Right motor forward |
| IN4       | Arduino pin 11      | Right motor reverse |
| ENA       | Arduino pin 7       | Left motor PWM |
| ENB       | Arduino pin 6       | Right motor PWM |
| VCC       | Arduino 5V          | Logic power |
| GND       | Arduino GND         | Common ground |

## Motor Diagram

| Motor | L298N Outputs |
|-------|---------------|
| Left  | OUT1, OUT2    |
| Right | OUT3, OUT4    |


## Installation

### 1. Arduino Setup

    Install Arduino IDE 2 from arduino.cc

    Connect Arduino Mega via USB

    Open src/chassis_controller.ino

    Tools → Board → "Arduino Mega or Mega 2560"

    Tools → Port → "/dev/ttyACM0" (Linux)

    Upload sketch (Ctrl+U)


### 2. Python Environment Setup

It is highly recommended to isolate dependencies using a Python virtual environment.

**Option A: Automated Setup (Recommended)**
We provide automated scripts to instantly download the correct dependencies, fetch the local LLaMA model, and boot the robot:
- **Windows:** Run `run.bat`
- **Linux/macOS:** Run `bash run.sh`

**Option B: Manual Virtual Environment Setup**
1. **Create** the virtual environment in the project root:
   ```bash
   python -m venv .venv
   ```
2. **Activate** the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`
3. **Install Dependencies** exactly matching the project standards:
   ```bash
   pip install -r requirements.txt
   ```
4. **Pull Local Brain Model** (Ensure Ollama is installed):
   ```bash
   ollama pull llama3.2:1b
   ```
5. **Run**:
   ```bash
   python src/robot_brain.py
   ```

### 3. Usage & Execution
1. Upload `motor_control.ino` to the Arduino Mega.
2. Note: If you test via Serial Monitor first, **CLOSE IT** before running Python, as it hogs the COM port!
3. Execute the Python script (or use the `run` scripts).
4. **Speak completely naturally**: *"Go fast forward for two seconds, then go left for one second."*
5. The Robot Brain will instantly parse the sequence using heuristics, invoke LLaMA for complex logic, confirm its plan out loud using TTS, and seamlessly move the chassis!

Terminal shows:
👂 Speak...
"forward" → FORWARD ✓
👂 Speak...
"left" → LEFT ✓  
👂 Speak...
"stop" → STOP ✓

Voice Commands: forward/back/left/right/stop/f/b/l/r/s
Example Serial Output

✅ SLOW Chassis Ready
Cmd: F → Moving
Cmd: L → Moving  
Cmd: S → STOPPED

Python Terminal Output

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

voice-llm-robot/

├── src/

│   ├── chassis_controller.ino     # Arduino firmware
│   ├── voice_controller.py        # Python voice system
│   └── find_mic.py               # Microphone detection

├── docs/
│   └── wiring_diagram.jpg        # Visual connections
└── README.md

Performance Metrics

Voice latency: ~0.5s end-to-end
Motor response: <50ms
Command accuracy: 95%
Tested: Ubuntu 24.04 + Arduino Mega 2560
