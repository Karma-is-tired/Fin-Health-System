import pandas as pd
import sqlite3
import os
 
# Sample invoices -- money customers owe this business. Deliberately spread
# across different ages so the aging module in Task 4 has something to show.
invoices = [
    {
        "customer": "Customer A",
        "amount": 850000,
        "due_date": "2026-04-30",
        "payment_date": "",
        "status": "overdue",
    },
    {
        "customer": "Customer B",
        "amount": 420000,
        "due_date": "2026-06-14",
        "payment_date": "",
        "status": "overdue",
    },
    {
        "customer": "Customer C",
        "amount": 90000,
        "due_date": "2026-06-28",
        "payment_date": "",
        "status": "outstanding",
    },
    {
        "customer": "Customer D",
        "amount": 300000,
        "due_date": "2026-05-20",
        "payment_date": "2026-05-18",
        "status": "paid",
    },
    {
        "customer": "Customer E",
        "amount": 610000,
        "due_date": "2026-03-28",
        "payment_date": "",
        "status": "overdue",
    },
    {
        "customer": "Customer B",
        "amount": 150000,
        "due_date": "2026-06-22",
        "payment_date": "",
        "status": "outstanding",
    },
    {
        "customer": "Customer A",
        "amount": 275000,
        "due_date": "2026-05-05",
        "payment_date": "2026-05-10",
        "status": "paid",
    },
    {
        "customer": "Customer C",
        "amount": 530000,
        "due_date": "2026-05-22",
        "payment_date": "",
        "status": "overdue",
    },
]
 
df = pd.DataFrame(invoices)
df["upload_id"] = 1
 
os.makedirs("data", exist_ok=True)
df.to_csv("data/sample_invoices.csv", index=False)
 
connection = sqlite3.connect("database/finance_tool.db")
df.to_sql("invoices", connection, if_exists="append", index=False)
connection.close()
 
print(f"Loaded {len(df)} invoices into the database.")
 
