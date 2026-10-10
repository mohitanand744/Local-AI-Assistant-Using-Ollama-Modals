import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dev_tools import git_status, git_branch, open_project, start_server, stop_server
import config

def test_git_status_clean(mocker):
    mock_run = mocker.patch("dev_tools.subprocess.run")
    mock_run.return_value.returncode = 0
    # Mock a clean repository (no output from git status -s)
    mock_run.return_value.stdout = ""
    
    mocker.patch.dict("dev_tools.PROJECTS", {"myproject": Path("/fake/path")})
    mocker.patch.object(Path, "exists", return_value=True)
    
    result = git_status("myproject")
    assert "clean" in result
    mock_run.assert_called_once()

def test_git_status_modified(mocker):
    mock_run = mocker.patch("dev_tools.subprocess.run")
    mock_run.return_value.returncode = 0
    # Mock 2 modified files
    mock_run.return_value.stdout = " M file1.py\n M file2.py\n"
    
    mocker.patch.dict("dev_tools.PROJECTS", {"myproject": Path("/fake/path")})
    mocker.patch.object(Path, "exists", return_value=True)
    
    result = git_status("myproject")
    assert "2 modified files" in result

def test_git_status_denied(mocker):
    mock_run = mocker.patch("dev_tools.subprocess.run")
    mocker.patch.dict("dev_tools.PROJECTS", {})
    
    result = git_status("secretproject")
    assert "don't know the project" in result
    mock_run.assert_not_called()

def test_open_project_allowed(mocker):
    mock_popen = mocker.patch("dev_tools.subprocess.Popen")
    mocker.patch.dict("dev_tools.PROJECTS", {"myproject": Path("/fake/path")})
    mocker.patch.object(Path, "exists", return_value=True)
    
    result = open_project("myproject")
    assert "opening myproject in VS Code" in result
    mock_popen.assert_called_once()

def test_start_server_allowed(mocker):
    mock_popen = mocker.patch("dev_tools.subprocess.Popen")
    mocker.patch.dict("dev_tools.DEV_SERVERS", {
        "myproject": {
            "frontend": {"command": "npm run dev", "cwd": "/fake/path"}
        }
    })
    mocker.patch.object(Path, "exists", return_value=True)
    
    result = start_server("myproject", "frontend")
    assert "started the frontend server" in result
    mock_popen.assert_called_once()

def test_start_server_denied(mocker):
    mock_popen = mocker.patch("dev_tools.subprocess.Popen")
    mocker.patch.dict("dev_tools.DEV_SERVERS", {})
    
    result = start_server("myproject", "frontend")
    assert "don't have server configs" in result
    mock_popen.assert_not_called()

def test_stop_server_not_running(mocker):
    mocker.patch.dict("dev_tools.RUNNING_SERVERS", {}, clear=True)
    
    result = stop_server("myproject", "frontend")
    assert "not currently running" in result
