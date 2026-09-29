import sqlite3
import pandas as pd
 
connection = sqlite3.connect("database/finance_tool.db")
df = pd.read_sql_query("SELECT * FROM transactions WHERE type = 'expense'", connection)
connection.close()
 
by_category = df.groupby("category")["amount"].sum().sort_values(ascending=False)
total_expenses = by_category.sum()
share = (by_category / total_expenses * 100).round(1)
 
report = pd.DataFrame({
    "total_spent": by_category,
    "share_of_expenses_pct": share,
})
 
print("MODULE 4 -- EXPENSE ANALYSIS")
print(report)
print(f"\nTotal expenses: {total_expenses:,.0f}")
