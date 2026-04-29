import serial, time, re, requests, json, threading, os, sys, pyttsx3
import speech_recognition as sr
from contextlib import contextmanager

PORT = '/dev/robot_nano' 
ROBOT_SPEED_CM_S = 41.25 
MODEL = "llama3.2:1b"

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
r.energy_threshold = 350
r.dynamic_energy_threshold = True
r.pause_threshold = 1.2 

stop_execution_flag = False

# Initialize TTS engine
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
    
    # Fallback to espeak
    os.system(f'espeak -s 175 "{text}" --stdout | aplay > /dev/null 2>&1')

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

        if action in ['L', 'R']:
            wait_time = (value / 90.0) * 1.65
        elif unit == 'time':
            wait_time = value
        else:
            wait_time = (value / ROBOT_SPEED_CM_S) + 0.5
        time.sleep(wait_time)
        
    try: ser.write(b'S0;')
    except: pass

def parse_command(text):
    text = text.replace("one", "1").replace("two", "2").replace("three", "3")
    nums = re.findall(r'\d+', text)
    val = float(nums[0]) if nums else None
    unit, mult, u_label = None, 1, ""
    if "degree" in text or " deg" in text: unit, u_label = 'deg', "degrees"
    elif "meter" in text or " m " in text or text.endswith(" m"): unit, mult, u_label = 'dist', 100, "meters"
    elif "cm" in text or "centimeter" in text: unit, u_label = 'dist', "centimeters"
    elif "second" in text or "sec" in text: unit, u_label = 'time', "seconds"

    action, dir_name = None, ""
    if 'left' in text: action, dir_name = 'L', "turning left"
    elif 'right' in text: action, dir_name = 'R', "turning right"
    elif any(w in text for w in ['back', 'backward', 'reverse']): action, dir_name = 'B', "moving backward"
    elif any(w in text for w in ['forward', 'go', 'move', 'front']): action, dir_name = 'F', "moving forward"
    
    if action in ['L', 'R'] and val is not None:
        unit, u_label = 'deg', "degrees"
        
    return action, val, unit, mult, u_label, dir_name

def ask_llama_sequence(user_input):
    url = "http://localhost:11434/api/generate"
    prompt = (
        f"Task: Convert robot commands to JSON movement list.\n"
        f"Mapping: Forward=F, Backward=B, Left=L, Right=R, Stop=S.\n"
        f"Input: '{user_input}'\n"
        f"Output format: [{{'cmd': 'LETTER', 'val': NUMBER, 'unit': 'dist/deg/time'}}]\n"
        f"Output ONLY the JSON."
    )
    try:
        response = requests.post(url, json={
            "model": MODEL, "prompt": prompt, "stream": False, "format": "json", "options": {"temperature": 0}
        }, timeout=10)
        return json.loads(response.json().get('response', '[]'))
    except: return []

device_index = None
if len(sys.argv) > 1:
    try:
        device_index = int(sys.argv[1])
        print(f"🎤 Using Microphone Index: {device_index}")
    except: pass

# --- MIC INITIALIZATION ---
def safe_mic_call(func, *args, **kwargs):
    """Safely handles mic operations with sample rate retries for Pi/USB hardware."""
    global device_index
    rates = [16000, 44100, 48000]
    last_err = None

    for rate in rates:
        try:
            with silence_stderr():
                # We use a smaller chunk_size for better responsiveness on Pi
                with sr.Microphone(device_index=device_index, sample_rate=rate) as source:
                    if source.stream is None:
                        raise RuntimeError("Microphone stream is None")
                    # Success!
                    return func(source, *args, **kwargs)
        except (AttributeError, AssertionError, Exception) as e:
            last_err = e
            continue # Try next sample rate
            
    # If all rates failed for the specific device, try falling back to default
    if device_index is not None:
        print(f"⚠️ Mic ID {device_index} failed at all rates. Trying default device...")
        device_index = None
        return safe_mic_call(func, *args, **kwargs)
    else:
        print(f"❌ Microphone Error: {last_err}")
        if "No Default Input Device Available" in str(last_err):
            print("\n💡 TROUBLESHOOTING TIPS:")
            print("1. Raspberry Pi: Ensure your USB mic is set as default in /etc/asound.conf")
            print("2. Linux Permissions: Run 'sudo usermod -aG audio $USER' and restart.")
            print("3. Busy Device: Run 'fuser -v /dev/snd/*' to see what is using audio.")
        speak("I can't access the microphone. Please check connections.")
        sys.exit(1)

try:
    print("🔍 Calibrating Mic...")
    safe_mic_call(r.adjust_for_ambient_noise, duration=2)
    speak("Ready for you, Yaseen.")
    
    while True:
        try:
            print("\n👂 Listening...")
            audio = safe_mic_call(r.listen, phrase_time_limit=15)
            if not audio: continue
            
            text = r.recognize_google(audio).lower()
            print(f"👤 Yaseen: {text}")

            if any(w in text for w in ["stop", "halt"]):
                stop_execution_flag = True
                try: ser.write(b"S0;")
                except: pass
                speak("Stopping.")
                continue

            # --- HYBRID BRAIN PROCESSING ---
            all_tasks = []
            replies = []

            # Phase 1: Keyword/Regex Parsing (Instant)
            # Split input to handle sequences like "move forward and then turn left"
            text_parts = re.split(r' then | and | after that | followed by ', text)
            for part in text_parts:
                action, val, unit, mult, u_label, dir_name = parse_command(part)
                if action and val is not None:
                    all_tasks.append((action, val * mult, unit))
                    replies.append(f"{dir_name} for {int(val)} {u_label}")

            # Phase 2: Local LLM Fallback (Smart but Slower)
            # Only call the LLM if keyword parsing found nothing
            if not all_tasks:
                print("🧠 Keywords didn't catch that, asking AI Brain...")
                moves = ask_llama_sequence(text)
                for move in moves:
                    action = move.get('cmd', 'S').upper()
                    val = float(move.get('val', 2.0))
                    unit = move.get('unit', 'dist')
                    
                    dir_map = {'F': "moving forward", 'B': "moving backward", 'L': "turning left", 'R': "turning right"}
                    if action in dir_map:
                        all_tasks.append((action, val, unit))
                        replies.append(f"{dir_map.get(action)} for {int(val)} {unit}")
            else:
                print("⚡ Instant Keyword match!")

            if all_tasks:
                speak("Got it Yaseen, I am " + " then ".join(replies) + ".")
                threading.Thread(target=execute_moves, args=(all_tasks,), daemon=True).start()

        except Exception: pass
except KeyboardInterrupt:
    print("\n👋 Shutdown.")