# Financial Health & Cash-Flow System
 
A web tool that turns a small business's transaction history into a
financial health report, a cash-flow forecast, and risk alerts.
 
## Running it locally
 
Backend (from the project root):
    python -m pip install -r requirements.txt
    python -m uvicorn main:app --reload
    -> runs at http://127.0.0.1:8000
 
Frontend (in a second terminal):
    cd frontend
    npm install
    npm run dev
    -> runs at http://localhost:5173
 
## What's here
 
- create_database.py       - builds the SQLite schema (8 tables)
- extend_sample_data.py    - loads 6 months of sample transactions
- load_sample_invoices.py  - loads sample receivables
- load_sample_budgets.py   - loads a sample June 2026 budget
- module_*.py              - the six standalone analytics modules
- financial_health_score.py - the weighted scoring engine
- main.py                  - the FastAPI backend (protected by an API key)
- frontend/                - the React dashboard
- test_main.py             - pytest coverage for the API
 
## Notes
 
- The API key in main.py (API_KEY = "dev-secret-key-change-later") is a
  development placeholder. Before sharing this publicly, move it into an
  environment variable instead of leaving it in the source code.
- Sample data covers January-June 2026 for a fictional retail business.
