from record import record_audio
from speech import transcribe
from brain import ask_coding_beast
from voice import speak


def main():
    print("\n🐉 Coding Beast continuous conversation started.")
    
    while True:
        print("\n🎙️ Listening...")

        # Record your voice (now uses VAD, waits for you to speak)
        try:
            record_audio()
        except KeyboardInterrupt:
            print("\nCoding Beast: Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Recording error: {e}")
            break

        # Convert voice to text
        text = transcribe("command.wav")

        if not text:
            # If nothing was understood, just quietly listen again
            continue

        print(f"\nYou: {text}")

        # Check for exit commands
        clean_text = text.lower().strip()
        # Remove punctuation for reliable exit matching
        for punct in ['.', ',', '!', '?']:
            clean_text = clean_text.replace(punct, '')
            
        if clean_text in ["exit", "stop", "quit", "goodbye"]:
            print("\nCoding Beast: See you later, bro.")
            speak("See you later, bro.")
            break

        # Send text to local AI
        response = ask_coding_beast(text)

        print(f"\nCoding Beast: {response}")

        # Speak AI response
        speak(response)


if __name__ == "__main__":
    main()