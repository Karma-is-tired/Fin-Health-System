import pandas as pd
import sqlite3
import os
 
# A budget for June 2026 -- the most recent month in our sample data --
# set up to deliberately produce a couple of real variances to flag.
budgets = [
    {
        "business_id": 1,
        "category": "marketing",
        "period": "2026-06",
        "budgeted_amount": 30000,
    },
    {
        "business_id": 1,
        "category": "transportation",
        "period": "2026-06",
        "budgeted_amount": 25000,
    },
    {
        "business_id": 1,
        "category": "utilities",
        "period": "2026-06",
        "budgeted_amount": 40000,
    },
    {
        "business_id": 1,
        "category": "inventory",
        "period": "2026-06",
        "budgeted_amount": 200000,
    },
    {
        "business_id": 1,
        "category": "salaries",
        "period": "2026-06",
        "budgeted_amount": 160000,
    },
    {
        "business_id": 1,
        "category": "rent",
        "period": "2026-06",
        "budgeted_amount": 90000,
    },
]
 
df = pd.DataFrame(budgets)
 
os.makedirs("data", exist_ok=True)
df.to_csv("data/sample_budgets.csv", index=False)
 
connection = sqlite3.connect("database/finance_tool.db")
df.to_sql("budgets", connection, if_exists="append", index=False)
connection.close()
 
print(f"Loaded {len(df)} budget rows into the database.")

