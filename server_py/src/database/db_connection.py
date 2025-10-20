import sqlite3
from sqlite3 import Connection, Cursor
from dotenv import load_dotenv
import os

load_dotenv()

db_path = os.getenv("DATABASE_URL", "./data/gupshup-database.db")
print(db_path)
print("SQLite Version:", sqlite3.sqlite_version)

# Use a connection timeout and allow usage across threads for FastAPI workers
conn: Connection = sqlite3.connect(db_path, timeout=5.0, check_same_thread=False)
cursor: Cursor = conn.cursor()

# Improve concurrency to reduce 'database is locked'
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")
cursor.execute("PRAGMA busy_timeout=5000;")
conn.commit()
