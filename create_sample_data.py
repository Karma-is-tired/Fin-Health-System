import pandas as pd
import os
 
# A small, realistic set of transactions for a fictional retail business.
# This stands in for a real uploaded file until we build the upload
# feature itself later in the build.
data = [
    {
        "txn_date": "2026-01-05",
        "amount": 450000,
        "type": "income",
        "category": "sales",
        "description": "Weekly sales - week 1",
        "customer_vendor": "Walk-in customers",
        "account": "GTBank Current",
    },
    {
        "txn_date": "2026-01-07",
        "amount": 85000,
        "type": "expense",
        "category": "inventory",
        "description": "Stock restock",
        "customer_vendor": "Lagos Wholesale Ltd",
        "account": "GTBank Current",
    },
    {
        "txn_date": "2026-01-10",
        "amount": 12000,
        "type": "expense",
        "category": "transportation",
        "description": "Fuel for delivery van",
        "customer_vendor": "Total Filling Station",
        "account": "Cash",
    },
    {
        "txn_date": "2026-01-15",
        "amount": 520000,
        "type": "income",
        "category": "sales",
        "description": "Weekly sales - week 2",
        "customer_vendor": "Walk-in customers",
        "account": "GTBank Current",
    },
    {
        "txn_date": "2026-01-18",
        "amount": 45000,
        "type": "expense",
        "category": "utilities",
        "description": "Electricity bill",
        "customer_vendor": "EKEDC",
        "account": "GTBank Current",
    },
    {
        "txn_date": "2026-01-20",
        "amount": 150000,
        "type": "expense",
        "category": "salaries",
        "description": "Staff wages - mid month",
        "customer_vendor": "Staff",
        "account": "GTBank Current",
    },
    {
        "txn_date": "2026-02-02",
        "amount": 610000,
        "type": "income",
        "category": "sales",
        "description": "Weekly sales - week 1",
        "customer_vendor": "Walk-in customers",
        "account": "GTBank Current",
    },
    {
        "txn_date": "2026-02-05",
        "amount": 95000,
        "type": "expense",
        "category": "inventory",
        "description": "Stock restock",
        "customer_vendor": "Lagos Wholesale Ltd",
        "account": "GTBank Current",
    },
    {
        "txn_date": "2026-02-09",
        "amount": 18000,
        "type": "expense",
        "category": "transportation",
        "description": "Fuel for delivery van",
        "customer_vendor": "Total Filling Station",
        "account": "Cash",
    },
    {
        "txn_date": "2026-02-14",
        "amount": 480000,
        "type": "income",
        "category": "sales",
        "description": "Weekly sales - week 2",
        "customer_vendor": "Walk-in customers",
        "account": "GTBank Current",
    },
]
 
df = pd.DataFrame(data)
 
os.makedirs("data", exist_ok=True)
df.to_csv("data/sample_transactions.csv", index=False)
 
print(f"Sample file created with {len(df)} rows: data/sample_transactions.csv")
