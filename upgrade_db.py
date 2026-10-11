"""Kept for convenience: runs the same safe setup the server runs on start-up.

The old version of this file dropped the users table, which would have wiped
every account. It no longer does that.
"""
import os

from db_setup import init_db

if __name__ == "__main__":
    init_db(os.environ.get("DB_PATH", "database/finance_tool.db"))
    print("Database is ready.")
