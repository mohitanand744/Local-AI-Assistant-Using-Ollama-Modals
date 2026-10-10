import pytest
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from codebase_tools import (
    index_project,
    search_code,
    explain_codebase,
    code_index_status,
    _chunk_text,
    get_db_connection
)

@pytest.fixture
def mock_code_db(tmp_path, mocker):
    db_path = tmp_path / "test_code_index.db"
    mocker.patch("codebase_tools.INDEX_DB_PATH", db_path)
    # Re-init db since the global one in module load might be different
    import codebase_tools
    codebase_tools.init_index_db()
    return db_path

@pytest.fixture
def mock_dummy_repo(tmp_path):
    repo = tmp_path / "dummy_repo"
    repo.mkdir()
    
    # Valid file
    (repo / "main.py").write_text("def hello():\n    print('world')", encoding='utf-8')
    
    # Excluded dirs
    git_dir = repo / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\nbare=false")
    
    # Excluded files
    (repo / ".env").write_text("SECRET=12345")
    (repo / "secrets.json").write_text('{"token": "abcd"}')
    (repo / "app.exe").write_bytes(b"binarydata")
    
    # Nested valid file
    nested = repo / "src"
    nested.mkdir()
    (nested / "utils.js").write_text("console.log('utils');")
    
    return repo

def test_chunk_text():
    text = "line1\nline2\nline3\nline4\nline5"
    chunks = _chunk_text(text, max_lines=3, overlap=1)
    assert len(chunks) == 3
    assert chunks[0] == (1, 3, "line1\nline2\nline3")
    assert chunks[1] == (3, 5, "line3\nline4\nline5")
    assert chunks[2] == (5, 5, "line5")

def test_index_unconfigured_project():
    result = index_project("unknown")
    assert "configured yet" in result

def test_missing_model(mocker, mock_dummy_repo, mock_code_db):
    mocker.patch.dict("codebase_tools.PROJECTS", {"dummy": str(mock_dummy_repo)})
    mocker.patch("codebase_tools._check_embedding_model", return_value=False)
    
    result = index_project("dummy")
    assert "missing" in result
    assert "nomic-embed-text" in result

def test_index_success_and_exclusions(mocker, mock_dummy_repo, mock_code_db):
    mocker.patch.dict("codebase_tools.PROJECTS", {"dummy": str(mock_dummy_repo)})
    mocker.patch("codebase_tools._check_embedding_model", return_value=True)
    mocker.patch("codebase_tools._get_embedding", return_value=[0.1, 0.2, 0.3])
    
    result = index_project("dummy")
    assert "indexed" in result
    
    # Check DB
    conn = get_db_connection()
    files = conn.execute("SELECT filepath FROM files WHERE project = 'dummy'").fetchall()
    conn.close()
    
    paths = [f['filepath'] for f in files]
    assert len(paths) == 2
    assert "main.py" in paths
    assert "src/utils.js" in paths
    assert ".env" not in paths
    assert ".git/config" not in paths

def test_incremental_update(mocker, mock_dummy_repo, mock_code_db):
    mocker.patch.dict("codebase_tools.PROJECTS", {"dummy": str(mock_dummy_repo)})
    mocker.patch("codebase_tools._check_embedding_model", return_value=True)
    mocker.patch("codebase_tools._get_embedding", return_value=[0.1, 0.2, 0.3])
    
    # First index
    index_project("dummy")
    
    # Second index should be fast (0 files)
    result = index_project("dummy")
    assert "up to date" in result

def test_search_code_not_indexed(mocker, mock_dummy_repo, mock_code_db):
    mocker.patch.dict("codebase_tools.PROJECTS", {"dummy": str(mock_dummy_repo)})
    mocker.patch("codebase_tools._check_embedding_model", return_value=True)
    
    result = search_code("dummy", "hello")
    assert "hasn't been indexed" in result

def test_search_code_returns_results(mocker, mock_dummy_repo, mock_code_db):
    mocker.patch.dict("codebase_tools.PROJECTS", {"dummy": str(mock_dummy_repo)})
    mocker.patch("codebase_tools._check_embedding_model", return_value=True)
    
    # Dummy embedding mock that returns exactly same vector to force cosine similarity = 1.0
    mocker.patch("codebase_tools._get_embedding", return_value=[1.0, 0.0, 0.0])
    
    index_project("dummy")
    result = search_code("dummy", "query")
    
    assert "main.py" in result
    assert "Lines" in result

def test_explain_codebase(mocker, mock_dummy_repo, mock_code_db):
    mocker.patch.dict("codebase_tools.PROJECTS", {"dummy": str(mock_dummy_repo)})
    mocker.patch("codebase_tools._check_embedding_model", return_value=True)
    mocker.patch("codebase_tools._get_embedding", return_value=[1.0, 0.0, 0.0])
    
    # Mock the LLM generation
    mock_chat = mocker.patch("codebase_tools.ollama.chat")
    mock_chat.return_value = {"message": {"content": "The file main.py prints world."}}
    
    index_project("dummy")
    result = explain_codebase("dummy", "What does main do?")
    
    assert "main.py prints world" in result
    
    # Ensure the prompt passed to ollama contained the retrieved context
    call_args = mock_chat.call_args[1]["messages"][0]["content"]
    assert "main.py" in call_args
