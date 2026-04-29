import serial, time, re, speech_recognition as sr
import pyttsx3, os, sys, threading
from contextlib import contextmanager

# --- CONFIG ---
PORT = '/dev/robot_nano' 
ROBOT_SPEED_CM_S = 41.25 

# --- INIT ---
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 175) 

@contextmanager
def silence_stderr():
    new_stderr = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    try:
        os.dup2(new_stderr, 2)
        os.close(new_stderr)
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

def init_serial():
    try:
        s = serial.Serial(PORT, 9600, timeout=1)
        time.sleep(1)
        return s
    except: return None

ser = init_serial()
r = sr.Recognizer()
# Microphone Sensitivity Tuning
r.energy_threshold = 350
r.dynamic_energy_threshold = True
r.pause_threshold = 1.2 

stop_execution_flag = False

def speak(text):
    print(f"\n🤖 {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def execute_moves(planned_moves):
    global stop_execution_flag, ser
    stop_execution_flag = False
    
    for action, value, unit in planned_moves:
        if stop_execution_flag: break
        
        cmd_letter = 'b' if (unit == 'time' and action == 'B') else \
                     ('t' if unit == 'time' else action)

        packet = f"{cmd_letter}{int(value)};"
        
        try:
            ser.write(packet.encode())
            print(f"📡 Sending: {packet}")
        except:
            time.sleep(1)
            ser = init_serial()
            if ser: ser.write(packet.encode())

        # Dynamic Wait Calculation
        if action in ['L', 'R']:
            wait_time = (value / 90.0) * 1.65 # Extra time for long turns
        elif unit == 'time':
            wait_time = value
        else:
            wait_time = (value / ROBOT_SPEED_CM_S) + 0.5
        time.sleep(wait_time)
        
    try: ser.write(b'S0;')
    except: pass

def parse_command(text):
    # Word-to-Digit cleanup
    text = text.replace("one", "1").replace("two", "2").replace("three", "3")
    
    nums = re.findall(r'\d+', text)
    val = float(nums[0]) if nums else None
    
    unit, mult, u_label = None, 1, ""
    
    # Unit mapping (Meter detection prioritized over CM)
    if "degree" in text or " deg" in text: 
        unit, u_label = 'deg', "degrees"
    elif "meter" in text or " m " in text or text.endswith(" m"): 
        unit, mult, u_label = 'dist', 100, "meters"
    elif "cm" in text or "centimeter" in text: 
        unit, u_label = 'dist', "centimeters"
    elif "second" in text or "sec" in text: 
        unit, u_label = 'time', "seconds"

    action, dir_name = None, ""
    if 'left' in text: action, dir_name = 'L', "turning left"
    elif 'right' in text: action, dir_name = 'R', "turning right"
    elif any(w in text for w in ['back', 'backward', 'reverse']): action, dir_name = 'B', "moving backward"
    elif any(w in text for w in ['forward', 'go', 'move', 'front']): action, dir_name = 'F', "moving forward"
    
    # Instant Turn Override
    if action in ['L', 'R'] and val is not None:
        unit = 'deg'
        u_label = "degrees"
        
    return action, val, unit, mult, u_label, dir_name

# --- MIC SELECTION ---
device_index = None
if len(sys.argv) > 1:
    try:
        device_index = int(sys.argv[1])
        print(f"🎤 Using Microphone Index: {device_index}")
    except: pass

try:
    with silence_stderr():
        mic = sr.Microphone(device_index=device_index)
    
    with mic as source:
        print("🔍 Calibrating Mic...")
        r.adjust_for_ambient_noise(source, duration=2)
        speak("Ready for you, Yaseen.")
        
        while True:
            try:
                print("\n👂 Listening...")
                audio = r.listen(source, phrase_time_limit=15)
                text = r.recognize_google(audio).lower()
                print(f"👤 Yaseen: {text}")

                if any(w in text for w in ["stop", "halt"]):
                    stop_execution_flag = True
                    try: ser.write(b"S0;")
                    except: pass
                    speak("Stopping.")
                    continue

                # Sequential Parser
                parts = re.split(r' then | and | after that ', text)
                all_tasks = []
                replies = []

                for part in parts:
                    action, val, unit, mult, u_label, dir_name = parse_command(part)

                    if action:
                        # Instant 180/360 logic
                        if action in ['L', 'R'] and val is None:
                            val, unit, u_label = 90, 'deg', "degrees"
                        
                        # Clarification loop for linear moves
                        if action in ['F', 'B'] and val is None:
                            speak(f"How far should I {dir_name}?")
                            a_sub = r.listen(source, timeout=5, phrase_time_limit=5)
                            s_text = r.recognize_google(a_sub).lower()
                            _, val, unit, mult, u_label, _ = parse_command(s_text)

                        if action and val is not None:
                            if unit is None: unit = 'dist'
                            all_tasks.append((action, val * mult, unit))
                            replies.append(f"{dir_name} for {int(val)} {u_label}")

                if all_tasks:
                    speak("Got it Yaseen, I am " + " then ".join(replies) + ".")
                    threading.Thread(target=execute_moves, args=(all_tasks,), daemon=True).start()

            except Exception: pass
except KeyboardInterrupt:
    print("\n👋 Shutdown.")