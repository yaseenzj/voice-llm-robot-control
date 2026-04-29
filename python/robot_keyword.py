import serial, time, re, speech_recognition as sr
import pyttsx3, os, sys, threading
from contextlib import contextmanager

PORT = '/dev/ttyUSB0' 

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 160)

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

try:
    ser = serial.Serial(PORT, 9600, timeout=1)
    time.sleep(3) 
except:
    pass

r = sr.Recognizer()
r.pause_threshold = 1.5 
r.dynamic_energy_threshold = True

stop_execution_flag = False

def execute_moves(planned_moves):
    global stop_execution_flag
    stop_execution_flag = False
    for action, seconds, speed_mod in planned_moves:
        if stop_execution_flag: break
        if speed_mod == 'fast': ser.write(b'2')
        elif speed_mod == 'slow': ser.write(b'0')
        else: ser.write(b'1')
        ser.write(action.encode())
        elapsed = 0
        while elapsed < seconds:
            if stop_execution_flag: break
            time.sleep(0.1)
            elapsed += 0.1
        if stop_execution_flag: break
    ser.write(b'S')
    time.sleep(0.5)

try:
    with silence_stderr():
        mic = sr.Microphone()
    
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=2)
        while True:
            try:
                audio = r.listen(source, phrase_time_limit=15)
                text = r.recognize_google(audio).lower()
                parts = re.split(r'then|and', text)
                valid_parts = [p.strip() for p in parts if p.strip() and len(p.strip()) >= 2]
                planned_moves = []
                if valid_parts:
                    for part in valid_parts:
                        fast_action = None
                        if any(w in part for w in ["pause", "stop", "wait", "stay", "halt", "freeze", "hold"]): fast_action = 'S'
                        elif any(w in part for w in ["left", "west"]): fast_action = 'L'
                        elif any(w in part for w in ["right", "east"]): fast_action = 'R'
                        elif any(w in part for w in ["back", "reverse", "retreat", "rear"]): fast_action = 'B'
                        elif any(w in part for w in ["straight", "forward", "great", "fast", "cruise", "advance", "zoom", "ahead", "go", "call"]): fast_action = 'F'
                        
                        if fast_action:
                            voice_nums = re.findall(r'\d+', part)
                            seconds = float(voice_nums[0]) if voice_nums else 2.0
                            speed_mod = 'normal'
                            if "fast" in part: speed_mod = 'fast'
                            elif "slow" in part: speed_mod = 'slow'
                            planned_moves.append((fast_action, seconds, speed_mod))

                if planned_moves:
                    threading.Thread(target=execute_moves, args=(planned_moves,), daemon=True).start()

            except sr.UnknownValueError: pass
            except: pass
except:
    pass
