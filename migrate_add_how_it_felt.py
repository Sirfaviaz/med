# Migration: add how_it_felt column to SmokingLog if not exists
from app import app
from models import db
from sqlalchemy import text

# Works for SQLite
CHECK_SQL = "PRAGMA table_info(SmokingLog)"
ADD_SQL = "ALTER TABLE SmokingLog ADD COLUMN how_it_felt VARCHAR(200)"

with app.app_context():
    conn = db.engine.connect()
    res = conn.execute(text(CHECK_SQL))
    cols = [row[1] for row in res]
    if 'how_it_felt' not in cols:
        conn.execute(text(ADD_SQL))
        conn.commit()
        print("Added column how_it_felt to SmokingLog")
    else:
        print("Column how_it_felt already exists; nothing to do.")
