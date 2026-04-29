import speech_recognition as sr
import sys

device_index = None
if len(sys.argv) > 1:
    device_index = int(sys.argv[1])

print(f"Testing Mic with index: {device_index}")
try:
    mic = sr.Microphone(device_index=device_index)
    print(f"Mic object created: {mic}")
    with mic as source:
        print(f"Entered with block. source.stream: {source.stream}")
        if source.stream is None:
            print("CRITICAL: source.stream is None inside with block!")
        else:
            print("Success: source.stream is not None")
except Exception as e:
    print(f"Exception during mic test: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
