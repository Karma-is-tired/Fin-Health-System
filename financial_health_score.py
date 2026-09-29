import sqlite3
import pandas as pd
 
connection = sqlite3.connect("database/finance_tool.db")
transactions = pd.read_sql_query("SELECT * FROM transactions", connection)
invoices = pd.read_sql_query("SELECT * FROM invoices", connection)
budgets = pd.read_sql_query("SELECT * FROM budgets", connection)
connection.close()
 
transactions["txn_date"] = pd.to_datetime(transactions["txn_date"])
transactions["month"] = transactions["txn_date"].dt.to_period("M")
 
# ---------- Profitability ----------
monthly = transactions.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
if "income" not in monthly.columns: monthly["income"] = 0
if "expense" not in monthly.columns: monthly["expense"] = 0
monthly["net_profit"] = monthly["income"] - monthly["expense"]
monthly["margin_pct"] = (monthly["net_profit"] / monthly["income"] * 100)
avg_margin = monthly["margin_pct"].mean()
profitability_score = max(0, min(100, 50 + avg_margin))
 
# ---------- Cash flow ----------
positive_months = (monthly["net_profit"] > 0).sum()
total_months = len(monthly)
cash_flow_score = (positive_months / total_months) * 100
 
# ---------- Receivables ----------
unpaid = invoices[invoices["status"] != "paid"].copy()
unpaid["due_date"] = pd.to_datetime(unpaid["due_date"])
as_of_date = pd.Timestamp("2026-07-01")
unpaid["days_overdue"] = (as_of_date - unpaid["due_date"]).dt.days.clip(lower=0)
total_outstanding = unpaid["amount"].sum()
total_overdue = unpaid[unpaid["days_overdue"] > 0]["amount"].sum()
receivables_score = 100 - (total_overdue / total_outstanding * 100) if total_outstanding > 0 else 100
 
# ---------- Budget performance + expense control ----------
expenses = transactions[transactions["type"] == "expense"].copy()
expenses["period"] = expenses["txn_date"].dt.to_period("M").astype(str)
budgets_by_cat = budgets.set_index("category")["budgeted_amount"]
june_actual = expenses[expenses["period"] == "2026-06"].groupby("category")["amount"].sum()
compare = pd.DataFrame({"budgeted": budgets_by_cat, "actual": june_actual}).fillna(0)
compare["variance_pct"] = (
    (compare["actual"] - compare["budgeted"]).abs() / compare["budgeted"].replace(0, pd.NA) * 100
)
avg_variance = compare["variance_pct"].mean()
budget_score = max(0, min(100, 100 - avg_variance))
 
breaches = (compare["variance_pct"] > 15).sum()
expense_control_score = max(0, 100 - (breaches * 20))
 
# ---------- Weighted overall score (weights from Section 12) ----------
WEIGHTS = {
    "profitability": 0.25,
    "cash_flow": 0.25,
    "expense_control": 0.15,
    "receivables": 0.20,
    "budget": 0.15,
}
 
scores = {
    "profitability": round(profitability_score, 1),
    "cash_flow": round(cash_flow_score, 1),
    "expense_control": round(expense_control_score, 1),
    "receivables": round(receivables_score, 1),
    "budget": round(budget_score, 1),
}
 
overall = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
 
def band(score):
    if score >= 71:
        return "Strong"
    if score >= 41:
        return "Moderate"
    return "Weak"
 
print("FINANCIAL HEALTH SCORE")
print("=" * 40)
for factor, score in scores.items():
    print(f"  {factor:18s}: {score:5.1f} / 100  (weight {int(WEIGHTS[factor]*100)}%)")
print("-" * 40)
print(f"  {'OVERALL':18s}: {overall:5.1f} / 100  -- {band(overall)}")
