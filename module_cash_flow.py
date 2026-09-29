import sqlite3
import pandas as pd
 
connection = sqlite3.connect("database/finance_tool.db")
df = pd.read_sql_query("SELECT * FROM transactions", connection)
connection.close()
 
df["txn_date"] = pd.to_datetime(df["txn_date"])
df["month"] = df["txn_date"].dt.to_period("M")
 
# Every income row is a cash inflow, every expense row is a cash outflow
df["flow"] = df.apply(lambda row: row["amount"] if row["type"] == "income" else -row["amount"], axis=1)
 
monthly_net = df.groupby("month")["flow"].sum()
running_balance = monthly_net.cumsum()
 
print("MODULE 2 -- CASH-FLOW ANALYSIS")
for month, net in monthly_net.items():
    flag = "  <-- NEGATIVE MONTH" if net < 0 else ""
    print(f"{month}: net flow = {net:,.0f}{flag}")
 
print("\nRunning balance by end of each month:")
print(running_balance)
 
negative_months = monthly_net[monthly_net < 0]
if len(negative_months) > 0:
    print(f"\nWARNING: {len(negative_months)} month(s) had negative cash flow: {list(negative_months.index.astype(str))}")
else:
    print("\nNo negative-cash-flow months detected.")
