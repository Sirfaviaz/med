# Migration: add how_it_felt column to SmokingLog if not exists
from app import app
from models import db
from sqlalchemy import text

# SQLite table name for SQLAlchemy model SmokingLog is 'smoking_log'
TABLE_NAME = 'smoking_log'

with app.app_context():
    conn = db.engine.connect()

    # Ensure table exists
    table_exists = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"), {"t": TABLE_NAME}
    ).fetchone()

    if not table_exists:
        print(f"Table {TABLE_NAME} not found. Creating all tables...")
        db.create_all()
        table_exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"), {"t": TABLE_NAME}
        ).fetchone()
        if not table_exists:
            raise SystemExit(f"Fatal: table {TABLE_NAME} still not found after create_all().")

    # Check existing columns
    res = conn.execute(text(f"PRAGMA table_info({TABLE_NAME})"))
    cols = [row[1] for row in res]
    if 'how_it_felt' in cols:
        print("Column how_it_felt already exists; nothing to do.")
    else:
        conn.execute(text(f"ALTER TABLE {TABLE_NAME} ADD COLUMN how_it_felt VARCHAR(200)"))
        conn.commit()
        print("Added column how_it_felt to smoking_log")
