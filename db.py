import sqlite3

def get_db():
    conn = sqlite3.connect("quotes.db")
    conn.row_factory = sqlite3.Row  # Для удобства чтения данных
    return conn

def init_db():
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS phrases (
        id TEXT PRIMARY KEY,
        text TEXT,
        author_id TEXT,
        amount REAL,
        created_at TEXT,
        likes_count INTEGER DEFAULT 0,
        used_in_top INTEGER DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS winners (
        id TEXT PRIMARY KEY,
        phrase_id TEXT,
        won_at TEXT,
        amount_at_win REAL
    )
    ''')

    conn.commit()
    conn.close()
