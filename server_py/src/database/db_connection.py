import sqlite3
from sqlite3 import Connection, Cursor
from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("DATABASE_URL"))
print("SQLite Version:", sqlite3.sqlite_version)
conn = sqlite3.connect(os.getenv("DATABASE_URL", "./data/gupshup-database.db"))
# Create a cursor object
cursor = conn.cursor()
