import sounddevice as sd
import soundfile as sf

RATE = 16000
SECONDS = 5


def record_audio(output_file="command.wav"):
    # Use Windows' default input microphone
    device = sd.default.device[0]

    if device is None or device < 0:
        raise RuntimeError("No default microphone is selected in Windows.")

    device_info = sd.query_devices(device)

    print(f"🎙️ Using microphone: {device_info['name']}")
    print("Speak now...")

    audio = sd.rec(
        int(RATE * SECONDS),
        samplerate=RATE,
        channels=1,
        dtype="float32",
        device=device
    )

    sd.wait()

    sf.write(output_file, audio, RATE)

    print("✅ Recording saved.")


if __name__ == "__main__":
    record_audio()