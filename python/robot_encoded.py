import serial, time, re, threading, os, sys, pyttsx3
import speech_recognition as sr
from contextlib import contextmanager

# Configuration
PORT = '/dev/robot_nano' 
ROBOT_SPEED_CM_S = 41.25 

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
r.dynamic_energy_threshold = True
r.pause_threshold = 0.8 # Faster listening

stop_execution_flag = False

# Initialize TTS
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 175)
except:
    tts_engine = None

def speak(text):
    print(f"\n🤖 {text}")
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
            return
        except: pass
    os.system(f'espeak -s 175 "{text}" --stdout | aplay > /dev/null 2>&1')

def execute_moves(planned_moves):
    global stop_execution_flag, ser
    stop_execution_flag = False
    for action, value, unit in planned_moves:
        if stop_execution_flag: break
        cmd_letter = 'b' if (unit == 'time' and action == 'B') else ('t' if unit == 'time' else action)
        packet = f"{cmd_letter}{int(value)};"
        try:
            ser.write(packet.encode())
            print(f"📡 Sending: {packet}")
        except:
            ser = init_serial()
            if ser: ser.write(packet.encode())
        
        # Timing
        if action in ['L', 'R']: wait_time = (value / 90.0) * 1.65
        elif unit == 'time': wait_time = value
        else: wait_time = (value / ROBOT_SPEED_CM_S) + 0.5
        time.sleep(wait_time)
        
    try: ser.write(b'S0;')
    except: pass

def parse_command(text):
    text = text.replace("one", "1").replace("two", "2").replace("three", "3")
    nums = re.findall(r'\d+', text)
    val = float(nums[0]) if nums else 2.0
    unit, mult, u_label = 'dist', 1, "cm"
    
    if "degree" in text or " deg" in text: unit, u_label = 'deg', "degrees"
    elif "meter" in text or " m " in text: unit, mult, u_label = 'dist', 100, "meters"
    elif "second" in text or "sec" in text: unit, u_label = 'time', "seconds"

    action, dir_name = None, ""
    if 'left' in text: action, dir_name = 'L', "turning left"
    elif 'right' in text: action, dir_name = 'R', "turning right"
    elif any(w in text for w in ['back', 'backward', 'reverse']): action, dir_name = 'B', "moving backward"
    elif any(w in text for w in ['forward', 'go', 'move', 'front']): action, dir_name = 'F', "moving forward"
    
    if action in ['L', 'R'] and unit != 'time': unit, u_label = 'deg', "degrees"
    return action, val * mult, unit, u_label, dir_name

def safe_mic_call(func, *args, **kwargs):
    global device_index
    rates = [16000, 44100, 48000]
    for rate in rates:
        try:
            with silence_stderr():
                with sr.Microphone(device_index=device_index, sample_rate=rate) as source:
                    if source.stream: return func(source, *args, **kwargs)
        except: continue
    if device_index is not None:
        device_index = None
        return safe_mic_call(func, *args, **kwargs)
    sys.exit(1)

device_index = int(sys.argv[1]) if len(sys.argv) > 1 else None

try:
    print("🔍 Calibrating Mic...")
    safe_mic_call(r.adjust_for_ambient_noise, duration=1)
    speak("Ready for you, Yaseen.")
    
    while True:
        try:
            print("\n👂 Listening...")
            audio = safe_mic_call(r.listen, phrase_time_limit=10)
            text = r.recognize_google(audio).lower()
            print(f"👤 Yaseen: {text}")

            if any(w in text for w in ["stop", "halt"]):
                stop_execution_flag = True
                if ser: ser.write(b"S0;")
                speak("Stopping.")
                continue

            all_tasks, replies = [], []
            parts = re.split(r' then | and | after | followed by ', text)
            for part in parts:
                action, val, unit, u_label, dir_name = parse_command(part)
                if action:
                    all_tasks.append((action, val, unit))
                    replies.append(f"{dir_name} for {int(val)} {u_label}")

            if all_tasks:
                speak("I am " + " then ".join(replies) + ".")
                threading.Thread(target=execute_moves, args=(all_tasks,), daemon=True).start()

        except Exception: pass
except KeyboardInterrupt:
    print("\n👋 Shutdown.")