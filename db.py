import sqlite3

conn = sqlite3.connect('studb.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    full_name TEXT,
    university TEXT,
    faculty TEXT,
    group_name TEXT,
    role TEXT
)
''')
conn.commit()

def add_user(telegram_id, full_name, university, faculty, group_name, role):
    cursor.execute("INSERT INTO users (telegram_id, full_name, university, faculty, group_name, role) VALUES (?, ?, ?, ?, ?, ?)", 
                   (telegram_id, full_name, university, faculty, group_name, role))
    conn.commit()