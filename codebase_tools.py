import os
import json
import sqlite3
import hashlib
from pathlib import Path
from config import DATA_DIR, PROJECTS
import ollama

# We configure an explicit embedding model for Ollama
# Nomic is lightweight, fully local, and optimized for embeddings.
EMBEDDING_MODEL = "nomic-embed-text"
INDEX_DB_PATH = DATA_DIR / "code_index.db"

# Exclusions
EXCLUDED_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", 
    "dist", "build", ".next", ".cache", "out"
}
EXCLUDED_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".png", ".jpg", ".jpeg", ".gif", 
    ".pdf", ".zip", ".tar", ".gz", ".mp3", ".mp4", ".db", ".sqlite", ".onnx", ".wav"
}

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".md", ".json", 
    ".txt", ".sh", ".bat", ".sql", ".java", ".c", ".cpp", ".h", ".cs"
}

def get_db_connection():
    conn = sqlite3.connect(INDEX_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_index_db():
    conn = get_db_connection()
    # We store the file hash to know if it needs re-indexing
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            filepath TEXT NOT NULL,
            mtime REAL NOT NULL,
            hash TEXT NOT NULL,
            UNIQUE(project, filepath)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding_json TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB on load
init_index_db()

def _check_embedding_model():
    """Verify Ollama has the embedding model installed."""
    try:
        models_response = ollama.list()
        models = [m.get("model", m.get("name", "")) for m in models_response.get("models", [])]
        for m in models:
            if m.startswith(EMBEDDING_MODEL):
                return True
        return False
    except Exception:
        return False

def _chunk_text(text, max_lines=40, overlap=10):
    lines = text.splitlines()
    chunks = []
    i = 0
    while i < len(lines):
        start_line = i
        end_line = min(i + max_lines, len(lines))
        chunk_content = "\n".join(lines[start_line:end_line])
        chunks.append((start_line + 1, end_line, chunk_content))
        i += (max_lines - overlap)
    return chunks

def _get_embedding(text):
    res = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
    return res["embedding"]

def _cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = sum(a * a for a in vec1) ** 0.5
    mag2 = sum(b * b for b in vec2) ** 0.5
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

def index_project(project_name):
    project_name = project_name.lower().strip()
    
    if project_name not in PROJECTS:
        return f"I don't have that project's local folder configured yet."
        
    project_path = Path(PROJECTS[project_name])
    if not project_path.exists():
        return f"The folder for {project_name} does not exist."
        
    if not _check_embedding_model():
        return (f"I cannot index the code because the required embedding model '{EMBEDDING_MODEL}' is missing. "
                f"Please open your terminal and run 'ollama pull {EMBEDDING_MODEL}'.")
                
    conn = get_db_connection()
    files_indexed = 0
    
    try:
        for root, dirs, files in os.walk(project_path):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]
            
            for file in files:
                # Security exclusions
                if file.startswith('.') or file.lower() in [".env", "secrets.json"]:
                    continue
                    
                ext = Path(file).suffix.lower()
                if ext not in ALLOWED_EXTENSIONS or ext in EXCLUDED_EXTENSIONS:
                    continue
                    
                file_path = Path(root) / file
                rel_path = file_path.relative_to(project_path).as_posix()
                
                # Check if file changed
                mtime = file_path.stat().st_mtime
                row = conn.execute("SELECT mtime, id FROM files WHERE project = ? AND filepath = ?", 
                                   (project_name, rel_path)).fetchone()
                                   
                if row and row['mtime'] >= mtime:
                    continue # File unchanged
                    
                # Read content
                try:
                    content = file_path.read_text(encoding='utf-8')
                except Exception:
                    continue
                    
                # Hash content
                file_hash = hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()
                
                # Update DB
                if row:
                    file_id = row['id']
                    conn.execute("DELETE FROM chunks WHERE file_id = ?", (file_id,))
                    conn.execute("UPDATE files SET mtime = ?, hash = ? WHERE id = ?", (mtime, file_hash, file_id))
                else:
                    cursor = conn.execute("INSERT INTO files (project, filepath, mtime, hash) VALUES (?, ?, ?, ?)", 
                                          (project_name, rel_path, mtime, file_hash))
                    file_id = cursor.lastrowid
                    
                # Chunk and embed
                chunks = _chunk_text(content)
                for start_line, end_line, chunk_content in chunks:
                    try:
                        emb = _get_embedding(f"File: {rel_path}\nLine {start_line}-{end_line}\n{chunk_content}")
                        emb_json = json.dumps(emb)
                        conn.execute("INSERT INTO chunks (file_id, start_line, end_line, content, embedding_json) VALUES (?, ?, ?, ?, ?)",
                                     (file_id, start_line, end_line, chunk_content, emb_json))
                    except Exception as e:
                        # Log locally, don't crash
                        pass
                        
                files_indexed += 1
                conn.commit()
                
    except Exception as e:
        conn.close()
        return f"I encountered an error while indexing: {e}"
        
    conn.close()
    
    if files_indexed > 0:
        return f"I've indexed {files_indexed} new or changed files for {project_name}. I'm ready to answer questions about its code."
    else:
        return f"Your index for {project_name} is fully up to date."

def search_code(project_name, query, top_k=3):
    project_name = project_name.lower().strip()
    
    if project_name not in PROJECTS:
        return f"I don't have that project's local folder configured yet."
        
    if not _check_embedding_model():
        return f"The embedding model '{EMBEDDING_MODEL}' is missing. Please run 'ollama pull {EMBEDDING_MODEL}'."
        
    conn = get_db_connection()
    file_count = conn.execute("SELECT COUNT(*) as c FROM files WHERE project = ?", (project_name,)).fetchone()['c']
    if file_count == 0:
        conn.close()
        return f"That project hasn't been indexed yet. Let me index its source files first."
        
    try:
        query_emb = _get_embedding(query)
    except Exception as e:
        conn.close()
        return f"I couldn't search because I failed to generate an embedding: {e}"
        
    # Retrieve all chunks for the project (in a massive project we would use a vector DB, but SQLite + Python is fine for small/medium local repos)
    chunks = conn.execute("""
        SELECT f.filepath, c.start_line, c.end_line, c.content, c.embedding_json
        FROM chunks c
        JOIN files f ON c.file_id = f.id
        WHERE f.project = ?
    """, (project_name,)).fetchall()
    conn.close()
    
    results = []
    for c in chunks:
        emb = json.loads(c['embedding_json'])
        sim = _cosine_similarity(query_emb, emb)
        results.append((sim, c))
        
    # Sort and take top_k
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Filter out poor matches
    best_results = [c for sim, c in results[:top_k] if sim > 0.3]
    
    if not best_results:
        return "I couldn't find any relevant code in the index for that query."
        
    response = f"I found the following relevant code in {project_name}:\n\n"
    for c in best_results:
        response += f"--- {c['filepath']} (Lines {c['start_line']}-{c['end_line']}) ---\n"
        response += f"{c['content']}\n\n"
        
    return response.strip()

def explain_codebase(project_name, query):
    # This combines search and generation
    project_name = project_name.lower().strip()
    
    if project_name not in PROJECTS:
        return f"I don't have that project's local folder configured yet."
        
    # Get context
    context = search_code(project_name, query, top_k=4)
    if "hasn't been indexed yet" in context or "is missing" in context:
        return context
        
    if "couldn't find any relevant code" in context:
        return f"I couldn't find any relevant code in {project_name} to answer your question."
        
    prompt = f"""
You are a friendly coding mentor. Based ONLY on the following retrieved code snippets from the local project, answer the user's question. 
When answering, ALWAYS cite the relevant file paths and line ranges provided in the snippets.
If the retrieved code does not contain the answer, admit that you don't have enough evidence in the current index. Do not invent endpoints, filenames, or logic.
Keep your response concise but conversational.

Retrieved Context:
{context}

User Question: {query}
"""
    
    try:
        from config import OLLAMA_MODEL
        res = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
        return res["message"]["content"].strip()
    except Exception as e:
        return f"I found the code, but encountered an error explaining it: {e}"

def code_index_status(project_name):
    project_name = project_name.lower().strip()
    if project_name not in PROJECTS:
        return f"I don't have that project's local folder configured yet."
        
    conn = get_db_connection()
    files = conn.execute("SELECT COUNT(*) as c FROM files WHERE project = ?", (project_name,)).fetchone()['c']
    chunks = conn.execute("""
        SELECT COUNT(*) as c FROM chunks c 
        JOIN files f ON c.file_id = f.id 
        WHERE f.project = ?
    """, (project_name,)).fetchone()['c']
    conn.close()
    
    if files == 0:
        return f"That project hasn't been indexed yet."
        
    return f"The index for {project_name} contains {files} files and {chunks} chunks of code."
