import sqlite3
import pandas as pd
 
connection = sqlite3.connect("database/finance_tool.db")
df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'paid'", connection)
connection.close()
 
df["due_date"] = pd.to_datetime(df["due_date"])
as_of_date = pd.Timestamp("2026-07-01")  # treat this as "today" for our sample data
 
df["days_overdue"] = (as_of_date - df["due_date"]).dt.days.clip(lower=0)
 
def risk_tier(days):
    if days >= 60:
        return "High"
    elif days >= 15:
        return "Medium"
    else:
        return "Low"
 
df["risk"] = df["days_overdue"].apply(risk_tier)
 
print("MODULE 3 -- RECEIVABLES & AGING")
print(df[["customer", "amount", "days_overdue", "risk"]].sort_values("days_overdue", ascending=False))
 
print(f"\nTotal outstanding: {df['amount'].sum():,.0f}")
print(f"Number of overdue invoices: {(df['days_overdue'] > 0).sum()}")
 
# Aging buckets, matching Section 08 of the guide
bins = [0, 30, 60, 90, float("inf")]
labels = ["0-30", "31-60", "61-90", "90+"]
df["bucket"] = pd.cut(df["days_overdue"], bins=bins, labels=labels, include_lowest=True)
print("\nAging schedule:")
print(df.groupby("bucket", observed=False)["amount"].sum())
