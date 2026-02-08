import sqlite3
from .config import DB_FILE

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
      uid TEXT PRIMARY KEY,
      email TEXT UNIQUE,
      name TEXT,
      verified INTEGER default 0,
      last_online INTEGER,
      sid TEXT
    );
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_users_sid ON users(sid);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_users_last_online ON users(last_online);")

    c.execute("""
    CREATE TABLE IF NOT EXISTS friend_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_uid TEXT NOT NULL,
        receiver_uid TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        timestamp INTEGER,
        UNIQUE(sender_uid, receiver_uid)
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_uid TEXT NOT NULL,
        friend_uid TEXT NOT NULL,
        since INTEGER,
        UNIQUE(user_uid, friend_uid)
    );
    """)

    conn.commit()
    conn.close()