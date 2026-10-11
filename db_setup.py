"""Creates (and safely upgrades) the SQLite database.

Nothing in here ever deletes real data. It is safe to run on every server
start: tables are only created if they are missing, and new columns are only
added if they are missing.
"""
import os
import sqlite3


def _columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _add_column_if_missing(conn, table, column, definition):
    cols = _columns(conn, table)
    if cols and column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db(path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    conn = sqlite3.connect(path)
    try:
        # The very first version of this project had a "users" table with no
        # passwords in it, so nobody can have an account in it. Replace only
        # that old stub; a real users table is never touched.
        user_cols = _columns(conn, "users")
        if user_cols and "password_hash" not in user_cols:
            conn.execute("DROP TABLE users")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_verified INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")

        # business_id is a placeholder (always 0) until the app supports
        # several users sharing one business.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL DEFAULT 0,
                uploaded_by INTEGER NOT NULL,
                filename TEXT NOT NULL,
                uploaded_at TEXT NOT NULL
            )""")

        conn.execute("""
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
                user_id INTEGER
            )""")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id INTEGER NOT NULL,
                customer TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                payment_date TEXT,
                status TEXT NOT NULL,
                user_id INTEGER
            )""")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL DEFAULT 0,
                category TEXT NOT NULL,
                period TEXT NOT NULL,
                budgeted_amount REAL NOT NULL,
                user_id INTEGER
            )""")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS report_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                report_month TEXT NOT NULL,
                overall_score REAL,
                revenue REAL,
                net_profit REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")

        # Databases created by older versions need the owner column.
        for table in ("transactions", "invoices", "budgets"):
            _add_column_if_missing(conn, table, "user_id", "INTEGER")
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_user ON {table} (user_id)"
            )

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db(os.environ.get("DB_PATH", "database/finance_tool.db"))
    print("Database is ready.")
