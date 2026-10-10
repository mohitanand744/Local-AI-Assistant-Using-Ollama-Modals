import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from brain import parse_command

def test_parse_command_pure_json():
    text = '{"action": "chat", "text": "Hello"}'
    result = parse_command(text)
    assert result is not None
    assert result["action"] == "chat"
    assert result["text"] == "Hello"

def test_parse_command_markdown_json():
    text = '''```json
{
  "action": "open_app",
  "app": "vscode"
}
```'''
    result = parse_command(text)
    assert result is not None
    assert result["action"] == "open_app"
    assert result["app"] == "vscode"

def test_parse_command_hallucinated_text():
    text = '''Sure, I can help with that.
{
  "action": "list_tasks"
}
Let me know if you need anything else!'''
    result = parse_command(text)
    assert result is not None
    assert result["action"] == "list_tasks"

def test_parse_command_invalid_json():
    text = "I don't have any JSON here."
    result = parse_command(text)
    assert result is None
