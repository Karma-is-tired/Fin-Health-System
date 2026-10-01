from fastapi import FastAPI, Header, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from docx import Document
from docx.shared import Pt, Inches
import sqlite3
import pandas as pd
import io
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fin-health-system.vercel.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

API_KEY = "dev-secret-key-change-later"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

# ==========================================
# 1. ADAPTIVE DATA NORMALIZATION
# ==========================================
def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Intelligently maps messy user columns to our exact database schema."""
    df.columns = df.columns.str.lower().str.strip()
    
    # Common column aliases users might upload
    column_mapping = {
        "date": "txn_date",
        "transaction date": "txn_date",
        "value": "amount",
        "price": "amount",
        "total": "amount",
        "transaction type": "type",
        "cat": "category",
        "desc": "description",
        "memo": "description",
        "vendor": "customer_vendor",
        "customer": "customer_vendor"
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Ensure mandatory columns exist; if not, create safe fallbacks
    if "txn_date" not in df.columns:
        df["txn_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    if "amount" not in df.columns:
        df["amount"] = 0.0
    if "type" not in df.columns:
        # Guess based on amount if missing (positive = income, negative = expense)
        df["type"] = df["amount"].apply(lambda x: "income" if float(x) > 0 else "expense")
    
    df["amount"] = df["amount"].abs() # Keep amounts positive in DB, use 'type' to determine flow
    
    # Filter only the columns our SQL database expects
    expected_cols = ["txn_date", "amount", "type", "category", "description", "customer_vendor", "account", "upload_id"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = "Uncategorized" if col in ["category", "description", "customer_vendor", "account"] else None
            
    return df[expected_cols]

# ==========================================
# 2. DYNAMIC SCORING ENGINE
# ==========================================
def get_health_score():
    connection = sqlite3.connect("database/finance_tool.db")
    transactions = pd.read_sql_query("SELECT * FROM transactions", connection)
    invoices = pd.read_sql_query("SELECT * FROM invoices", connection)
    budgets = pd.read_sql_query("SELECT * FROM budgets", connection)
    connection.close()

    scores = {}
    weights = {}

    # Core Metric 1: Profitability (Needs Transactions)
    if not transactions.empty:
        transactions["txn_date"] = pd.to_datetime(transactions["txn_date"])
        transactions["month"] = transactions["txn_date"].dt.to_period("M")
        monthly = transactions.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
        
        if "income" not in monthly.columns: monthly["income"] = 0
        if "expense" not in monthly.columns: monthly["expense"] = 0
        
        monthly["net_profit"] = monthly["income"] - monthly["expense"]
        monthly["margin_pct"] = (monthly["net_profit"] / monthly["income"].replace(0, pd.NA)) * 100
        
        avg_margin = float(monthly["margin_pct"].mean()) if pd.notna(monthly["margin_pct"].mean()) else 0.0
        scores["profitability"] = round(max(0.0, min(100.0, 50.0 + avg_margin)), 1)
        weights["profitability"] = 0.30
        
        positive_months = int((monthly["net_profit"] > 0).sum())
        scores["cash_flow"] = round(float((positive_months / len(monthly)) * 100) if len(monthly) > 0 else 0.0, 1)
        weights["cash_flow"] = 0.30
    else:
        scores["profitability"] = 0
        scores["cash_flow"] = 0

    # Core Metric 2: Receivables (Only if invoices exist)
    if not invoices.empty:
        unpaid = invoices[invoices["status"] != "paid"].copy()
        unpaid["due_date"] = pd.to_datetime(unpaid["due_date"])
        unpaid["days_overdue"] = (pd.Timestamp.now() - unpaid["due_date"]).dt.days.clip(lower=0)
        total_out = float(unpaid["amount"].sum())
        total_over = float(unpaid[unpaid["days_overdue"] > 0]["amount"].sum())
        
        scores["receivables"] = round(100.0 - (total_over / total_out * 100.0) if total_out > 0 else 100.0, 1)
        weights["receivables"] = 0.20

    # Core Metric 3: Budgets (Only if budgets exist)
    if not budgets.empty and not transactions.empty:
        scores["budget"] = 85.0 # Simplified adaptive budget score fallback
        weights["budget"] = 0.20

    # DYNAMIC WEIGHT REDISTRIBUTION (The magic trick to prevent crashes on missing data)
    total_weight = sum(weights.values())
    if total_weight == 0:
        return {"scores": {"No Data": 0}, "overall": 0}
        
    normalized_weights = {k: v / total_weight for k, v in weights.items()}
    overall = round(sum(scores[k] * normalized_weights[k] for k in scores), 1)

    return {"scores": scores, "overall": overall}


def get_financial_summary():
    connection = sqlite3.connect("database/finance_tool.db")
    transactions = pd.read_sql_query("SELECT * FROM transactions", connection)
    invoices = pd.read_sql_query("SELECT * FROM invoices", connection)
    connection.close()

    if transactions.empty:
        return {"latest_month": "N/A", "revenue": 0, "expenses": 0, "net_profit": 0, "overdue_receivables": 0}

    transactions["txn_date"] = pd.to_datetime(transactions["txn_date"])
    transactions["month"] = transactions["txn_date"].dt.to_period("M")
    monthly = transactions.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    
    if "income" not in monthly.columns: monthly["income"] = 0
    if "expense" not in monthly.columns: monthly["expense"] = 0
    monthly["net_profit"] = monthly["income"] - monthly["expense"]

    latest = monthly.iloc[-1]
    
    overdue_total = 0.0
    if not invoices.empty:
        overdue_total = float(invoices[invoices["status"] == "overdue"]["amount"].sum())

    return {
        "latest_month": str(monthly.index[-1]),
        "revenue": round(float(latest["income"]), 0),
        "expenses": round(float(latest["expense"]), 0),
        "net_profit": round(float(latest["net_profit"]), 0),
        "overdue_receivables": round(overdue_total, 0),
    }

# ==========================================
# 3. ENDPOINTS
# ==========================================
@app.get("/")
def home():
    return {"message": "Financial Health System API is running"}

@app.get("/health-score")
def health_score(_: None = Depends(verify_api_key)):
    return get_health_score()

@app.get("/financial-summary")
def financial_summary(_: None = Depends(verify_api_key)):
    return get_financial_summary()

@app.post("/upload-transactions")
async def upload_transactions(file: UploadFile = File(...), _: None = Depends(verify_api_key)):
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported")
        
        df["upload_id"] = 3
        df = normalize_dataframe(df) # Run the adaptive cleaner
        
        connection = sqlite3.connect("database/finance_tool.db")
        df.to_sql("transactions", connection, if_exists="append", index=False)
        connection.close()
        
        return {"message": f"Processed {len(df)} transactions cleanly."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 4. THE AUTOMATED ANALYST (DOCX GENERATOR)
# ==========================================
@app.get("/download-report")
def download_report(_: None = Depends(verify_api_key)):
    scores_data = get_health_score()
    summary = get_financial_summary()
    
    # Create the Word Document
    doc = Document()
    
    # Title
    title = doc.add_heading('Executive Financial Health Report', 0)
    
    # Summary Section
    doc.add_heading('1. Executive Summary', level=1)
    doc.add_paragraph(f"Latest Analysis Period: {summary['latest_month']}")
    
    overall_score = scores_data['overall']
    health_status = "Strong" if overall_score > 75 else "Moderate" if overall_score > 50 else "Critical"
    
    p = doc.add_paragraph(f"The business currently has an overall Financial Health Score of ")
    p.add_run(f"{overall_score}/100").bold = True
    p.add_run(f", indicating a ")
    p.add_run(f"{health_status}").bold = True
    p.add_run(" financial position.")

    # Key Metrics Table
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Shading Accent 1'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Metric'
    hdr_cells[1].text = 'Value'
    
    row_cells = table.add_row().cells
    row_cells[0].text = "Revenue"
    row_cells[1].text = f"${summary['revenue']:,.2f}"
    
    row_cells = table.add_row().cells
    row_cells[0].text = "Net Profit"
    row_cells[1].text = f"${summary['net_profit']:,.2f}"
    
    row_cells = table.add_row().cells
    row_cells[0].text = "Overdue Receivables"
    row_cells[1].text = f"${summary['overdue_receivables']:,.2f}"

    # Automated Advice Section
    doc.add_heading('2. Automated Strategic Advice', level=1)
    
    # Profitability Advice
    if scores_data['scores'].get('profitability', 0) < 50:
        doc.add_paragraph("⚠️ PROFITABILITY: Your profit margins are dangerously thin or negative. Immediate action is required to cut non-essential expenses and re-evaluate pricing structures.")
    else:
        doc.add_paragraph("✅ PROFITABILITY: Profit margins are healthy and sustainable. Consider reinvesting excess capital into growth channels.")

    # Cash Flow Advice
    if scores_data['scores'].get('cash_flow', 0) < 60:
        doc.add_paragraph("⚠️ CASH FLOW: The business is experiencing multiple months of negative cash flow. You are burning through your cash buffer. Prioritize immediate revenue collection and halt large capital expenditures.")
    
    # Receivables Advice
    if summary['overdue_receivables'] > (summary['revenue'] * 0.2):
        doc.add_paragraph("⚠️ ACCOUNTS RECEIVABLE: Overdue invoices exceed 20% of your monthly revenue. Implement stricter payment terms (e.g., Net-15) and follow up aggressively on outstanding invoices to unlock trapped liquidity.")

    # Save to a temporary file and return it
    fd, path = tempfile.mkstemp(suffix=".docx")
    try:
        with os.fdopen(fd, 'wb') as f:
            doc.save(f)
        return FileResponse(path, filename=f"Financial_Report_{summary['latest_month']}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))