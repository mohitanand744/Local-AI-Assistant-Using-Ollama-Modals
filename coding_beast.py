from wake_word import wait_for_wake_word
from conversation import main as active_conversation
from voice import speak
from config import WAKE_WORD
import random

def main():
    print("========================================")
    print("🐉 CODING BEAST - LOCAL AI ASSISTANT")
    print("========================================")
    
    while True:
        try:
            # 1. Low Resource Idle Mode
            wait_for_wake_word()
            
            # 2. Wake Acknowledgment
            greetings = [
                "I'm here.",
                "How can I help?",
                "What's up?",
                "I'm listening.",
                "Yes, Mohit?",
                "Ready when you are."
            ]
            speak(random.choice(greetings))
            
            # 3. Active Conversation Mode (VAD + Whisper + Qwen)
            # This loops until the user says "exit", "stop", or "quit",
            # at which point it returns here and goes back to idle mode.
            active_conversation()
            
            print(f"\nReturning to idle mode. Say '{WAKE_WORD}' to wake me again.")
            
        except KeyboardInterrupt:
            print("\nShutting down Coding Beast completely. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error in main loop: {e}")
            # Prevent rapid error looping
            import time
            time.sleep(2)

if __name__ == "__main__":
    main()
