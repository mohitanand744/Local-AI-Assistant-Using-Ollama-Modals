import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# AI Models
OLLAMA_MODEL = "qwen2.5-coder:7b"
WHISPER_MODEL = "small"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"

# Piper Voice Settings (Jenny Dioco - Natural Female)
PIPER_MODEL = MODELS_DIR / "en_GB-jenny_dioco-medium.onnx"
PIPER_LENGTH_SCALE = 1.15  # Slightly slower for better natural rhythm
PIPER_NOISE_SCALE = 0.667
PIPER_NOISE_W = 0.8

# Audio Settings
AUDIO_SAMPLE_RATE = 16000
WAKE_WORD = "hey coding beast"

# VAD Settings
VAD_THRESHOLD = 0.015
VAD_SILENCE_DURATION = 1.5

# PC Tools Configuration
ALLOWED_APPS = {
    "vscode": "code",
    "visual studio code": "code",
    "chrome": "chrome",
    "google chrome": "chrome",
    "notepad": "notepad",
    "calculator": "calc",
}

ALLOWED_FOLDERS = {
    "ai assistant": str(BASE_DIR),
}

# Developer Tools Configuration
# You can add more projects here, like "nextchapter": r"C:\path\to\nextchapter"
PROJECTS = {
    "ai assistant": BASE_DIR,
}

# Safe Development Server Allowlist
DEV_SERVERS = {
    "nextchapter": {
        "frontend": {
            "command": "npm run dev",
            "cwd": r"C:\path\to\your\NextChapter\frontend"
        },
        "backend": {
            "command": "npm run dev",
            "cwd": r"C:\path\to\your\NextChapter\backend"
        }
    },
    "ai assistant": {
        "python": {
            "command": "python coding_beast.py",
            "cwd": str(BASE_DIR)
        }
    }
}
