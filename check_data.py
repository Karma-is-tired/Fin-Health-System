import sqlite3
 
connection = sqlite3.connect("database/finance_tool.db")
cursor = connection.cursor()
 
cursor.execute("SELECT COUNT(*) FROM transactions")
count = cursor.fetchone()[0]
print(f"Total rows in transactions table: {count}")
 
cursor.execute("SELECT txn_date, amount, type, category FROM transactions LIMIT 5")
rows = cursor.fetchall()
print("\nFirst 5 rows:")
for row in rows:
    print(" ", row)
 
connection.close()
