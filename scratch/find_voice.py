from huggingface_hub import HfApi
api = HfApi()
files = api.list_repo_files("rhasspy/piper-voices")
jenny_files = [f for f in files if "jenny" in f]
print("Jenny files found:")
for f in jenny_files:
    print(f)
