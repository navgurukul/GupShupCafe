import sqlite3

# Connect to the database
conn = sqlite3.connect('data/gupshup-database.db')
cursor = conn.cursor()

# Check if agents table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agents'")
tables = cursor.fetchall()
print("Tables:", tables)

# Check agents for the specific room
cursor.execute("SELECT * FROM agents WHERE room_id = '37423ccd79b548588825581e9a700c48'")
agents = cursor.fetchall()
print("Agents for room 37423ccd79b548588825581e9a700c48:", agents)

# Check all agents
cursor.execute("SELECT agent_id, room_id, agent_type FROM agents LIMIT 10")
all_agents = cursor.fetchall()
print("All agents (first 10):", all_agents)

conn.close()
