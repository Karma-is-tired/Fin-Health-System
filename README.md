# FinHealth: Financial Health & Cash-Flow Analysis

A web app for small businesses. Sign up with an email and password, upload your
transactions, and get a financial health score, a cash-flow chart and Word reports.

## How accounts work
Enter an email and password and press **Sign up**. Next time, sign in with the same two.
There is no OTP or email code. Each account only ever sees its own data.

## Run it locally
Backend (from the project root):

    pip install -r requirements.txt
    python -m uvicorn main:app --reload

Frontend:

    cd frontend
    npm install
    npm run dev

Run the tests: `python -m pytest -q`

## Settings (environment variables)
See `.env.example`. On Render add them under **Environment**:

| Name | What it does |
| --- | --- |
| `SECRET_KEY` | Long random text that signs login tokens. **Required in production.** |
| `ALLOWED_ORIGINS` | Website addresses allowed to call the API, comma separated. |
| `CURRENCY_SYMBOL` | Symbol used in Word reports (default ₦). |
| `DB_PATH` | Where the SQLite file lives (default `database/finance_tool.db`). |

On Vercel you can set `VITE_API_BASE` to point the frontend at a different backend.

## Upload formats
Download a ready-made template from the **Upload data** page.

- **Transactions:** date, amount, type (income or expense), category, description.
  Without a type column, write expenses as negative amounts.
- **Invoices:** customer, amount, due_date, status (paid or unpaid).
- **Budgets:** category, period (YYYY-MM), budgeted_amount.

## The five scores
Profitability, cash flow, expense control, receivables and budget adherence. A score
only appears when there is data for it, and the overall score is re-weighted across
the scores that exist.

## Important: database storage
The database is a single SQLite file and is **not stored in Git**. On Render's free
tier the disk is wiped on every redeploy and restart, which deletes all accounts and
uploads. For real use, attach a Render persistent disk and set `DB_PATH` to a path on
it, or move to a hosted database such as Postgres.
