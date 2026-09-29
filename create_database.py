import sqlite3
import os
 
# Make sure a "database" folder exists to hold our .db file
os.makedirs("database", exist_ok=True)
 
# Connect to (and create, if it doesn't exist yet) the database file
connection = sqlite3.connect("database/finance_tool.db")
cursor = connection.cursor()
 
# Table 1: businesses -- one row per business using the tool
cursor.execute("""
CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'NGN',
    sector TEXT,
    created_at TEXT NOT NULL
)
""")
 
# Table 2: users -- the people who can log in, tied to one business
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    email TEXT NOT NULL,
    FOREIGN KEY (business_id) REFERENCES businesses (id)
)
""")
 
# Table 3: uploads -- one row per file a user uploads
cursor.execute("""
CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    uploaded_by INTEGER NOT NULL,
    filename TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    FOREIGN KEY (business_id) REFERENCES businesses (id),
    FOREIGN KEY (uploaded_by) REFERENCES users (id)
)
""")
 
# Table 4: transactions -- the actual income/expense rows from an upload
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL,
    txn_date TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    category TEXT,
    description TEXT,
    customer_vendor TEXT,
    account TEXT,
    FOREIGN KEY (upload_id) REFERENCES uploads (id)
)
""")
 
# Table 5: invoices -- money owed to or by the business
cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL,
    customer TEXT NOT NULL,
    amount REAL NOT NULL,
    due_date TEXT NOT NULL,
    payment_date TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (upload_id) REFERENCES uploads (id)
)
""")
 
# Table 6: budgets -- the budget-vs-actual targets per category/period
cursor.execute("""
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    period TEXT NOT NULL,
    budgeted_amount REAL NOT NULL,
    FOREIGN KEY (business_id) REFERENCES businesses (id)
)
""")
 
# Table 7: analysis_jobs -- tracks each "Run Analysis" click
cursor.execute("""
CREATE TABLE IF NOT EXISTS analysis_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    requested_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (upload_id) REFERENCES uploads (id)
)
""")
 
# Table 8: analysis_results -- what each module produced for a given job
cursor.execute("""
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    module_name TEXT NOT NULL,
    result_json TEXT NOT NULL,
    score REAL,
    FOREIGN KEY (job_id) REFERENCES analysis_jobs (id)
)
""")
 
# Save everything to disk and close the connection
connection.commit()
connection.close()
 
print("Database created successfully with all 8 tables.")
 
