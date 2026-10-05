import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Conversations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        mode TEXT DEFAULT 'general',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        mode TEXT DEFAULT 'general',
        model TEXT,
        latency_ms REAL DEFAULT 0,
        metadata TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
    )
    """)
    
    # Feedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedbacks (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        message_id TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        mode TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
    )
    """)
    
    # Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        size INTEGER NOT NULL,
        char_count INTEGER NOT NULL,
        content TEXT NOT NULL,
        preview TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

# Conversation Operations
def create_conversation(title: str = "New Conversation", mode: str = "general") -> Dict[str, Any]:
    conv_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (id, title, mode, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (conv_id, title, mode, now, now)
    )
    conn.commit()
    conn.close()
    return {"id": conv_id, "title": title, "mode": mode, "created_at": now, "updated_at": now}

def get_conversations() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_conversation_title(conv_id: str, title: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?", (title, now, conv_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def update_conversation_mode(conv_id: str, mode: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("UPDATE conversations SET mode = ?, updated_at = ? WHERE id = ?", (mode, now, conv_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def delete_conversation(conv_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedbacks WHERE conversation_id = ?", (conv_id,))
    cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def clear_all_conversations() -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedbacks")
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM conversations")
    conn.commit()
    conn.close()
    return True

# Message Operations
def add_message(conversation_id: str, role: str, content: str, mode: str = "general",
                model: Optional[str] = None, latency_ms: float = 0, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    meta_json = json.dumps(metadata or {})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Ensure conversation exists
    cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
    if not cursor.fetchone():
        # Create conversation with snippet of user message
        title = content[:30] + "..." if len(content) > 30 else content
        cursor.execute(
            "INSERT INTO conversations (id, title, mode, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (conversation_id, title or "New Conversation", mode, now, now)
        )
    else:
        cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
        
    cursor.execute(
        """INSERT INTO messages (id, conversation_id, role, content, mode, model, latency_ms, metadata, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (msg_id, conversation_id, role, content, mode, model, latency_ms, meta_json, now)
    )
    conn.commit()
    conn.close()
    return {
        "id": msg_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "mode": mode,
        "model": model,
        "latency_ms": latency_ms,
        "metadata": metadata or {},
        "created_at": now
    }

def get_messages(conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT ?",
        (conversation_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["metadata"] = json.loads(d.get("metadata") or "{}")
        except Exception:
            d["metadata"] = {}
        result.append(d)
    return result

# Feedback Operations
def save_feedback(conversation_id: str, message_id: str, rating: int, comment: Optional[str] = None, mode: Optional[str] = None) -> Dict[str, Any]:
    feedback_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    
    # Replace existing feedback for this message if exists
    cursor.execute("DELETE FROM feedbacks WHERE message_id = ?", (message_id,))
    cursor.execute(
        "INSERT INTO feedbacks (id, conversation_id, message_id, rating, comment, mode, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (feedback_id, conversation_id, message_id, rating, comment, mode, now)
    )
    conn.commit()
    conn.close()
    return {"id": feedback_id, "message_id": message_id, "rating": rating, "comment": comment, "created_at": now}

def get_feedback_stats() -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as positive, SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as negative FROM feedbacks")
    row = cursor.fetchone()
    conn.close()
    return {
        "total": row["total"] if row else 0,
        "positive": row["positive"] if row and row["positive"] else 0,
        "negative": row["negative"] if row and row["negative"] else 0
    }

# Document Operations
def save_document(doc_id: str, filename: str, file_type: str, size: int, content: str, preview: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    char_count = len(content)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (id, filename, file_type, size, char_count, content, preview, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (doc_id, filename, file_type, size, char_count, content, preview, now)
    )
    conn.commit()
    conn.close()
    return {
        "id": doc_id,
        "filename": filename,
        "file_type": file_type,
        "size": size,
        "char_count": char_count,
        "preview": preview,
        "created_at": now
    }

def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_documents() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, file_type, size, char_count, preview, created_at FROM documents ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_document(doc_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected
