from record import record_audio
from speech import transcribe
from brain import ask_coding_beast
from voice import speak


def main():
    print("\n🎙️ Coding Beast is listening...")

    # Record your voice
    record_audio()

    # Convert voice to text
    text = transcribe("command.wav")

    if not text:
        print("❌ I couldn't understand you.")
        speak("Sorry, I couldn't understand you.")
        return

    print(f"\nYou: {text}")

    # Send text to local AI
    response = ask_coding_beast(text)

    print(f"\nCoding Beast: {response}")

    # Speak AI response
    speak(response)


if __name__ == "__main__":
    main()