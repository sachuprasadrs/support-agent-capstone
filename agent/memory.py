import sqlite3
import json
import os
from typing import Dict, List, Any

DB_PATH = "agent_memory.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
      CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        profile TEXT
      )
    """)

    c.execute("""
      CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT,
        events TEXT
      )
    """)

    c.execute("""
      CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        mem_type TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    """)

    conn.commit()
    conn.close()


def save_user(user_id: str, name: str, email: str, profile: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO users (user_id,name,email,profile) VALUES (?,?,?,?)",
        (user_id, name, email, json.dumps(profile))
    )
    conn.commit()
    conn.close()


def append_session_event(session_id: str, user_id: str, event: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT events FROM sessions WHERE session_id=?", (session_id,))
    row = c.fetchone()

    if row:
        events = json.loads(row[0])
        events.append(event)
        c.execute("UPDATE sessions SET events=? WHERE session_id=?", (json.dumps(events), session_id))
    else:
        events = [event]
        c.execute(
            "INSERT INTO sessions (session_id,user_id,events) VALUES (?,?,?)",
            (session_id, user_id, json.dumps(events))
        )

    conn.commit()
    conn.close()


def add_memory(user_id: str, mem_type: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "INSERT INTO memories (user_id,mem_type,content) VALUES (?,?,?)",
        (user_id, mem_type, content)
    )

    conn.commit()
    conn.close()


def retrieve_memories(user_id: str, keyword: str = None, limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if keyword:
        pattern = f"%{keyword.lower()}%"
        c.execute(
            "SELECT mem_type, content FROM memories WHERE user_id=? AND lower(content) LIKE ? ORDER BY created_at DESC LIMIT ?",
            (user_id, pattern, limit)
        )
    else:
        c.execute(
            "SELECT mem_type, content FROM memories WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )

    rows = c.fetchall()
    conn.close()

    return [{"mem_type": r[0], "content": r[1]} for r in rows]
