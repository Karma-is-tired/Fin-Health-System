from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from docx import Document
import jwt
import sqlite3
import pandas as pd
import io
import tempfile
import os
import hashlib
from datetime import datetime, timedelta

# ==========================================
# 0. SERVER INITIALIZATION & FOLDER SAFETY
# ==========================================
os.makedirs("database", exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fin-health-system.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

@app.exception_handler(Exception)
async def global_crash_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"CRITICAL BACKEND CRASH: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": "*"}
    )

# ==========================================
# 1. SECURITY & AUTH SETUP
# ==========================================
SECRET_KEY = "your-super-secret-production-key" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserCreate(BaseModel):
    email: str
    password: str

def get_db():
    conn = sqlite3.connect("database/finance_tool.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def hash_password(password: str) -> str:
    # Bulletproof hashing that never crashes regardless of length or characters
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ==========================================
# 2. AUTHENTICATION ENDPOINTS (NO OTP, NO BCRYPT)
# ==========================================
@app.post("/signup")
def signup(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        existing = db.execute("SELECT * FROM users WHERE email = ?", (user.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        secure_hash = hash_password(user.password)
        
        # Instantly mark user as verified
        db.execute(
            "INSERT INTO users (email, password_hash, is_verified) VALUES (?, ?, 1)",
            (user.email, secure_hash)
        )
        db.commit()
        
        return {"message": "Account created successfully! You can now log in."}
    
    except sqlite3.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database Crash: {str(e)}. Did you run /run-db-upgrade?")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Crash: {str(e)}")

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE email = ?", (form_data.username,)).fetchone()
    
    if not user or hash_password(form_data.password) != user["password_hash"]:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = jwt.encode(
        {"sub": user["email"], "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# 3. ADAPTIVE DATA NORMALIZATION
# ==========================================
def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower().str.strip()
    column_mapping = {
        "date": "txn_date", "transaction date": "txn_date", "value": "amount",
        "price": "amount", "total": "amount", "transaction type": "type",
        "cat": "category", "desc": "description", "memo": "description",
        "vendor": "customer_vendor", "customer": "customer_vendor"
    }
    df.rename(columns=column_mapping, inplace=True)
    
    if "txn_date" not in df.columns: df["txn_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    if "amount" not in df.columns: df["amount"] = 0.0
    if "type" not in df.columns:
        df["type"] = df["amount"].apply(lambda x: "income" if float(x) > 0 else "expense")
    
    df["amount"] = df["amount"].abs()
    expected_cols = ["txn_date", "amount", "type", "category", "description", "customer_vendor", "account", "upload_id"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = "Uncategorized" if col in ["category", "description", "customer_vendor", "account"] else None
            
    return df[expected_cols]

# ==========================================
# 4. CORE ANALYTICS ENDPOINTS
# ==========================================
@app.get("/health-score")
def health_score(current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    transactions = pd.read_sql_query("SELECT * FROM transactions", db)
    invoices = pd.read_sql_query("SELECT * FROM invoices", db)
    
    scores = {}
    weights = {}

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
        weights["profitability"] = 0.35
        
        positive_months = int((monthly["net_profit"] > 0).sum())
        scores["cash_flow"] = round(float((positive_months / len(monthly)) * 100) if len(monthly) > 0 else 0.0, 1)
        weights["cash_flow"] = 0.35
    else:
        scores["profitability"] = 0
        scores["cash_flow"] = 0

    if not invoices.empty:
        unpaid = invoices[invoices["status"] != "paid"].copy()
        unpaid["due_date"] = pd.to_datetime(unpaid["due_date"])
        unpaid["days_overdue"] = (pd.Timestamp.now() - unpaid["due_date"]).dt.days.clip(lower=0)
        total_out = float(unpaid["amount"].sum())
        total_over = float(unpaid[unpaid["days_overdue"] > 0]["amount"].sum())
        scores["receivables"] = round(100.0 - (total_over / total_out * 100.0) if total_out > 0 else 100.0, 1)
        weights["receivables"] = 0.30

    total_weight = sum(weights.values())
    if total_weight == 0: return {"scores": {"No Data": 0}, "overall": 0}
        
    normalized_weights = {k: v / total_weight for k, v in weights.items()}
    overall = round(sum(scores[k] * normalized_weights[k] for k in scores), 1)

    return {"scores": scores, "overall": overall}

@app.get("/financial-summary")
def financial_summary(current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    transactions = pd.read_sql_query("SELECT * FROM transactions", db)
    if transactions.empty:
        return {"latest_month": "N/A", "revenue": 0, "expenses": 0, "net_profit": 0, "overdue_receivables": 0}

    transactions["txn_date"] = pd.to_datetime(transactions["txn_date"])
    transactions["month"] = transactions["txn_date"].dt.to_period("M")
    monthly = transactions.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    
    if "income" not in monthly.columns: monthly["income"] = 0
    if "expense" not in monthly.columns: monthly["expense"] = 0
    monthly["net_profit"] = monthly["income"] - monthly["expense"]

    latest = monthly.iloc[-1]
    
    invoices = pd.read_sql_query("SELECT * FROM invoices", db)
    overdue_total = float(invoices[invoices["status"] == "overdue"]["amount"].sum()) if not invoices.empty else 0.0

    return {
        "latest_month": str(monthly.index[-1]),
        "revenue": round(float(latest["income"]), 0),
        "expenses": round(float(latest["expense"]), 0),
        "net_profit": round(float(latest["net_profit"]), 0),
        "overdue_receivables": round(overdue_total, 0),
    }

@app.post("/upload-transactions")
async def upload_transactions(file: UploadFile = File(...), current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'): df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.xlsx'): df = pd.read_excel(io.BytesIO(contents))
        else: raise HTTPException(status_code=400, detail="Only CSV/Excel supported")
        
        df["upload_id"] = 3
        df = normalize_dataframe(df)
        df.to_sql("transactions", db, if_exists="append", index=False)
        db.commit()
        return {"message": f"Processed {len(df)} transactions cleanly."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 5. HISTORY & REPORT GENERATION
# ==========================================
def generate_docx(month, overall, revenue, profit):
    doc = Document()
    doc.add_heading('Executive Financial Health Report', 0)
    doc.add_heading('1. Executive Summary', level=1)
    doc.add_paragraph(f"Analysis Period: {month}")
    
    status = "Strong" if overall > 75 else "Moderate" if overall > 50 else "Critical"
    p = doc.add_paragraph(f"Overall Financial Health Score: ")
    p.add_run(f"{overall}/100").bold = True
    p.add_run(f" ({status})")

    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Shading Accent 1'
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text = 'Metric', 'Value'
    
    r1 = table.add_row().cells
    r1[0].text, r1[1].text = "Revenue", f"${revenue:,.2f}"
    r2 = table.add_row().cells
    r2[0].text, r2[1].text = "Net Profit", f"${profit:,.2f}"

    doc.add_heading('2. Automated Strategic Advice', level=1)
    if profit < (revenue * 0.1):
        doc.add_paragraph("⚠️ PROFITABILITY: Margins are tight. Immediate action is required to cut non-essential expenses.")
    else:
        doc.add_paragraph("✅ PROFITABILITY: Margins are healthy. Consider reinvesting excess capital.")

    fd, path = tempfile.mkstemp(suffix=".docx")
    with os.fdopen(fd, 'wb') as f:
        doc.save(f)
    return path

@app.get("/download-report")
def download_report(current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    scores = health_score(current_user, db)
    summary = financial_summary(current_user, db)
    
    db.execute(
        "INSERT INTO report_history (user_id, report_month, overall_score, revenue, net_profit) VALUES (?, ?, ?, ?, ?)",
        (current_user["id"], summary["latest_month"], scores["overall"], summary["revenue"], summary["net_profit"])
    )
    db.commit()

    path = generate_docx(summary["latest_month"], scores["overall"], summary["revenue"], summary["net_profit"])
    return FileResponse(path, filename=f"FinHealth_{summary['latest_month']}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.get("/history")
def get_history(current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT id, report_month, overall_score, revenue, created_at FROM report_history WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],)).fetchall()
    return [dict(row) for row in rows]

@app.get("/download-past-report/{report_id}")
def download_past_report(report_id: int, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    report = db.execute("SELECT * FROM report_history WHERE id = ? AND user_id = ?", (report_id, current_user["id"])).fetchone()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    path = generate_docx(report["report_month"], report["overall_score"], report["revenue"], report["net_profit"])
    return FileResponse(path, filename=f"FinHealth_Archive_{report['report_month']}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.get("/run-db-upgrade")
def run_db_upgrade():
    import upgrade_db
    os.makedirs("database", exist_ok=True) 
    upgrade_db.upgrade_database()
    return {"message": "Success: Render database has been upgraded!"}