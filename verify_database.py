import sqlite3
 
connection = sqlite3.connect("database/finance_tool.db")
cursor = connection.cursor()
 
# Ask SQLite for the names of every table it knows about
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
 
print("Tables in the database:")
for table in tables:
    print(" -", table[0])
 
connection.close()
