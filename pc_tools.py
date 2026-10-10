import os
import subprocess
import webbrowser
from pathlib import Path
from config import ALLOWED_APPS, ALLOWED_FOLDERS


# ============================================================
# OPEN APPLICATION
# ============================================================

def open_app(app_name):
    app_name = app_name.lower().strip()

    if app_name not in ALLOWED_APPS:
        return f"I don't have permission to open {app_name}."

    command = ALLOWED_APPS[app_name]

    try:
        subprocess.Popen(
            command,
            shell=True
        )

        return f"Sure, opening {app_name}."

    except Exception as error:
        return f"I couldn't open {app_name}. {error}"


# ============================================================
# OPEN FOLDER
# ============================================================

def open_folder(folder_name):
    folder_name = folder_name.lower().strip()

    if folder_name not in ALLOWED_FOLDERS:
        return f"I don't have permission to open {folder_name}."

    folder_path = Path(ALLOWED_FOLDERS[folder_name])

    if not folder_path.exists():
        return f"The folder {folder_name} does not exist."

    try:
        os.startfile(folder_path)
        return f"Got it, opening the {folder_name} folder."

    except Exception as error:
        return f"I couldn't open {folder_name}. {error}"


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(url):
    url = url.strip()

    if not url.startswith(("https://", "http://")):
        url = "https://" + url

    try:
        webbrowser.open(url)
        return f"Sure, opening {url} in your browser."

    except Exception as error:
        return f"I couldn't open the website. {error}"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print(open_folder("ai assistant"))