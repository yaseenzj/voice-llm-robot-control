#!/usr/bin/env python3
import speech_recognition as sr

print("Python Mic List:")
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")

