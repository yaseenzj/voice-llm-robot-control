import serial, time, requests, json, re, speech_recognition as sr
import pyttsx3, os, sys, threading
from contextlib import contextmanager

# --- CONFIG ---
PORT = '/dev/robot_nano' 
ROBOT_SPEED_CM_S = 41.25 

# --- INIT ---
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 170) 

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
r.non_speaking_duration = 0.2
r.phrase_threshold = 0.2
stop_execution_flag = False

def speak(text):
    print(f"\n🤖 {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def execute_moves(planned_moves):
    global stop_execution_flag, ser
    stop_execution_flag = False
    time.sleep(0.3)
    
    for action, value, unit in planned_moves:
        if stop_execution_flag: break
        
        # --- CRITICAL FIX: BACKWARD TIME vs DISTANCE ---
        if unit == 'time':
            cmd_letter = 'b' if action == 'B' else 't'
        else:
            cmd_letter = action # F, B, L, R

        packet = f"{cmd_letter}{int(value)};"
        
        try:
            ser.write(packet.encode())
            print(f"📡 Sent to Arduino: {packet}")
        except:
            time.sleep(1)
            ser = init_serial()
            if ser: ser.write(packet.encode())

        if action in ['L', 'R']:
            wait_time = (value / 90.0) * 1.5 if value > 0 else 1.5
        elif unit == 'time':
            wait_time = value
        else:
            wait_time = (value / ROBOT_SPEED_CM_S) + 0.5
        time.sleep(wait_time)
        
    try: ser.write(b'S0;')
    except: pass

def parse_command(text):
    nums = re.findall(r'\d+', text)
    val = float(nums[0]) if nums else None
    
    unit, mult, u_label = None, 1, ""
    if "degree" in text: unit, u_label = 'deg', "degrees"
    elif "cm" in text or "centimeter" in text: unit, u_label = 'dist', "centimeters"
    elif "meter" in text or " m " in text: unit, mult, u_label = 'dist', "meters", 100
    elif "second" in text or "sec" in text: unit, u_label = 'time', "seconds"

    action, dir_name = None, ""
    if 'left' in text: action, dir_name = 'L', "turning left"
    elif 'right' in text: action, dir_name = 'R', "turning right"
    elif any(w in text for w in ['back', 'backward', 'reverse']): action, dir_name = 'B', "moving backward"
    elif any(w in text for w in ['forward', 'go', 'move', 'front']): action, dir_name = 'F', "moving forward"
    
    return action, val, unit, mult, u_label, dir_name

try:
    with silence_stderr():
        mic = sr.Microphone()
    
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)
        speak("Ready for you, Yaseen.")
        
        while True:
            try:
                print("\n👂 Listening...")
                audio = r.listen(source, phrase_time_limit=5)
                text = r.recognize_google(audio).lower()
                print(f"👤 Yaseen: {text}")

                if any(w in text for w in ["stop", "halt"]):
                    stop_execution_flag = True
                    try: ser.write(b"S0;")
                    except: pass
                    speak("Stopping.")
                    continue

                action, val, unit, mult, u_label, dir_name = parse_command(text)

                if action:
                    # --- RULE: If it's a TURN, default to 90 degrees ---
                    if action in ['L', 'R'] and val is None:
                        val = 90
                        unit = 'deg'
                        u_label = "degrees"

                    # --- RULE: If it's a MOVE and missing info, ASK ---
                    if action in ['F', 'B'] and (val is None or unit is None):
                        speak(f"How far should I {dir_name}?")
                        audio_sub = r.listen(source, timeout=4, phrase_time_limit=4)
                        sub_text = r.recognize_google(audio_sub).lower()
                        _, val, unit, mult, u_label, _ = parse_command(sub_text)

                    if action and unit:
                        final_val = val * mult
                        speak(f"Got it Yaseen, I am {dir_name} for {int(val)} {u_label} now.")
                        threading.Thread(target=execute_moves, args=([(action, final_val, unit)],), daemon=True).start()

            except Exception: pass
except KeyboardInterrupt:
    print("\n👋 Shutdown.")