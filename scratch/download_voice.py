from huggingface_hub import hf_hub_download
import shutil
import os

print("Downloading Piper voice en_GB-jenny_dioco-medium...")
try:
    onnx_path = hf_hub_download(repo_id="rhasspy/piper-voices", filename="en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx")
    json_path = hf_hub_download(repo_id="rhasspy/piper-voices", filename="en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx.json")

    shutil.copy(onnx_path, "models/en_GB-jenny_dioco-medium.onnx")
    shutil.copy(json_path, "models/en_GB-jenny_dioco-medium.onnx.json")

    print("Download complete and models copied to models/")
except Exception as e:
    print(f"Error: {e}")
