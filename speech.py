import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SITE_PACKAGES = BASE_DIR / ".venv" / "Lib" / "site-packages"

CUDA_DIRS = [
    SITE_PACKAGES / "nvidia" / "cublas" / "bin",
    SITE_PACKAGES / "nvidia" / "cudnn" / "bin",
    SITE_PACKAGES / "nvidia" / "cuda_nvrtc" / "bin",
]

# Add NVIDIA CUDA DLL folders to Windows DLL search path
for dll_dir in CUDA_DIRS:
    if dll_dir.exists():
        os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ["PATH"]

        try:
            os.add_dll_directory(str(dll_dir))
        except Exception:
            pass

from faster_whisper import WhisperModel
from config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE


print("Loading Whisper model...")

model = WhisperModel(
    WHISPER_MODEL,
    device=WHISPER_DEVICE,
    compute_type=WHISPER_COMPUTE_TYPE
)

print("Whisper model loaded.")


def transcribe(audio_file):
    segments, info = model.transcribe(
        audio_file,
        beam_size=5,
        language="en",
        vad_filter=True,
        condition_on_previous_text=False
    )

    return " ".join(
        segment.text for segment in segments
    ).strip()