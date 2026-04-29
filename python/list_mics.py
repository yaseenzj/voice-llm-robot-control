#!/usr/bin/env python3
import speech_recognition as sr

def list_mics():
    print("\nAvailable Microphones:")
    print("-" * 30)
    mics = sr.Microphone.list_microphone_names()
    for i, name in enumerate(mics):
        is_external = "array" not in name.lower() and "built-in" not in name.lower()
        status = "RECOMMENDED EXTERNAL" if is_external else "Internal/System"
        print(f"[{i}] {name} ({status})")
    print("-" * 30)
    print("TIP: Look for your Digitek or USB Microphone index.\n")

if __name__ == "__main__":
    list_mics()
