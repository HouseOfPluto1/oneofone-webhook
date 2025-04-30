# db.py

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "db.sqlite3"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS access (
                user_id TEXT PRIMARY KEY,
                access_type TEXT,
                expires TEXT
            )
        """)
    # ✅ DEV-ONLY: Grant testing access to your Telegram ID
    grant_access("5690326807", "lifetime")

def grant_access(user_id, access_type):
    expiry = "9999-12-31" if access_type == "lifetime" else (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("REPLACE INTO access (user_id, access_type, expires) VALUES (?, ?, ?)",
                     (user_id, access_type, expiry))

def has_access(user_id):
    status = get_access_status(user_id)
    if not status:
        return False
    return datetime.strptime(status['expires'], "%Y-%m-%d") >= datetime.now()

def get_access_status(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT access_type, expires FROM access WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        return {"type": row[0], "expires": row[1]} if row else None
