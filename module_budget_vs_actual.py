import sqlite3
import pandas as pd
 
connection = sqlite3.connect("database/finance_tool.db")
budget_df = pd.read_sql_query("SELECT * FROM budgets WHERE period = '2026-06'", connection)
actual_df = pd.read_sql_query("SELECT * FROM transactions WHERE type='expense'", connection)
connection.close()
 
actual_df["txn_date"] = pd.to_datetime(actual_df["txn_date"])
actual_df["period"] = actual_df["txn_date"].dt.to_period("M").astype(str)
june_actual = actual_df[actual_df["period"] == "2026-06"].groupby("category")["amount"].sum()
 
merged = budget_df.set_index("category")[["budgeted_amount"]].join(
    june_actual.rename("actual"), how="outer"
).fillna(0)
merged["variance"] = merged["actual"] - merged["budgeted_amount"]
merged["variance_pct"] = (merged["variance"] / merged["budgeted_amount"].replace(0, pd.NA) * 100).round(1)
 
print("MODULE 5 -- BUDGET VS ACTUAL (June 2026)")
print(merged)
 
MIN_FLAG_AMOUNT = 10000
flags = merged[(merged["variance_pct"].abs() > 15) & (merged["variance"].abs() > MIN_FLAG_AMOUNT)]
print("\nFlags:")
if len(flags) == 0:
    print("  None -- everything stayed within threshold.")
for category, row in flags.iterrows():
    direction = "above" if row["variance"] > 0 else "below"
    print(f"  {category}: {abs(row['variance_pct'])}% {direction} budget")
