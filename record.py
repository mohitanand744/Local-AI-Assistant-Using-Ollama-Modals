import sounddevice as sd
import soundfile as sf
import numpy as np
from config import AUDIO_SAMPLE_RATE, VAD_THRESHOLD, VAD_SILENCE_DURATION

def record_audio(output_file="command.wav"):
    device = sd.default.device[0]

    if device is None or device < 0:
        raise RuntimeError("No default microphone is selected in Windows.")

    device_info = sd.query_devices(device)
    print(f"🎙️ Using microphone: {device_info['name']}")
    print("Speak now...")

    recorded_frames = []
    has_started_speaking = False
    silent_chunks = 0
    
    # Process audio in 100ms chunks
    chunk_size = int(AUDIO_SAMPLE_RATE * 0.1)
    max_silent_chunks = int(VAD_SILENCE_DURATION / 0.1)

    with sd.InputStream(samplerate=AUDIO_SAMPLE_RATE, channels=1, dtype='float32', device=device) as stream:
        while True:
            audio_chunk, overflowed = stream.read(chunk_size)
            recorded_frames.append(audio_chunk)

            # Calculate RMS (Root Mean Square) volume for the chunk
            volume = np.sqrt(np.mean(audio_chunk**2))

            if volume > VAD_THRESHOLD:
                if not has_started_speaking:
                    has_started_speaking = True
                silent_chunks = 0
            else:
                if has_started_speaking:
                    silent_chunks += 1

            # Stop if we've been silent for long enough after starting
            if has_started_speaking and silent_chunks >= max_silent_chunks:
                break
                
            # Hard limit: stop after 30 seconds to prevent endless recording
            if len(recorded_frames) > 300: 
                print("Max recording limit reached (30s).")
                break

    print("✅ Silence detected. Recording saved.")
    
    # Flatten the list of arrays and save
    audio_data = np.concatenate(recorded_frames, axis=0)
    sf.write(output_file, audio_data, AUDIO_SAMPLE_RATE)

if __name__ == "__main__":
    record_audio()