#!/usr/bin/env python3
import speech_recognition as sr
import serial
import time
import os
import sys
import warnings

# --- 1. SILENCE SYSTEM ERRORS ---
# This stops the "ALSA/JACK" wall of text from appearing
sys.stderr = open(os.devnull, 'w')
warnings.filterwarnings("ignore")

# --- 2. SERIAL SETUP ---
# Update '/dev/ttyACM0' if your Arduino shows up on a different port
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    print("? Connected to Arduino Mega on /dev/ttyACM0")
    print("? Waiting 3s for Arduino to initialize...")
    time.sleep(3) 
except Exception as e:
    print(f"? SERIAL ERROR: {e}")
    print("Check if Arduino is plugged in and you have permissions (sudo chmod 666 /dev/ttyACM0)")
    sys.exit()

# --- 3. VOICE ENGINE SETUP ---
r = sr.Recognizer()
mic_index = 1  # Your Wireless Mic Index from list_mics.py
r.energy_threshold = 500  # Sensitivity: Lower = More sensitive
r.dynamic_energy_threshold = True

# Mapping voice keywords to Arduino character commands
COMMANDS = {
    'forward': 'F', 'go forward': 'F',
    'back': 'B', 'backward': 'B', 'reverse': 'B',
    'left': 'L', 'turn left': 'L',
    'right': 'R', 'turn right': 'R',
    'stop': 'S', 'halt': 'S'
}

print("\n?? ROBOT VOICE CONTROL ACTIVE")
print("Commands: 'Forward', 'Back', 'Left', 'Right', 'Stop'")

try:
    with sr.Microphone(device_index=mic_index) as source:
        print("?? Calibrating mic for background noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            print("\n?? Listening for your command...")
            try:
                # Listen for 5 seconds max, limit phrase to 3 seconds
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
                
                # Recognize using Indian English (en-IN)
                text = r.recognize_google(audio, language='en-IN').lower()
                print(f'?? Recognized: "{text}"')

                # Check if any keyword is in the recognized text
                cmd_found = False
                for word in text.split():
                    if word in COMMANDS:
                        target_cmd = COMMANDS[word]
                        ser.write(target_cmd.encode())
                        print(f"?? ACTION: {word.upper()} (Sent '{target_cmd}')")
                        cmd_found = True
                        break
                
                if not cmd_found:
                    print("? Command not found in dictionary.")

            except sr.WaitTimeoutError:
                # No sound detected, just loop back
                continue
            except sr.UnknownValueError:
                print("?? Audio not clear enough.")
            except sr.RequestError:
                print("?? Internet Error: Google API unreachable.")
            except Exception as e:
                print(f"?? Error: {e}")

except KeyboardInterrupt:
    print("\n?? Shutting down... Sending STOP command.")
    ser.write(b'S')
    ser.close()
    sys.exit()