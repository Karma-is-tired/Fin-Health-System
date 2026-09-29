import pandas as pd
import sqlite3
 
# Read the CSV we just generated -- this stands in for "a user uploaded a file"
df = pd.read_csv("data/sample_transactions.csv")
 
# We haven't built the upload feature yet (that comes in a later week),
# so for now every row is tagged with a placeholder upload_id of 1
df["upload_id"] = 1
 
connection = sqlite3.connect("database/finance_tool.db")
 
# Append these rows into the transactions table we created in Session 1
df.to_sql("transactions", connection, if_exists="append", index=False)
 
connection.close()
 
print(f"Loaded {len(df)} rows into the transactions table.")
