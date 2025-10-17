import sqlite3
from sqlite3 import Connection, Cursor
conn = sqlite3.connect('database/gupshup_database.db')
# Create a cursor object
cursor = conn.cursor()
