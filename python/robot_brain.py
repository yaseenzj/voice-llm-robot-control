import serial, time, requests, json, re, speech_recognition as sr
import pyttsx3, os, sys
from contextlib import contextmanager

# --- CONFIG ---
# --- CONFIG ---
import serial.tools.list_ports

def get_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # Arduino Nano often shows up as USB-SERIAL CH340 or CP2102
        if "USB-SERIAL" in p.description.upper() or "CH340" in p.description.upper() or "ARDUINO" in p.description.upper():
            return p.device
    return 'COM3' if os.name == 'nt' else '/dev/ttyUSB0'

PORT = get_arduino_port()
MODEL = "llama3.2:1b"
MIC_INDEX = int(sys.argv[1]) if len(sys.argv) > 1 else None

# --- TTS INIT ---
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 160) # Clear speaking rate

@contextmanager
def silence_stderr():
    """Context manager to suppress low-level system noise (ALSA, JACK, etc)"""
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

try:
    ser = serial.Serial(PORT, 9600, timeout=1)
    print(f"Initializing Arduino Nano on {PORT}... Wait 3 seconds.")
    time.sleep(3) 
    print(f"DONE: Robot Connected on {PORT}")
except Exception as e:
    print(f"SERIAL ERROR: Could not connect to {PORT}. {e}")
    print("TIP: Check if your Arduino Nano is plugged in and you're using the right port.")
    exit()

r = sr.Recognizer()
r.pause_threshold = 1.5 
r.dynamic_energy_threshold = True

import threading
stop_execution_flag = False

def execute_moves(planned_moves):
    global stop_execution_flag
    stop_execution_flag = False
    print("\n🚀 Executing Sequence...")
    for action, seconds, speed_mod in planned_moves:
        if stop_execution_flag:
            print("🛑 EXECUTION ABORTED BY USER!")
            break
            
        print(f"   -> EXECUTING: {action} ({speed_mod}) for {seconds}s")
        if speed_mod == 'fast': ser.write(b'2')
        elif speed_mod == 'slow': ser.write(b'0')
        else: ser.write(b'1')
        
        ser.write(action.encode())
        
        # Chunked sleep to allow instant interruption
        elapsed = 0
        while elapsed < seconds:
            if stop_execution_flag:
                print("🛑 EXECUTION ABORTED BY USER!")
                break
            time.sleep(0.1)
            elapsed += 0.1
            
        if stop_execution_flag: break
            
    ser.write(b'S') # Always stop motors after sequence or abort
    time.sleep(0.5) # Allow serial buffer to clear
    print("✅ Full Mission Sequence Finished.")

def ask_llama_sequence(user_input):
    url = "http://localhost:11434/api/generate"
    # Prompt simplified to focus on Letter/Number extraction
    prompt = (
        f"Task: Convert robot commands to JSON movement list.\n"
        f"Mapping: Forward=F, Backward=B, Left=L, Right=R, Stop=S.\n"
        f"Slangs: 'cruise/zoom/advance/go' -> F, 'pull a left/hang a left' -> L, 'stay/wait there' -> S.\n"
        f"Durations: 'a bit/shortly' -> 3, 'a while' -> 10, 'forever' -> 30.\n"
        f"Input: '{user_input}'\n"
        f"Output format: [{{'cmd': 'LETTER', 'sec': NUMBER}}]\n"
        f"Output ONLY the JSON."
    )
    try:
        response = requests.post(url, json={
            "model": MODEL, "prompt": prompt, "stream": False, "format": "json", "options": {"temperature": 0}
        }, timeout=10)
        data = json.loads(response.json().get('response', '[]'))
        return [data] if isinstance(data, dict) else data
    except:
        return []

try:
    with silence_stderr():
        if MIC_INDEX is None:
            print("WARNING: No Microphone Index provided. Listing available mics...")
            import subprocess
            subprocess.run([sys.executable, "list_mics.py"])
            print("\n")
            # In some environments, input() might be tricky in a background process, 
            # but since this is run by the user in a terminal it should be fine.
            try:
                user_choice = input("Enter the index of your EXTERNAL microphone: ")
                MIC_INDEX = int(user_choice)
            except ValueError:
                print("ERROR: Invalid input. Please enter a number.")
                exit()
        
        # Validation: Check if it's likely a built-in mic
        mics = sr.Microphone.list_microphone_names()
        if MIC_INDEX < 0 or MIC_INDEX >= len(mics):
            print(f"ERROR: Index {MIC_INDEX} is out of range.")
            exit()

        selected_mic_name = mics[MIC_INDEX].lower()
        if "array" in selected_mic_name or "built-in" in selected_mic_name:
            print(f"WARNING: '{mics[MIC_INDEX]}' looks like a built-in mic!")
            print("This project requires an EXTERNAL microphone (like Digitek) for better accuracy.")
            try:
                choice = input("Do you want to continue anyway? (y/N): ").lower()
                if choice != 'y':
                    print("Exiting. Please connect an external mic and try again.")
                    exit()
            except EOFError:
                print("Skipping confirmation due to environment constraints.")

        mic = sr.Microphone(device_index=MIC_INDEX)
    
    with mic as source:
        print("🧹 Calibrating mic... stay quiet.")
        r.adjust_for_ambient_noise(source, duration=2)
        print(f"🚀 BRAIN ONLINE! Talk naturally to the robot.")
        
        while True:
            try:
                print("\n👂 Listening...")
                audio = r.listen(source, phrase_time_limit=15)
                text = r.recognize_google(audio).lower()
                print(f"👤 You: {text}")

                # Split sentence by "then" or "and" for small-chunk processing
                parts = re.split(r'then|and', text)
                
                # Phase 1: Planning
                import concurrent.futures
                valid_parts = [p.strip() for p in parts if p.strip() and len(p.strip()) >= 2]
                planned_moves = []
                
                if valid_parts:
                    print(f"🤖 Analyzing {len(valid_parts)} steps...")
                    
                    results = []
                    for part in valid_parts:
                        # Fast Heuristic Bypass to eliminate LLM processing delay!
                        fast_action = None
                        if any(w in part for w in ["pause", "stop", "wait", "stay", "halt", "freeze", "hold"]): fast_action = 'S'
                        elif any(w in part for w in ["left", "west"]): fast_action = 'L'
                        elif any(w in part for w in ["right", "east"]): fast_action = 'R'
                        elif any(w in part for w in ["back", "reverse", "retreat", "rear"]): fast_action = 'B'
                        elif any(w in part for w in ["straight", "forward", "great", "fast", "cruise", "advance", "zoom", "ahead", "go", "call"]): fast_action = 'F'
                        
                        results.append([{'cmd': fast_action, 'sec': 2.0}] if fast_action else None)

                    # Only invoke LLM on ambiguous steps
                    llm_indices = [i for i, r in enumerate(results) if r is None]
                    if llm_indices:
                        print(f"🧠 Deep LLM Brain engaged for {len(llm_indices)} complex steps...")
                        parts_for_llm = [valid_parts[i] for i in llm_indices]
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            llm_results = list(executor.map(ask_llama_sequence, parts_for_llm))
                        for idx, res in zip(llm_indices, llm_results):
                            results[idx] = res
                    
                    for part, steps in zip(valid_parts, results):
                        for step in steps:
                            # Extract Command
                            raw_cmd = str(step.get('cmd', 'S')).strip().upper()
                            action = raw_cmd[0] if raw_cmd else 'S'
                            
                            # Extract Seconds (Prioritize voice detection over LLM guess)
                            voice_nums = re.findall(r'\d+', part)
                            seconds = float(voice_nums[0]) if voice_nums else float(step.get('sec', 2.0))
                            
                            # --- SLANG DURATION PARSING ---
                            if not voice_nums:
                                if any(w in part for w in ["a bit", "a little", "shortly", "briefly"]): 
                                    seconds = 3.0
                                elif any(w in part for w in ["a while", "long time", "forever"]): 
                                    seconds = 10.0
                                elif "a second" in part:
                                    seconds = 1.0

                            # --- REFINED HEURISTIC SAFETY LAYER ---
                            # Always trust explicitly spoken keywords over the 1B LLM's guess
                            if any(w in part for w in ["pause", "stop", "wait", "stay", "halt", "freeze", "hold"]):
                                action = 'S'
                            elif any(w in part for w in ["left", "west"]): 
                                action = 'L'
                            elif any(w in part for w in ["right", "east"]):
                                action = 'R'
                            elif any(w in part for w in ["back", "reverse", "retreat", "rear"]):
                                action = 'B'
                            elif any(w in part for w in ["straight", "forward", "great", "fast", "cruise", "advance", "zoom", "ahead", "go", "call"]):
                                action = 'F'
                            elif action == 'S' or action == 'G' or action not in ['F', 'B', 'L', 'R', 'S']:
                                if "go" in part or "move" in part:
                                    action = 'F'

                            speed_mod = 'normal'
                            if "fast" in part or "quick" in part or "speed" in part: speed_mod = 'fast'
                            elif "slow" in part: speed_mod = 'slow'

                            if action in ['F', 'B', 'L', 'R', 'S']:
                                if action == 'S':
                                    stop_execution_flag = True
                                planned_moves.append((action, seconds, speed_mod))

                # Phase 2: Execution
                if planned_moves:
                    # Real-Time Voice Feedback
                    response_text = "Understood Yaseen, I will "
                    move_desc = []
                    for action, seconds, speed_mod in planned_moves:
                        s = f"{seconds} seconds" if seconds != 1 else "1 second"
                        sp_adj = f" at {speed_mod} speed" if speed_mod != 'normal' and action != 'S' else ""
                        
                        if action == 'F': move_desc.append(f"move forward{sp_adj} for {s}")
                        elif action == 'B': move_desc.append(f"move backward{sp_adj} for {s}")
                        elif action == 'L': move_desc.append(f"turn left{sp_adj} for {s}")
                        elif action == 'R': move_desc.append(f"turn right{sp_adj} for {s}")
                        elif action == 'S': move_desc.append(f"pause for {s}")
                    
                    if len(move_desc) > 1:
                        response_text += ", then ".join(move_desc[:-1]) + ", and then " + move_desc[-1]
                    elif move_desc:
                        response_text += move_desc[0]
                    
                    print(f"\n🔊 Robot says: '{response_text}.'")
                    if not stop_execution_flag:
                        tts_engine.say(response_text)
                        tts_engine.runAndWait()

                    # Start execution in the background so we can immediately resume listening for "stop" commands!
                    threading.Thread(target=execute_moves, args=(planned_moves,), daemon=True).start()

            except sr.UnknownValueError: pass
            except Exception as e: print(f"❌ Error: {e}")

except Exception as e:
    print(f"❌ MIC ERROR: {e}")