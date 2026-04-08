import serial, time, requests, json, re, speech_recognition as sr
import pyttsx3

# --- CONFIG ---
PORT = 'COM3' 
MODEL = "llama3.2:1b"

# --- TTS INIT ---
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 160) # Clear speaking rate

try:
    ser = serial.Serial(PORT, 9600, timeout=1)
    print("⏳ Initializing Arduino Mega... Wait 3 seconds.")
    time.sleep(3) 
    print(f"✅ Robot Connected on {PORT}")
except Exception as e:
    print(f"❌ SERIAL ERROR: {e}"); exit()

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
        f"Input: '{user_input}'\n"
        f"Task: Output ONLY a JSON list for robot movement.\n"
        f"Map: Forward=F, Backward=B, Left=L, Right=R, Stop=S.\n"
        f"Format: [{{'cmd': 'LETTER', 'sec': NUMBER}}]"
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
    with sr.Microphone(device_index=1) as source:
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
                        if "pause" in part or "stop" in part or "wait" in part: fast_action = 'S'
                        elif "left" in part or "call" in part: fast_action = 'L'
                        elif "right" in part: fast_action = 'R'
                        elif "back" in part or "reverse" in part: fast_action = 'B'
                        elif any(w in part for w in ["straight", "forward", "great", "fast"]): fast_action = 'F'
                        
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

                            # --- REFINED HEURISTIC SAFETY LAYER ---
                            # Always trust explicitly spoken keywords over the 1B LLM's guess
                            if "pause" in part or "stop" in part or "wait" in part:
                                action = 'S'
                            elif "left" in part or "call" in part: # 'call' often misheard for 'go'
                                action = 'L'
                            elif "right" in part:
                                action = 'R'
                            elif "back" in part or "reverse" in part:
                                action = 'B'
                            elif any(w in part for w in ["straight", "forward", "great", "fast"]):
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