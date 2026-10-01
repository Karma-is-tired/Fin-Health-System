import pandas as pd
import random
from datetime import date, timedelta

# Set a seed so the random numbers look realistic and consistent
random.seed(42)

records = []
current_date = date(2026, 7, 1) # Starts exactly where your Phase 1 data ended

expense_configs = [
    ("inventory", 50000, 250000, "Lagos Wholesale Ltd"),
    ("transportation", 5000, 25000, "Total Filling Station"),
    ("marketing", 10000, 50000, "Meta Ads"),
    ("utilities", 20000, 60000, "EKEDC"),
    ("salaries", 100000, 200000, "Staff")
]

for _ in range(100):
    # Advance the date by 0 to 2 days per transaction to spread them out
    current_date += timedelta(days=random.randint(0, 2))
    
    # 30% chance of a high-revenue sales day, 70% chance of a standard expense
    if random.random() < 0.3:
        records.append({
            "txn_date": current_date.strftime("%Y-%m-%d"),
            "amount": round(random.uniform(200000, 900000), 2),
            "type": "income",
            "category": "sales",
            "description": "Weekly sales revenue",
            "customer_vendor": "Walk-in customers",
            "account": "GTBank Current"
        })
    else:
        cat, min_amt, max_amt, vendor = random.choice(expense_configs)
        records.append({
            "txn_date": current_date.strftime("%Y-%m-%d"),
            "amount": round(random.uniform(min_amt, max_amt), 2),
            "type": "expense",
            "category": cat,
            "description": f"Standard {cat} expense",
            "customer_vendor": vendor,
            "account": "GTBank Current"
        })

# Convert to a DataFrame and save as a CSV spreadsheet
df = pd.DataFrame(records)
df.to_csv("large_test_data.csv", index=False)
print(f"Success! Generated 'large_test_data.csv' with {len(df)} rows ending on {current_date.strftime('%Y-%m-%d')}.")