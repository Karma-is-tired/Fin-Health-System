"""Run with:  python -m pytest -q"""
import os
import tempfile

# These must be set BEFORE main is imported.
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["SECRET_KEY"] = "test-secret-key-for-the-test-suite-only-1234567890"
os.environ["PBKDF2_ITERATIONS"] = "1000"  # fast hashing for tests

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)
PASSWORD = "password123"
CSV = (
    "date,amount,type,category\n"
    "2026-01-05,1000,income,Sales\n"
    "2026-01-10,400,expense,Rent\n"
    "2026-02-05,1200,income,Sales\n"
    "2026-02-10,500,expense,Rent\n"
)


def register(email):
    res = client.post("/signup", json={"email": email, "password": PASSWORD})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def upload_csv(headers, kind="transactions", text=CSV, name="data.csv"):
    return client.post(f"/upload/{kind}", headers=headers, files={"file": (name, text.encode(), "text/csv")})


def test_root_is_public():
    assert client.get("/").status_code == 200


def test_signup_signs_you_in_and_login_works_later():
    headers = register("ada@example.com")
    assert client.get("/me", headers=headers).json() == {"email": "ada@example.com"}

    res = client.post("/login", data={"username": "ADA@example.com", "password": PASSWORD})
    assert res.status_code == 200 and res.json()["access_token"]


def test_signup_rejects_duplicates_bad_emails_and_short_passwords():
    register("dup@example.com")
    assert client.post("/signup", json={"email": "dup@example.com", "password": PASSWORD}).status_code == 400
    assert client.post("/signup", json={"email": "not-an-email", "password": PASSWORD}).status_code == 400
    assert client.post("/signup", json={"email": "short@example.com", "password": "abc"}).status_code == 400


def test_wrong_password_is_rejected_and_repeated_failures_lock_out():
    register("lock@example.com")
    for _ in range(5):
        res = client.post("/login", data={"username": "lock@example.com", "password": "wrong-password"})
        assert res.status_code == 401
    res = client.post("/login", data={"username": "lock@example.com", "password": "wrong-password"})
    assert res.status_code == 429


def test_protected_routes_need_a_token():
    for path in ("/health-score", "/financial-summary", "/monthly-trend", "/history", "/download-report", "/me"):
        assert client.get(path).status_code == 401
    assert client.get("/health-score", headers={"Authorization": "Bearer nonsense"}).status_code == 401


def test_new_account_starts_empty():
    headers = register("empty@example.com")
    assert client.get("/health-score", headers=headers).json()["scores"] == {}
    assert client.get("/financial-summary", headers=headers).json()["has_data"] is False
    assert client.get("/monthly-trend", headers=headers).json() == []


def test_upload_then_scores_summary_and_trend():
    headers = register("upload@example.com")
    res = upload_csv(headers)
    assert res.status_code == 200 and "Added 4" in res.json()["message"]

    scores = client.get("/health-score", headers=headers).json()
    assert 0 <= scores["overall"] <= 100
    assert {"profitability", "cash_flow"} <= set(scores["scores"])

    summary = client.get("/financial-summary", headers=headers).json()
    assert summary["latest_month"] == "2026-02" and summary["revenue"] == 1200
    assert len(client.get("/monthly-trend", headers=headers).json()) == 2


def test_users_cannot_see_each_others_data():
    first = register("first@example.com")
    second = register("second@example.com")
    upload_csv(first)
    assert client.get("/financial-summary", headers=first).json()["has_data"] is True
    assert client.get("/financial-summary", headers=second).json()["has_data"] is False
    assert client.get("/monthly-trend", headers=second).json() == []


def test_bad_uploads_get_clear_400_errors():
    headers = register("bad@example.com")
    assert upload_csv(headers, name="notes.txt").status_code == 400
    assert upload_csv(headers, text="foo,bar\n1,2\n").status_code == 400
    assert upload_csv(headers, text="date,amount\n2026-01-01,100\n").status_code == 400  # income or expense?
    assert upload_csv(headers, kind="mystery").status_code == 404


def test_sample_data_fills_all_five_scores():
    headers = register("demo@example.com")
    assert client.post("/load-demo-data", headers=headers).status_code == 200
    scores = client.get("/health-score", headers=headers).json()["scores"]
    assert set(scores) == {"profitability", "cash_flow", "expense_control", "receivables", "budget"}
    # Loading it twice must not double the numbers.
    before = client.get("/financial-summary", headers=headers).json()["revenue"]
    client.post("/load-demo-data", headers=headers)
    assert client.get("/financial-summary", headers=headers).json()["revenue"] == before


def test_report_download_and_history():
    headers = register("report@example.com")
    assert client.get("/download-report", headers=headers).status_code == 400  # no data yet
    upload_csv(headers)

    res = client.get("/download-report", headers=headers)
    assert res.status_code == 200 and res.content[:2] == b"PK"  # a .docx is a zip file

    history = client.get("/history", headers=headers).json()
    assert len(history) == 1
    assert client.get(f"/download-past-report/{history[0]['id']}", headers=headers).status_code == 200

    other = register("report-other@example.com")
    assert client.get(f"/download-past-report/{history[0]['id']}", headers=other).status_code == 404


def test_the_dangerous_upgrade_route_is_gone():
    headers = register("route@example.com")
    assert client.get("/run-db-upgrade", headers=headers).status_code == 404
