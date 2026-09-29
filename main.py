 
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
 
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# A simple shared-secret check -- every request to a protected endpoint
# must include this exact value in an X-API-Key header, or it's rejected.
# This is a development-level protection, not production-grade security
# (a real system would issue a different key per user, not one shared
# value) -- but it demonstrates the core idea from Section 19 correctly.
API_KEY = "dev-secret-key-change-later"
 
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
 
 
def get_health_score():
    connection = sqlite3.connect("database/finance_tool.db")
    transactions = pd.read_sql_query("SELECT * FROM transactions", connection)
    invoices = pd.read_sql_query("SELECT * FROM invoices", connection)
    budgets = pd.read_sql_query("SELECT * FROM budgets", connection)
    connection.close()
 
    transactions["txn_date"] = pd.to_datetime(transactions["txn_date"])
    transactions["month"] = transactions["txn_date"].dt.to_period("M")
    monthly = transactions.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    if "income" not in monthly.columns: monthly["income"] = 0
    if "expense" not in monthly.columns: monthly["expense"] = 0
    monthly["net_profit"] = monthly["income"] - monthly["expense"]
    monthly["margin_pct"] = (monthly["net_profit"] / monthly["income"] * 100)
 
    mean_margin = monthly["margin_pct"].mean()
    avg_margin = float(mean_margin) if pd.notna(mean_margin) else 0.0
    profitability_score = max(0.0, min(100.0, 50.0 + avg_margin))
 
    positive_months = int((monthly["net_profit"] > 0).sum())
    cash_flow_score = float((positive_months / len(monthly)) * 100) if len(monthly) > 0 else 0.0
 
    unpaid = invoices[invoices["status"] != "paid"].copy()
    unpaid["due_date"] = pd.to_datetime(unpaid["due_date"])
    as_of_date = pd.Timestamp("2026-07-01")
    unpaid["days_overdue"] = (as_of_date - unpaid["due_date"]).dt.days.clip(lower=0)
 
    total_outstanding = float(unpaid["amount"].sum())
    total_overdue = float(unpaid[unpaid["days_overdue"] > 0]["amount"].sum())
    receivables_score = 100.0 - (total_overdue / total_outstanding * 100.0) if total_outstanding > 0 else 100.0
 
    expenses = transactions[transactions["type"] == "expense"].copy()
    expenses["period"] = expenses["txn_date"].dt.to_period("M").astype(str)
    budgets_by_cat = budgets.set_index("category")["budgeted_amount"]
    june_actual = expenses[expenses["period"] == "2026-06"].groupby("category")["amount"].sum()
    compare = pd.DataFrame({"budgeted": budgets_by_cat, "actual": june_actual}).fillna(0)
    compare["variance_pct"] = (
        (compare["actual"] - compare["budgeted"]).abs() / compare["budgeted"].replace(0, pd.NA) * 100
    )
 
    mean_variance = compare["variance_pct"].mean()
    mean_variance = float(mean_variance) if pd.notna(mean_variance) else 0.0
    budget_score = max(0.0, min(100.0, 100.0 - mean_variance))
 
    breaches = int((compare["variance_pct"] > 15).sum())
    expense_control_score = max(0.0, 100.0 - (breaches * 20.0))
 
    weights = {"profitability": 0.25, "cash_flow": 0.25, "expense_control": 0.15,
               "receivables": 0.20, "budget": 0.15}
    scores = {
        "profitability": round(profitability_score, 1),
        "cash_flow": round(cash_flow_score, 1),
        "expense_control": round(expense_control_score, 1),
        "receivables": round(receivables_score, 1),
        "budget": round(budget_score, 1),
    }
    overall = round(sum(scores[k] * weights[k] for k in weights), 1)
    return {"scores": scores, "overall": overall}
 
 
def get_financial_summary():
    connection = sqlite3.connect("database/finance_tool.db")
    transactions = pd.read_sql_query("SELECT * FROM transactions", connection)
    invoices = pd.read_sql_query("SELECT * FROM invoices", connection)
    connection.close()
 
    transactions["txn_date"] = pd.to_datetime(transactions["txn_date"])
    transactions["month"] = transactions["txn_date"].dt.to_period("M")
    monthly = transactions.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    if "income" not in monthly.columns: monthly["income"] = 0
    if "expense" not in monthly.columns: monthly["expense"] = 0
    monthly["net_profit"] = monthly["income"] - monthly["expense"]
 
    latest = monthly.iloc[-1]
    latest_month = str(monthly.index[-1])
    unpaid = invoices[invoices["status"] == "overdue"]
    overdue_total = float(unpaid["amount"].sum())
 
    return {
        "latest_month": latest_month,
        "revenue": round(float(latest["income"]), 0),
        "expenses": round(float(latest["expense"]), 0),
        "net_profit": round(float(latest["net_profit"]), 0),
        "overdue_receivables": round(overdue_total, 0),
    }
 
 
@app.get("/")
def home():
    return {"message": "Financial Health System API is running"}
 
 
@app.get("/health-score")
def health_score(_: None = Depends(verify_api_key)):
    return get_health_score()
 
 
@app.get("/financial-summary")
def financial_summary(_: None = Depends(verify_api_key)):
    return get_financial_summary()
