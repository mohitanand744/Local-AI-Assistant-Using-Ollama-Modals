import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pc_tools import open_app, open_folder, open_website
import config

def test_open_app_allowed(mocker):
    # Mock subprocess.Popen so we don't actually open the app during tests
    mock_popen = mocker.patch("pc_tools.subprocess.Popen")
    
    # Fake an allowlist
    mocker.patch.dict("pc_tools.ALLOWED_APPS", {"vscode": "code"})
    
    result = open_app("vscode")
    assert "Sure, opening vscode" in result
    mock_popen.assert_called_once_with("code", shell=True)

def test_open_app_denied(mocker):
    mock_popen = mocker.patch("pc_tools.subprocess.Popen")
    mocker.patch.dict("pc_tools.ALLOWED_APPS", {"vscode": "code"})
    
    result = open_app("malicious_app")
    assert "don't have permission" in result
    mock_popen.assert_not_called()

def test_open_folder_allowed(mocker):
    mock_startfile = mocker.patch("pc_tools.os.startfile")
    
    # Use the current directory as a safe existing folder
    current_dir = str(Path(__file__).parent)
    mocker.patch.dict("pc_tools.ALLOWED_FOLDERS", {"test_dir": current_dir})
    
    result = open_folder("test_dir")
    assert "opening the test_dir folder" in result
    mock_startfile.assert_called_once()

def test_open_folder_denied(mocker):
    mock_startfile = mocker.patch("pc_tools.os.startfile")
    mocker.patch.dict("pc_tools.ALLOWED_FOLDERS", {})
    
    result = open_folder("private_folder")
    assert "don't have permission" in result
    mock_startfile.assert_not_called()
