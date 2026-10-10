import sqlite3
from pathlib import Path
from datetime import datetime
from config import DATA_DIR

DB_PATH = DATA_DIR / "assistant.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_task(title):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO tasks (title, created_at)
        VALUES (?, ?)
        """,
        (title, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()


def get_pending_tasks():
    conn = get_connection()

    tasks = conn.execute("""
        SELECT id, title
        FROM tasks
        WHERE completed = 0
        ORDER BY id ASC
    """).fetchall()

    conn.close()

    return tasks


def complete_task(task_id):
    conn = get_connection()

    conn.execute("""
        UPDATE tasks
        SET completed = 1,
            completed_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), task_id))

    conn.commit()
    conn.close()