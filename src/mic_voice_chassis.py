#!/usr/bin/env python3
import speech_recognition as sr
import serial
import time
import glob
import os
import warnings
import pyaudio

warnings.filterwarnings("ignore")
os.environ['PYALSA_NO_LIBASOUND'] = '1'

# Arduino
ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
if not ports: print("❌ Arduino?"); exit()
PORT = ports[0]; print(f"✅ {PORT}")
ser = serial.Serial(PORT, 9600, timeout=0.5)
time.sleep(2); ser.flushInput(); ser.flushOutput()

# Your mic #10
mic_index = 10
print("🎤 Mic #10 (wireless)")

r = sr.Recognizer()
r.energy_threshold = 2500
r.dynamic_energy_threshold = True
m = sr.Microphone(device_index=mic_index)

print("🎤 Calibrate (silent 3s)...")
with m as source:
    r.adjust_for_ambient_noise(source, duration=3)
print(f"✅ Threshold: {r.energy_threshold}")

print("🚗 Say SLOW/LOUD: 'forward', 'back', 'left', 'right', 'stop' (or f/b/l/r/s)")

COMMANDS = {
    'forward': 'F', 'forwards': 'F', 'go forward': 'F', 'f': 'F', 'fore': 'F',
    'back': 'B', 'backward': 'B', 'backwards': 'B', 'reverse': 'B', 'b': 'B',
    'left': 'L', 'turn left': 'L', 'go left': 'L', 'l': 'L',
    'right': 'R', 'turn right': 'R', 'go right': 'R', 'r': 'R',
    'stop': 'S', 'stops': 'S', 'halt': 'S', 's': 'S'
}

while True:
    try:
        print("👂 Speak...")
        with m as source:
            audio = r.listen(source, timeout=4, phrase_time_limit=4)
        
        text = r.recognize_google(audio, language='en-IN').lower()  # Indian English
        print(f'🎤 "{text}"')
        
        # Match any word in text
        cmd = None
        text_words = text.split()
        for word in text_words:
            if word in COMMANDS:
                cmd = COMMANDS[word]
                break
        
        if cmd:
            ser.write(f"{cmd}\n".encode())  # FIXED: Proper newline
            ser.flush()
            print(f"✅ {cmd} → Arduino!")
        else:
            print("❓ No match—try clearer")
            
    except sr.WaitTimeoutError:
        print("⏰ No sound...")
    except sr.UnknownValueError:
        print("🤐 Couldn't understand")
    except sr.RequestError as e:
        print(f"🌐 Google API: {e}")
    except KeyboardInterrupt:
        ser.close(); print("👋"); break
    except Exception as e:
        print(f"💥 {e}")

