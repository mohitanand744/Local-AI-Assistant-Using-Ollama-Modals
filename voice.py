import re
import subprocess
from pathlib import Path
import winsound


BASE_DIR = Path(__file__).parent
MODEL = BASE_DIR / "models" / "en_US-lessac-medium.onnx"
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

    return text.strip()


def speak(text):
    clean_text = clean_for_speech(text)

    if not clean_text:
        print("⚠️ Coding Beast returned an empty response. Nothing to speak.")
        return

    print(f"Coding Beast: {clean_text}")

    subprocess.run(
        [
            "python",
            "-m",
            "piper",
            "--model",
            str(MODEL),
            "--output_file",
            str(OUTPUT),
        ],
        input=clean_text,
        text=True,
        check=True,
    )

    winsound.PlaySound(
        str(OUTPUT),
        winsound.SND_FILENAME
    )


if __name__ == "__main__":
    speak(
        "Hello Mohit. I am Coding Beast. "
        "Your local AI assistant is ready."
    )
