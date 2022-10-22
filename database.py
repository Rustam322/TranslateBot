import sqlite3
db = sqlite3.connect('bot.db')
cursor = db.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS translate(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT,
    src TEXT,
    dest TEXT,
    original_text TEXT,
    translated_text TEXT
)
''')
db.commit()
db.close()