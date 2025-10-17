import sqlite3
from sqlite3 import Connection, Cursor
conn = sqlite3.connect('gupshup.db')
# Create a cursor object
cursor = conn.cursor()

# cursor.execute('''CREATE TABLE IF NOT EXISTS "rooms" (
# 	"room_id"	TEXT NOT NULL,
# 	"room_name"	TEXT NOT NULL,
# 	"room_topic"	TEXT NOT NULL,
#     "particaipants" INTEGER NOT NULL,
# 	PRIMARY KEY("room_id")
# )''')

# cursor.execute('''CREATE TABLE IF NOT EXISTS "users" (
# 	"user_id"	TEXT NOT NULL UNIQUE,
# 	"name"	TEXT NOT NULL,
#     "anonymous_name" TEXT,
# 	"email"	TEXT UNIQUE,
# 	"password"	TEXT NOT NULL,
# 	"category"	TEXT,
# 	PRIMARY KEY("id")
# )''')