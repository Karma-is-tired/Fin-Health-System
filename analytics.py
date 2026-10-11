"""All the number-crunching: reading uploaded files, scoring, summaries.

Every function takes the logged-in user's id, so one user can never see
another user's rows.
"""
import random
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

TABLES = ("transactions", "invoices", "budgets")

WEIGHTS = {
    "profitability": 0.25,
    "cash_flow": 0.25,
    "expense_control": 0.15,
    "receivables": 0.20,
    "budget": 0.15,
}

DEMO_FILENAME = "Sample data (demo)"


def band(score):
    if score >= 71:
        return "Strong"
    if score >= 41:
        return "Moderate"
    return "Weak"


def _clamp(value):
    return round(float(max(0.0, min(100.0, value))), 1)


# ---------------------------------------------------------------------------
# Reading uploaded files
# ---------------------------------------------------------------------------
def _clean_names(df, aliases):
    df = df.copy()
    cleaned = [
        str(c).strip().lower().replace("_", " ").replace("-", " ") for c in df.columns
    ]
    cleaned = [aliases.get(c, c.replace(" ", "_")) for c in cleaned]
    df.columns = cleaned
    # If two columns ended up with the same name, keep the first.
    return df.loc[:, ~pd.Index(df.columns).duplicated()]


def _to_number(series):
    text = series.astype(str).str.replace(r"[^\d.\-]", "", regex=True)
    return pd.to_numeric(text, errors="coerce")


def _to_dates(series):
    """Understands 2026-01-31 (year first) and 31/01/2026 (day first)."""
    parsed = pd.to_datetime(series, errors="coerce", format="ISO8601")
    leftover = parsed.isna() & series.notna()
    if leftover.any():
        other = pd.to_datetime(series[leftover], errors="coerce", format="mixed", dayfirst=True)
        parsed = parsed.where(~leftover, other)
    return parsed


def _text(df, column, default=""):
    if column not in df.columns:
        return pd.Series(default, index=df.index)
    values = df[column].fillna("").astype(str).str.strip()
    return values.mask(values == "", default)


def _require(df, columns, kind):
    missing = [c for c in columns if c not in df.columns]
    if missing:
        names = ", ".join(missing)
        raise ValueError(
            f"Your {kind} file is missing: {names}. "
            "Use 'Download template' on this page to see the columns we expect."
        )


TXN_ALIASES = {
    "date": "txn_date", "transaction date": "txn_date", "txn date": "txn_date",
    "value": "amount", "price": "amount", "total": "amount",
    "transaction amount": "amount", "transaction type": "type",
    "cat": "category", "desc": "description", "memo": "description",
    "details": "description", "narration": "description",
    "vendor": "customer_vendor", "customer": "customer_vendor",
    "payee": "customer_vendor",
}
INCOME_WORDS = {"income", "credit", "revenue", "sale", "sales", "deposit", "inflow", "cr"}
EXPENSE_WORDS = {"expense", "debit", "cost", "payment", "withdrawal", "outflow", "dr", "purchase"}


def normalize_transactions(raw):
    df = _clean_names(raw, TXN_ALIASES)
    _require(df, ["txn_date", "amount"], "transactions")

    amounts = _to_number(df["amount"])
    dates = _to_dates(df["txn_date"])

    if "type" in df.columns:
        words = df["type"].fillna("").astype(str).str.strip().str.lower()
        types = words.map(
            lambda w: "income" if w in INCOME_WORDS else "expense" if w in EXPENSE_WORDS else None
        )
        guessed = pd.Series(np.where(amounts > 0, "income", "expense"), index=df.index)
        types = types.fillna(guessed)
    else:
        if not (amounts < 0).any():
            raise ValueError(
                "We can't tell which rows are income and which are expenses. "
                "Add a 'type' column (income or expense), or write expenses as negative amounts."
            )
        types = pd.Series(np.where(amounts > 0, "income", "expense"), index=df.index)

    keep = amounts.notna() & dates.notna() & (amounts != 0)
    if not keep.any():
        raise ValueError("No usable rows found. Check that your dates and amounts are filled in.")

    out = pd.DataFrame({
        "txn_date": dates[keep].dt.strftime("%Y-%m-%d"),
        "amount": amounts[keep].abs().round(2),
        "type": types[keep],
        "category": _text(df, "category", "Uncategorized")[keep],
        "description": _text(df, "description")[keep],
        "customer_vendor": _text(df, "customer_vendor")[keep],
        "account": _text(df, "account")[keep],
    })
    return out.reset_index(drop=True), int((~keep).sum())


INV_ALIASES = {
    "client": "customer", "customer name": "customer",
    "due date": "due_date", "due": "due_date",
    "invoice amount": "amount", "total": "amount", "balance": "amount",
    "paid date": "payment_date", "payment date": "payment_date",
}
PAID_WORDS = {"paid", "settled", "complete", "completed"}


def normalize_invoices(raw):
    df = _clean_names(raw, INV_ALIASES)
    _require(df, ["customer", "amount", "due_date"], "invoices")

    amounts = _to_number(df["amount"])
    due = _to_dates(df["due_date"])
    keep = amounts.notna() & due.notna() & (amounts > 0)
    if not keep.any():
        raise ValueError("No usable rows found. Check customers, amounts and due dates.")

    paid_on = _to_dates(df["payment_date"]) if "payment_date" in df.columns else pd.Series(pd.NaT, index=df.index)
    if "status" in df.columns:
        words = df["status"].fillna("").astype(str).str.strip().str.lower()
        status = np.where(words.isin(PAID_WORDS), "paid", "unpaid")
    else:
        status = np.where(paid_on.notna(), "paid", "unpaid")

    out = pd.DataFrame({
        "customer": _text(df, "customer", "Unknown")[keep],
        "amount": amounts[keep].round(2),
        "due_date": due[keep].dt.strftime("%Y-%m-%d"),
        "payment_date": paid_on[keep].dt.strftime("%Y-%m-%d"),
        "status": pd.Series(status, index=df.index)[keep],
    })
    out["payment_date"] = out["payment_date"].where(out["payment_date"].notna(), None)
    return out.reset_index(drop=True), int((~keep).sum())


BUDGET_ALIASES = {
    "budget": "budgeted_amount", "amount": "budgeted_amount",
    "budget amount": "budgeted_amount", "month": "period", "date": "period",
}


def normalize_budgets(raw):
    df = _clean_names(raw, BUDGET_ALIASES)
    _require(df, ["category", "period", "budgeted_amount"], "budget")

    amounts = _to_number(df["budgeted_amount"])
    periods = _to_dates(df["period"])
    keep = amounts.notna() & periods.notna() & (amounts >= 0)
    if not keep.any():
        raise ValueError("No usable rows found. Check categories, months and amounts.")

    out = pd.DataFrame({
        "category": _text(df, "category", "Uncategorized")[keep],
        "period": periods[keep].dt.strftime("%Y-%m"),
        "budgeted_amount": amounts[keep].round(2),
    })
    return out.reset_index(drop=True), int((~keep).sum())


NORMALIZERS = {
    "transactions": normalize_transactions,
    "invoices": normalize_invoices,
    "budgets": normalize_budgets,
}


def save_upload(db, user_id, kind, filename, df):
    """Stores a cleaned DataFrame, tagged with the owner's id."""
    now = datetime.now().isoformat(timespec="seconds")
    cur = db.execute(
        "INSERT INTO uploads (business_id, uploaded_by, filename, uploaded_at) VALUES (0, ?, ?, ?)",
        (user_id, filename, now),
    )
    upload_id = cur.lastrowid

    df = df.copy()
    df["user_id"] = user_id
    if kind in ("transactions", "invoices"):
        df["upload_id"] = upload_id
    else:  # budgets: a new upload replaces the same months
        for period in df["period"].unique():
            db.execute("DELETE FROM budgets WHERE user_id = ? AND period = ?", (user_id, period))
        df["business_id"] = 0

    df.to_sql(kind, db, if_exists="append", index=False)
    db.commit()
    return len(df)


# ---------------------------------------------------------------------------
# Loading + monthly maths
# ---------------------------------------------------------------------------
def load_frame(db, table, user_id):
    if table not in TABLES:
        raise ValueError("unknown table")
    return pd.read_sql_query(f"SELECT * FROM {table} WHERE user_id = ?", db, params=(user_id,))


def _prepare_transactions(tx):
    tx = tx.copy()
    tx["txn_date"] = pd.to_datetime(tx["txn_date"], errors="coerce")
    tx = tx.dropna(subset=["txn_date"])
    tx["month"] = tx["txn_date"].dt.to_period("M")
    return tx


def monthly_table(tx):
    columns = ["income", "expense", "net_profit"]
    if tx.empty:
        return pd.DataFrame(columns=columns)
    tx = _prepare_transactions(tx)
    if tx.empty:
        return pd.DataFrame(columns=columns)
    table = tx.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    for column in ("income", "expense"):
        if column not in table.columns:
            table[column] = 0.0
    table["net_profit"] = table["income"] - table["expense"]
    return table.sort_index()[columns]


# ---------------------------------------------------------------------------
# Scores
# ---------------------------------------------------------------------------
def _expense_control(tx):
    """Starts at 100 and loses 20 for every category whose spending in the
    latest month ran more than 15% above its own earlier monthly average."""
    expenses = _prepare_transactions(tx)
    expenses = expenses[expenses["type"] == "expense"]
    if expenses.empty:
        return None
    by_category = expenses.groupby(["category", "month"])["amount"].sum().unstack(fill_value=0)
    if by_category.shape[1] < 2:
        return None  # needs at least two months of history
    latest = by_category.columns.max()
    earlier_average = by_category.drop(columns=latest).mean(axis=1)
    breaches = int(((by_category[latest] > earlier_average * 1.15) & (earlier_average > 0)).sum())
    return _clamp(100 - breaches * 20)


def _overdue_amount(inv, today):
    if inv.empty:
        return 0.0
    unpaid = inv[inv["status"] != "paid"].copy()
    unpaid["due_date"] = pd.to_datetime(unpaid["due_date"], errors="coerce")
    return float(unpaid[unpaid["due_date"] < today]["amount"].sum())


def _receivables(inv, today):
    if inv.empty:
        return None
    outstanding = float(inv[inv["status"] != "paid"]["amount"].sum())
    if outstanding <= 0:
        return 100.0
    return _clamp(100 - _overdue_amount(inv, today) / outstanding * 100)


def _budget(tx, budgets):
    if tx.empty or budgets.empty:
        return None
    prepared = _prepare_transactions(tx)
    if prepared.empty:
        return None
    latest = str(prepared["month"].max())
    planned = budgets[budgets["period"] == latest]
    if planned.empty:
        return None
    planned = planned.assign(key=planned["category"].str.strip().str.lower())
    planned = planned.groupby("key")["budgeted_amount"].sum()

    spent = prepared[(prepared["type"] == "expense") & (prepared["month"].astype(str) == latest)]
    spent = spent.assign(key=spent["category"].str.strip().str.lower())
    actual = spent.groupby("key")["amount"].sum().reindex(planned.index).fillna(0)

    variance = (actual - planned).abs() / planned.replace(0, np.nan) * 100
    average = variance.mean()
    if pd.isna(average):
        return None
    return _clamp(100 - average)


def compute_scores(db, user_id, today=None):
    today = today or pd.Timestamp.now().normalize()
    tx = load_frame(db, "transactions", user_id)
    inv = load_frame(db, "invoices", user_id)
    budgets = load_frame(db, "budgets", user_id)

    scores = {}
    monthly = monthly_table(tx)
    if not monthly.empty:
        with_income = monthly[monthly["income"] > 0]
        if with_income.empty:
            scores["profitability"] = 0.0
        else:
            margin = (with_income["net_profit"] / with_income["income"] * 100).mean()
            scores["profitability"] = _clamp(50 + margin)
        scores["cash_flow"] = _clamp((monthly["net_profit"] > 0).sum() / len(monthly) * 100)

        for name, value in (
            ("expense_control", _expense_control(tx)),
            ("budget", _budget(tx, budgets)),
        ):
            if value is not None:
                scores[name] = value

    receivables = _receivables(inv, today)
    if receivables is not None:
        scores["receivables"] = receivables

    if not scores:
        return {"scores": {}, "overall": 0, "band": "No data"}

    total_weight = sum(WEIGHTS[k] for k in scores)
    overall = round(sum(scores[k] * WEIGHTS[k] for k in scores) / total_weight, 1)
    return {"scores": scores, "overall": overall, "band": band(overall)}


# ---------------------------------------------------------------------------
# Summaries for the dashboard
# ---------------------------------------------------------------------------
def _pct_change(current, previous):
    if previous in (0, None) or pd.isna(previous):
        return None
    return float(round((current - previous) / previous * 100, 1))


def financial_summary(db, user_id, today=None):
    today = today or pd.Timestamp.now().normalize()
    monthly = monthly_table(load_frame(db, "transactions", user_id))
    overdue = round(_overdue_amount(load_frame(db, "invoices", user_id), today), 2)

    if monthly.empty:
        return {
            "has_data": False, "latest_month": "N/A", "revenue": 0, "expenses": 0,
            "net_profit": 0, "overdue_receivables": overdue,
            "revenue_change_pct": None, "expense_change_pct": None,
        }

    latest = monthly.iloc[-1]
    previous = monthly.iloc[-2] if len(monthly) > 1 else None
    return {
        "has_data": True,
        "latest_month": str(monthly.index[-1]),
        "revenue": round(float(latest["income"]), 2),
        "expenses": round(float(latest["expense"]), 2),
        "net_profit": round(float(latest["net_profit"]), 2),
        "overdue_receivables": overdue,
        "revenue_change_pct": None if previous is None else _pct_change(latest["income"], previous["income"]),
        "expense_change_pct": None if previous is None else _pct_change(latest["expense"], previous["expense"]),
    }


def monthly_trend(db, user_id, limit=12):
    monthly = monthly_table(load_frame(db, "transactions", user_id)).tail(limit)
    return [
        {
            "month": str(month),
            "income": round(float(row["income"]), 2),
            "expense": round(float(row["expense"]), 2),
            "net_profit": round(float(row["net_profit"]), 2),
        }
        for month, row in monthly.iterrows()
    ]


# ---------------------------------------------------------------------------
# Sample data so a new account is not an empty screen
# ---------------------------------------------------------------------------
def load_demo_data(db, user_id, today=None):
    today = today or date.today()
    rng = random.Random(7)

    for (upload_id,) in db.execute(
        "SELECT id FROM uploads WHERE uploaded_by = ? AND filename = ?", (user_id, DEMO_FILENAME)
    ).fetchall():
        db.execute("DELETE FROM transactions WHERE upload_id = ? AND user_id = ?", (upload_id, user_id))
        db.execute("DELETE FROM invoices WHERE upload_id = ? AND user_id = ?", (upload_id, user_id))
        db.execute("DELETE FROM uploads WHERE id = ?", (upload_id,))

    months = []
    for back in range(5, -1, -1):
        year, month = today.year, today.month - back
        while month <= 0:
            month += 12
            year -= 1
        months.append((year, month))

    rows = []

    def add(year, month, day, amount, kind, category, description):
        is_latest = (year, month) == months[-1]
        day = min(day, today.day) if is_latest else day
        rows.append({
            "txn_date": date(year, month, day).isoformat(), "amount": float(amount),
            "type": kind, "category": category, "description": description,
            "customer_vendor": "", "account": "Main account",
        })

    for index, (year, month) in enumerate(months):
        is_latest = index == len(months) - 1
        for i in range(10):
            add(year, month, 2 + i * 2, rng.randint(150_000, 280_000), "income", "Product Sales", "Shop sales")
        for i in range(2):
            add(year, month, 10 + i * 9, rng.randint(120_000, 200_000), "income", "Services", "Service income")
        add(year, month, 1, 450_000, "expense", "Rent", "Shop rent")
        add(year, month, 25, 800_000, "expense", "Salaries", "Staff salaries")
        add(year, month, 8, rng.randint(520_000, 640_000), "expense", "Inventory", "Stock purchase")
        add(year, month, 12, rng.randint(80_000, 100_000), "expense", "Utilities", "Power and water")
        add(year, month, 15, 210_000 if is_latest else rng.randint(100_000, 130_000), "expense", "Marketing", "Adverts")
        add(year, month, 18, rng.randint(60_000, 90_000), "expense", "Transport", "Deliveries")

    stamp = lambda days: (today + timedelta(days=days)).isoformat()
    invoices = pd.DataFrame([
        {"customer": "Adebayo Stores", "amount": 380_000, "due_date": stamp(-40), "payment_date": stamp(-35), "status": "paid"},
        {"customer": "Kemi Fashion", "amount": 260_000, "due_date": stamp(-20), "payment_date": stamp(-18), "status": "paid"},
        {"customer": "Lagos Eats Ltd", "amount": 540_000, "due_date": stamp(-12), "payment_date": None, "status": "unpaid"},
        {"customer": "Greenfield Schools", "amount": 720_000, "due_date": stamp(10), "payment_date": None, "status": "unpaid"},
        {"customer": "Okoro and Sons", "amount": 310_000, "due_date": stamp(25), "payment_date": None, "status": "unpaid"},
    ])
    period = f"{months[-1][0]}-{months[-1][1]:02d}"
    budgets = pd.DataFrame([
        {"category": c, "period": period, "budgeted_amount": a}
        for c, a in [("Rent", 450_000), ("Salaries", 800_000), ("Inventory", 600_000),
                     ("Utilities", 90_000), ("Marketing", 120_000), ("Transport", 80_000)]
    ])

    save_upload(db, user_id, "transactions", DEMO_FILENAME, pd.DataFrame(rows))
    save_upload(db, user_id, "invoices", DEMO_FILENAME, invoices)
    save_upload(db, user_id, "budgets", DEMO_FILENAME, budgets)
    return len(rows)
