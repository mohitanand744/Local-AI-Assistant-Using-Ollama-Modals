import re
import subprocess
from pathlib import Path
import winsound
import time
from config import (
    PIPER_MODEL,
    PIPER_LENGTH_SCALE,
    PIPER_NOISE_SCALE,
    PIPER_NOISE_W
)

BASE_DIR = Path(__file__).parent
MODEL = PIPER_MODEL
OUTPUT = BASE_DIR / "coding_beast_response.wav"


def clean_for_speech(text):
    """
    Remove Markdown and formatting that should not be spoken.
    """

    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove bold / italic markers
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("*", "")
    text = text.replace("_", " ")

    # Remove Markdown headings
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)

    # Remove numbered-list formatting
    text = re.sub(r"^\s*\d+\.\s*", "", text, flags=re.MULTILINE)

    # Remove bullet points
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)

    # Remove excessive blank lines
    text = re.sub(r"\n+", " ", text)

    # Remove excessive spaces
    text = re.sub(r"\s+", " ", text)
    
    text = text.strip()
    
    # Ensure text ends with punctuation so the TTS doesn't abruptly cut off the last word
    if text and text[-1] not in ['.', '!', '?']:
        text += '.'

    return text


def speak(text):
    clean_text = clean_for_speech(text)

    if not clean_text:
        print("⚠️ Coding Beast returned an empty response. Nothing to speak.")
        return

    subprocess.run(
        [
            "python",
            "-m",
            "piper",
            "--model",
            str(MODEL),
            "--output_file",
            str(OUTPUT),
            "--length_scale",
            str(PIPER_LENGTH_SCALE),
            "--noise_scale",
            str(PIPER_NOISE_SCALE),
            "--noise_w",
            str(PIPER_NOISE_W),
        ],
        input=clean_text,
        text=True,
        check=True,
    )

    winsound.PlaySound(
        str(OUTPUT),
        winsound.SND_FILENAME
    )
    
    # Wait 400ms after the AI finishes speaking to make the conversation feel more natural
    time.sleep(0.4)


if __name__ == "__main__":
    speak(
        "Hello Mohit. I am Coding Beast. "
        "Your local AI assistant is ready."
    )
