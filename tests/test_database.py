import pytest
import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import database

@pytest.fixture
def mock_db(tmp_path, monkeypatch):
    """
    Fixture that redirects the database to a temporary file.
    This prevents testing from polluting the real assistant.db.
    """
    temp_db = tmp_path / "test_assistant.db"
    
    # Monkeypatch the module's DB_PATH
    monkeypatch.setattr(database, "DB_PATH", temp_db)
    
    # Initialize the tables in the temp db
    database.init_db()
    
    return temp_db

def test_add_and_get_tasks(mock_db):
    # Verify it starts empty
    tasks = database.get_pending_tasks()
    assert len(tasks) == 0
    
    # Add a task
    database.add_task("Test task 1")
    database.add_task("Test task 2")
    
    # Verify tasks are returned
    tasks = database.get_pending_tasks()
    assert len(tasks) == 2
    
    assert tasks[0][1] == "Test task 1"
    assert tasks[1][1] == "Test task 2"

def test_complete_task(mock_db):
    database.add_task("Task to complete")
    tasks = database.get_pending_tasks()
    assert len(tasks) == 1
    
    task_id = tasks[0][0]
    
    # Complete the task
    database.complete_task(task_id)
    
    # Verify it's no longer pending
    pending = database.get_pending_tasks()
    assert len(pending) == 0
