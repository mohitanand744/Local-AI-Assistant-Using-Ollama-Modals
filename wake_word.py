import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from config import MODELS_DIR, AUDIO_SAMPLE_RATE, WAKE_WORD

VOSK_MODEL_PATH = MODELS_DIR / "vosk-model"

def wait_for_wake_word():
    """
    Listens continuously using an ultra-lightweight Vosk model.
    Blocks until the wake word is spoken.
    """
    if not VOSK_MODEL_PATH.exists():
        raise RuntimeError(f"Vosk model not found at {VOSK_MODEL_PATH}")

    # Load the Vosk model quietly
    model = Model(str(VOSK_MODEL_PATH))
    recognizer = KaldiRecognizer(model, AUDIO_SAMPLE_RATE)
    
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """Called for each audio block by sounddevice."""
        if status:
            pass
        q.put(bytes(indata))

    device = sd.default.device[0]
    if device is None or device < 0:
        raise RuntimeError("No default microphone is selected in Windows.")

    device_info = sd.query_devices(device)
    print(f"🎙️ Using microphone: {device_info['name']}")

    print("💤 Coding Beast is in low-resource idle mode.")
    print(f"Say '{WAKE_WORD}' to wake me up.")

    with sd.RawInputStream(samplerate=AUDIO_SAMPLE_RATE, blocksize=8000, device=device, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            
            # Check if a full phrase is ready
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                
                if text:
                    print(f"[Debug] Vosk heard: {text}")

                if WAKE_WORD.lower() in text:
                    print("\n⏰ Wake word detected!")
                    return True
            else:
                # Check partial results for faster detection
                partial_result = json.loads(recognizer.PartialResult())
                partial_text = partial_result.get("partial", "").lower()
                
                if WAKE_WORD.lower() in partial_text:
                    print("\n⏰ Wake word detected!")
                    return True

if __name__ == "__main__":
    wait_for_wake_word()
