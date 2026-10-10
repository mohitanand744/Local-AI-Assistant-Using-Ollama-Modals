import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from voice import clean_for_speech

def test_clean_for_speech_removes_code_blocks():
    text = "Here is an example: ```python\nprint('hello')\n``` What do you think?"
    result = clean_for_speech(text)
    assert result == "Here is an example: What do you think?"

def test_clean_for_speech_removes_bold_and_italic():
    text = "This is **bold** and this is *italic*."
    result = clean_for_speech(text)
    assert result == "This is bold and this is italic."

def test_clean_for_speech_removes_numbered_lists():
    text = "I can do these:\n1. Manage tasks\n2. Open apps"
    result = clean_for_speech(text)
    # The newlines might be stripped or replaced by spaces depending on implementation
    assert "1." not in result
    assert "2." not in result
    assert "Manage tasks" in result
    assert "Open apps" in result

def test_clean_for_speech_removes_bullet_points():
    text = "Here is a list:\n- First item\n- Second item"
    result = clean_for_speech(text)
    assert "-" not in result
    assert "First item" in result
    assert "Second item" in result

def test_clean_for_speech_adds_trailing_punctuation():
    text = "Hello Coding Beast"
    result = clean_for_speech(text)
    assert result == "Hello Coding Beast."
    
    text_with_punct = "Hello Coding Beast!"
    result = clean_for_speech(text_with_punct)
    assert result == "Hello Coding Beast!"
