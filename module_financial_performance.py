import sqlite3
import pandas as pd
 
connection = sqlite3.connect("database/finance_tool.db")
df = pd.read_sql_query("SELECT * FROM transactions", connection)
connection.close()
 
# Make sure txn_date is treated as an actual date, not plain text
df["txn_date"] = pd.to_datetime(df["txn_date"])
 
# Add a "month" column so we can group everything by it
df["month"] = df["txn_date"].dt.to_period("M")
 
# Income and expense totals, side by side, per month
monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
 
# Guard in case a month has no income or no expense rows at all
if "income" not in monthly.columns:
    monthly["income"] = 0
if "expense" not in monthly.columns:
    monthly["expense"] = 0
 
monthly["net_profit"] = monthly["income"] - monthly["expense"]
monthly["margin_pct"] = (monthly["net_profit"] / monthly["income"] * 100).round(1)
monthly["revenue_growth_pct"] = (monthly["income"].pct_change() * 100).round(1)
 
print("MODULE 1 -- FINANCIAL PERFORMANCE")
print(monthly[["income", "expense", "net_profit", "margin_pct", "revenue_growth_pct"]])
